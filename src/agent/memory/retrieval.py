import sys
from .schema import Conversation, Preference, Context
import numpy as np
from typing import List, Tuple
import ollama

EMBEDDING_MODEL = "all-minilm:latest"

try:
    installed_models: ollama.ListResponse = ollama.list()
    installed_model_names = [m.model for m in installed_models.models]
    print(f"Found installed Ollama models: {installed_model_names}")
    if EMBEDDING_MODEL not in installed_model_names:
        print(f"Model {EMBEDDING_MODEL} not found. Installing...")
        ollama.pull(EMBEDDING_MODEL)
        print(f"Model {EMBEDDING_MODEL} installed successfully.")
except Exception as e:
    print(f"Ollama client not installed or not running: {e}")
    print("Please install the ollama client and start the app.")
    sys.exit(1)


def retrieve(
    conversations: list[Conversation], conversation_index: int, top_k: int = 5, long_term_retrieval: bool = True
) -> List[Preference]:
    """Retrieve relevant preference memories from these conversations, based on the current conversation"""

    current_context = conversations[conversation_index]["context"]
    current_embedding = embed_context(current_context)

    memories = []
    context_similarities = []

    if not long_term_retrieval:
        return reversed(conversations[conversation_index]["preferences"])[:top_k] # Return the most recent preferences

    # Compare current context with all other conversations
    for i, conversation in enumerate(conversations):
        if i == conversation_index:
            context_sim = 1
        context_sim = compute_context_sim(current_embedding, conversation["context"])

        # add all preferences with the same context similarity
        prefs = conversation["preferences"]
        memories.extend(prefs)
        context_similarities.extend([context_sim] * len(prefs))

    # Sort memories by context similarity (highest to lowest)
    sorted_indices = np.argsort(context_similarities)[::-1]
    memories = [memories[i] for i in sorted_indices[:top_k]] # Return the most recent preferences of the most similar conversations
    return memories


def compute_context_sim(current_embedding, context):
    other_embedding = embed_context(context)
    dot_product = np.dot(current_embedding, other_embedding)
    return dot_product  # equal to cossim since norm is 1 for both


def embed_context(context: Context) -> np.ndarray:
    """Generate embeddings for a context using nomic-embed-text model"""

    # Convert to a single string
    text = f"The occasion is {context['occasion']}, the weather is {context['weather']}, the preferred style is {context['style']}"

    # Call ollama to get embedding(s)
    response = ollama.embed(model=EMBEDDING_MODEL, input=text)
    embeddings = np.array(response["embeddings"])

    # average embeddings if there are more than one. Ensure norm
    embedding = np.mean(embeddings, axis=0)
    norm = np.linalg.norm(embedding)
    if not np.isclose(norm, 1, rtol=1e-3):
        raise ValueError("Embedding is not normalized!")

    return embedding
