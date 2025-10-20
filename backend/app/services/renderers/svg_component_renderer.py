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
    def get_port_position(
        self, component: Component, port_name: str
    ) -> tuple[Position, str]:
        """
        Returns the absolute position and egress direction of a specific port.

        :param component: The component.
        :param port_name: The name of the port.
        :return: A tuple containing the position and direction of the port.
        """

    @abstractmethod
    def get_bounding_box(self, component: Component) -> tuple[int, int]:
        """
        Returns the bounding box (width, height) of the component.

        :param component: The component.
        :return: A tuple containing the width and height of the bounding box.
        """
        pass
        pass
