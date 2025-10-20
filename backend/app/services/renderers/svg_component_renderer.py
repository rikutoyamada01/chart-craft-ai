from abc import ABC, abstractmethod

from svgwrite import Drawing

from app.models.circuit import Component, Position


class SvgComponentRenderer(ABC):
    @abstractmethod
    def render(self, dwg: Drawing, component: Component) -> None:
        """
        Renders a component onto the SVG drawing.

        :param dwg: The svgwrite Drawing object.
        :param component: The component to render.
        """
        pass

    @abstractmethod
    def get_port_position(self, component: Component, port_name: str) -> Position:
        """
        Returns the absolute position of a specific port on the component.

        :param component: The component.
        :param port_name: The name of the port.
        :return: The position of the port.
        """
        pass
