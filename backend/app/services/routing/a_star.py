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

        # Bounding box for the search
        min_x = min(start_node[0], end_node[0])
        max_x = max(start_node[0], end_node[0])
        min_y = min(start_node[1], end_node[1])
        max_y = max(start_node[1], end_node[1])

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

                # Bounding box penalty
                if not (
                    min_x <= neighbor[0] <= max_x and min_y <= neighbor[1] <= max_y
                ):
                    tentative_g_score += 1  # Penalty for going outside the bounding box

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
        if direction:
            if direction == "up":
                neighbors = [(x, y - 1)]
            elif direction == "down":
                neighbors = [(x, y + 1)]
            elif direction == "left":
                neighbors = [(x - 1, y)]
            elif direction == "right":
                neighbors = [(x + 1, y)]
            else:
                neighbors = []
        else:
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [
            n
            for n in neighbors
            if 0 <= n[0] < self.grid.grid_width and 0 <= n[1] < self.grid.grid_height
        ]

    def _cost_to_move(
        self,
        current: tuple[int, int],
        neighbor: tuple[int, int],
        parent: tuple[int, int] | None,
    ) -> float:
        cost = 1  # Base cost

        # Turn penalty
        if parent:
            dx1 = current[0] - parent[0]
            dy1 = current[1] - parent[1]
            dx2 = neighbor[0] - current[0]
            dy2 = neighbor[1] - current[1]
            if dx1 != dx2 or dy1 != dy2:
                cost += 1  # Add penalty for turning

        return cost

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
