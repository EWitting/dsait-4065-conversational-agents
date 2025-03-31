import random
import string
import time

import requests
from mistralai import Mistral
from PIL import Image
from io import BytesIO
import os

class Generator:
    def __init__(self):
        # key_file_path = os.path.join(os.path.dirname(__file__), "mistral_api")
        self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "mistral-large-latest"
        self.initialisation_prompt = """You are a fashion outfit generator. Based on the provided CONTEXT (occasion), your Previous Suggestions (so that you know what was suggested in the conversation) and PREFERENCES (the preferences of the person regarding clothing), create an outfit with this structure:
1. Top: Upper garments (color, material, style)
2. Bottom: Lower garments (color, material, style)
3. Footwear: Shoes/boots description
4. Accessories: Essential add-ons
5. Suggestions: 1 styling tip

Be specific with colors and materials for image generation.

Provide me a short summary of the outfit you create so that I can use the text to speech model to describe the outfit. Add it a the end and start with Summary:
"""
        # Create a cache directory if it doesn't exist
        self.cache_dir = os.path.join(os.path.dirname(__file__), "image_cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def generate(self, context: str, user_attributes: dict, memories: list[str], previous_suggestions_text: list[str] = None):
        if previous_suggestions_text is None:
            previous_suggestions_text = []
        text = self.generate_text(context, user_attributes, memories, previous_suggestions_text)
        image = self.generate_image(text)
        return text, image

    def generate_text(self, context: str, user_attributes: dict, memories: list[str], previous_suggestions_text: list[str]) -> str:
        # Construct the prompt using the initialization prompt, context and memories
        prompt = f"{self.initialisation_prompt}\n\nUSER: {user_attributes}\nCONTEXT: {context}\n\n"

        if memories:
            prompt += "PREFERENCES:\n"
            for i, memory in enumerate(memories):
                prompt += f"{i + 1}. {memory}\n"
        if previous_suggestions_text:
            prompt += "PREVIOUS SUGGESTIONS:\n"
            for i, suggestion in enumerate(previous_suggestions_text):
                prompt += f"{i + 1}. {suggestion}\n"

        # Generate text using Mistral API
        chat_response = self.mistral_client.chat.complete(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        return chat_response.choices[0].message.content

    def generate_image(self, description: str) -> Image:
        # Generate a unique request identifier using timestamp and random string
        unique_id = f"{int(time.time())}_{self._random_string(6)}"

        # URL encode the prompt
        intro_prompt = "Show the outfit you generate on a manikin and only the manikin should be in the picture. The outfit consists of:\n"
        image_prompt = f"{intro_prompt}{description}"

        encoded_prompt = image_prompt.replace(' ', '%20')

        # Add a unique cache-busting parameter to avoid getting the same image
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=384&height=512&model=flux&seed={unique_id}"

        # Create a unique filename for this request
        cache_filename = os.path.join(self.cache_dir, f"outfit_{unique_id}.png")

        # Make the GET request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Load the image from the response
            image = Image.open(BytesIO(response.content))

            # Save the image to the cache
            image.save(cache_filename)

            return image
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
            return None

    def _random_string(self, length=6):
        """Generate a random string to ensure uniqueness"""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))


if __name__ == "__main__":
    generator = Generator()
    context = "Attending a summer wedding on a beach"
    memories = [
        "Prefers bright colors",
        "Likes comfortable but elegant clothes",
        "Dislikes formal suits"
    ]

    text, image = generator.generate(context, memories, [])
    print(f"Generated outfit:\n{text}")

    if image:
        image.show()
