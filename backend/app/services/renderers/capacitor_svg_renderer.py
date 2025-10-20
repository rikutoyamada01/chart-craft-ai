from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class CapacitorSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a capacitor component.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            if component.properties.rotation is not None:
                group.rotate(component.properties.rotation, center=(0, 0))

            # Capacitor plates
            group.add(dwg.line(start=(-2, -10), end=(-2, 10), stroke="black"))
            group.add(dwg.line(start=(2, -10), end=(2, 10), stroke="black"))

            # Connection leads
            group.add(dwg.line(start=(-15, 0), end=(-2, 0), stroke="black"))
            group.add(dwg.line(start=(2, 0), end=(15, 0), stroke="black"))

            dwg.add(group)

    def get_port_position(self, component: Component, port_name: str) -> Position:
        """
        Returns the absolute position of a specific port on the capacitor.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Capacitor {component.id} has no position defined.")

        pos = component.properties.position
        if port_name == "left":
            return Position(x=pos.x - 15, y=pos.y)
        elif port_name == "right":
            return Position(x=pos.x + 15, y=pos.y)
        else:
            raise ValueError(f"Unknown port '{port_name}' for capacitor {component.id}")
