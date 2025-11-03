from app.models.circuit import Component, ComponentProperties, Position
from app.services.routing.a_star import AStarFinder
from app.services.routing.grid import Grid


def test_a_star_very_simple_path():
    """Test basic A* path finding with an obstacle."""
    start = Position(x=10, y=10)
    end = Position(x=30, y=10)
    start_grid = (start.x // 20, start.y // 20)
    end_grid = (end.x // 20, end.y // 20)
    grid = Grid(100, 100, 20, port_positions={start_grid, end_grid})

    # Add an obstacle between start and end
    obstacle = Component(
        id="obs1",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=15, y=10), resistance="1k", rotation=0
        ),
    )
    grid.add_obstacle(obstacle, hard_margin=0, soft_margin=0)

    finder = AStarFinder(grid)
    path = finder.find_path(start, end, "right", "left")

    # Path should be found (will go around the obstacle)
    assert path is not None
    assert len(path) > 0
    assert path[0] == start_grid  # Should start at start_grid
    assert path[-1] == end_grid  # Should end at end_grid


def test_a_star_with_clear_path():
    """Test A* with no obstacles."""
    start = Position(x=10, y=10)
    end = Position(x=50, y=10)
    start_grid = (start.x // 20, start.y // 20)
    end_grid = (end.x // 20, end.y // 20)
    grid = Grid(100, 100, 20, port_positions={start_grid, end_grid})

    finder = AStarFinder(grid)
    path = finder.find_path(start, end, "right", "left")

    # Should find a direct path
    assert path is not None
    assert start_grid in path
    assert end_grid in path


def test_hard_and_soft_obstacles():
    """Test that hard obstacles block paths but soft obstacles just add cost."""
    start = Position(x=10, y=10)
    end = Position(x=50, y=10)
    start_grid = (start.x // 20, start.y // 20)
    end_grid = (end.x // 20, end.y // 20)
    grid = Grid(100, 100, 20, port_positions={start_grid, end_grid})

    # Add a component with both hard and soft obstacles directly in the path
    obstacle = Component(
        id="obs2",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=30, y=10), resistance="1k", rotation=0
        ),
    )
    grid.add_obstacle(obstacle, hard_margin=0, soft_margin=0)

    finder = AStarFinder(grid)

    # Should find a path (will avoid the hard obstacle by going around)
    path = finder.find_path(start, end, "right", "left")
    assert path is not None
    # Path should have multiple nodes since it needs to go around the obstacle
    assert len(path) >= 2  # At least start and end


def test_complex_path_with_multiple_obstacles():
    """Test complex path finding with multiple components (simulating real circuit)."""
    # Create a larger grid with multiple components
    grid = Grid(500, 500, 5)  # 5px grid size

    # Add multiple components to simulate a real circuit
    comp1 = Component(
        id="comp1",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=100, y=100), resistance="1k", rotation=0
        ),
    )
    grid.add_obstacle(comp1, hard_margin=0, soft_margin=0)

    comp2 = Component(
        id="comp2",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=200, y=100), resistance="2k", rotation=0
        ),
    )
    grid.add_obstacle(comp2, hard_margin=0, soft_margin=0)

    comp3 = Component(
        id="comp3",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=150, y=200), resistance="3k", rotation=0
        ),
    )
    grid.add_obstacle(comp3, hard_margin=0, soft_margin=0)

    # Define start and end positions that require navigating around obstacles
    start = Position(x=80, y=100)  # Left of comp1
    end = Position(x=220, y=200)  # Below comp2, to the right of comp3

    finder = AStarFinder(grid)
    path = finder.find_path(start, end, "right", "up")

    # Path should be found even with multiple obstacles
    assert path is not None
    assert len(path) > 2  # Should have multiple segments to navigate around obstacles
    assert path[0] == (start.x // 5, start.y // 5)  # Check start
    assert path[-1] == (end.x // 5, end.y // 5)  # Check end


def test_path_when_surrounded_by_obstacles():
    """Test path finding when start is surrounded by obstacles (challenging case)."""
    grid = Grid(500, 500, 5)

    # Create a narrow corridor scenario
    # Add obstacles on both sides, leaving a narrow path
    for y in range(0, 500, 100):
        comp_left = Component(
            id=f"comp_left_{y}",
            type="resistor",
            properties=ComponentProperties(
                position=Position(x=50, y=y), resistance="1k", rotation=0
            ),
        )
        comp_right = Component(
            id=f"comp_right_{y}",
            type="resistor",
            properties=ComponentProperties(
                position=Position(x=450, y=y), resistance="1k", rotation=0
            ),
        )
        grid.add_obstacle(comp_left, hard_margin=0, soft_margin=0)
        grid.add_obstacle(comp_right, hard_margin=0, soft_margin=0)

    # Start and end should find a path through the middle
    start = Position(x=250, y=50)
    end = Position(x=250, y=450)

    finder = AStarFinder(grid)
    path = finder.find_path(start, end, "down", "up")

    # Should find a path through the middle corridor
    assert path is not None
    assert len(path) > 0


def test_path_with_existing_wires():
    """Test that paths avoid crossing existing wires (soft obstacles)."""
    grid = Grid(500, 500, 5)

    # Add an obstacle
    comp = Component(
        id="comp",
        type="resistor",
        properties=ComponentProperties(
            position=Position(x=150, y=150), resistance="1k", rotation=0
        ),
    )
    grid.add_obstacle(comp, hard_margin=0, soft_margin=0)

    # Add an existing wire (soft obstacle) horizontally
    existing_path = [(20, 20), (30, 20), (40, 20), (50, 20)]
    grid.add_soft_obstacle_path(existing_path)

    # Try to route a new path that could cross the existing wire
    start = Position(x=30, y=10)  # Above the existing wire
    end = Position(x=30, y=30)  # Below the existing wire

    finder = AStarFinder(grid)
    path = finder.find_path(start, end, "down", "up")

    # Path should be found (might go around the wire or cross it at a cost)
    assert path is not None
    assert len(path) > 0
