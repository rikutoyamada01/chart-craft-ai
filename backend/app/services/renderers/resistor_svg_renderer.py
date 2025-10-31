from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class ResistorSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a resistor component as a rectangle, applying rotation if specified.
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
            group.add(dwg.line(start=(-25, 0), end=(-15, 0), stroke="black"))
            group.add(dwg.line(start=(15, 0), end=(25, 0), stroke="black"))

            # Draw a simple rectangle for the resistor body at (0,0) relative to group
            group.add(
                dwg.rect(
                    insert=(-15, -5),  # Relative to component center
                    size=(30, 10),
                    stroke="black",
                    fill="white",
                )
            )
            dwg.add(group)

    def get_port_position(
        self, component: Component, port_name: str
    ) -> tuple[Position, str]:
        """
        Returns the absolute position of a specific port on the resistor.
        Assumes 'left' and 'right' ports.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Resistor {component.id} has no position defined.")

        pos = component.properties.position
        if port_name == "left":
            return Position(x=pos.x - 25, y=pos.y), "left"
        elif port_name == "right":
            return Position(x=pos.x + 25, y=pos.y), "right"
        else:
            raise ValueError(f"Unknown port '{port_name}' for resistor {component.id}")

    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        return 50, 10
