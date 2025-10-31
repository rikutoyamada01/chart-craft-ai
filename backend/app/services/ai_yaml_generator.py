class AiYamlGenerator:
    def generate(self, prompt: str) -> str:
        """
        Generates a YAML circuit definition from a natural language prompt.
        (This is a mock implementation).
        """
        prompt = prompt.lower()

        if "realistic" in prompt:
            return self._get_realistic_test_circuit_yaml()
        if "transistor switch" in prompt:
            return self._get_transistor_switch_yaml()
        elif "resistor" in prompt and "led" in prompt:
            return self._get_resistor_led_yaml()
        elif "capacitor" in prompt:
            return self._get_capacitor_yaml()
        elif "coil" in prompt:
            return self._get_coil_yaml()
        elif "resistor" in prompt:
            return self._get_resistor_yaml()
        elif "battery" in prompt:
            return self._get_battery_yaml()
        else:
            return self._get_default_yaml(prompt)

    def _get_realistic_test_circuit_yaml(self) -> str:
        # NOTE: This circuit avoids using rotation on components because the current
        # implementation of the renderers' get_port_position method does not
        # dynamically calculate port positions based on the rotation angle.
        # Using rotation would lead to incorrect wiring visuals.
        return """
circuit:
  name: "Realistic Transistor LED Switch"
  components:
    - id: "vcc"
      type: "battery"
      properties:
        position: {x: 200, y: 50}
    - id: "gnd"
      type: "junction"
      properties:
        position: {x: 200, y: 350}
    - id: "q1"
      type: "transistor_npn"
      properties:
        position: {x: 300, y: 200}
    - id: "r_led"
      type: "resistor"
      properties:
        position: {x: 400, y: 100}
        rotation: 90
    - id: "led1"
      type: "led"
      properties:
        position: {x: 400, y: 200}
    - id: "r_base"
      type: "resistor"
      properties:
        position: {x: 200, y: 200}
    - id: "j_in"
      type: "junction"
      properties:
        position: {x: 100, y: 200}
    - id: "j_vcc"
      type: "junction"
      properties:
        position: {x: 400, y: 50}

  connections:
    # Power connections
    - source: {component_id: "vcc", port: "positive"}
      target: {component_id: "j_vcc"}
    - source: {component_id: "vcc", port: "negative"}
      target: {component_id: "gnd"}
    - source: {component_id: "q1", port: "emitter"}
      target: {component_id: "gnd"}

    # Input signal path
    - source: {component_id: "j_in"}
      target: {component_id: "r_base", port: "left"}
    - source: {component_id: "r_base", port: "right"}
      target: {component_id: "q1", port: "base"}

    # Output LED path
    - source: {component_id: "j_vcc"}
      target: {component_id: "r_led", port: "left"}
    - source: {component_id: "r_led", port: "right"}
      target: {component_id: "led1", port: "left"}
    - source: {component_id: "led1", port: "right"}
      target: {component_id: "q1", port: "collector"}
"""

    def _get_transistor_switch_yaml(self) -> str:
        return """
circuit:
  name: "Transistor Switch"
  components:
    - id: "batt1"
      type: "battery"
      properties:
        position: {x: 50, y: 50}
        rotation: 0
    - id: "r1"
      type: "resistor"
      properties:
        position: {x: 200, y: 50}
        rotation: 0
    - id: "led1"
      type: "led"
      properties:
        position: {x: 350, y: 50}
        rotation: 0
    - id: "q1"
      type: "transistor_npn"
      properties:
        position: {x: 200, y: 200}
        rotation: 90
    - id: "gnd"
      type: "junction"
      properties:
        position: {x: 200, y: 350}
  connections:
    - source: {component_id: "batt1", port: "positive"}
      target: {component_id: "r1", port: "left"}
    - source: {component_id: "r1", port: "right"}
      target: {component_id: "led1", port: "left"}
    - source: {component_id: "led1", port: "right"}
      target: {component_id: "q1", port: "collector"}
    - source: {component_id: "batt1", port: "negative"}
      target: {component_id: "q1", port: "base"}
    - source: {component_id: "q1", port: "emitter"}
      target: {component_id: "gnd"}
"""

    def _get_resistor_yaml(self) -> str:
        return """
circuit:
  name: "Resistor Circuit"
  components:
    - id: "R1"
      type: "resistor"
      properties:
        resistance: "1k"
        position: { x: 100, y: 100 }
        rotation: 0
    - id: "J1"
      type: "junction"
      properties:
        position: { x: 200, y: 100 }
        rotation: 0
  connections:
    - source: { component_id: "R1", port: "right" }
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
        position: { x: 100, y: 100 }
        rotation: 0
    - id: "D1"
      type: "led"
      properties:
        position: { x: 200, y: 100 }
        rotation: 0
  connections:
    - source: { component_id: "R1", port: "right" }
      target: { component_id: "D1", port: "left" }
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
        position: { x: 100, y: 100 }
        rotation: 0
  connections: []
"""

    def _get_capacitor_yaml(self) -> str:
        return """
circuit:
  name: "Capacitor Circuit"
  components:
    - id: "C1"
      type: "capacitor"
      properties:
        capacitance: "100uF"
        position: { x: 100, y: 100 }
        rotation: 0
  connections: []
"""

    def _get_coil_yaml(self) -> str:
        return """
circuit:
  name: "Coil Circuit"
  components:
    - id: "L1"
      type: "coil"
      properties:
        inductance: "10mH"
        position: { x: 100, y: 100 }
        rotation: 0
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
