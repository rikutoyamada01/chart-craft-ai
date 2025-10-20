from app.models.circuit import Component
from app.services.renderers.svg_component_renderer_factory import (
    svg_component_renderer_factory,
)


class Grid:
    def __init__(self, width: int, height: int, grid_size: int):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_width = width // grid_size
        self.grid_height = height // grid_size
        self.obstacles: set[tuple[int, int]] = set()

    def add_obstacle(self, component: Component, margin: int = 1):
        """
        Marks the area occupied by a component as an obstacle on the grid.
        """
        if not component.properties or not component.properties.position:
            return

        renderer = svg_component_renderer_factory.get_renderer(component.type)
        if not renderer:
            return

        comp_width, comp_height = renderer.get_bounding_box(component)

        min_x = component.properties.position.x - comp_width // 2
        max_x = component.properties.position.x + comp_width // 2
        min_y = component.properties.position.y - comp_height // 2
        max_y = component.properties.position.y + comp_height // 2

        start_grid_x = max(0, min_x // self.grid_size - margin)
        end_grid_x = min(self.grid_width, max_x // self.grid_size + 1 + margin)
        start_grid_y = max(0, min_y // self.grid_size - margin)
        end_grid_y = min(self.grid_height, max_y // self.grid_size + 1 + margin)

        for x in range(start_grid_x, end_grid_x):
            for y in range(start_grid_y, end_grid_y):
                self.obstacles.add((x, y))

    def is_obstacle(self, x: int, y: int) -> bool:
        """
        Checks if a grid cell is an obstacle.
        """
        return (x, y) in self.obstacles
