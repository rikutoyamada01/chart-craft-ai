from .base import YamlGenerator
from .image_to_yaml_gemini import ImageToYamlGeminiGenerator
from .image_to_yaml_vision import ImageToYamlVisionGenerator
from .text_to_yaml_gemini import TextToYamlGeminiGenerator
from .text_to_yaml_llm import TextToYamlLLMGenerator
from .text_to_yaml_openai import TextToYamlOpenAIGenerator


class GeneratorFactory:
    def __init__(self):
        self._generators = {
            "text_llm_v1": TextToYamlLLMGenerator(),
            "image_vision_v1": ImageToYamlVisionGenerator(),
            "text_openai_v1": TextToYamlOpenAIGenerator(),
            "image_gemini_vision_v1": ImageToYamlGeminiGenerator(),
            "text_gemini_pro_v1": TextToYamlGeminiGenerator(),
        }

    def get_generator(self, generator_name: str) -> YamlGenerator:
        generator = self._generators.get(generator_name)
        if not generator:
            raise ValueError(f"Generator '{generator_name}' not found.")
        return generator


generator_factory = GeneratorFactory()
