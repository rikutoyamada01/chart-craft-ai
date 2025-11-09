from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_generation.text_to_yaml_openai import TextToYamlOpenAIGenerator


@pytest.fixture
def openai_generator():
    """Fixture to create a TextToYamlOpenAIGenerator instance with a mocked OpenAI client."""
    with patch("openai.OpenAI"):
        # Mock the settings attribute
        with patch(
            "app.services.ai_generation.text_to_yaml_openai.settings"
        ) as mock_settings:
            mock_settings.OPENAI_API_KEY = "fake_api_key"
            generator = TextToYamlOpenAIGenerator()
            # Replace the client instance with a mock
            generator.client = MagicMock()
            return generator


def test_generate_success(openai_generator):
    """Tests successful YAML generation."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "circuit:\n  name: 'test circuit'"
    openai_generator.client.chat.completions.create.return_value = mock_response

    prompt = "a simple test circuit"
    result = openai_generator.generate(prompt)

    assert "circuit:" in result
    assert "name: 'test circuit'" in result
    openai_generator.client.chat.completions.create.assert_called_once()


def test_generate_no_content(openai_generator):
    """Tests handling of no content in the API response."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = None
    openai_generator.client.chat.completions.create.return_value = mock_response

    with pytest.raises(
        ValueError, match="OpenAI API call failed: No content returned."
    ):
        openai_generator.generate("a prompt that returns no content")

    mock_response.choices = []
    openai_generator.client.chat.completions.create.return_value = mock_response
    with pytest.raises(
        ValueError, match="OpenAI API call failed: No content returned."
    ):
        openai_generator.generate("a prompt that returns no content")


def test_generate_api_error(openai_generator):
    """Tests handling of an OpenAI API error."""
    openai_generator.client.chat.completions.create.side_effect = Exception("API Error")

    with pytest.raises(ValueError, match="OpenAI API call failed: API Error"):
        openai_generator.generate("a prompt that causes an error")


def test_init_no_api_key():
    """Tests that the generator raises an error if the API key is not set."""
    with patch(
        "app.services.ai_generation.text_to_yaml_openai.settings"
    ) as mock_settings:
        mock_settings.OPENAI_API_KEY = None
        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set."):
            TextToYamlOpenAIGenerator()
