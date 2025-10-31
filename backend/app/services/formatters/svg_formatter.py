import logging
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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="routing_debug.log",
    filemode="w",
)
logger = logging.getLogger(__name__)


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
                        port_pos, _ = renderer.get_port_position(component, port_name)
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
        # Sort by distance (longest first) - route long connections first
        # This allows shorter connections to route around them, creating cleaner layouts
        def connection_priority(conn):
            from_comp = components_by_id[conn.source.component_id]
            to_comp = components_by_id[conn.target.component_id]

            distance = 0
            if (
                from_comp.properties
                and from_comp.properties.position
                and to_comp.properties
                and to_comp.properties.position
            ):
                dx = to_comp.properties.position.x - from_comp.properties.position.x
                dy = to_comp.properties.position.y - from_comp.properties.position.y
                distance = abs(dx) + abs(dy)

            # Return negative distance to sort longest first (reverse order)
            return -distance

        sorted_connections = sorted(data.circuit.connections, key=connection_priority)

        finder = AStarFinder(grid)
        for connection in sorted_connections:
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

                start_rotation = from_comp.properties.rotation or 0
                end_rotation = to_comp.properties.rotation or 0

                final_start_direction = self._rotate_direction(
                    start_direction, start_rotation
                )
                final_end_direction = self._rotate_direction(
                    end_direction, end_rotation
                )

                if start_pos and end_pos:
                    logger.debug("-" * 20)
                    logger.debug(
                        f"Routing connection: {from_comp.id}:{connection.source.port} -> {to_comp.id}:{connection.target.port}"
                    )
                    logger.debug(
                        f"Start: {start_pos}, Direction: {final_start_direction}"
                    )
                    logger.debug(f"End: {end_pos}, Direction: {final_end_direction}")
                    logger.debug(f"Hard Obstacles: {grid.hard_obstacles}")
                    logger.debug(f"Soft Obstacles: {grid.soft_obstacles}")
                    logger.debug(f"Port Positions: {grid.port_positions}")

                    path = None

                    # Multi-stage path finding:
                    # Stage 1: Try with high soft obstacle cost (avoids crossing existing wires)
                    grid.set_soft_obstacle_cost(5.0)
                    path = finder.find_path(
                        start_pos, end_pos, final_start_direction, final_end_direction
                    )
                    logger.debug(
                        f"Stage 1 (cost=5.0): {'Path found' if path else 'No path'}"
                    )

                    if not path:
                        # Stage 2: Reduce penalty for soft obstacles (allow crossing at higher cost)
                        grid.set_soft_obstacle_cost(1.0)
                        path = finder.find_path(
                            start_pos,
                            end_pos,
                            final_start_direction,
                            final_end_direction,
                        )
                        logger.debug(
                            f"Stage 2 (cost=1.0): {'Path found' if path else 'No path'}"
                        )

                    if not path:
                        # Stage 3: No penalty for soft obstacles (desperate attempt)
                        grid.set_soft_obstacle_cost(0.0)
                        path = finder.find_path(
                            start_pos,
                            end_pos,
                            final_start_direction,
                            final_end_direction,
                        )
                        logger.debug(
                            f"Stage 3 (cost=0.0): {'Path found' if path else 'No path'}"
                        )

                    if path:
                        grid.add_soft_obstacle_path(path)
                        points = [
                            (x * grid.grid_size, y * grid.grid_size) for x, y in path
                        ]
                        # Correct the start and end points to align perfectly with the ports
                        if points:
                            points[0] = (start_pos.x, start_pos.y)
                            points[-1] = (end_pos.x, end_pos.y)
                        dwg.add(dwg.polyline(points, stroke="black", fill="none"))
                        logger.debug("Route found successfully.")
                    else:
                        # Fallback to a straight line if both stages fail
                        dwg.add(
                            dwg.line(
                                start=(start_pos.x, start_pos.y),
                                end=(end_pos.x, end_pos.y),
                                stroke="red",  # Draw in red to indicate a failed route
                            )
                        )
                        logger.debug("Route not found. Drawing fallback line.")
                    logger.debug("-" * 20)

        svg_content = dwg.tostring()
        return FileContent(
            filename="circuit.svg",
            content=svg_content,
            mime_type="image/svg+xml",
        )

    def _rotate_direction(self, direction: str, angle: float) -> str:
        if not direction:
            return ""

        angle = angle % 360

        # Map component-specific port names to cardinal directions
        if direction in ["positive", "base"]:
            direction = "left"
        elif direction == "negative":
            direction = "right"
        elif direction == "collector":
            direction = "up"
        elif direction == "emitter":
            direction = "down"

        try:
            directions = ["right", "down", "left", "up"]
            initial_index = directions.index(direction)
        except ValueError:
            return direction  # Return original if not a cardinal direction

        rotation_steps = round(angle / 90)
        final_index = (initial_index + rotation_steps) % 4
        return directions[final_index]

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
