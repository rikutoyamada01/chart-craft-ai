from .base import YamlGenerator
from .image_to_yaml_gemini import ImageToYamlGeminiGenerator
from .image_to_yaml_vision import ImageToYamlVisionGenerator
from .text_to_yaml_gemini import TextToYamlGeminiGenerator
from .text_to_yaml_llm import TextToYamlLLMGenerator
from .text_to_yaml_openai import TextToYamlOpenAIGenerator


class GeneratorFactory:
    def __init__(self):
        self._generator_classes = {
            "text_llm_v1": TextToYamlLLMGenerator,
            "image_vision_v1": ImageToYamlVisionGenerator,
            "text_openai_v1": TextToYamlOpenAIGenerator,
            "image_gemini_vision_v1": ImageToYamlGeminiGenerator,
            "text_gemini_pro_v1": TextToYamlGeminiGenerator,
        }
        self._generators = {}

    def get_generator(self, generator_name: str) -> YamlGenerator:
        if generator_name not in self._generators:
            if generator_name in self._generator_classes:
                self._generators[generator_name] = self._generator_classes[
                    generator_name
                ]()
            else:
                raise ValueError(f"Generator '{generator_name}' not found.")
        return self._generators[generator_name]


generator_factory = GeneratorFactory()
