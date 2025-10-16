from svgwrite import Drawing

from app.models.circuit import Component
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class ResistorSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a resistor component as a rectangle.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            # Draw a simple rectangle for the resistor body
            dwg.add(
                dwg.rect(
                    insert=(pos.x - 15, pos.y - 5),
                    size=(30, 10),
                    stroke="black",
                    fill="none",
                )
            )
