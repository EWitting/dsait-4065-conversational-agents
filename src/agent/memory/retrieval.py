from .schema import Conversation, Preference, Context
import numpy as np
from typing import List, Tuple
import ollama


def retrieve(conversations: list[Conversation],
             conversation_index: int,
             top_k: int = 5) -> List[Preference]:
    """Retrieve relevant preference memories from these conversations, based on the current conversation"""

    current_context = conversations[conversation_index]['context']
    current_embedding = embed_context(current_context)

    memories = []
    context_similarities = []

    # Compare current context with all other conversations
    for i, conversation in enumerate(conversations):
        if i == conversation_index:
            context_sim = 1
        context_sim = compute_context_sim(current_embedding, conversation['context'])

        # add all preferences with the same context similarity
        prefs = conversation['preferences']
        memories.extend(prefs)
        context_similarities.extend([context_sim] * len(prefs))

    # Sort memories by context similarity (highest to lowest)
    sorted_indices = np.argsort(context_similarities)[::-1]
    memories = [memories[i] for i in sorted_indices[top_k]]
    return memories

def compute_context_sim(current_embedding, context):
    other_embedding = embed_context(context)
    dot_product = np.dot(current_embedding, other_embedding)
    return dot_product # equal to cossim since norm is 1 for both

def embed_context(context: Context) -> np.ndarray:
    """Generate embeddings for a context using nomic-embed-text model"""
    
    # Convert to a single string
    text = f"The occasion is {context['occasion']}, the weather is {context['weather']}, the preferred style is {context['style']}"
    
    # Call ollama to get embedding(s)
    response = ollama.embed(
        model='all-minilm',
        input=text)
    embeddings = np.array(response['embeddings'])

    # average embeddings if there are more than one. Ensure norm
    embedding = np.mean(embeddings, axis=0)
    norm = np.linalg.norm(embedding)
    if not np.isclose(norm, 1, rtol=1e-3):
        raise ValueError("Embedding is not normalized!")
    
    return embedding



