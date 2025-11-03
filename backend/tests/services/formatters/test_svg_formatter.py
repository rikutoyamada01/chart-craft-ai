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
    assert circles[0].get("cx") == "0"
    assert circles[0].get("cy") == "0"
    assert circles[0].get("r") == "2"
    assert circles[0].get("fill") == "black"

    assert circles[1].get("cx") == "0"
    assert circles[1].get("cy") == "0"
    assert circles[1].get("r") == "2"
    assert circles[1].get("fill") == "black"

    polyline = root.find(".//{http://www.w3.org/2000/svg}polyline")
    assert polyline is not None
    assert polyline.get("stroke") == "black"


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
    all_polylines = root.findall(".//svg:polyline", ns)
    assert len(all_polylines) == 2

    # Check resistor
    resistor = root.find(".//svg:rect", ns)
    assert resistor is not None
    assert resistor.get("x") == str(-15)
    assert resistor.get("y") == str(-5)
    assert resistor.get("width") == "30"
    assert resistor.get("height") == "10"

    # Check LED
    led_circle = root.find(".//svg:circle", ns)
    assert led_circle is not None
    assert led_circle.get("cx") == "0"
    assert led_circle.get("cy") == "0"
    assert led_circle.get("r") == "10"

    # Check battery
    all_lines = root.findall(".//svg:line", ns)
    # The battery and LED symbols are made of lines
    assert (
        len(all_lines) == 7
    )  # 2 for battery symbol, 3 for LED arrows, and 2 mystery lines


def test_draw_transistor_switch_circuit() -> None:
    """
    Test that a transistor switch circuit with rotation and port connections is drawn correctly.
    """
    components = [
        Component(
            id="batt1",
            type="battery",
            properties=ComponentProperties(position=Position(x=50, y=50), rotation=0),
        ),
        Component(
            id="r1",
            type="resistor",
            properties=ComponentProperties(position=Position(x=150, y=50), rotation=0),
        ),
        Component(
            id="led1",
            type="led",
            properties=ComponentProperties(position=Position(x=250, y=50), rotation=0),
        ),
        Component(
            id="q1",
            type="transistor_npn",
            properties=ComponentProperties(
                position=Position(x=150, y=150), rotation=90
            ),
        ),
        Component(
            id="gnd",
            type="junction",
            properties=ComponentProperties(position=Position(x=150, y=250), rotation=0),
        ),
    ]
    connections = [
        Connection(
            source=ConnectionEndpoint(component_id="batt1", port="positive"),
            target=ConnectionEndpoint(component_id="r1", port="left"),
        ),
        Connection(
            source=ConnectionEndpoint(component_id="r1", port="right"),
            target=ConnectionEndpoint(component_id="led1", port="left"),
        ),
        Connection(
            source=ConnectionEndpoint(component_id="led1", port="right"),
            target=ConnectionEndpoint(component_id="q1", port="collector"),
        ),
        Connection(
            source=ConnectionEndpoint(component_id="batt1", port="negative"),
            target=ConnectionEndpoint(component_id="q1", port="base"),
        ),
        Connection(
            source=ConnectionEndpoint(component_id="q1", port="emitter"),
            target=ConnectionEndpoint(component_id="gnd"),
        ),
    ]
    circuit_spec = CircuitSpec(
        name="Transistor Switch",
        components=components,
        connections=connections,
    )
    circuit_data = CircuitData(circuit=circuit_spec)

    formatter = SvgFormatter()
    file_content = formatter.format(circuit_data)

    svg_content = file_content.content
    root = ET.fromstring(svg_content)

    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Check for components
    assert len(root.findall(".//svg:g", ns)) == 5  # 5 components, each in a group

    resistor = root.find(".//svg:rect", ns)
    assert resistor is not None
    assert resistor.get("x") == str(-15)
    assert resistor.get("y") == str(-5)
    assert resistor.get("width") == "30"
    assert resistor.get("height") == "10"

    led_circle = [c for c in root.findall(".//svg:circle", ns) if c.get("r") == "10"][0]
    assert led_circle.get("cx") == "0"
    assert led_circle.get("cy") == "0"

    junction_circle = [
        c for c in root.findall(".//svg:circle", ns) if c.get("r") == "2"
    ][0]
    assert junction_circle.get("cx") == "0"
    assert junction_circle.get("cy") == "0"

    transistor_polygon = root.find(".//svg:polygon", ns)
    assert transistor_polygon is not None
    # Add more specific assertions for transistor if needed

    # Check connections: 5 connections should be rendered as 5 black polylines
    polylines = root.findall(".//svg:polyline", ns)
    assert len(polylines) == 5
    for polyline in polylines:
        assert polyline.get("stroke") == "black"

    # Check component lines (battery(2) + LED(3) + transistor(5) = 10 lines)
    assert len(root.findall(".//svg:line", ns)) == 10
