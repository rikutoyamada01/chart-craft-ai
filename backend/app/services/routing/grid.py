from app.models.circuit import Component
from app.services.renderers.svg_component_renderer_factory import (
    svg_component_renderer_factory,
)


class Grid:
    def __init__(
        self,
        width: int,
        height: int,
        grid_size: int,
        port_positions: set[tuple[int, int]] | None = None,
    ):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_width = width // grid_size
        self.grid_height = height // grid_size
        self.hard_obstacles: set[tuple[int, int]] = set()
        self.soft_obstacles: set[tuple[int, int]] = set()
        self.port_positions = port_positions if port_positions is not None else set()
        self.soft_obstacle_cost: float = 1.0  # Default soft obstacle cost

    def set_soft_obstacle_cost(self, cost: float):
        """
        Sets the cost for moving into a soft obstacle.
        """
        self.soft_obstacle_cost = cost

    def add_obstacle(
        self, component: Component, hard_margin: int = 0, soft_margin: int = 0
    ):
        """
        Marks the area occupied by a component as hard and soft obstacles.

        Args:
            component: Component to add as obstacle
            hard_margin: Margin for hard obstacles (component body, impassable)
            soft_margin: Margin for soft obstacles (safety zone, high cost but passable)
        """
        if not component.properties or not component.properties.position:
            return

        renderer = svg_component_renderer_factory.get_renderer(component.type)
        if not renderer:
            return

        comp_width, comp_height = renderer.get_bounding_box(component)

        # Hard obstacles (component body with hard_margin) - IMPASSABLE
        min_x_hard = component.properties.position.x - comp_width // 2 - hard_margin
        max_x_hard = component.properties.position.x + comp_width // 2 + hard_margin
        min_y_hard = component.properties.position.y - comp_height // 2 - hard_margin
        max_y_hard = component.properties.position.y + comp_height // 2 + hard_margin

        start_grid_x_hard = max(0, min_x_hard // self.grid_size)
        end_grid_x_hard = min(self.grid_width, max_x_hard // self.grid_size + 1)
        start_grid_y_hard = max(0, min_y_hard // self.grid_size)
        end_grid_y_hard = min(self.grid_height, max_y_hard // self.grid_size + 1)

        for x in range(start_grid_x_hard, end_grid_x_hard):
            for y in range(start_grid_y_hard, end_grid_y_hard):
                self.hard_obstacles.add((x, y))

        # Soft obstacles (safety zone beyond hard obstacles) - HIGH COST but passable

        # Add soft obstacles around the hard obstacles
        for x in range(start_grid_x_hard, end_grid_x_hard):
            for y in range(start_grid_y_hard, end_grid_y_hard):
                # Add surrounding cells as soft obstacles
                for dx in range(-soft_margin, soft_margin + 1):
                    for dy in range(-soft_margin, soft_margin + 1):
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < self.grid_width
                            and 0 <= ny < self.grid_height
                            and (nx, ny) not in self.hard_obstacles
                        ):
                            self.soft_obstacles.add((nx, ny))

    def add_soft_obstacle_path(self, path: list[tuple[int, int]]):
        """
        Adds a routed path to the soft obstacles.
        This makes subsequent routings avoid crossing this path.
        """
        for node in path:
            self.soft_obstacles.add(node)

    def is_hard_obstacle(self, x: int, y: int) -> bool:
        """
        Checks if a grid cell is a hard obstacle (impassable).
        Ports are never obstacles.
        """
        if (x, y) in self.port_positions:
            return False
        return (x, y) in self.hard_obstacles

    def is_soft_obstacle(self, x: int, y: int) -> bool:
        """
        Checks if a grid cell is a soft obstacle (high cost but passable).
        """
        return (x, y) in self.soft_obstacles
