# ADR-HFG-5B — Manufacturing Review Rendering Contract

**Status:** Accepted

---

## Context

- **SceneRenderer** (scene_graph/renderer.py) is the canonical manufacturing
  renderer per ADR-HFG-1.
- **HFG-3** added manufacturing overlays via
  `build_visual_overlays` → `build_viewport_overlay_commands`.
- **HFG-4** added hole visualization metadata:
  - `hole_style`
  - `drill_direction`
  - `hole_depth`
  - `hole_depth_mode`
- **HFG-5A** added manufacturing review metadata:
  - `review_mode`
  - `review_category`
  - `review_priority`

Each series extended SceneRenderer's overlay pipeline with rendering-only
fields derived from the existing manufacturing model. No series introduced
business logic, cost computation, or production-decision code into the
renderer.

This ADR formalises the boundary that those series implicitly respected,
so future HFG work stays within the rendering contract.

---

## Decision

1. **SceneRenderer may derive rendering-only metadata** from existing overlay
   fields using pure, side-effect-free mappings.

2. **Allowed derivations:**

   | Source field            | Derived rendering metadata                     |
   |-------------------------|------------------------------------------------|
   | `overlay_type`          | `review_category`, `review_priority` defaults  |
   | `overlay_type`          | `hole_style` defaults                          |
   | `face`                  | `drill_direction`                              |
   | `depth`, `is_through`   | `hole_depth`, `hole_depth_mode`                |

   These mappings are pure functions: same input always produces the same
   output, no external state is consulted.

3. **SceneRenderer must not:**

   - Compute manufacturing feasibility
   - Compute costs
   - Compute factory readiness scores
   - Modify `VisualMetadata` after creation
   - Change manufacturing-operation semantics (e.g. reinterpret a pocket as
     a drill)
   - Become a workflow, engine, controller, or service

4. **Future extraction rule:**

   If rendering-classification logic grows beyond a simple pure mapping
   (e.g. requires state, external data, or multi-step derivation), extract
   it to a helper module inside `scene_graph/` only — never to a new
   engine, service, or renderer.

---

## Consequences

### Positive

- Clear rendering boundary protects SceneRenderer from scope creep.
- Better manufacturing review UX through richer visual metadata.
- No duplication of manufacturing-domain logic inside rendering code.
- Preserves the layered architecture established in ADR-HFG-1.

### Negative

- SceneRenderer carries more responsibility for rendering metadata than
  before HFG-3.
- Maintaining the boundary requires code-review discipline — any new
  overlay field must be classified as rendering-only or business logic
  before merging.

---

## Non-goals

This ADR explicitly does **not** address:

- A new rendering engine
- CNC machining logic
- Cost estimation or quoting logic
- Factory-dashboard business rules
- AI or agent-based feature generation

These remain in their respective architectural layers (manufacturing domain,
factory optimisation, etc.).

---

## Validation

The contract is validated by the current passing test groups:

| Test area                                      | Passing count |
|------------------------------------------------|---------------|
| `tests/scene_graph`                            | 216           |
| `tests/factory_dashboard`,                     |               |
| `tests/factory_operational_intelligence`,      | 159           |
| `tests/architecture`                           |               |

All pre-HFG-5B rendering tests continue to pass. No tests were modified as
part of this ADR.

---

## Recommendation

Continue HFG series work **only** if new features improve manufacturing
review value without crossing the rendering boundary defined above. Any
proposed derivation that does not appear in the allowed-derivations table
requires a new ADR.
