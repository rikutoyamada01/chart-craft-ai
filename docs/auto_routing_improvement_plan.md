# Auto-Routing Algorithm Improvement Plan

## 1. Current Issues

The current A* routing algorithm faces two primary challenges:

1.  **Routing Failures (Red Lines):** For certain complex component layouts, the router fails to find a path, resulting in a direct, diagonal red line. This is caused by a simplistic obstacle model where component margins can completely block valid paths.
2.  **Unnatural Pathing:** Successfully routed paths often take unnatural routes, with unnecessary bends and proximity to components. This is due to a naive cost function that doesn't penalize turns or proximity to obstacles.

## 2. Proposed Solution: Introduce "Soft" and "Hard" Obstacles

To fundamentally solve these issues, we propose evolving the obstacle model and cost function by introducing a two-tiered obstacle system.

### 2.1. Hard Obstacles (Impassable)

-   **Definition:** The core area of a component's body.
-   **Implementation:** These will be the areas defined by a component's bounding box with a `margin=0`.
-   **Rule:** A path can **never** cross a hard obstacle.

### 2.2. Soft Obstacles (High-Penalty)

-   **Definition:** Areas that are valid for routing but should be avoided if possible.
    1.  The safety margin around a component (the area equivalent to `margin=1`).
    2.  The path taken by any previously routed wire.
-   **Implementation:** These areas will be tracked in a separate `soft_obstacles` set in the `Grid`.
-   **Rule:** The A* algorithm's cost function (`_cost_to_move`) will be modified to return a significantly higher cost (e.g., `10.0`) for moving into a soft obstacle.

## 3. Implementation Steps

1.  **Modify `grid.py`:**
    -   Rename `self.obstacles` to `self.hard_obstacles`.
    -   Add a new `self.soft_obstacles` set.
    -   Modify `add_obstacle()` to populate both `hard_obstacles` (with `margin=0`) and `soft_obstacles` (the area between `margin=0` and `margin=1`).
    -   Create `is_hard_obstacle()` and `is_soft_obstacle()` methods.

2.  **Modify `a_star.py`:**
    -   Update `_cost_to_move()` to return a high cost if the neighboring node is in `grid.soft_obstacles`. This will be in addition to the existing turn penalty.

3.  **Modify `svg_formatter.py`:**
    -   In the connection routing loop, after a path is successfully found, iterate through the grid cells of that path and add them to the `grid.soft_obstacles` set for the next iteration.

## 4. Expected Outcomes

-   **Elimination of Routing Failures:** By allowing the router to cross "soft" obstacles (at a high cost), a path will always be found as long as one is physically possible, eliminating red lines.
-   **Aesthetically Pleasing Paths:** The combination of turn penalties and soft obstacle penalties will guide the algorithm to find paths that are straighter and maintain a safe, natural distance from components and other wires.
