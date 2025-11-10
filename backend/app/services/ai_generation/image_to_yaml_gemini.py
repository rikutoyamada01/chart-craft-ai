import base64

import google.generativeai as genai
from app.core.config import settings

from .base import YamlGenerator
from .prompt import get_prompt_for_image_generation


class ImageToYamlGeminiGenerator(YamlGenerator):
    """Generates YAML from an image using the Google Gemini Pro Vision model."""

    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google API key is not configured.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro-vision")

    def generate(self, input_data: bytes) -> str:
        """
        Generates a YAML circuit definition from an image using Gemini Pro Vision.

        :param input_data: The image bytes.
        :return: The generated YAML string.
        """
        # Gemini API requires a PIL Image object, not base64
        # Let's try to create an image part from bytes directly
        # The SDK likely handles the conversion.
        image_part = {
            'mime_type': 'image/png', # Assuming PNG, might need to be more flexible
            'data': input_data
        }

        prompt = get_prompt_for_image_generation()
        
        # The content for gemini-pro-vision should be a list of parts
        response = self.model.generate_content([prompt, image_part])

        # Extract YAML from the response
        # Basic extraction assuming the YAML is in a code block
        text_response = response.text
        if "```yaml" in text_response:
            yaml_content = text_response.split("```yaml")[1].split("```")[0]
        elif "```" in text_response:
            yaml_content = text_response.split("```")[1].split("```")[0]
        else:
            # Fallback if no code block is found
            yaml_content = text_response

        return yaml_content.strip()
