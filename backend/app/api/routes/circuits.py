from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlmodel import Session

from app import crud
from app.api import deps
from app.models.circuit import (
    CircuitCreate,
    CircuitPublic,
    CircuitRenderRequest,
    CircuitUpdate,
)
from app.services.ai_generation.factory import generator_factory
from app.services.circuit_exporter import circuit_exporter

router = APIRouter()


@router.post("/", response_model=CircuitPublic, status_code=201)
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
    file_content = circuit_exporter.render_from_yaml(
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

    file_content = circuit_exporter.render_from_yaml(
        yaml_data=circuit.content, format=format
    )
    return Response(content=file_content.content, media_type=file_content.mime_type)


@router.post("/generate-and-render", response_class=Response)
async def generate_and_render_circuit(
    *,
    generator_name: str = Form(...),
    prompt: str = Form(None),
    image: UploadFile = File(None),
    format: str = Form("svg"),
) -> Response:
    """
    Generates a YAML from a prompt or an image, renders it, and returns the image.
    """
    try:
        generator = generator_factory.get_generator(generator_name)

        if prompt:
            input_data = prompt
        elif image:
            input_data = await image.read()
        else:
            raise HTTPException(
                status_code=400, detail="Either 'prompt' or 'image' must be provided."
            )

        generated_yaml = generator.generate(input_data)

        file_content = circuit_exporter.render_from_yaml(
            yaml_data=generated_yaml, format=format
        )

        return Response(content=file_content.content, media_type=file_content.mime_type)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")
