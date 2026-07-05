# ADR-CV2-26 — Projection Adapter Pattern for Configurator V2

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Date** | 2026-07-05 |
| **Author** | Architecture Gate Review |
| **Approvers** | AG-CV2-Adapters |
| **Supersedes** | — |

---

## 1. Context

Configurator V2 (CV2) consumes backend facts from multiple domains — Engineering, Manufacturing, Validation, and soon Cost, Commercial, Optimization, and Release. Each domain produces structured data that the UI must display without importing domain internals.

The pattern was proven across three implementations:

| Domain | Adapter | Wiring | Read Model |
|--------|---------|--------|------------|
| Engineering | `project_engineering_source()` | `EngineeringProjectionResult` → workspace via `set_preview_*` / `set_inspector_*` | `SceneProjection`, `PreviewReadModel`, `InspectorReadModel` |
| Manufacturing | `build_manufacturing_review_projection()` | `refresh_manufacturing_review()` → panel merge → `set_review_panel_read_models` | `ReviewPanelReadModel(panel_name="Manufacturing")` |
| Validation | `build_validation_review_projection()` | `refresh_validation()` → panel merge → `set_review_panel_read_models` | `ReviewPanelReadModel(panel_name="Validation")` |

Each adapter follows the same structural template. The Architecture Gate (AG-CV2-Adapters) confirmed the pattern is stable, maintainable, and suitable for the remaining domains.

---

## 2. Problem

Without a documented pattern, future adapter authors may:

- Import domain modules directly into UI code (`from manufacturing import ...` inside `service_integration.py`)
- Create new read model subclasses when `ReviewPanelReadModel` is sufficient
- Introduce engines, services, or workflows on the UI side
- Calculate business decisions in the adapter layer
- Create inconsistent section naming, field extraction, or fallback behaviour
- Duplicate the merge logic differently each time
- Skip import-boundary tests and drift undetected

A documented, approved pattern prevents architectural decay without requiring a framework or library.

---

## 3. Decision

**Approve the Projection Adapter Pattern.**

### 3.1 General Form

```
Backend Source (duck-typed)
        ↓
Projection Adapter (pure function in projection_adapters.py)
        ↓
CV2-native Read Model (frozen dataclass from read_models.py)
        ↓
Existing UI Path (workspace / service_integration)
```

### 3.2 Review-Panel Form (Cost, Commercial, Validation, Manufacturing, Release)

```
Backend Source (duck-typed)
        ↓
build_<domain>_review_projection(source)     ← projection_adapters.py
        ↓
ReviewPanelReadModel(panel_name="<Domain>")  ← read_models.py
        ↓
refresh_<domain>(source)                      ← service_integration.py
        ↓
merge into 5-panel tuple                      ← private to method
        ↓
workspace.set_review_panel_read_models()      ← workspace.py
```

### 3.3 Engineering Adapter (Separate Pattern)

Engineering follows a different pipeline because it produces visual/interactive/presentation data, not review panel data:

```
SceneGraph source
        ↓
build_scene_projection() → build_visual_components()
        → [optional] build_interactive_visual_components() → synchronize_presentation()
        ↓
EngineeringProjectionResult (frozen, CV2-native)
        ↓
workspace.set_preview_* / set_inspector_*
```

This pattern is **not consolidated** with the review-panel pattern. The two should remain separate because their outputs target different UI regions (preview/inspector vs. review panel).

---

## 4. Allowed Adapter Responsibilities

Adapters **may**:

- Accept duck-typed sources (objects, dicts, lists, tuples, generators)
- Extract UI-safe facts (`str`, `bool`, `tuple[str, str]`, `tuple[str, ...]`)
- Map already-existing backend facts into CV2 read models — **no derivation, no inference**
- Group rows into meaningful sections for UI display
- Provide safe fallbacks for `None`, empty, or missing data
- Remain **deterministic** — same input always produces same output
- Remain **side-effect free** — never mutate input or external state
- Reject backend geometry objects (`FreeCAD`, `Part`, `Sketcher`) via `_reject_backend_like_object()`
- Use private helper functions prefixed with the domain abbreviation (e.g. `_mfg_*`, `_val_*`)

---

## 5. Forbidden Adapter Responsibilities

Adapters **must not**:

- Calculate domain decisions (e.g. "is this cabinet valid?" — project the validation result, don't re-validate)
- Calculate manufacturing decisions (e.g. "can this be CNC'd?" — project the CNC result, don't re-derive)
- Calculate cost (e.g. "material × quantity = total" — project the cost data, don't compute)
- Calculate optimization
- Create engines, workflows, services, controllers, stores, event buses, renderers, or registries
- Create new UI read model types when `ReviewPanelReadModel` is sufficient
- Import domain modules (`domain.*`, `manufacturing.*`, `cost_intelligence.*`, `commercial_outputs.*`, `optimization.*`)
- Import Qt or FreeCAD modules
- Expose backend objects (objects with `.Shape`, `.ViewObject`, `.Document`, or module origins in `FreeCAD`, `Part`, `Sketcher`)
- Store raw domain objects in the workspace, inspector, preview, or read models

---

## 6. Wiring Pattern

Every wired review domain must follow this exact structure in `service_integration.py`:

```python
def refresh_<domain>(self, source: Any = None):
    if source is None:
        return self._refresh_review_panels(
            source=source,
            message_text="<Domain> integration not available yet",
            source_reference="ConfiguratorV2ServiceIntegration.refresh_<domain>",
        )
    panel = build_<domain>_review_projection(source)
    existing = tuple(self.workspace.review_panel_read_models or ())
    names = self.workspace.review_panel_names
    merged = tuple(
        panel if name == "<Domain>"
        else existing[i] if i < len(existing)
        else ReviewPanelReadModel(panel_name=name)
        for i, name in enumerate(names)
    )
    self.workspace.set_review_panel_read_models(merged)
    return merged
```

Where `<domain>` is replaced with the panel name matching the constant in `_REQUIRED_PANEL_NAMES`:

```python
_REQUIRED_PANEL_NAMES = (
    "Validation",
    "Manufacturing",
    "Cost",
    "Commercial",
    "Release",
)
```

### 6.1 Rules

| Rule | Rationale |
|------|-----------|
| Guard `source is None` → existing `_refresh_review_panels` fallback | Preserves backward compatibility; emits an info message for the message center |
| Call adapter → merge → set → return | Single path; the workspace always holds a 5-panel tuple |
| Merge replaces only the matching panel name | Other panels (e.g. Validation while wiring Manufacturing) retain their existing state |
| Do not change other `refresh_*` methods | Each method is independently understandable and testable |

---

## 7. Test Contract Requirements

Every domain adapter + wiring pair must have contract tests proving:

### Adapter Tests (`test_<domain>_projection_adapter_contract.py`)

1. Converts domain-like source into `ReviewPanelReadModel`
2. Supports duck-typed objects (attribute-based and dict-like)
3. Supports list/tuple bare input
4. Output contains only CV2 read models (no `Shape`, no `all_nodes`, no domain type attributes)
5. No raw domain object field names leak into output row values
6. Severity/status/message fields are preserved as UI-safe strings
7. Missing optional fields fall back safely (no crashes, sensible defaults)
8. `None` source returns `available=False` panel with no sections
9. Empty source returns a safe placeholder panel (`available=False`)
10. Deterministic — same input, same output
11. No input mutation
12. No domain/manufacturing/cost/`FreeCAD`/`Qt` imports in `projection_adapters.py`
13. No engine/workflow/service/controller naming in the adapter function
14. Items are correctly grouped into sections by status/severity

### Wiring Tests (`test_<domain>_review_wiring_contract.py`)

1. `refresh_<domain>` routes source through the adapter function
2. Output tuple contains `ReviewPanelReadModel` instances
3. Output rows are `(str, str)` tuples — no raw objects leak into workspace
4. No raw domain objects stored in workspace
5. `_refresh_review_panels` still works directly (existing path preserved)
6. Other `refresh_*` methods still delegate to `_refresh_review_panels` (untouched)
7. `None` source falls back to empty panels
8. Empty source falls back to `available=False` panel
9. Deterministic
10. No input mutation
11. No domain/manufacturing/cost/`FreeCAD`/`Qt` imports in `service_integration.py`
12. No engine/workflow naming in the method name
13. Existing UI tests pass (run `tests/ui -q`)
14. Architecture tests pass (run `tests/architecture -q`)

### Test Import Pattern

Tests must use `patch.dict(sys.modules, {"core.qt_compat": fake_qt_module})` + `importlib.import_module` to avoid PySide6 SIGILL when importing `workspace.py` and `service_integration.py`. Adapter-only tests may use the direct `SourceFileLoader` pattern since they don't depend on `workspace.py`.

---

## 8. Refactor Policy

**Do not extract generic helpers or split files until evidence proves maintenance risk.**

### Current Duplication (Acceptable)

| Duplicate | Location | Lines | Trigger for Extraction |
|-----------|----------|-------|-----------------------|
| Item extraction from source: `isinstance(list/tuple)` / `hasattr(__iter__)` ... | Each adapter in `projection_adapters.py` | 8 lines | 4th adapter |
| Row value concatenation: `status | message | [cid]` | Each adapter | ~6 lines | 4th adapter |
| Panel merge in wiring: `panel if name == "X" else ...` | Each wiring method in `service_integration.py` | 8 lines | 3rd wiring |
| Test file boilerplate (fake classes, import pattern) | Each test pair | ~40 lines | 4th test pair |

### Refactor Triggers

Refactoring is warranted when:

- **4+ adapters share identical helper logic**: extract `_extract_items(source, key="<items>")` into a shared helper in `projection_adapters.py`
- **3+ wiring methods share identical merge logic**: extract `_merge_review_panel(self, panel: ReviewPanelReadModel)` into `ConfiguratorV2ServiceIntegration`
- **projection_adapters.py exceeds 1800 lines**: split into `projection_adapters/` package with one file per domain adapter, plus a `_shared.py` for common utilities
- **service_integration.py exceeds 800 lines**: split into domain-specific mixin classes or wire modules
- **Tests reveal brittle duplication**: extract a shared test base class or pytest fixtures

### Anti-Patterns to Avoid

- Creating a generic `AdapterBase` class — adapters are pure functions, inheritance adds coupling without value
- Creating a `ReviewPanelService` — the wiring is 14 lines; a service class adds ceremony without abstraction
- Merging Engineering pipeline with review-panel pattern — different outputs, different UI targets
- Premature package splitting — a single 1500-line file is navigable; three 500-line files in a package require cross-file context switching

---

## 9. Future Extension Path

Recommended sprint order:

| Sprint | Deliverable | Depends On |
|--------|-------------|------------|
| CV2-26 | Cost Projection Adapter | This ADR |
| CV2-27 | Cost Review Wiring | CV2-26 |
| CV2-28 | Commercial Projection Adapter | CV2-26 (pattern) |
| CV2-29 | Commercial Review Wiring | CV2-28 |
| CV2-30 | Optimization Projection Adapter | CV2-29 |
| CV2-31 | Optimization Review Wiring | CV2-30 |
| CV2-32 | Release Projection Adapter | CV2-31 |
| CV2-33 | Release Review Wiring | CV2-32 |
| CV2-34 | Post-Completion Refactor (if triggered) | All above |

Each adapter + wiring pair is two sprints: adapter-only, then wiring-only. This cadence keeps each increment reviewable and testable independently.

---

## 10. Business Value

| Benefit | Stakeholder | Impact |
|---------|-------------|--------|
| Faster design review | Designers, engineers | Validation and Manufacturing facts displayed instantly in the review panel |
| Fewer manufacturing mistakes | Production | CNC and assembly operations visible before release |
| Clearer validation feedback | Engineers | Rule violations grouped by severity; no raw data noise |
| Cost visibility (future) | Sales, management | Material/labor/hardware costs aggregated in the review panel |
| Commercial readiness (future) | Sales | Pricing, discounts, terms surfaced during configuration |
| Optimization transparency (future) | Engineers | Material yield, panel utilization visible |
| SaaS readiness | Architecture | UI never imports backend modules — clean separation for API-backed deployment |
| Team scaling | Architecture | Clear cookbook; any engineer can add a new domain adapter without architectural guidance |
| Testability | QA | Deterministic, side-effect-free adapters are trivially unit-testable |

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Duck-typing becomes too broad | Low | Medium | `_reject_backend_like_object` guards; contract tests verify type safety |
| `projection_adapters.py` grows too large | Medium | Medium | Split trigger at 1800 lines; monitor per-sprint |
| `service_integration.py` accumulates wiring | Medium | Low | Each wiring method is 14 lines; hard to accumulate significant bloat |
| Adapters accidentally gain business logic | Low | High | Code review guard: "is this extracting a fact or computing it?"; contract test `test_no_forbidden_imports` enforces boundary |
| New developer creates service/engine instead of adapter | Medium | Low | This ADR serves as the reference; review checklist includes naming scan |
| Merge conflicts on `projection_adapters.py` | Low | Medium | Single-file edit conflicts are rare; reviewers will catch them |
| Duplication rot — 4th copy written without extraction | Medium | Low | Refactor trigger at 4th adapter is explicit; enforcement via code review |

---

## 12. Recommendation

**APPROVED.**

The Projection Adapter Pattern is documented, stable across two domains, and approved by the Architecture Gate (AG-CV2-Adapters). Future domain authors must follow this ADR. Deviations require a new ADR or an amendment to this one.

### Key Commitments

1. **Adapters are pure functions** — deterministic, side-effect free
2. **Adapters project facts only** — no calculation, no inference, no derivation
3. **Adapters produce CV2-native read models only** — no domain types in the output
4. **Wiring is 14 lines** — adapter → merge → set → return
5. **Refactoring is deferred** — extract helpers when 3–4 copies exist, not before
6. **Contract tests are mandatory** — adapter + wiring tests per domain
7. **Engineering adapter stays separate** — different pipeline, different output, different UI target

---

## Appendix A: File Map

```
ui/configurator_v2/
├── projection_adapters.py        ← All projection adapter functions
│   ├── _as_dict(), _get_value()  ← Shared utilities
│   ├── _reject_backend_like_object()
│   ├── build_project_tree_read_model()
│   ├── build_inspector_read_model()
│   ├── build_preview_read_model()
│   ├── build_message_center_read_model()
│   ├── build_review_panel_read_models()
│   ├── build_manufacturing_review_projection()    ← + _mfg_* helpers
│   ├── build_validation_review_projection()       ← + _val_* helpers
│   └── __all__                       ← Export all public functions
├── service_integration.py        ← Wiring layer
│   ├── ConfiguratorV2ServiceIntegration
│   │   ├── refresh_project_tree()
│   │   ├── refresh_inspector()
│   │   ├── refresh_preview()
│   │   ├── refresh_validation()               ← wired
│   │   ├── refresh_manufacturing_review()     ← wired
│   │   ├── refresh_cost_review()              ← stub
│   │   ├── refresh_commercial_review()        ← stub
│   │   └── refresh_release_review()           ← stub
│   ├── project_engineering_source()           ← Engineering pipeline
│   └── EngineeringProjectionResult            ← Engineering output model
├── read_models.py                ← All CV2-native read models
│   ├── ReviewPanelReadModel
│   ├── ReviewSectionReadModel
│   └── ... (7 other read models)
└── workspace.py                  ← State container + UI bindings
    ├── ConfiguratorV2Workspace
    └── set_review_panel_read_models()
```

## Appendix B: Template for a New Domain Adapter

When adding a new review domain (e.g. Cost):

**Step 1 — `projection_adapters.py`:**

```python
def _cost_item_label(...): ...
def _cost_item_value(...): ...

def build_cost_review_projection(
    source: Any = None,
) -> ReviewPanelReadModel:
    _reject_backend_like_object(source, "cost source")
    if source is None:
        return ReviewPanelReadModel(panel_name="Cost", available=False)
    # ... extract items, build sections, return panel ...
```

Add to `__all__`.

**Step 2 — `ui/configurator_v2/__init__.py`:**

Add `build_cost_review_projection` to imports and `__all__`.

**Step 3 — `service_integration.py`:**

Wire `refresh_cost_review` following Section 6 pattern.

**Step 4 — Tests:**

Create `test_cost_projection_adapter_contract.py` and `test_cost_review_wiring_contract.py` following Section 7 contract.

**Step 5 — Verify:**

`python3 -m pytest tests/ui -q && python3 -m pytest tests/architecture -q`

---

## Appendix C: Change History

| Date | Change | Author |
|------|--------|--------|
| 2026-07-05 | Initial ADR — pattern documented after AG-CV2-Adapters | Architecture Gate |
