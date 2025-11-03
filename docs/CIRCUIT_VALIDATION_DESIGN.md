/# Circuit Validation Algorithm - Definition and Design Document

## 1. Overview and Goal

**Goal:** To establish a quality gate for AI-generated circuit definitions. This algorithm will act as a validation layer, ensuring any given circuit YAML is both logically correct as a circuit and visually coherent as a schematic before it is rendered.

**Purpose:** To prevent the generation of nonsensical or unreadable circuit diagrams, thereby improving the reliability and quality of the final output.

## 2. System Architecture

The `CircuitValidator` will be a new service that integrates into the existing data flow after the circuit definition is parsed but before the rendering process begins.

**Data Flow:**

```
[AI Model] -> [YAML String] -> [Parser] -> [CircuitData Object] -> [CircuitValidator] -> [SvgFormatter] -> [SVG Output]
```

The validator will be implemented as a class, `CircuitValidator`, located in a new module at `backend/app/services/validation/circuit_validator.py`.

## 3. Detailed Requirements & Verification Methods

### 3.1. Logical Validation Requirements

These checks ensure the circuit is electronically sound.

*   **REQ-L1: No Floating Ports**
    *   **Requirement:** All component ports defined in the circuit must be part of at least one connection.
    *   **Verification Method:**
        1.  Build a set of all ports mentioned in the `connections` list.
        2.  Iterate through each component in the `components` list.
        3.  For each component, retrieve its list of valid ports (e.g., `["left", "right"]` for a resistor).
        4.  Check if each of these valid ports exists in the set of connected ports. If not, raise a validation error.

*   **REQ-L2: Complete Power Loops**
    *   **Requirement:** There must be at least one complete, non-shorted path from a power source (e.g., a `battery`) to ground (`gnd`).
    *   **Verification Method:**
        1.  Represent the circuit as a graph data structure where components are nodes and connections are edges.
        2.  Identify all power source components (e.g., `type: "battery"`).
        3.  For each power source, perform a graph traversal (e.g., Depth-First Search - DFS) starting from its positive terminal.
        4.  The traversal must not visit the source's own negative terminal directly (see REQ-L3).
        5.  Verify that the traversal can reach a designated `gnd` node. If no path to ground is found for any power source, raise an error.

*   **REQ-L3: No Short Circuits**
    *   **Requirement:** A power source's positive and negative terminals must not be connected directly or through zero-resistance paths.
    *   **Verification Method:**
        1.  During the graph traversal for REQ-L2, if the path from the positive terminal reaches the negative terminal of the same component without passing through any load-bearing components (resistors, LEDs, etc.), it is a short circuit. A predefined list of "load-bearing" component types will be used to check this.

*   **REQ-L4: Valid Port Names**
    *   **Requirement:** All `port` names used in the `connections` list must be valid for the specified `component_id`.
    *   **Verification Method:**
        1.  When iterating through the `connections` list, for each `source` and `target`:
        2.  Look up the component by its `component_id`.
        3.  Get the corresponding renderer for the component type.
        4.  Call `get_port_position()` with the specified port name. If this call raises a `ValueError` (as currently implemented), the port name is invalid. Catch this exception and register a validation error.

### 3.2. Visual (Layout) Validation Requirements

These checks ensure the schematic will be readable.

*   **REQ-V1: No Component Overlaps**
    *   **Requirement:** The bounding boxes of any two components must not intersect.
    *   **Verification Method:**
        1.  For every unique pair of components in the circuit:
        2.  Retrieve the bounding box for each component using its renderer's `get_bounding_box()` method. Remember to account for rotation (e.g., a 50x10 resistor rotated 90 degrees becomes 10x50).
        3.  Calculate the absolute coordinates of each bounding box (min_x, min_y, max_x, max_y).
        4.  Perform an Axis-Aligned Bounding Box (AABB) intersection test. If `box1.max_x < box2.min_x` (and so on for all four checks) is false, the boxes overlap.

*   **REQ-V2: Minimum Component Spacing**
    *   **Requirement:** A minimum distance must be maintained between components.
    *   **Verification Method:** Similar to REQ-V1, but perform the AABB test on bounding boxes that have been expanded by a predefined margin (e.g., `10` pixels).

*   **REQ-V3: Adherence to Layout Conventions**
    *   **Requirement:** The layout should follow standard schematic conventions.
    *   **Verification Method:** This will be a series of heuristic checks:
        *   **Power Placement:** Get all `battery` and `gnd` components. Check that the average `y` coordinate of batteries is significantly lower (visually higher on the canvas) than the average `y` coordinate of ground junctions.
        *   **Signal Flow:** Identify input components (e.g., components connected to nothing on one side) and output components. Check that the average `x` coordinate of inputs is less than that of outputs.
        *   **Component Rotation:** For specific contexts, check for conventional rotation. E.g., find a transistor and its collector resistor. If the resistor is connected between VCC and the collector, and its `x` coordinates are roughly aligned with the transistor, verify its `rotation` is 90 degrees.

## 4. Class and Data Structure Design

### 4.1. `ValidationError` Data Class

A structured object for reporting errors.

```python
# in backend/app/models/validation.py
from enum import Enum
from pydantic import BaseModel
from typing import list

class ErrorCode(str, Enum):
    LOGIC_FLOATING_PORT = "LOGIC_FLOATING_PORT"
    LOGIC_NO_POWER_LOOP = "LOGIC_NO_POWER_LOOP"
    LOGIC_SHORT_CIRCUIT = "LOGIC_SHORT_CIRCUIT"
    VISUAL_COMPONENT_OVERLAP = "VISUAL_COMPONENT_OVERLAP"
    VISUAL_MINIMUM_SPACING = "VISUAL_MINIMUM_SPACING"
    VISUAL_CONVENTION_VCC_HIGH = "VISUAL_CONVENTION_VCC_HIGH"
    VISUAL_CONVENTION_GND_LOW = "VISUAL_CONVENTION_GND_LOW"

class ValidationError(BaseModel):
    error_code: ErrorCode
    message: str
    offending_components: list[str] = []
```

### 4.2. `CircuitValidator` Class

```python
# in backend/app/services/validation/circuit_validator.py
from app.models.circuit import CircuitData
from app.models.validation import ValidationError

class CircuitValidator:
    def __init__(self, circuit_data: CircuitData):
        self.circuit = circuit_data.circuit
        self.components_by_id = {c.id: c for c in self.circuit.components}
        self._build_graph() # Build a graph representation for traversal checks

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        errors.extend(self._check_floating_ports())
        errors.extend(self._check_power_loops_and_shorts())
        errors.extend(self._check_component_overlaps())
        # ... other checks
        return errors

    def _build_graph(self):
        # Implementation to build an adjacency list or similar graph structure
        # from self.circuit.connections
        pass

    def _check_floating_ports(self) -> list[ValidationError]:
        # Implementation for REQ-L1
        pass

    def _check_power_loops_and_shorts(self) -> list[ValidationError]:
        # Implementation for REQ-L2 and REQ-L3 using graph traversal
        pass

    def _check_component_overlaps(self) -> list[ValidationError]:
        # Implementation for REQ-V1
        pass
```

## 5. Error Reporting Examples

When the validator is run, it will produce a JSON array of `ValidationError` objects.

**Example 1: Overlapping Components**
```json
[
  {
    "error_code": "VISUAL_COMPONENT_OVERLAP",
    "message": "Component R1 is overlapping with C1.",
    "offending_components": ["R1", "C1"]
  }
]
```

**Example 2: Floating Port**
```json
[
  {
    "error_code": "LOGIC_FLOATING_PORT",
    "message": "Port 'left' of component R2 is not connected.",
    "offending_components": ["R2"]
  }
]
```
