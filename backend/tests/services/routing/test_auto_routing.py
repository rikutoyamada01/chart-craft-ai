from app.models.circuit import Component, ComponentProperties, Position
from app.services.routing.a_star import AStarFinder
from app.services.routing.grid import Grid


def test_a_star_simple_path():
    grid = Grid(100, 100, 10)
    finder = AStarFinder(grid)
    start = Position(x=10, y=10)
    end = Position(x=80, y=10)

    path = finder.find_path(start, end, "right", "left")

    assert path is not None
    assert path[0] == (1, 1)
    assert path[-1] == (8, 1)
    assert len(path) == 2


def test_a_star_with_obstacle():
    grid = Grid(100, 100, 10)
    obstacle = Component(
        id="C1",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=50, y=10), resistance="1k", rotation=0
        ),
    )
    grid.add_obstacle(obstacle, margin=0)

    finder = AStarFinder(grid)
    start = Position(x=10, y=10)
    end = Position(x=80, y=10)

    path = finder.find_path(start, end, "right", "left")

    assert path is not None
    assert not all(y == 1 for x, y in path)
    obstacle_x = obstacle.properties.position.x // grid.grid_size
    obstacle_y = obstacle.properties.position.y // grid.grid_size
    assert (obstacle_x, obstacle_y) not in path


def test_a_star_blocked_path():
    grid = Grid(100, 100, 10)
    # Create a wall of obstacles
    for i in range(10):
        obstacle = Component(
            id=f"C{i}",
            type="resistor",
            properties=ComponentProperties(
                position=Position(x=50, y=i * 10), resistance="1k", rotation=0
            ),
        )
        grid.add_obstacle(obstacle, margin=0)

    finder = AStarFinder(grid)
    start = Position(x=10, y=50)
    end = Position(x=80, y=50)

    path = finder.find_path(start, end, "right", "left")

    assert path is None


def test_a_star_egress_direction():
    grid = Grid(100, 100, 10)
    finder = AStarFinder(grid)
    start = Position(x=50, y=50)
    end = Position(x=80, y=50)

    # Force the path to start by going up
    path = finder.find_path(start, end, "up", "left")

    assert path is not None
    assert path[0] == (5, 5)
    assert path[1] == (5, 4)
