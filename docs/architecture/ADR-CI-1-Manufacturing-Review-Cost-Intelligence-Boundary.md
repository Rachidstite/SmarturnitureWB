# ADR-CI-1 — Manufacturing Review and Cost Intelligence Boundary

**Status:** Accepted

---

## Context

- **ManufacturingReviewSummary** (`factory_dashboard/review_summary.py`)
  summarises rendering metadata from SceneRenderer-produced viewport
  command dicts.  It counts review items by priority (`review_priority`)
  and category (`review_category`) — fields that SceneRenderer already
  derived from overlay data via `_decorate_manufacturing_review_command`
  and `_decorate_hole_command`.

- **Cost Intelligence** (`cost_intelligence/`) computes actual
  manufacturing costs from `ManufacturingCostContext` and production
  metrics (`ManufacturingMetricsReport`).  The pipeline runs through
  `ManufacturingCostPipelineBuilder` which orchestrates:
  `ManufacturingMetricsBuilder → ManufacturingCostContextBuilder →
  ManufacturingCostInsightsBuilder → ManufacturingCostRiskReportBuilder
  → ManufacturingCostCalculator → ManufacturingCostSummaryBuilder`.

- The **CI-1 architecture audit** examined all 27 production modules
  across `cost_intelligence/`, `costing/`, `domain/`, and the Configurator
  V2 cost review projection adapter.  It found:

  - No existing dependency from Cost Intelligence to SceneRenderer.
  - No existing dependency from Factory Dashboard to Cost Intelligence.
  - Separate data sources: the review summary reads renderer command
    fields; the cost pipeline reads production-package metrics.
  - The only natural integration point is an orchestrator-level adapter
    (such as `ConfiguratorV2ServiceIntegration`) that already holds
    both pipelines and can merge them without cross-layer imports.

---

## Decision

1. **Cost Intelligence must not consume SceneRenderer or viewport
   commands directly.**  The cost pipeline receives its context from
   `ManufacturingProductionPackage` / `FactoryReleasePackage` — not
   from rendering metadata.

2. **Manufacturing Review must not compute costs.**  The review summary
   counts items by priority and category; it never estimates material,
   labour, machining, or hardware cost.

3. **Any future bridge between the two domains must consume:**
   - `ManufacturingReviewSummary` (or its constituent counts)
   - Pre-computed cost context / report data (duck-typed, not
     necessarily the concrete `ManufacturingCostContext` type)

4. **Any bridge must be an adapter / read-model / projection only.**
   No arithmetic beyond counting.  No derivation of new cost values.
   No engineering of feasibility, readiness, or production decisions.

5. **No new engine or workflow** is allowed for the bridge.

6. **No direct `import factory_dashboard` inside `cost_intelligence`**
   unless a future ADR justifies the coupling.  The preferred pattern
   is for an orchestrator (e.g. `ConfiguratorV2ServiceIntegration`)
   that already has access to both summaries and cost data to call
   the bridge.

---

## Forbidden

- Cost calculation in `factory_dashboard/`.
- Rendering-metadata derivation in `cost_intelligence/`.
- Direct `scene_graph.renderer` import in `cost_intelligence/`.
- Production decision or readiness logic in any cost-impact bridge.
  Possible values for impact flags are limited to: `"none"`,
  `"low"`, `"medium"`, `"high"`.

---

## Consequences

### Positive

- Single source of truth for each domain is preserved: SceneRenderer
  owns `review_category`/`review_priority`; Cost Intelligence owns
  cost estimates.
- Prevents cross-layer coupling that would make both domains harder
  to test and evolve independently.
- Allows future cost-impact UI to be built safely by adding a thin
  adapter in the orchestrator layer without touching either pipeline.

### Negative

- Any future bridge requires an explicit adapter / projection module.
  A one-liner `getattr` is not enough — the adapter must be tested
  and maintained.
- Some duplication of display rows may arise (e.g. both the review
  panel and the cost panel show a drilling count, but from different
  sources with different semantics).  This is intentional — the
  review count reflects rendered overlay commands; the cost count
  reflects production-package drill operations.  Both are meaningful.

---

## Validation

The boundary is validated by the current passing test groups:

| Test area                                      | Passing count |
|------------------------------------------------|---------------|
| `tests/factory_dashboard`                      | 100           |
| `tests/ui`                                     | 499 + 5       |
| `tests/scene_graph`,                           |               |
| `tests/factory_operational_intelligence`,      | 349           |
| `tests/architecture`                           |               |

All CI-1-adjacent tests continue to pass.  No code was modified as
part of this ADR.

---

## Recommendation

**Do not implement a cost-impact bridge** until a concrete Business
Story proves value.  The current separation:

```
SceneRenderer → viewport commands → ManufacturingReviewSummary
                                            ↓
Cost Intelligence → ManufacturingCostContext → ManufacturingCostReport
```

is correct.  A bridge would only be justified when a production user
can articulate a specific triage question that requires both review
priority AND cost impact in a single view.  At that point, the bridge
should be a thin adapter in the orchestrator layer, not a new engine
or a cross-layer import.
