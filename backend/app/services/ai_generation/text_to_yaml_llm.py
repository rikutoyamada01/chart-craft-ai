from .base import YamlGenerator


class TextToYamlLLMGenerator(YamlGenerator):
    """Generates YAML from a text prompt using an LLM."""

    def generate(self, input_data: str) -> str:
        # For now, this is a mock implementation.
        # In the future, this will call the LLM API.
        return f"""circuit:
  name: "Generated from Text: {input_data}"
  components:
    - id: "R1"
      type: "resistor"
      properties:
        resistance: "1k"
        position: {{ x: 100, y: 100 }}
  connections: []
"""
