# Refactoring Proposal: Port Indexing

## 1. Context & Problem

Currently, the circuit's `connections` are defined in the YAML using string-based port names, like `port: "collector"` or `port: "left"`.

While human-readable, this approach creates a **brittle interface** between the AI agent generating the YAML and the rendering/validation system. The system relies on the AI perfectly adhering to a convention of names. This is a known weakness in LLM-based generation, as it's prone to typos, case-sensitivity issues, or other minor variations that would break the system (`"collector"` vs. `"colector"` vs. `"Collector"`).

This forces the `CircuitValidator` to have a rule (`LOGIC_INVALID_PORT_NAME`) just to catch these simple errors, which could be prevented at a deeper, structural level.

## 2. Proposed Solution: Port Indexing

To create a more robust, contract-based interface, this proposal recommends moving from string-based names to **stable, integer-based indices** for identifying ports.

Each component type will have a documented, canonical order for its ports. For example:

-   **Resistor:** `[0: left, 1: right]`
-   **NPN Transistor:** `[0: base, 1: collector, 2: emitter]`
-   **Battery:** `[0: positive, 1: negative]`

The YAML definition would be updated to use a `port_index` field instead of `port`.

### Example

**Before (Current):**
```yaml
- source: {component_id: "r1", port: "right"}
  target: {component_id: "q1", port: "base"}
```

**After (Proposed):**
```yaml
- source: {component_id: "r1", port_index: 1}  # 1 corresponds to "right"
  target: {component_id: "q1", port_index: 0}  # 0 corresponds to "base"
```

## 3. Architectural Justification & Alignment

This change strongly aligns with the project's core goal of reliably generating correct circuits from an AI.

-   **For the AI:** A constrained, integer-based schema (`port_index: <int>`) is easier for an LLM to generate reliably than a free-form string. This reduces the likelihood of the AI producing invalid YAML.
-   **For the System:** It eliminates an entire class of potential bugs related to naming. The system becomes more robust, and the validation logic simplifies, as it no longer needs to validate names.
-   **For Future Extensibility:** When adding complex components (e.g., ICs with many pins), a zero-based index is a clean, scalable, and unambiguous way to define connection points.

## 4. Trade-offs

-   **Pro:** Greatly improves the reliability and robustness of the AI-to-system interface.
-   **Pro:** Simplifies validation logic.
-   **Con:** The raw YAML becomes slightly less human-readable, as one must know that `port_index: 1` on a resistor means "right". This is a minor trade-off that can be easily mitigated with clear documentation.

## 5. Conclusion

This refactoring is a strategic architectural improvement. It hardens the core data structure against the most likely source of AI-generation errors, making the entire system more reliable and scalable for the future.
