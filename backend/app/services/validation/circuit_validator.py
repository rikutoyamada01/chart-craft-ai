from collections import defaultdict
from itertools import combinations

from app.models.circuit import CircuitData
from app.models.validation import ErrorCode, ValidationError
from app.services.renderers.svg_component_renderer_factory import (
    svg_component_renderer_factory,
)


class CircuitValidator:
    def __init__(self, circuit_data: CircuitData):
        self.circuit = circuit_data.circuit
        self.components_by_id = {c.id: c for c in self.circuit.components}
        self.port_graph = self._build_port_graph()

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        errors.extend(self._check_component_overlaps())
        errors.extend(self._check_floating_ports())
        errors.extend(self._check_power_loops_and_shorts())
        errors.extend(self._check_minimum_spacing())
        errors.extend(self._check_layout_conventions())
        return errors

    def _build_port_graph(self) -> dict[tuple[str, int], list[tuple[str, int]]]:
        graph = defaultdict(list)

        # Add external connections (wires)
        for conn in self.circuit.connections:
            source_node = (conn.source.component_id, conn.source.port_index)
            target_node = (conn.target.component_id, conn.target.port_index)
            graph[source_node].append(target_node)
            graph[target_node].append(source_node)

        # Efficiently handle bare junctions by first grouping ports by junction
        junctions = defaultdict(list)
        for conn in self.circuit.connections:
            # A junction is identified by a connection endpoint having a component_id but no port_index.
            # The current model makes port_index required, but this logic anticipates a more flexible model.
            source_is_port = (
                hasattr(conn.source, "port_index")
                and conn.source.port_index is not None
            )
            target_is_port = (
                hasattr(conn.target, "port_index")
                and conn.target.port_index is not None
            )

            if source_is_port and not target_is_port:
                junctions[conn.target.component_id].append(
                    (conn.source.component_id, conn.source.port_index)
                )
            elif target_is_port and not source_is_port:
                junctions[conn.source.component_id].append(
                    (conn.target.component_id, conn.target.port_index)
                )

        for junction_id in junctions:
            ports_at_junction = junctions[junction_id]
            for p1, p2 in combinations(ports_at_junction, 2):
                graph[p1].append(p2)
                graph[p2].append(p1)

        # Add internal connections (through components)
        for comp in self.circuit.components:
            if comp.type == "junction":
                continue
            renderer = svg_component_renderer_factory.get_renderer(comp.type)
            if not renderer:
                continue

            ports_on_comp = []
            for i in range(len(renderer.ports)):
                try:
                    renderer.get_port_position(comp, i)
                    ports_on_comp.append(i)
                except ValueError:
                    continue

            # A more sophisticated model is needed for internal connections.
            # For now, only model simple two-port pass-through components.
            if (
                comp.type in ["resistor", "led", "capacitor", "coil"]
                and len(ports_on_comp) == 2
            ):
                p1, p2 = ports_on_comp
                node1 = (comp.id, p1)
                node2 = (comp.id, p2)
                graph[node1].append(node2)
                graph[node2].append(node1)
            elif comp.type == "transistor_npn":
                # For validation, model a path between collector and emitter.
                # This doesn't account for the base signal, but allows loop checking.
                try:
                    collector_index = renderer.ports.index("collector")
                    emitter_index = renderer.ports.index("emitter")
                    node1 = (comp.id, collector_index)
                    node2 = (comp.id, emitter_index)
                    graph[node1].append(node2)
                    graph[node2].append(node1)
                except ValueError:
                    # This case would be rare, but handles missing ports gracefully
                    continue
        return graph

    def _check_component_overlaps(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        component_ids = [c.id for c in self.circuit.components]

        for id1, id2 in combinations(component_ids, 2):
            comp1 = self.components_by_id[id1]
            comp2 = self.components_by_id[id2]

            if not (
                comp1.properties
                and comp1.properties.position
                and comp2.properties
                and comp2.properties.position
            ):
                continue

            renderer1 = svg_component_renderer_factory.get_renderer(comp1.type)
            renderer2 = svg_component_renderer_factory.get_renderer(comp2.type)

            if not (renderer1 and renderer2):
                continue

            width1, height1 = renderer1.get_bounding_box(comp1)
            rot1 = (comp1.properties.rotation or 0) % 360
            if rot1 in [90, 270]:
                width1, height1 = height1, width1

            width2, height2 = renderer2.get_bounding_box(comp2)
            rot2 = (comp2.properties.rotation or 0) % 360
            if rot2 in [90, 270]:
                width2, height2 = height2, width2

            box1_min_x = comp1.properties.position.x - width1 / 2
            box1_max_x = comp1.properties.position.x + width1 / 2
            box1_min_y = comp1.properties.position.y - height1 / 2
            box1_max_y = comp1.properties.position.y + height1 / 2

            box2_min_x = comp2.properties.position.x - width2 / 2
            box2_max_x = comp2.properties.position.x + width2 / 2
            box2_min_y = comp2.properties.position.y - height2 / 2
            box2_max_y = comp2.properties.position.y + height2 / 2

            if not (
                box1_max_x < box2_min_x
                or box1_min_x > box2_max_x
                or box1_max_y < box2_min_y
                or box1_min_y > box2_max_y
            ):
                errors.append(
                    ValidationError(
                        error_code=ErrorCode.VISUAL_COMPONENT_OVERLAP,
                        message=f"Component '{comp1.id}' is overlapping with component '{comp2.id}'.",
                        offending_components=[comp1.id, comp2.id],
                    )
                )
        return errors

    def _check_floating_ports(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        connected_ports: set[tuple[str, int]] = set()
        for conn in self.circuit.connections:
            connected_ports.add((conn.source.component_id, conn.source.port_index))
            connected_ports.add((conn.target.component_id, conn.target.port_index))

        for comp in self.circuit.components:
            if comp.type == "junction":
                continue

            renderer = svg_component_renderer_factory.get_renderer(comp.type)
            if not renderer:
                continue

            for i in range(len(renderer.ports)):
                try:
                    renderer.get_port_position(comp, i)
                    if (comp.id, i) not in connected_ports:
                        errors.append(
                            ValidationError(
                                error_code=ErrorCode.LOGIC_FLOATING_PORT,
                                message=f"Port index {i} of component '{comp.id}' is not connected.",
                                offending_components=[comp.id],
                            )
                        )
                except ValueError:
                    continue
        return errors

    def _check_power_loops_and_shorts(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        power_sources = [c for c in self.circuit.components if c.type == "battery"]
        # Capacitors block DC current, so they are not considered a load in a DC short-circuit check.
        load_types = {"resistor", "led", "coil", "transistor_npn"}

        if not power_sources:
            return []

        for source in power_sources:
            renderer = svg_component_renderer_factory.get_renderer(source.type)
            if not renderer:
                continue
            try:
                positive_index = renderer.ports.index("positive")
                negative_index = renderer.ports.index("negative")
            except ValueError:
                # If a battery renderer doesn't define these ports, skip it.
                continue

            start_node = (source.id, positive_index)
            end_node = (source.id, negative_index)

            q = [(start_node, [source.id])]
            visited = {start_node}
            path_found_to_negative = False

            while q:
                current_node, path = q.pop(0)

                if current_node == end_node:
                    path_found_to_negative = True
                    has_load = False
                    for comp_id in path:
                        if self.components_by_id[comp_id].type in load_types:
                            has_load = True
                            break
                    if not has_load:
                        errors.append(
                            ValidationError(
                                error_code=ErrorCode.LOGIC_SHORT_CIRCUIT,
                                message=f"Short circuit detected across power source '{source.id}'.",
                                offending_components=[source.id],
                            )
                        )
                    continue

                for neighbor_node in self.port_graph.get(current_node, []):
                    if neighbor_node not in visited:
                        visited.add(neighbor_node)
                        new_path = path + [neighbor_node[0]]
                        q.append((neighbor_node, new_path))

            if not path_found_to_negative:
                errors.append(
                    ValidationError(
                        error_code=ErrorCode.LOGIC_NO_POWER_LOOP,
                        message=f"Power source '{source.id}' does not have a closed loop from positive to negative terminal.",
                        offending_components=[source.id],
                    )
                )
        return errors

    def _check_minimum_spacing(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        spacing_margin = 10
        component_ids = [c.id for c in self.circuit.components]

        for id1, id2 in combinations(component_ids, 2):
            comp1 = self.components_by_id[id1]
            comp2 = self.components_by_id[id2]

            if not (
                comp1.properties
                and comp1.properties.position
                and comp2.properties
                and comp2.properties.position
            ):
                continue

            renderer1 = svg_component_renderer_factory.get_renderer(comp1.type)
            renderer2 = svg_component_renderer_factory.get_renderer(comp2.type)

            if not (renderer1 and renderer2):
                continue

            width1, height1 = renderer1.get_bounding_box(comp1)
            rot1 = (comp1.properties.rotation or 0) % 360
            if rot1 in [90, 270]:
                width1, height1 = height1, width1

            width2, height2 = renderer2.get_bounding_box(comp2)
            rot2 = (comp2.properties.rotation or 0) % 360
            if rot2 in [90, 270]:
                width2, height2 = height2, width2

            box1_min_x = comp1.properties.position.x - (width1 / 2) - spacing_margin
            box1_max_x = comp1.properties.position.x + (width1 / 2) + spacing_margin
            box1_min_y = comp1.properties.position.y - (height1 / 2) - spacing_margin
            box1_max_y = comp1.properties.position.y + (height1 / 2) + spacing_margin

            box2_min_x = comp2.properties.position.x - width2 / 2
            box2_max_x = comp2.properties.position.x + width2 / 2
            box2_min_y = comp2.properties.position.y - height2 / 2
            box2_max_y = comp2.properties.position.y + height2 / 2

            if not (
                box1_max_x < box2_min_x
                or box1_min_x > box2_max_x
                or box1_max_y < box2_min_y
                or box1_min_y > box2_max_y
            ):
                errors.append(
                    ValidationError(
                        error_code=ErrorCode.VISUAL_MINIMUM_SPACING,
                        message=f"Component '{comp1.id}' is too close to component '{comp2.id}'.",
                        offending_components=[comp1.id, comp2.id],
                    )
                )
        return errors

    def _check_layout_conventions(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        # Power Placement Check: VCC should be higher than GND
        power_sources = [
            c
            for c in self.circuit.components
            if c.type == "battery" and c.properties and c.properties.position
        ]
        ground_nodes = [
            c
            for c in self.circuit.components
            if "gnd" in c.id.lower() and c.properties and c.properties.position
        ]

        if power_sources and ground_nodes:
            avg_power_y = sum(c.properties.position.y for c in power_sources) / len(
                power_sources
            )
            avg_gnd_y = sum(c.properties.position.y for c in ground_nodes) / len(
                ground_nodes
            )

            if avg_power_y >= avg_gnd_y:
                errors.append(
                    ValidationError(
                        error_code=ErrorCode.VISUAL_CONVENTION_VCC_HIGH,
                        message="Layout convention violated: Power sources (VCC) should be placed above ground (GND) nodes.",
                        offending_components=[c.id for c in power_sources]
                        + [c.id for c in ground_nodes],
                    )
                )

        # TODO: Implement Signal Flow Check (REQ-V3)
        # This would require identifying input/output nodes and checking their relative X positions.

        # TODO: Implement Component Rotation Convention Check (REQ-V3)
        # This would require identifying circuit patterns (e.g., voltage dividers, collector resistors)
        # and checking for conventional rotations (e.g., 90 degrees for a collector resistor).

        return errors
