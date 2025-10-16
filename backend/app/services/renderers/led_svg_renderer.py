from svgwrite import Drawing

from app.models.circuit import Component
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class LedSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders an LED component.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            # Draw the LED body (circle)
            dwg.add(
                dwg.circle(center=(pos.x, pos.y), r=10, stroke="black", fill="none")
            )
            # Draw two small arrows to indicate light
            dwg.add(
                dwg.line(
                    start=(pos.x + 8, pos.y - 8),
                    end=(pos.x + 15, pos.y - 15),
                    stroke="black",
                )
            )
            dwg.add(
                dwg.line(
                    start=(pos.x + 12, pos.y - 15),
                    end=(pos.x + 15, pos.y - 15),
                    stroke="black",
                )
            )
            dwg.add(
                dwg.line(
                    start=(pos.x + 15, pos.y - 12),
                    end=(pos.x + 15, pos.y - 15),
                    stroke="black",
                )
            )
