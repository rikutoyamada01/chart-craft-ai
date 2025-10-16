import xml.etree.ElementTree as ET

from app.models.circuit import (
    CircuitData,
    CircuitSpec,
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
    circuit_spec = CircuitSpec(
        name="Test Circuit", components=components, connections=connections
    )
    circuit_data = CircuitData(circuit=circuit_spec)

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


def test_draw_real_circuit() -> None:
    """
    Test that a more complex circuit with various components is drawn correctly.
    """
    components = [
        Component(
            id="batt1",
            type="battery",
            properties=ComponentProperties(position=Position(x=50, y=100)),
        ),
        Component(
            id="r1",
            type="resistor",
            properties=ComponentProperties(position=Position(x=150, y=100)),
        ),
        Component(
            id="led1",
            type="led",
            properties=ComponentProperties(position=Position(x=250, y=100)),
        ),
    ]
    connections = [
        Connection(
            source=ConnectionEndpoint(component_id="batt1"),
            target=ConnectionEndpoint(component_id="r1"),
        ),
        Connection(
            source=ConnectionEndpoint(component_id="r1"),
            target=ConnectionEndpoint(component_id="led1"),
        ),
    ]
    circuit_spec = CircuitSpec(
        name="Simple LED Circuit",
        components=components,
        connections=connections,
    )
    circuit_data = CircuitData(circuit=circuit_spec)

    formatter = SvgFormatter()
    file_content = formatter.format(circuit_data)

    svg_content = file_content.content
    root = ET.fromstring(svg_content)

    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Check connections
    all_lines = root.findall("svg:line", ns)
    connection_lines = [
        line
        for line in all_lines
        if (line.get("x1"), line.get("y1")) in [("50", "100"), ("150", "100")]
    ]
    assert len(connection_lines) == 2

    # Check resistor
    resistor = root.find("svg:rect", ns)
    assert resistor is not None
    assert resistor.get("x") == str(150 - 15)
    assert resistor.get("y") == str(100 - 5)
    assert resistor.get("width") == "30"
    assert resistor.get("height") == "10"

    # Check LED
    led_circle = root.find("svg:circle", ns)
    assert led_circle is not None
    assert led_circle.get("cx") == "250"
    assert led_circle.get("cy") == "100"
    assert led_circle.get("r") == "10"

    # Check battery
    battery_lines = [
        line
        for line in all_lines
        if (line.get("x1"), line.get("y1")) not in [("50", "100"), ("150", "100")]
    ]
    assert len(battery_lines) == 5  # 2 for battery symbol, 3 for LED arrows
