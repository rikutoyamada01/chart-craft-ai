def get_prompt_for_image_generation() -> str:
    # Basic prompt, can be improved with schema and examples later
    return """
You are an expert in electronic circuit design.
Analyze the provided image of a circuit diagram and generate its representation in the custom YAML format described below.

The YAML format should follow this structure:
- A top-level `circuit` object.
- A `name` for the circuit.
- A list of `components`, each with an `id`, `type`, and `properties`.
- A list of `connections`, each specifying the `source` and `target` component IDs, `port_index`, and optional `terminal` or `port`.

Example of a simple resistor-LED circuit:
```yaml
circuit:
  name: "Simple LED Circuit"
  components:
    - id: "R1"
      type: "resistor"
      properties:
        resistance: "1k"
        position: { x: 50, y: 50 }
    - id: "D1"
      type: "led"
      properties:
        color: "red"
        position: { x: 150, y: 50 }
    - id: "V1"
      type: "voltage_source"
      properties:
        voltage: "5V"
        position: { x: 100, y: 150 }
  connections:
    - source:
        component_id: "V1"
        port_index: 0 # Assuming 0 is positive terminal
      target:
        component_id: "R1"
        port_index: 0 # Assuming 0 is first terminal
    - source:
        component_id: "R1"
        port_index: 1 # Assuming 1 is second terminal
      target:
        component_id: "D1"
        port_index: 0 # Assuming 0 is anode
    - source:
        component_id: "D1"
        port_index: 1 # Assuming 1 is cathode
      target:
        component_id: "V1"
        port_index: 1 # Assuming 1 is negative terminal
```

Now, analyze the user-provided image and generate the corresponding YAML code block.
"""


def get_prompt_for_text_generation(user_prompt: str) -> str:
    # This is a placeholder for the text generation prompt
    return f"""
You are an expert in electronic circuit design.
Based on the user's request, generate a circuit in the custom YAML format.

User request: "{user_prompt}"

The YAML format should follow this structure:
- A top-level `circuit` object.
- A `name` for the circuit.
- A list of `components`, each with an `id`, `type`, and `properties`.
- A list of `connections`, each specifying the `from` and `to` component IDs and ports.

Example of a simple resistor-LED circuit:
```yaml
circuit:
  name: "Simple LED Circuit"
  components:
    - id: "R1"
      type: "resistor"
      properties:
        resistance: "1k"
        position: {{ x: 50, y: 50 }}
    - id: "D1"
      type: "led"
      properties:
        color: "red"
        position: {{ x: 150, y: 50 }}
    - id: "V1"
      type: "voltage_source"
      properties:
        voltage: "5V"
        position: {{ x: 100, y: 150 }}
  connections:
    - from: "V1.+"
      to: "R1.1"
    - from: "R1.2"
      to: "D1.A"
    - from: "D1.C"
      to: "V1.-"
```

Now, fulfill the user's request and generate the corresponding YAML code block.
"""
