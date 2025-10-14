class AiYamlGenerator:
    def generate(self, prompt: str) -> str:
        """
        Generates a YAML circuit definition from a natural language prompt.
        (This is a mock implementation).
        """
        prompt = prompt.lower()

        if "resistor" in prompt and "led" in prompt:
            return self._get_resistor_led_yaml()
        elif "resistor" in prompt:
            return self._get_resistor_yaml()
        elif "battery" in prompt:
            return self._get_battery_yaml()
        else:
            return self._get_default_yaml(prompt)

    def _get_resistor_yaml(self) -> str:
        return """
circuit:
  name: "Resistor Circuit"
  components:
    - id: "R1"
      type: "resistor"
      properties:
        resistance: "1k"
        position: { x: 50, y: 50 }
    - id: "J1"
      type: "junction"
      properties:
        position: { x: 50, y: 100 }
  connections:
    - source: { component_id: "R1" }
      target: { component_id: "J1" }
"""

    def _get_resistor_led_yaml(self) -> str:
        return """
circuit:
  name: "Resistor-LED Circuit"
  components:
    - id: "R1"
      type: "resistor"
      properties:
        resistance: "330"
        position: { x: 50, y: 50 }
    - id: "D1"
      type: "led"
      properties:
        position: { x: 50, y: 150 }
  connections:
    - source: { component_id: "R1" }
      target: { component_id: "D1" }
"""

    def _get_battery_yaml(self) -> str:
        return """
circuit:
  name: "Battery Circuit"
  components:
    - id: "BAT1"
      type: "battery"
      properties:
        voltage: "9V"
        position: { x: 50, y: 50 }
  connections: []
"""

    def _get_default_yaml(self, prompt: str) -> str:
        return f"""
circuit:
  name: "Default Circuit"
  description: "Could not generate a specific circuit for the prompt: {prompt}"
  components:
    - id: "j1"
      type: "junction"
      properties:
        position: {{x: 50, y: 50}}
  connections: []
"""


ai_yaml_generator = AiYamlGenerator()
