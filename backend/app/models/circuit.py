from typing import Any

from pydantic import BaseModel, Field


class CircuitGenerationRequest(BaseModel):
    """回路生成リクエストのデータモデル"""

    prompt: str


class CircuitGenerationResponse(BaseModel):
    """回路生成レスポンスのデータモデル（今はダミー）"""

    message: str
    yaml_data: str


class Position(BaseModel):
    x: int
    y: int


class ConnectionEndpoint(BaseModel):
    component_id: str
    port: str | None = None
    terminal: str | None = None


class Connection(BaseModel):
    from_node: ConnectionEndpoint = Field(alias="from")
    to_node: ConnectionEndpoint = Field(alias="to")


class Component(BaseModel):
    id: str
    type: str
    properties: dict[str, Any]

    internal_components: list["Component"] | None = None
    internal_connections: list["Connection"] | None = None


Component.model_rebuild()


class Circuit(BaseModel):
    name: str
    description: str | None = None
    components: list[Component]
    connections: list[Connection]


class CircuitData(BaseModel):
    circuit: Circuit
