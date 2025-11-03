import datetime

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel

# =================================================================
# 1. SQLModel for Database Table and API Schemas
# =================================================================


class CircuitBase(SQLModel):
    """Base model with shared attributes for a circuit."""

    name: str = Field(index=True)
    description: str | None = Field(default=None, index=True)
    content: str  # The YAML content of the circuit


class Circuit(CircuitBase, table=True):
    """Database model for a circuit."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.datetime.utcnow},
    )


class CircuitPublic(CircuitBase):
    """Schema for returning a circuit to the client."""

    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CircuitCreate(CircuitBase):
    """Schema for creating a new circuit."""

    pass


class CircuitUpdate(SQLModel):
    """Schema for updating a circuit (all fields optional)."""

    name: str | None = None
    description: str | None = None
    content: str | None = None


# =================================================================
# 2. Schemas for YAML content structure
#    (These models define the structure within the 'content' field)
# =================================================================


class Position(BaseModel):
    x: int
    y: int


class Port(BaseModel):
    name: str
    direction: str | None = None


class ComponentProperties(BaseModel):
    model_config = ConfigDict(extra="allow")
    position: Position | None = None
    rotation: float | None = None
    ports: list["Port"] | None = None


class ConnectionEndpoint(BaseModel):
    component_id: str
    port_index: int
    terminal: str | None = None


class Connection(BaseModel):
    source: ConnectionEndpoint
    target: ConnectionEndpoint


class Component(BaseModel):
    id: str
    type: str
    properties: ComponentProperties
    internal_components: list["Component"] | None = None
    internal_connections: list["Connection"] | None = None


Component.model_rebuild()


class CircuitSpec(BaseModel):
    name: str
    description: str | None = None
    components: list[Component]
    connections: list[Connection]


class CircuitData(BaseModel):
    circuit: CircuitSpec


# =================================================================
# 3. Schemas for specific endpoints
# =================================================================


class CircuitRenderRequest(BaseModel):
    """Request model for the stateless render endpoint."""

    content: str


class CircuitGenerateFromPromptRequest(BaseModel):
    """Request model for the AI prompt-based generation endpoint."""

    prompt: str
