from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class JunctionSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a junction component as a small circle, applying rotation if specified.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            # Apply rotation if specified
            if component.properties.rotation is not None:
                group.rotate(
                    component.properties.rotation, center=(0, 0)
                )  # Rotate around its own center (0,0 relative to group)

            group.add(
                dwg.circle(center=(0, 0), r=2, fill="black")
            )  # Draw at (0,0) relative to group
            dwg.add(group)

    def get_port_position(self, component: Component, port_name: str) -> Position:
        """
        Returns the absolute position of a specific port on the junction.
        For a junction, the port position is its own position.
        Rotation is handled by the SvgFormatter when drawing connections.
        """
        if component.properties and component.properties.position:
            return component.properties.position
        raise ValueError(f"Junction {component.id} has no position defined.")
