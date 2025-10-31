from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class LedSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders an LED component, applying rotation if specified.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            # Apply rotation if specified
            if component.properties.rotation is not None:
                group.rotate(
                    component.properties.rotation, center=(0, 0)
                )  # Rotate around its own center (0,0 relative to group)

            # Connection leads
            group.add(dwg.line(start=(-20, 0), end=(-10, 0), stroke="black"))
            group.add(dwg.line(start=(10, 0), end=(20, 0), stroke="black"))

            # Draw the LED body (circle) at (0,0) relative to group
            group.add(dwg.circle(center=(0, 0), r=10, stroke="black", fill="white"))
            # Draw two small arrows to indicate light, relative to group
            group.add(
                dwg.line(
                    start=(8, -8),
                    end=(15, -15),
                    stroke="black",
                )
            )
            group.add(
                dwg.line(
                    start=(12, -15),
                    end=(15, -15),
                    stroke="black",
                )
            )
            group.add(
                dwg.line(
                    start=(15, -12),
                    end=(15, -15),
                    stroke="black",
                )
            )
            dwg.add(group)

    def get_port_position(
        self, component: Component, port_name: str
    ) -> tuple[Position, str]:
        """
        Returns the absolute position of a specific port on the LED.
        Assumes 'left' (anode) and 'right' (cathode) ports.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"LED {component.id} has no position defined.")

        pos = component.properties.position
        if port_name == "left":  # Anode side
            return Position(x=pos.x - 20, y=pos.y), "left"
        elif port_name == "right":  # Cathode side
            return Position(x=pos.x + 20, y=pos.y), "right"
        else:
            raise ValueError(f"Unknown port '{port_name}' for LED {component.id}")

    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        return 40, 20
