from svgwrite import Drawing

from app.models.circuit import Component
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class BatterySvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a battery component.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            # Long line for positive terminal
            dwg.add(
                dwg.line(
                    start=(pos.x - 10, pos.y - 15),
                    end=(pos.x + 10, pos.y - 15),
                    stroke="black",
                )
            )
            # Short line for negative terminal
            dwg.add(
                dwg.line(
                    start=(pos.x - 5, pos.y + 15),
                    end=(pos.x + 5, pos.y + 15),
                    stroke="black",
                )
            )
