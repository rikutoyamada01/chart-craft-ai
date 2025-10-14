from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session

from app import crud
from app.api import deps
from app.models.circuit import (
    CircuitCreate,
    CircuitGenerateFromPromptRequest,
    CircuitPublic,
    CircuitRenderRequest,
    CircuitUpdate,
)
from app.services.ai_yaml_generator import ai_yaml_generator
from app.services.circuit_renderer import circuit_renderer

router = APIRouter()


@router.post("/", response_model=CircuitPublic)
def create_circuit(
    *, session: Session = Depends(deps.get_db), circuit_in: CircuitCreate
) -> Any:
    """
    Create new circuit.
    """
    circuit = crud.create_circuit(session=session, circuit_in=circuit_in)
    return circuit


@router.get("/", response_model=list[CircuitPublic])
def read_circuits(
    *, session: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve circuits.
    """
    circuits = crud.get_multi_circuits(session=session, skip=skip, limit=limit)
    return circuits


@router.get("/{id}", response_model=CircuitPublic)
def read_circuit(*, session: Session = Depends(deps.get_db), id: int) -> Any:
    """
    Get circuit by ID.
    """
    circuit = crud.get_circuit(session=session, id=id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit


@router.put("/{id}", response_model=CircuitPublic)
def update_circuit(
    *, session: Session = Depends(deps.get_db), id: int, circuit_in: CircuitUpdate
) -> Any:
    """
    Update a circuit.
    """
    db_circuit = crud.get_circuit(session=session, id=id)
    if not db_circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    circuit = crud.update_circuit(
        session=session, db_circuit=db_circuit, circuit_in=circuit_in
    )
    return circuit


@router.delete("/{id}", response_model=CircuitPublic)
def delete_circuit(*, session: Session = Depends(deps.get_db), id: int) -> Any:
    """
    Delete a circuit.
    """
    circuit = crud.remove_circuit(session=session, id=id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit


@router.post("/render", response_class=Response)
def render_circuit_stateless(
    *, request: CircuitRenderRequest, format: str = "svg"
) -> Response:
    """
    Render a circuit diagram from a YAML definition without saving it.
    """
    file_content = circuit_renderer.render_from_yaml(
        yaml_data=request.content, format=format
    )
    return Response(content=file_content.content, media_type=file_content.mime_type)


@router.get("/{id}/render", response_class=Response)
def render_saved_circuit(
    *, session: Session = Depends(deps.get_db), id: int, format: str = "svg"
) -> Response:
    """
    Render a saved circuit diagram by its ID.
    """
    circuit = crud.get_circuit(session=session, id=id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")

    file_content = circuit_renderer.render_from_yaml(
        yaml_data=circuit.content, format=format
    )
    return Response(content=file_content.content, media_type=file_content.mime_type)


@router.post("/generate-and-render", response_class=Response)
def generate_and_render_circuit(
    *, request: CircuitGenerateFromPromptRequest, format: str = "svg"
) -> Response:
    """
    Generates a YAML from a prompt, renders it, and returns the image.
    """
    # Step 1: Generate YAML from prompt
    generated_yaml = ai_yaml_generator.generate(prompt=request.prompt)

    # Step 2: Render image from generated YAML
    file_content = circuit_renderer.render_from_yaml(
        yaml_data=generated_yaml, format=format
    )

    return Response(content=file_content.content, media_type=file_content.mime_type)
