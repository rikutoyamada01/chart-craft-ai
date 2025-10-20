from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class CoilSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a coil (inductor) component.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            if component.properties.rotation is not None:
                group.rotate(component.properties.rotation, center=(0, 0))

            # Coil as a path of arcs
            group.add(
                dwg.path(
                    d="M -15,0 A 5,5 0 0 1 -5,0 A 5,5 0 0 1 5,0 A 5,5 0 0 1 15,0",
                    stroke="black",
                    fill="none",
                )
            )

            dwg.add(group)

    def get_port_position(
        self, component: Component, port_name: str
    ) -> tuple[Position, str]:
        """
        Returns the absolute position of a specific port on the coil.
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Coil {component.id} has no position defined.")

        pos = component.properties.position
        if port_name == "left":
            return Position(x=pos.x - 15, y=pos.y), "left"
        elif port_name == "right":
            return Position(x=pos.x + 15, y=pos.y), "right"
        else:
            raise ValueError(f"Unknown port '{port_name}' for coil {component.id}")

    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        return 30, 10
