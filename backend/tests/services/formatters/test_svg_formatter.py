import xml.etree.ElementTree as ET

from app.models.circuit import (
    Circuit,
    CircuitData,
    Component,
    ComponentProperties,
    Connection,
    ConnectionEndpoint,
    Position,
)
from app.services.formatters.svg_formatter import SvgFormatter


def test_draw_junctions_and_connections() -> None:
    """
    Test that junctions and connections are drawn correctly.
    """
    components = [
        Component(
            id="j1",
            type="junction",
            properties=ComponentProperties(position=Position(x=10, y=10)),
        ),
        Component(
            id="j2",
            type="junction",
            properties=ComponentProperties(position=Position(x=100, y=50)),
        ),
    ]
    connections = [
        Connection(
            source=ConnectionEndpoint(component_id="j1"),
            target=ConnectionEndpoint(component_id="j2"),
        )
    ]
    circuit = Circuit(
        name="Test Circuit", components=components, connections=connections
    )
    circuit_data = CircuitData(circuit=circuit)

    formatter = SvgFormatter()
    file_content = formatter.format(circuit_data)

    assert file_content.filename == "circuit.svg"
    assert file_content.mime_type == "image/svg+xml"

    svg_content = file_content.content
    root = ET.fromstring(svg_content)

    circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
    assert len(circles) == 2

    # Note: The order of attributes is not guaranteed, so we check them individually
    assert circles[0].get("cx") == "10"
    assert circles[0].get("cy") == "10"
    assert circles[0].get("r") == "2"
    assert circles[0].get("fill") == "black"

    assert circles[1].get("cx") == "100"
    assert circles[1].get("cy") == "50"
    assert circles[1].get("r") == "2"
    assert circles[1].get("fill") == "black"

    line = root.find(".//{http://www.w3.org/2000/svg}line")
    assert line is not None
    assert line.get("x1") == "10"
    assert line.get("y1") == "10"
    assert line.get("x2") == "100"
    assert line.get("y2") == "50"
    assert line.get("stroke") == "black"
