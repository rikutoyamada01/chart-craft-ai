from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class BatterySvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a battery component, applying rotation if specified.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            # Apply rotation if specified
            if component.properties.rotation is not None:
                group.rotate(
                    component.properties.rotation, center=(0, 0)
                )  # Rotate around its own center (0,0 relative to group)

            # Long line for positive terminal, relative to group
            group.add(
                dwg.line(
                    start=(-10, -15),
                    end=(10, -15),
                    stroke="black",
                )
            )
            # Short line for negative terminal, relative to group
            group.add(
                dwg.line(
                    start=(-5, 15),
                    end=(5, 15),
                    stroke="black",
                )
            )
            dwg.add(group)

    def get_port_position(self, component: Component, port_name: str) -> Position:
        """
        Returns the absolute position of a specific port on the battery.
        Assumes 'positive' and 'negative' ports.
        Rotation is handled by the SvgFormatter when drawing connections.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Battery {component.id} has no position defined.")

        pos = component.properties.position
        # Port positions are relative to the component's center, before rotation
        if port_name == "positive":
            return Position(x=pos.x, y=pos.y - 15)
        elif port_name == "negative":
            return Position(x=pos.x, y=pos.y + 15)
        else:
            raise ValueError(f"Unknown port '{port_name}' for battery {component.id}")
