import math

import svgwrite

from app.models.circuit import CircuitData, Component, Position
from app.models.file_content import FileContent
from app.services.formatters.base import FileFormatter
from app.services.renderers.svg_component_renderer_factory import (
    svg_component_renderer_factory,
)
from app.services.routing.a_star import AStarFinder
from app.services.routing.grid import Grid


class SvgFormatter(FileFormatter):
    def format(self, data: CircuitData) -> FileContent:
        """
        Generates SVG file content from CircuitData.
        """
        dwg = svgwrite.Drawing(profile="tiny", size=("500px", "500px"))
        current_grid_size = 5  # Use a variable for grid_size

        all_port_grid_positions: set[tuple[int, int]] = set()
        components_by_id: dict[str, Component] = {
            comp.id: comp for comp in data.circuit.components
        }

        # Collect all port positions first
        for component in data.circuit.components:
            renderer = svg_component_renderer_factory.get_renderer(component.type)
            if renderer:
                # Assuming a component can have multiple ports, we need to iterate
                # For simplicity, let's assume 'left', 'right', 'up', 'down' ports exist if applicable
                # This part might need more sophisticated logic based on actual port definitions
                for port_name in [
                    "left",
                    "right",
                    "up",
                    "down",
                    "positive",
                    "negative",
                    "base",
                    "collector",
                    "emitter",
                ]:
                    try:
                        port_pos_raw, _ = renderer.get_port_position(
                            component, port_name
                        )
                        port_pos = self._apply_rotation_to_point(
                            component, port_pos_raw
                        )
                        if port_pos:
                            all_port_grid_positions.add(
                                (
                                    port_pos.x // current_grid_size,
                                    port_pos.y // current_grid_size,
                                )
                            )
                    except ValueError:  # Port might not exist for this component
                        pass

        grid = Grid(500, 500, current_grid_size, all_port_grid_positions)

        # Draw components and add them to the grid as obstacles
        for component in data.circuit.components:
            renderer = svg_component_renderer_factory.get_renderer(component.type)
            if renderer:
                renderer.render(dwg, component)
                grid.add_obstacle(component)

        # Draw connections
        finder = AStarFinder(grid)
        for connection in data.circuit.connections:
            from_comp = components_by_id.get(connection.source.component_id)
            to_comp = components_by_id.get(connection.target.component_id)

            if from_comp and to_comp:
                from_renderer = svg_component_renderer_factory.get_renderer(
                    from_comp.type
                )
                to_renderer = svg_component_renderer_factory.get_renderer(to_comp.type)

                start_pos_raw = None
                end_pos_raw = None
                start_direction = ""
                end_direction = ""

                if from_renderer and connection.source.port:
                    start_pos_raw, start_direction = from_renderer.get_port_position(
                        from_comp, connection.source.port
                    )
                elif from_comp.properties and from_comp.properties.position:
                    start_pos_raw = from_comp.properties.position

                if to_renderer and connection.target.port:
                    end_pos_raw, end_direction = to_renderer.get_port_position(
                        to_comp, connection.target.port
                    )
                elif to_comp.properties and to_comp.properties.position:
                    end_pos_raw = to_comp.properties.position

                start_pos = self._apply_rotation_to_point(from_comp, start_pos_raw)
                end_pos = self._apply_rotation_to_point(to_comp, end_pos_raw)

                if start_pos and end_pos:
                    path = finder.find_path(
                        start_pos, end_pos, start_direction, end_direction
                    )
                    if path:
                        points = [
                            (x * grid.grid_size, y * grid.grid_size) for x, y in path
                        ]
                        # Correct the start and end points to align perfectly with the ports
                        if points:
                            points[0] = (start_pos.x, start_pos.y)
                            points[-1] = (end_pos.x, end_pos.y)
                        dwg.add(dwg.polyline(points, stroke="black", fill="none"))
                    else:
                        # Fallback to a straight line if no path is found
                        dwg.add(
                            dwg.line(
                                start=(start_pos.x, start_pos.y),
                                end=(end_pos.x, end_pos.y),
                                stroke="red",  # Draw in red to indicate a failed route
                            )
                        )

        svg_content = dwg.tostring()
        return FileContent(
            filename="circuit.svg",
            content=svg_content,
            mime_type="image/svg+xml",
        )

    def _apply_rotation_to_point(
        self, component: Component, point: Position | None
    ) -> Position | None:
        """
        Applies the component's rotation to a given point.
        """
        if (
            not point
            or not component.properties
            or component.properties.rotation is None
        ):
            return point

        if not component.properties.position:
            return point  # Rotation center not defined

        cx, cy = component.properties.position.x, component.properties.position.y
        angle_rad = math.radians(component.properties.rotation)

        # Translate point so component center is at origin
        translated_x = point.x - cx
        translated_y = point.y - cy

        # Rotate point
        rotated_x = translated_x * math.cos(angle_rad) - translated_y * math.sin(
            angle_rad
        )
        rotated_y = translated_x * math.sin(angle_rad) + translated_y * math.cos(
            angle_rad
        )

        # Translate point back
        final_x = rotated_x + cx
        final_y = rotated_y + cy

        return Position(x=final_x, y=final_y)
