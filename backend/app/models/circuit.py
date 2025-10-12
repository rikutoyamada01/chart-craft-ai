from pydantic import BaseModel, ConfigDict


class CircuitGenerationRequest(BaseModel):
    """回路生成リクエストのデータモデル"""

    circuit_yaml: str


class CircuitGenerationResponse(BaseModel):
    """回路生成レスポンスのデータモデル（今はダミー）"""

    message: str
    yaml_data: str


class Position(BaseModel):
    x: int
    y: int


class Port(BaseModel):
    name: str
    direction: str | None = None


class ComponentProperties(BaseModel):
    # 他の未知のプロパティ（例: voltage, resistance）も許容する設定
    model_config = ConfigDict(extra="allow")

    # YAML仕様で定義されているプロパティを明示的に定義し、構造を検証
    position: Position | None = None
    rotation: float | None = None
    ports: list["Port"] | None = None


class ConnectionEndpoint(BaseModel):
    component_id: str
    port: str | None = None
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


class Circuit(BaseModel):
    name: str
    description: str | None = None
    components: list[Component]
    connections: list[Connection]


class CircuitData(BaseModel):
    circuit: Circuit
