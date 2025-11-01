from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class CoilSvgRenderer(SvgComponentRenderer):
    ports = ["left", "right"]

    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a coil component.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            if component.properties.rotation is not None:
                group.rotate(component.properties.rotation, center=(0, 0))

            # Coil body (simplified as a zigzag line)
            points = [
                (-15, 0),
                (-10, 5),
                (-5, -5),
                (0, 5),
                (5, -5),
                (10, 5),
                (15, 0),
            ]
            group.add(dwg.polyline(points, stroke="black", fill="none"))

            # Connection leads
            group.add(dwg.line(start=(-25, 0), end=(-15, 0), stroke="black"))
            group.add(dwg.line(start=(15, 0), end=(25, 0), stroke="black"))

            dwg.add(group)

    def get_port_position(
        self, component: Component, port_index: int
    ) -> tuple[Position, str]:
        """
        Returns the absolute position of a specific port on the coil.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Coil {component.id} has no position defined.")

        port_name = self.get_port_name_by_index(port_index)
        pos = component.properties.position
        if port_name == "left":
            return Position(x=pos.x - 25, y=pos.y), "left"
        elif port_name == "right":
            return Position(x=pos.x + 25, y=pos.y), "right"
        else:
            raise ValueError(f"Unknown port '{port_name}' for coil {component.id}")

    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        return 50, 10
