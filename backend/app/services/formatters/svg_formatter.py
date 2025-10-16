import svgwrite

from app.models.circuit import CircuitData, Component
from app.models.file_content import FileContent
from app.services.formatters.base import FileFormatter
from app.services.renderers.svg_component_renderer_factory import (
    svg_component_renderer_factory,
)


class SvgFormatter(FileFormatter):
    def format(self, data: CircuitData) -> FileContent:
        """
        Generates SVG file content from CircuitData.
        """
        dwg = svgwrite.Drawing(profile="tiny", size=("500px", "500px"))

        components_by_id: dict[str, Component] = {
            comp.id: comp for comp in data.circuit.components
        }

        # Draw components
        for component in data.circuit.components:
            renderer = svg_component_renderer_factory.get_renderer(component.type)
            if renderer:
                renderer.render(dwg, component)

        # Draw connections
        for connection in data.circuit.connections:
            from_comp = components_by_id.get(connection.source.component_id)
            to_comp = components_by_id.get(connection.target.component_id)

            if from_comp and to_comp:
                if (
                    from_comp.properties
                    and from_comp.properties.position
                    and to_comp.properties
                    and to_comp.properties.position
                ):
                    start_pos = from_comp.properties.position
                    end_pos = to_comp.properties.position
                    dwg.add(
                        dwg.line(
                            start=(start_pos.x, start_pos.y),
                            end=(end_pos.x, end_pos.y),
                            stroke="black",
                        )
                    )

        svg_content = dwg.tostring()
        return FileContent(
            filename="circuit.svg",
            content=svg_content,
            mime_type="image/svg+xml",
        )
