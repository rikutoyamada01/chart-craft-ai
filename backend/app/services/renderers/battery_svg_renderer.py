from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class BatterySvgRenderer(SvgComponentRenderer):
    ports = ["positive", "negative"]

    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a battery component, applying rotation if specified.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            # Apply rotation if specified
            if component.properties.rotation is not None:
                group.rotate(component.properties.rotation, center=(0, 0))

            # Long line for positive terminal
            group.add(dwg.line(start=(-2, -10), end=(-2, 10), stroke="black"))
            # Short line for negative terminal
            group.add(dwg.line(start=(2, -5), end=(2, 5), stroke="black"))

            # Connection leads
            group.add(dwg.line(start=(-15, 0), end=(-2, 0), stroke="black"))
            group.add(dwg.line(start=(2, 0), end=(15, 0), stroke="black"))

            dwg.add(group)

    def get_port_position(
        self, component: Component, port_index: int
    ) -> tuple[Position, str]:
        """
        Returns the absolute position of a specific port on the battery.
        Assumes 'positive' (left) and 'negative' (right) ports.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Battery {component.id} has no position defined.")

        port_name = self.get_port_name_by_index(port_index)
        pos = component.properties.position
        if port_name == "positive":
            return Position(x=pos.x - 15, y=pos.y), "left"
        elif port_name == "negative":
            return Position(x=pos.x + 15, y=pos.y), "right"
        else:
            raise ValueError(f"Unknown port '{port_name}' for battery {component.id}")

    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        return 30, 20
