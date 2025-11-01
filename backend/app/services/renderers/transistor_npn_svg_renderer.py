from svgwrite import Drawing

from app.models.circuit import Component, Position
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class TransistorNpnSvgRenderer(SvgComponentRenderer):
    ports = ["base", "collector", "emitter"]

    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders an NPN transistor component, applying rotation if specified.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            group = dwg.g(transform=f"translate({pos.x}, {pos.y})")

            # Apply rotation if specified
            if component.properties.rotation is not None:
                group.rotate(
                    component.properties.rotation, center=(0, 0)
                )  # Rotate around its own center (0,0 relative to group)

            # Draw base line, relative to group
            group.add(dwg.line(start=(-20, 0), end=(0, 0), stroke="black"))
            # Draw triangle (emitter/collector), relative to group
            group.add(
                dwg.polygon(
                    points=[(0, -15), (15, 0), (0, 15)], stroke="black", fill="none"
                )
            )
            # Draw collector line, relative to group
            group.add(dwg.line(start=(0, -15), end=(0, -30), stroke="black"))
            # Draw emitter line with arrow, relative to group
            group.add(dwg.line(start=(0, 15), end=(0, 30), stroke="black"))
            # Emitter arrow (simplified for now), relative to group
            group.add(dwg.line(start=(0, 30), end=(-5, 25), stroke="black"))
            group.add(dwg.line(start=(0, 30), end=(5, 25), stroke="black"))

            dwg.add(group)

    def get_port_position(
        self, component: Component, port_index: int
    ) -> tuple[Position, str]:
        """
        Returns the absolute position of a specific port on the NPN transistor.
        Assumes default orientation (base left, collector top, emitter bottom).
        """
        if not component.properties or not component.properties.position:
            raise ValueError(f"Transistor {component.id} has no position defined.")

        port_name = self.get_port_name_by_index(port_index)
        pos = component.properties.position
        if port_name == "base":
            return Position(x=pos.x - 20, y=pos.y), "left"
        elif port_name == "collector":
            return Position(x=pos.x, y=pos.y - 30), "up"
        elif port_name == "emitter":
            return Position(x=pos.x, y=pos.y + 30), "down"
        else:
            raise ValueError(
                f"Unknown port '{port_name}' for transistor {component.id}"
            )

    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        return 40, 60
