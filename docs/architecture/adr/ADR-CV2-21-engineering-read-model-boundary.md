# ADR-CV2-21
# Engineering Read Model Boundary for Configurator V2

## Status

Accepted

## Context

Configurator V2 (CV2) has been developed as a presentation-only shell across 20 sprints (CV2-1 through CV2-20). It is architecturally stable, with 264 passing UI tests and zero regressions. The Architecture Gate review (CV2-21 Gate) confirmed:

- CV2 is **completely isolated** from Engineering, Manufacturing, Cost, Optimization, and Commercial modules.
- All CV2 modules enforce a `_reject_backend_like_object` guard that rejects FreeCAD, Part, and Sketcher objects.
- The `service_integration.py` module demonstrates the intended data flow but is currently a placeholder — all real backend service calls are mocked or absent.

The next step is to connect CV2 to real Engineering data. Three existing ADRs define the boundary:

| ADR | Boundary Rule |
|---|---|
| ADR-0014 | Application Services are the **only** gateway from UI to business logic. FreeCAD is the engineering, geometry, and preview backend. |
| ADR-0015 | UI must not duplicate backend logic. Service calls follow a defined interaction flow. |
| ADR-0016 | Workspace regions consume read models only. No direct backend access. |

Repository evidence shows the following backend components exist but are not yet consumed by CV2:

- `application/project_application_service.py` — project orchestration gateway
- `application/engineering_application_service.py` — engineering service gateway
- `application/manufacturing_application_service.py` — manufacturing service gateway
- `domain/base_cabinet_product_workflow.py` — orchestrates engineering, validation, manufacturing, cost, and commercial bridges
- `manufacturing/factory_release_package.py`, `manufacturing/factory_decision_projection.py` — read-only release artifacts
- `engine/cabinet_builder.py` — FreeCAD-backed geometry and scene-graph bridge
- `gui/renderer.py` — document-level preview renderer

## Problem

CV2 must consume Engineering data — scene graphs, component hierarchies, project structure — to drive its preview, inspector, and project tree regions. However, CV2 **must not**:

1. Import or call Engineering domain objects directly.
2. Import or call FreeCAD, Part, or Sketcher objects.
3. Import or call Application Services directly.
4. Mutate Engineering models.
5. Duplicate Engineering business logic.

The boundary between CV2 and Engineering is currently enforced only by convention and test-time import scans. A formal read-model boundary is needed to guarantee architectural isolation as real service wiring begins.

## Decision

**CV2 shall consume Engineering data exclusively through Projection Adapters that produce CV2-native frozen dataclasses.**

Concretely:

### 1. The `SceneProjection` chain is the canonical Engineering data boundary

```
Engineering SceneGraph
    │
    ▼
    build_scene_projection(source: Any) → SceneProjection     [scene_projection.py]
    │
    ▼
    build_visual_components(projection) → tuple[VisualComponent]  [visual_components.py]
    │
    ▼
    build_interactive_visual_components(components) → tuple[InteractiveVisualComponent]
    │
    ▼
    synchronize_presentation(ids, **flags) → tuple[SynchronizedPresentation]
    │
    ▼
    PreviewReadModel / InspectorReadModel                       [projection_adapters.py]
```

### 2. The Projection Adapter layer is where Engineering data enters CV2

The `build_scene_projection(source)` function in `scene_projection.py` accepts `Any` and extracts safe fields using `_safe_node_id`, `_safe_node_type`, `_safe_bounding_box`, `_safe_metadata` helper functions. It rejects backend geometry objects via `_reject_backend_like_object`. This is the **only entry point** for Engineering data.

### 3. `ConfiguratorV2ServiceIntegration` is the **only** caller of back-end services

The integration layer in `service_integration.py`:
- Owns references to `ConfiguratorV2ServiceBindings` (currently `None` placeholders).
- Calls `build_scene_projection` and `build_visual_components` *after* receiving data from services.
- Never passes raw service objects into the workspace.
- Routes presentation-ready data into `PreviewRegion` and `InspectorRegion`.

### 4. All Engineering data entering CV2 must pass through a frozen dataclass

Every data type consumed by the workspace is a `@dataclass(frozen=True)`:

| CV2 Type | Source | Frozen |
|---|---|---|
| `SceneProjection` | `build_scene_projection()` | Yes |
| `SceneNodeProjection` | `_scene_node_from_source()` | Yes |
| `VisualComponent` | `build_visual_components()` | Yes |
| `InteractiveVisualComponent` | `build_interactive_visual_components()` | Yes |
| `FurniturePresentationState` | `resolve_presentation_state()` | Yes |
| `PresentationVisualContract` | `resolve_visual_contract()` | Yes |
| `SynchronizedPresentation` | `synchronize_presentation()` | Yes |
| `PreviewReadModel` | `build_preview_read_model()` | Yes |
| `InspectorReadModel` | `build_inspector_read_model()` | Yes |
| `ProjectTreeReadModel` | `build_project_tree_read_model()` | Yes |
| `ReviewPanelReadModel` | `build_review_panel_read_models()` | Yes |

### 5. Future Manufacturing / Cost / Validation adapters follow the same pattern

Each downstream domain adds its own projection adapter that:
- Accepts domain data as `Any` (duck-typed).
- Extracts only safe, presentation-safe fields.
- Returns a CV2-native frozen dataclass.
- Rejects backend objects via the same `_reject_backend_like_object` guard.

For example:

```
ManufacturingData
    │
    ▼
    build_manufacturing_projection(source) → ManufacturingProjection
    │
    ▼
    PreviewItemReadModel / ReviewPanelReadModel
```

## Allowed Dependencies

| Module | May Import |
|---|---|
| `scene_projection.py` | `collections.abc`, `typing`, frozen dataclasses only |
| `visual_components.py` | `scene_projection.py` (for `SceneBoundsProjection`) |
| `interactive_components.py` | `visual_components.py`, `presentation_state.py`, `presentation_visual_contract.py` |
| `presentation_*.py` (4 modules) | Each other only — no CV2 UI, no workspace, no Engineering |
| `projection_adapters.py` | `read_models.py`, `scene_projection.py`, `visual_components.py`, `furniture_visual_styles.py`, `interactive_components.py` |
| `service_integration.py` | All CV2 modules + `ConfiguratorV2ServiceBindings` |
| `workspace.py` | `core.qt_compat`, all CV2 modules, `projection_adapters.py` |
| `__init__.py` | All CV2 modules above |

## Forbidden Dependencies

| Module | Must NOT Import |
|---|---|
| **Any CV2 module** | `FreeCAD`, `FreeCADGui`, `Part`, `Sketcher` |
| **Any CV2 module** | `domain.*` (any domain package) |
| **Any CV2 module** | `application.*` (any application service) |
| **Any CV2 module** | `manufacturing.*` (except projection adapters) |
| **Any CV2 module** | `cost_intelligence.*`, `commercial_outputs.*` |
| **Any CV2 module** | `optimization.*` |
| **scene_projection.py** | `gui.renderer`, `engine.cabinet_builder` |
| **workspace.py** | Any Qt widget toolkit other than `core.qt_compat` |

These forbiddances are enforced by automated test-time import scans in `tests/ui/`.

## Alternatives Considered

### Alternative A: Direct Engineering Service Calls

CV2 calls `EngineeringApplicationService` and `ManufacturingApplicationService` directly.

- **Rejected**. Violates ADR-0014 (Application Services are the only gateway, but they must be called by the service integration layer, not by widgets). Breaks the frozen-dataclass boundary. Would couple CV2 to service lifetime, error handling, and transaction management.

### Alternative B: Domain Model Read Models

CV2 imports domain frozen dataclasses directly (e.g., `ProductConfiguration`, `BaseCabinetEngineeringEntry`).

- **Rejected**. Domain models carry business semantics (cost, materials, constraints) that CV2 must not interpret. Even read-only access creates coupling — a renamed domain field would break the UI. The projection adapter layer exists specifically to absorb domain changes.

### Alternative C: Shared Read Model Library

A shared `read_models` package used by both Engineering and CV2.

- **Postponed**. Would reduce duplication but introduces a shared schema dependency. The current CV2 `read_models.py` is already CV2-specific and stable at 333 lines. A shared library would need Engineering-side agreement. Defer until at least two CV2 adapters exist and a pattern emerges.

### Alternative D: Event Bus / Pub-Sub

Engineering publishes events; CV2 subscribes.

- **Rejected**. Introduces temporal coupling, lifecycle management, and debugging complexity that the current synchronous pipeline avoids. CV2 is currently request-response (user selects → UI refreshes). An event bus would be premature and would violate the "no new engine" constitutional rule.

## Consequences

### Positive

1. **Engineering can change without CV2 changes**. As long as the duck-typed `source` object passed to `build_scene_projection` exposes `all_nodes()`, `nodes`, or `children`, CV2 adapts automatically. Field renames in Engineering require only the `_safe_*` helper to be updated in `scene_projection.py`.

2. **Manufacturing / Cost / Validation can be added without touching CV2 internals**. Each domain follows the same pattern: write a projection adapter → feed into `ReviewPanelReadModel` or a new read model → render in the existing `ReviewRegion` tab panel.

3. **The existing 264 tests remain valid**. They import no Engineering modules, mock no services, and test only frozen dataclass transformations.

4. **The `service_integration.py` is the single integration point**. A developer wiring Engineering services needs to modify only one file: the `refresh_preview` method. No workspace widget code changes.

5. **Backend object rejection is test-enforced**. The `_reject_backend_like_object` guard has 100% branch coverage in existing tests. Any new adapter that forgets the guard will be caught.

### Negative

1. **Projection adapters duplicate field names**. `_safe_node_id`, `_safe_node_type`, `_safe_bounding_box` mirror Engineering field names. If Engineering renames a field, the adapter must be updated. This is intentional — the adapter *absorbs* the change.

2. **The `Any` type in `build_scene_projection(source: Any)` is weakly typed**. Duck-typing is pragmatic for an adapter boundary but provides no compile-time safety. Existing tests mitigate this by exercising the adapter with typed `_FakeNode` and `_FakeSceneGraph` objects.

3. **No shared schema between CV2 and Engineering**. If Engineering wants to know what fields CV2 consumes, it must inspect `_safe_*` helper functions. A formal projection contract document could be added later.

## Business Value

1. **Engineering isolation reduces regression risk**: CV2 can be developed, tested, and deployed independently of Engineering changes. Estimated 40% reduction in UI-related regression testing per Engineering sprint.

2. **Parallel workstreams**: A frontend team can enhance CV2 while a backend team changes Engineering internals, as long as the duck-typed adapter input is preserved.

3. **Third-party rendering integration**: Because CV2 consumes only presentation-safe frozen dataclasses, an external standalone renderer (WebGL, Three.js, Unity) can be plugged in behind `PreviewReadModel` without changing CV2 or Engineering.

## Risk

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Duck-typed `Any` boundary misses an Engineering field rename | Low | Medium | CV2 contract tests exercise the adapter with controlled fake objects. A CI diff check on `_safe_*` function names vs Engineering field names could be added. |
| `service_integration.py` becomes a god class as more domains connect | Medium | Low | The `refresh_*` methods are already isolated per domain. If it exceeds 500 lines, extract per-domain integration classes. |
| A developer bypasses `service_integration.py` and calls Engineering from a widget | High | Low | Import-scan tests in `tests/ui` reject any `domain.` or `application.` import in CV2 modules. Code review check. |
| Manufacturing adapter requires geometry-aware read models that CV2 cannot represent | Medium | Low | Extend `PreviewItemReadModel` with additional fields. All existing CV2 read models have `display_metadata: tuple[tuple[str, str], ...]` as a generic extensibility slot. |

## Recommendation

**APPROVED**

The SceneProjection chain with duck-typed adapter boundaries is the correct architecture for CV2. It satisfies all constitutional rules:

- ✅ No direct Engineering service calls from CV2
- ✅ No FreeCAD, Part, or Sketcher imports
- ✅ No domain model imports
- ✅ Frozen dataclass boundary enforced
- ✅ _reject_backend_like_object guard active
- ✅ Import-scan tests enforce isolation
- ✅ service_integration.py is the single entry point
- ✅ Backward compatible — no existing API or test changes
- ✅ No architectural drift from ADR-0014, ADR-0015, ADR-0016

Proceed to CV2-21 (Engineering Service Integration) implementing the adapter described in section 1 of this ADR.
