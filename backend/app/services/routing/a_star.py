import heapq

from app.models.circuit import Position
from app.services.routing.grid import Grid


class AStarFinder:
    def __init__(self, grid: Grid):
        self.grid = grid

    def find_path(
        self,
        start_pos: Position,
        end_pos: Position,
        start_direction: str,
        end_direction: str,
    ) -> list[tuple[int, int]] | None:
        start_node = (
            start_pos.x // self.grid.grid_size,
            start_pos.y // self.grid.grid_size,
        )
        end_node = (
            end_pos.x // self.grid.grid_size,
            end_pos.y // self.grid.grid_size,
        )

        # Ensure the start and end nodes and their immediate neighbors in the exit direction are walkable
        nodes_to_clear = {start_node, end_node}

        def get_neighbor(node, direction):
            x, y = node
            if direction == "up":
                return (x, y - 1)
            if direction == "down":
                return (x, y + 1)
            if direction == "left":
                return (x - 1, y)
            if direction == "right":
                return (x + 1, y)
            return None

        start_neighbor = get_neighbor(start_node, start_direction)
        if start_neighbor:
            nodes_to_clear.add(start_neighbor)

        end_neighbor = get_neighbor(end_node, end_direction)
        if end_neighbor:
            nodes_to_clear.add(end_neighbor)

        for node in nodes_to_clear:
            if node in self.grid.obstacles:
                self.grid.obstacles.remove(node)

        open_set: list[tuple[float, tuple[int, int]]] = []
        heapq.heappush(open_set, (0, start_node))

        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start_node: None}
        g_score: dict[tuple[int, int], float] = {start_node: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == end_node:
                path = self._reconstruct_path(came_from, current)
                return self._smooth_path(path)

            is_start_node = current == start_node
            neighbors = self._get_neighbors(
                current, start_direction if is_start_node else None
            )

            for neighbor in neighbors:
                if self.grid.is_obstacle(neighbor[0], neighbor[1]):
                    continue

                tentative_g_score = g_score[current] + self._cost_to_move(
                    current, neighbor, came_from[current]
                )

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self._heuristic(neighbor, end_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        return None  # Path not found

    def _get_neighbors(
        self, node: tuple[int, int], direction: str | None = None
    ) -> list[tuple[int, int]]:
        x, y = node
        possible_neighbors = []

        if direction:
            # Try the preferred direction first
            if direction == "up":
                preferred_neighbor = (x, y - 1)
            elif direction == "down":
                preferred_neighbor = (x, y + 1)
            elif direction == "left":
                preferred_neighbor = (x - 1, y)
            elif direction == "right":
                preferred_neighbor = (x + 1, y)
            else:
                preferred_neighbor = None

            if (
                preferred_neighbor
                and 0 <= preferred_neighbor[0] < self.grid.grid_width
                and 0 <= preferred_neighbor[1] < self.grid.grid_height
                and not self.grid.is_obstacle(
                    preferred_neighbor[0], preferred_neighbor[1]
                )
            ):
                possible_neighbors.append(preferred_neighbor)
            else:
                # If preferred is blocked or invalid, consider all directions
                possible_neighbors.extend(
                    [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                )
        else:
            possible_neighbors.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

        return [
            n
            for n in possible_neighbors
            if 0 <= n[0] < self.grid.grid_width and 0 <= n[1] < self.grid.grid_height
        ]

    def _cost_to_move(
        self,
        current: tuple[int, int],
        neighbor: tuple[int, int],
        parent: tuple[int, int] | None,
    ) -> float:
        if parent is None:
            return 1.0  # No parent, no turn

        # Get the direction of movement
        dx1 = current[0] - parent[0]
        dy1 = current[1] - parent[1]
        dx2 = neighbor[0] - current[0]
        dy2 = neighbor[1] - current[1]

        # Check if the direction has changed
        if dx1 != dx2 or dy1 != dy2:
            return 1.5  # Penalize for turning

        return 1.0  # Cost for moving straight

    def _heuristic(self, node: tuple[int, int], end_node: tuple[int, int]) -> float:
        # Manhattan distance
        return abs(node[0] - end_node[0]) + abs(node[1] - end_node[1])

    def _reconstruct_path(
        self, came_from: dict, current: tuple[int, int]
    ) -> list[tuple[int, int]]:
        path = [current]
        while current in came_from and came_from[current] is not None:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def _smooth_path(self, path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(path) < 3:
            return path

        smoothed_path = [path[0]]
        for i in range(1, len(path) - 1):
            p1 = path[i - 1]
            p2 = path[i]
            p3 = path[i + 1]

            # Check for collinearity
            if (p2[0] - p1[0]) * (p3[1] - p1[1]) != (p3[0] - p1[0]) * (p2[1] - p1[1]):
                smoothed_path.append(p2)

        smoothed_path.append(path[-1])
        return smoothed_path
