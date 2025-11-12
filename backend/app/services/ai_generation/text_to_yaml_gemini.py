import google.generativeai as genai

from app.core.config import settings

from .base import YamlGenerator

YAML_SPEC = """
# Circuit Diagram YAML Specification

This document defines a YAML format for describing the components, connections, properties, and physical layout information of a circuit diagram. This YAML is intended to be used for generating and managing circuit diagrams.

## 1. Overall Structure

The root element of the YAML is `circuit`, which contains meta-information about the circuit, component definitions, and connection information.

```yaml
circuit:
  name: "Circuit Name"
  description: "Circuit Description"
  components:
    # List of components
  connections:
    # List of connections
```

## 2. `circuit` Section

Provides basic information about the entire circuit.

*   `name` (string): The name of the circuit.
*   `description` (string): A brief description of the circuit.

## 3. `components` Section

Defines each element (parts, junctions, modules, etc.) that makes up the circuit. This is a list of objects.

### Common Properties of Each Component

*   `id` (string, required): A unique identifier for the component within the circuit.
*   `type` (string, required): The type of the component (e.g., `resistor`, `led`, `battery`, `junction`, `module`, `power_supply`).
*   `properties` (object): Describes component-specific attributes in a key-value format.

### Common Properties within `properties`

All components can have the following physical layout-related properties.

*   `position` (object): The physical position of the component.
    *   `x` (number): X-coordinate.
    *   `y` (number): Y-coordinate.
*   `rotation` (number, optional): The rotation angle of the component in degrees. Default is 0.

### `ports` Property (Terminals for external connections)

Some components (especially `module` and `power_supply`) can have `ports` as connection points with the outside.

*   `ports` (list of objects):
    *   `name` (string): The name of the port (e.g., `VCC`, `GND`, `input_power`).
    *   `direction` (string, optional): The direction of the port (e.g., `input`, `output`, `bidirectional`).

### Special Component Types

#### `type: "junction"` (Branching point)

A virtual component for branching wires.

*   `properties`: Usually has no special properties other than `position`. A `name` can also be added.

#### `type: "module"` (Module)

A component for defining reusable sub-circuits. A module itself has `components` and `connections`.

*   `properties`:
    *   `name` (string): The name of the module.
    *   `ports` (list of objects): Ports for the module to connect with the external circuit. Same structure as the `ports` property above.
*   `internal_components` (list of objects): A list of components contained within the module. Same structure as the top-level `components`, but `position` is relative to the module.
*   `internal_connections` (list of objects): Defines connections between components inside the module, and between the module's `ports` and internal components. Same structure as the top-level `connections`.

## 4. `connections` Section

Defines the connections between components in the circuit. This is a list of objects.

*   `source` (object): The starting point of the connection.
    *   `component_id` (string): The `id` of the source component.
    *   `port_index` (integer, required): The index of the port on the component.
    *   `terminal` (string, optional): A specific terminal name of the component (e.g., `positive`, `negative`, `anode`, `cathode`, `any`).
    *   `port` (string, optional): The external port name of a module.
*   `target` (object): The end point of the connection.
    *   `component_id` (string): The `id` of the target component.
    *   `port_index` (integer, required): The index of the port on the component.
    *   `terminal` (string, optional): A specific terminal name of the component.
    *   `port` (string, optional): The external port name of a module.
"""


class TextToYamlGeminiGenerator(YamlGenerator):
    """
    Generates YAML from a text prompt using the Google Gemini Pro model.
    """

    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google API key is not configured.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-pro-latest")

    def generate(self, input_data: str) -> str:
        """
        Generates a YAML circuit definition from the given text prompt.
        """
        system_prompt = f"""
You are an expert in electronic circuit design.
Your task is to generate a YAML representation of a circuit based on a user's text description.
The YAML should follow this specification:
{YAML_SPEC}

Please output only the YAML content, without any additional explanations or markdown formatting.
"""
        try:
            response = self.model.generate_content([system_prompt, input_data])

            # Extract YAML from the response
            text_response = response.text
            if "```yaml" in text_response:
                yaml_content = text_response.split("```yaml")[1].split("```")[0]
            elif "```" in text_response:
                yaml_content = text_response.split("```")[1].split("```")[0]
            else:
                yaml_content = text_response

            return yaml_content.strip()
        except Exception as e:
            raise ValueError(f"Gemini API call failed: {e}")
