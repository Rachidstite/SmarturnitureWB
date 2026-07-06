# ADR-PD-1 — Production Decision Domain Definition

**Status:** Accepted

---

## Context

Multiple components across the codebase currently use decision-like names
but operate at different architectural layers and answer different questions:

| Component | Location | Scope | Current state |
|---|---|---|---|
| `ProductionDecisionReadModel` | `factory_operational_intelligence/` | Project-level go/no-go | Live in CV2 workspace |
| `OperationalDecision` | `domain/` | Single engineering choice | Live in engineering pipeline |
| `ManufacturingDecision` | `manufacturing/` | Single operation/component readiness | Live in app service |
| `FactoryDecisionReport` | `cost_intelligence/` | Project-level economic feasibility | No external consumers found |
| `FactoryGovernanceDecisionReport` | `cost_intelligence/` | Executive governance approval | No external consumers found |
| `FactoryDecisionProjection` | `manufacturing/` | UI wrapper for manufacturing decisions | Referenced in import guards |

The architecture analysis (Architecture Gate — Production Decision Domain
Definition) found that these concepts operate at different layers but that
`ProductionDecisionReadModel`, `FactoryDecisionReport`, and
`FactoryGovernanceDecisionReport` all answer the same high-level question —
*"can this project go to production?"* — though from different data sources
(review panels vs cost signals vs KPI management statuses).

A formal domain definition is needed before any ownership reassignment or
cleanup decisions can be made.  This ADR defines what "Production Decision"
means inside SmartFurnitureWB and establishes the boundary rules that all
decision-like components must obey.

---

## Domain Definition

**Production Decision** means:

> A project-level operational read model that communicates whether a
> project is ready to proceed toward production review/execution, based
> on already-computed engineering, manufacturing, validation, cost, and
> operational signals.

It is **NOT**:
- Raw manufacturing feasibility
- CNC operation generation
- Cost calculation
- Commercial quotation
- UI-only rendering metadata
- Scheduling
- AI/agent recommendation
- A state machine or workflow engine

A Production Decision:
- Is a **read model** — it reads pre-computed fields and never mutates
  source data
- Is **deterministic** — same inputs always produce the same output
- Is **traceable** — every output field references its source field
- Is **project-level** — never about a single panel, hole, or component
- Is **composite** — it aggregates signals from multiple domains but
  does not re-compute any of them

---

## Ownership

| Responsibility | Owner | Location |
|---|---|---|
| **Production Decision (project-level)** | FOI | `factory_operational_intelligence/` |
| Engineering decisions | Engineering | `domain/`, `project_engineering/` |
| Manufacturing decisions | Manufacturing | `manufacturing/` |
| Cost aggregation / economic feasibility | Cost Intelligence | `cost_intelligence/` |
| Commercial approval | Commercial | `commercial_outputs/` |
| UI/dashboard presentation | Presentation | `ui/`, `factory_dashboard/` |

The canonical Production Decision owner is `factory_operational_intelligence/`
because:
- `ProductionDecisionReadModel` is the only decision component that is
  live in production (consumed by Configurator V2 workspace and Factory
  Dashboard)
- The FOI pipeline is already wired into
  `ConfiguratorV2ServiceIntegration.refresh_factory_operations()`
- FOI consumes review panel data — the most natural evidence source for
  a production readiness determination

---

## Allowed Inputs

Production Decision may consume already-computed summaries and signals:

- Validation reports (violation counts, severity levels)
- Manufacturing readiness read models (operation statuses, blocking items)
- Blocking analysis (critical/error/warning counts with traceability)
- Action recommendations (with confidence scores)
- Cost readiness / status summaries (risk level, completeness flags)
- Operational constraints (capacity, schedule, load indicators)
- Manufacturing review summaries (high-priority counts, attention signals)

Every input must be a **pre-computed summary** — never a raw domain object,
never a FreeCAD geometry, never a viewport command dict.

---

## Forbidden

Production Decision must **not**:

- Compute geometry, panel shapes, or tool paths
- Compute manufacturing operations (CNC, edge banding, drilling)
- Compute CNC paths or nesting layouts
- Compute cost estimates or pricing
- Compute commercial quotations
- Mutate domain, manufacturing, or cost models
- Depend on `SceneRenderer` or viewport command fields directly
- Depend on Configurator UI types (`ui.configurator_v2.*`)
- Become an engine, workflow, service, controller, or scheduler
- Emit events, trigger side effects, or change application state

---

## Relationship to Existing Reports

1. **`ProductionDecisionReadModel`** (`factory_operational_intelligence/`)
   is the **candidate canonical** production decision read model.

2. **`FactoryDecisionReport`** and **`FactoryGovernanceDecisionReport`**
   (`cost_intelligence/`) remain **INVESTIGATE** — not DEPRECATE — until
   internal consumer verification is completed.  Lack of external
   consumers is not sufficient grounds for deprecation:
   - These reports may serve internal aggregation within the
     `cost_intelligence` commercial pipeline
   - Governance-like reports may remain valid internal aggregation models
     even if they never reach a UI consumer
   - CI-Audit Phase 3 is required to trace all internal consumers

3. **`OperationalDecision`** (`domain/`) and **`ManufacturingDecision`**
   (`manufacturing/`) operate at a different scope (single component /
   single operation) and are not affected by this ADR.

---

## Consequences

### Positive

- Removes ambiguity around "decision" vocabulary across the codebase.
- Prevents FOI / Governance duplication from being resolved prematurely.
- Protects Cost Intelligence from presentation-layer coupling —
  cost-economic feasibility is a valid internal concern even without a UI.
- Supports future Commercial Product Readiness by reserving the
  Production Decision concept for operational evidence only.

### Negative

- Requires future verification (CI-Audit Phase 3) before any cleanup
  decisions can be made.
- Similarly named reports will temporarily remain in `cost_intelligence/`
  until the Phase 3 verification is complete.
- The definition alone does not resolve the FOI / Governance overlap —
  it only establishes the boundary within which that overlap must be
  evaluated.

---

## Validation

The Production Decision boundary is validated by the current passing
test groups:

| Test area | Passing count |
|---|---|
| `tests/factory_dashboard` | 100 |
| `tests/ui` | 499 + 5 |
| `tests/scene_graph`, | |
| `tests/factory_operational_intelligence`, | 349 |
| `tests/architecture` | |

No code was modified as part of this ADR.

---

## Recommendation

The next step should be:

**CI-Audit Phase 3 — Internal Consumer Verification for
`FactoryDecisionReport` and `FactoryGovernanceDecisionReport`**

Trace every code path that reaches these reports inside
`cost_intelligence/`.  Determine whether they are:
- Genuinely required internal aggregation models (KEEP)
- Duplicates of FOI decision logic (DEPRECATE)
- Some combination with specific non-overlapping fields

Only after Phase 3 should any cleanup or merger decisions be made.
