import uuid

import yaml
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models.circuit import CircuitData, CircuitGenerationRequest
from app.services.formatters.svg_formatter import SvgFormatter

router = APIRouter()

# In-memory storage for circuit definitions
circuit_definitions: dict[uuid.UUID, str] = {}


@router.post("/definitions", status_code=201)
def save_circuit_definition(request: CircuitGenerationRequest) -> dict[str, uuid.UUID]:
    """
    Saves a circuit definition and returns a unique ID for it.
    """
    circuit_id = uuid.uuid4()
    circuit_definitions[circuit_id] = request.circuit_yaml
    return {"circuit_id": circuit_id}


@router.get("/{circuit_id}/render")
def render_circuit(circuit_id: uuid.UUID, format: str = "svg") -> Response:
    """
    Renders a circuit diagram from a saved definition.
    """
    if circuit_id not in circuit_definitions:
        raise HTTPException(status_code=404, detail="Circuit definition not found")

    if format.lower() != "svg":
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    yaml_data = circuit_definitions[circuit_id]
    try:
        data = yaml.safe_load(yaml_data)
        circuit_data = CircuitData.model_validate(data)
    except (yaml.YAMLError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML or data: {e}")

    formatter = SvgFormatter()
    file_content = formatter.format(circuit_data)

    return Response(content=file_content.content, media_type=file_content.mime_type)


@router.post("/generate")
def generate_circuit(_request: CircuitGenerationRequest) -> Response:
    """
    Accepts a natural language prompt and returns an SVG circuit diagram.
    For now, it uses a dummy YAML definition.
    """
    # TODO: In the future, use the request.prompt to call an AI model to generate YAML.

    # For now, use a hardcoded dummy YAML.
    dummy_yaml = """
    circuit:
      name: "Dummy Circuit"
      components:
        - id: "j1"
          type: "junction"
          properties:
            position: {x: 50, y: 50}
        - id: "j2"
          type: "junction"
          properties:
            position: {x: 200, y: 100}
      connections:
        - source: {component_id: "j1"}
          target: {component_id: "j2"}
    """

    try:
        data = yaml.safe_load(dummy_yaml)
        circuit_data = CircuitData.model_validate(data)
    except (yaml.YAMLError, ValueError) as e:
        # This should not happen with a hardcoded valid YAML, but it's good practice.
        raise HTTPException(status_code=500, detail=f"Internal YAML error: {e}")

    formatter = SvgFormatter()
    file_content = formatter.format(circuit_data)

    return Response(content=file_content.content, media_type=file_content.mime_type)
