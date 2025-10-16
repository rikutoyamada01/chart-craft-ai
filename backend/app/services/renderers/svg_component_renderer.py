from abc import ABC, abstractmethod

from svgwrite import Drawing

from app.models.circuit import Component


class SvgComponentRenderer(ABC):
    @abstractmethod
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a component onto the SVG drawing.

        :param dwg: The svgwrite Drawing object.
        :param component: The component to render.
        """
        pass
