import heapq
import logging

from app.models.circuit import Position
from app.services.routing.grid import Grid

logger = logging.getLogger(__name__)


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
        """
        Find a path from start to end using A* algorithm.

        Strategy:
        1. Clear obstacles around start and end nodes to ensure connectivity
        2. Explore all possible paths, avoiding hard obstacles
        3. Prefer paths that avoid soft obstacles
        4. Minimize turns for natural paths
        """
        start_node = (
            start_pos.x // self.grid.grid_size,
            start_pos.y // self.grid.grid_size,
        )
        end_node = (
            end_pos.x // self.grid.grid_size,
            end_pos.y // self.grid.grid_size,
        )

        # Ensure sufficient clearance around the start and end nodes
        # Need enough space to allow path finding while still respecting boundaries
        nodes_to_clear = {start_node, end_node}
        for node in [start_node, end_node]:
            x, y = node
            # Clear 1.5-cell radius (chevron pattern: 5x5 central area)
            # Provides good connectivity while limiting deep penetration
            for dx in [-1, 0, 1, -2, 2]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Skip the center node itself
                    nodes_to_clear.add((x + dx, y + dy))
            for dx in [-1, 0, 1]:
                for dy in [-2, 2]:
                    if dx == 0 and dy == 0:
                        continue
                    nodes_to_clear.add((x + dx, y + dy))

        for node in nodes_to_clear:
            if node in self.grid.hard_obstacles:
                self.grid.hard_obstacles.remove(node)
            if node in self.grid.soft_obstacles:
                self.grid.soft_obstacles.remove(node)

        # A* search
        open_set: list[tuple[float, tuple[int, int]]] = []
        heapq.heappush(open_set, (0, start_node))

        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start_node: None}
        g_score: dict[tuple[int, int], float] = {start_node: 0}
        # Track path length from start for each node
        path_length: dict[tuple[int, int], int] = {start_node: 0}
        visited: set[tuple[int, int]] = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in visited:
                continue
            visited.add(current)

            if current == end_node:
                path = self._reconstruct_path(came_from, current)
                logger.debug(f"Path found: {len(path)} nodes")
                return self._smooth_path(path)

            # Determine the preferred direction based on proximity to start or end
            preferred_direction = None
            is_near_end = self._heuristic(current, end_node) <= 3
            if current == start_node:
                preferred_direction = start_direction
            elif is_near_end:
                preferred_direction = end_direction

            current_path_length = path_length.get(current, 0)
            neighbors = self._get_neighbors(current)

            for neighbor in neighbors:
                if neighbor in visited:
                    continue

                if self.grid.is_hard_obstacle(neighbor[0], neighbor[1]):
                    continue

                tentative_g_score = g_score.get(
                    current, float("inf")
                ) + self._cost_to_move(
                    current,
                    neighbor,
                    came_from.get(current),
                    end_node,
                    preferred_direction,
                    current_path_length,
                )

                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    path_length[neighbor] = current_path_length + 1
                    f_score = tentative_g_score + self._heuristic(neighbor, end_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        logger.warning(f"No path found from {start_node} to {end_node}")
        return None  # Path not found

    def _get_neighbors(self, node: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Get valid neighboring nodes.
        """
        x, y = node
        possible_neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        # Filter to only valid grid coordinates
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
        end_node: tuple[int, int],
        preferred_direction: str | None = None,
        current_path_length: int = 0,
    ) -> float:
        """
        Calculate cost to move to a neighbor cell based on a strict priority hierarchy.
        """
        # 1. Base movement cost
        cost = 1.0

        # 2. Ultra-high penalty for immediate proximity to hard obstacles (1000s magnitude)
        is_adjacent_to_obstacle = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if self.grid.is_hard_obstacle(neighbor[0] + dx, neighbor[1] + dy):
                    is_adjacent_to_obstacle = True
                    break
            if is_adjacent_to_obstacle:
                break
        if is_adjacent_to_obstacle:
            cost += 1000.0

        # 3. Very high penalty for not following preferred direction at the start (500s magnitude)
        if parent is None and preferred_direction:
            dx = neighbor[0] - current[0]
            dy = neighbor[1] - current[1]
            is_moving_preferred = False
            if preferred_direction == "up" and dx == 0 and dy == -1:
                is_moving_preferred = True
            elif preferred_direction == "down" and dx == 0 and dy == 1:
                is_moving_preferred = True
            elif preferred_direction == "left" and dx == -1 and dy == 0:
                is_moving_preferred = True
            elif preferred_direction == "right" and dx == 1 and dy == 0:
                is_moving_preferred = True

            if not is_moving_preferred:
                cost += 500.0

        # 4. High penalty for turning (100s magnitude), with extreme penalty near the end node
        if parent is not None:
            dx1 = current[0] - parent[0]
            dy1 = current[1] - parent[1]
            dx2 = neighbor[0] - current[0]
            dy2 = neighbor[1] - current[1]

            is_straight = dx1 == dx2 and dy1 == dy2
            if not is_straight:
                turn_penalty = 100.0
                # If close to the end node, make turning extremely expensive to prevent overshooting
                if self._heuristic(current, end_node) <= 2:
                    turn_penalty = 1000.0
                cost += turn_penalty

        # 5. Medium penalty for crossing existing wires (soft obstacles)
        if self.grid.is_soft_obstacle(neighbor[0], neighbor[1]):
            cost += 50.0

        # 6. Penalty for moving against the dominant direction to the goal (10s magnitude)
        total_dx = abs(current[0] - end_node[0])
        total_dy = abs(current[1] - end_node[1])
        move_dx = neighbor[0] - current[0]
        move_dy = neighbor[1] - current[1]

        # Add a graded penalty for moving perpendicular to the dominant axis.
        # The penalty is proportional to how dominant one axis is over the other.
        macro_direction_penalty = 0.0
        # Avoid division by zero and apply only when not at the goal
        if total_dx + total_dy > 0:
            if total_dx > total_dy:  # Path is more horizontal than vertical
                if move_dy != 0:  # Penalize vertical movement
                    # Penalty is larger when the path is almost purely horizontal (dy is small compared to dx)
                    ratio = total_dy / total_dx
                    macro_direction_penalty = 20.0 * (1 - ratio)
            else:  # Path is more vertical than horizontal (or equal)
                if move_dx != 0:  # Penalize horizontal movement
                    # Penalty is larger when the path is almost purely vertical (dx is small compared to dy)
                    if total_dy > 0:  # Avoid division by zero if total_dy is 0
                        ratio = total_dx / total_dy
                        macro_direction_penalty = 20.0 * (1 - ratio)

        cost += macro_direction_penalty

        # 7. Low penalty for proximity to medium-range obstacles (1-20s magnitude)
        scan_radius = 3  # Scan a 7x7 area
        proximity_penalty = 0.0
        for dx in range(-scan_radius, scan_radius + 1):
            for dy in range(-scan_radius, scan_radius + 1):
                distance = abs(dx) + abs(dy)
                # Only consider obstacles that are not immediately adjacent (distance > 1)
                if distance <= 1:
                    continue

                check_x, check_y = neighbor[0] + dx, neighbor[1] + dy
                if self.grid.is_hard_obstacle(check_x, check_y):
                    # Penalty is inversely proportional to distance, ensuring it's a low-priority cost
                    proximity_penalty += 20.0 / (distance**2)

        cost += proximity_penalty

        return cost

    def _heuristic(self, node: tuple[int, int], end_node: tuple[int, int]) -> float:
        """
        Manhattan distance heuristic (admissible for A*).
        """
        return abs(node[0] - end_node[0]) + abs(node[1] - end_node[1])

    def _reconstruct_path(
        self, came_from: dict, current: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Reconstruct the path from start to current node.
        """
        path = [current]
        while current in came_from and came_from[current] is not None:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def _smooth_path(self, path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        Smooth the path by keeping only the start, end, and corner points.
        This ensures the path remains orthogonal (composed of only horizontal and vertical segments).
        """
        if len(path) < 3:
            return path

        smoothed_path = [path[0]]
        for i in range(1, len(path) - 1):
            p_prev = path[i - 1]
            p_curr = path[i]
            p_next = path[i + 1]

            # Calculate direction vectors
            dx1 = p_curr[0] - p_prev[0]
            dy1 = p_curr[1] - p_prev[1]
            dx2 = p_next[0] - p_curr[0]
            dy2 = p_next[1] - p_curr[1]

            # If the direction changes, it's a corner
            if dx1 != dx2 or dy1 != dy2:
                smoothed_path.append(p_curr)

        smoothed_path.append(path[-1])
        return smoothed_path
