from app.services.renderers.battery_svg_renderer import BatterySvgRenderer
from app.services.renderers.junction_svg_renderer import JunctionSvgRenderer
from app.services.renderers.led_svg_renderer import LedSvgRenderer
from app.services.renderers.resistor_svg_renderer import ResistorSvgRenderer
from app.services.renderers.svg_component_renderer import SvgComponentRenderer
from app.services.renderers.transistor_npn_svg_renderer import (
    TransistorNpnSvgRenderer,
)


class SvgComponentRendererFactory:
    def __init__(self) -> None:
        self._renderers: dict[str, SvgComponentRenderer] = {
            "junction": JunctionSvgRenderer(),
            "resistor": ResistorSvgRenderer(),
            "led": LedSvgRenderer(),
            "battery": BatterySvgRenderer(),
            "transistor_npn": TransistorNpnSvgRenderer(),
        }

    def get_renderer(self, component_type: str) -> SvgComponentRenderer | None:
        """
        Returns the renderer for the given component type.
        """
        return self._renderers.get(component_type.lower())


svg_component_renderer_factory = SvgComponentRendererFactory()
