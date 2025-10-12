import uuid

from fastapi.testclient import TestClient

from app.core.config import settings


def test_save_and_render_circuit(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    # Define a simple YAML for a circuit
    circuit_yaml = """
    circuit:
      name: "Test Circuit"
      components:
        - id: "j1"
          type: "junction"
          properties:
            position: {x: 10, y: 10}
        - id: "j2"
          type: "junction"
          properties:
            position: {x: 100, y: 50}
      connections:
        - source: {component_id: "j1"}
          target: {component_id: "j2"}
    """
    # 1. Save the circuit definition
    response = client.post(
        f"{settings.API_V1_STR}/circuits/definitions",
        headers=superuser_token_headers,
        json={"circuit_yaml": circuit_yaml},
    )
    assert response.status_code == 201
    data = response.json()
    assert "circuit_id" in data
    circuit_id = data["circuit_id"]

    # 2. Render the circuit
    response = client.get(
        f"{settings.API_V1_STR}/circuits/{circuit_id}/render?format=svg",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert "<svg" in response.text


def test_render_circuit_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    random_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/circuits/{random_id}/render",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_render_circuit_unsupported_format(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    circuit_yaml = """
    circuit:
      name: "Test Circuit"
      components: []
      connections: []
    """
    response = client.post(
        f"{settings.API_V1_STR}/circuits/definitions",
        headers=superuser_token_headers,
        json={"circuit_yaml": circuit_yaml},
    )
    circuit_id = response.json()["circuit_id"]

    response = client.get(
        f"{settings.API_V1_STR}/circuits/{circuit_id}/render?format=png",
        headers=superuser_token_headers,
    )
    assert response.status_code == 400
