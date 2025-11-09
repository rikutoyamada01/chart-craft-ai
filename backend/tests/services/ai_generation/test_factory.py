from unittest.mock import patch

import pytest

from app.services.ai_generation.factory import generator_factory
from app.services.ai_generation.image_to_yaml_vision import ImageToYamlVisionGenerator
from app.services.ai_generation.text_to_yaml_llm import TextToYamlLLMGenerator
from app.services.ai_generation.text_to_yaml_openai import TextToYamlOpenAIGenerator


def test_get_text_generator():
    """Tests that the factory returns the correct text generator instance and that it returns the expected dummy YAML."""
    generator = generator_factory.get_generator("text_llm_v1")
    assert isinstance(generator, TextToYamlLLMGenerator)

    prompt = "a simple resistor circuit"
    yaml_output = generator.generate(prompt)
    assert 'name: "Generated from Text: a simple resistor circuit"' in yaml_output
    assert 'type: "resistor"' in yaml_output


def test_get_image_generator():
    """Tests that the factory returns the correct image generator instance and that it returns the expected dummy YAML."""
    generator = generator_factory.get_generator("image_vision_v1")
    assert isinstance(generator, ImageToYamlVisionGenerator)

    # The actual image data doesn't matter for the mock generator
    image_data = b"dummy_image_data"
    yaml_output = generator.generate(image_data)
    assert 'name: "Generated from Image"' in yaml_output
    assert 'type: "capacitor"' in yaml_output


def test_get_unknown_generator():
    """Tests that a ValueError is raised for an unknown generator."""
    with pytest.raises(ValueError, match="Generator 'unknown_generator' not found."):
        generator_factory.get_generator("unknown_generator")


def test_get_openai_generator():
    """Tests that the factory returns the correct OpenAI generator instance."""
    with patch(
        "app.services.ai_generation.text_to_yaml_openai.settings"
    ) as mock_settings:
        mock_settings.OPENAI_API_KEY = "fake_api_key"
        generator = generator_factory.get_generator("text_openai_v1")
        assert isinstance(generator, TextToYamlOpenAIGenerator)
