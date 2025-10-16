from svgwrite import Drawing

from app.models.circuit import Component
from app.services.renderers.svg_component_renderer import SvgComponentRenderer


class JunctionSvgRenderer(SvgComponentRenderer):
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a junction component as a small circle.
        """
        if component.properties and component.properties.position:
            pos = component.properties.position
            dwg.add(dwg.circle(center=(pos.x, pos.y), r=2, fill="black"))
