# ADR-FOI-2 — Operational Language for Factory Intelligence

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Date** | 2026-07-05 |
| **Author** | FOI Architecture Gate |
| **Supersedes** | — |

---

## 1. Context

SmartFurnitureWB has completed three architectural phases:

1. **Configurator V2 Foundation** — workspace, navigation, selection, scene projection, visual components, interactive components, presentation layer, service integration
2. **Review Pipeline** — 5 domain adapters (Manufacturing, Validation, Cost, Commercial, Release) producing `ReviewPanelReadModel` data from backend facts
3. **Factory Readiness** — `build_factory_readiness_read_model()` consuming ReviewPanelReadModel objects to classify overall project readiness as READY, NOT_READY, NEEDS_REVIEW, BLOCKED, or UNKNOWN

The next phase — **Factory Operational Intelligence (FOI)** — must translate scattered domain facts into language that a factory operator, supervisor, or production manager can act on without reading code or parsing technical messages.

---

## 2. Problem

Current data sources produce **technical or scattered facts**:

| Domain | Typical Fact | Problem |
|--------|-------------|---------|
| Validation | `"Errors: Width Check — ERROR — Out of tolerance"` | What does this mean for production? |
| Manufacturing | `"Failed: CNC Cut — FAIL — Edge mismatch"` | Does it block the line or just need rework? |
| Cost | `"Totals: Total Cost — 500.00 USD"` | Is this within budget or over? |
| Commercial | `"Discounts: Quote — PENDING — Awaiting approval"` | Who needs to act? |
| Release | `"Approvals: QA Signoff — PENDING"` | Is this the only blocker? |

A factory operator does not ask "What is the validation error severity?". They ask:

- **What is stopping production?**
- **What is the impact?**
- **What is the priority?**
- **Who is responsible?**
- **Can we start or not?**

Without a unified operational language, every consumer of FOI must re-interpret raw facts, leading to inconsistent decisions and slower troubleshooting.

---

## 3. Decision

**Adopt Operational Language as an interpretive layer over existing facts.**

Every reason, blocker, diagnosis, or recommendation within FOI must carry structured operational fields, not just a raw domain fact.

### 3.1 Operational Blocking Item Structure

Future FOI read models that represent blockers, diagnoses, or recommendations must include (at minimum):

```python
@dataclass(frozen=True)
class OperationalBlockingItem:
    operational_category: str       # e.g. "ENGINEERING", "MANUFACTURING", "MATERIAL"
    source_panel: str               # e.g. "Validation", "Manufacturing"
    severity: str                   # "BLOCKED", "ERROR", "WARNING", "INFO"
    operational_impact: str         # Human-readable: "Blocks CNC cutting — 3 cabinets affected"
    human_message: str              # Human-readable: "Corner joint tolerance exceeded by 2mm"
    technical_detail: str           # Optional: "Rule: Width_Check, actual: 602mm, max: 600mm"
    component_id: str               # Optional reference
```

### 3.2 Translation Pattern

```
Raw Fact (ReviewPanelReadModel section/row)
    ↓
Diagnosis (what is the problem?)
    ↓
Operational Impact (what does it mean for the factory?)
    ↓
Categorization (which operational category?)
    ↓
OperationalBlockingItem (structured output)
```

### 3.3 The Readiness → Blocking pipeline

```
ReviewPanelReadModel[]
    ↓
FactoryReadinessReadModel(status=BLOCKED, reasons=[...])          ← FOI-1
    ↓
BlockingAnalysis(blockers=[OperationalBlockingItem, ...])         ← FOI-2 (future)
    ↓
ActionRecommendation(actions=[OperationalRecommendation, ...])    ← FOI-3 (future)
    ↓
FactoryDecision(proceed: bool, conditions: [...])                 ← FOI-4 (future)
```

Each layer reads only from the layer above it. FOI-2 reads FOI-1 output and ReviewPanelReadModel data. FOI-3 reads FOI-2 output. No layer reads directly from domain sources.

---

## 4. Allowed Operational Categories

Every `OperationalBlockingItem` must carry exactly one operational category. The initial set:

| Category | When to Use | Example human_message |
|----------|-------------|----------------------|
| `ENGINEERING` | Design geometry, tolerance, or constraint violations | "Cabinet width exceeds maximum machine capacity" |
| `MANUFACTURING` | CNC, assembly, edge-banding, drilling failures | "CNC tool path has uncuttable radius — manual rework required" |
| `MATERIAL` | Material availability, thickness, grade, or finish issues | "Specified veneer is out of stock — delivery delay expected" |
| `HARDWARE` | Missing or incompatible hardware items | "Hinge type not compatible with door thickness" |
| `MACHINE` | Machine-specific limitations or scheduling | "Panel length exceeds 2800mm — cannot run on CNC-1" |
| `COST` | Budget overrun or unpriced items | "Hardware cost exceeds estimate by 40% — reapproval needed" |
| `COMMERCIAL` | Pricing, discount, margin, or quotation issues | "Customer discount not yet approved — cannot finalize price" |
| `APPROVAL` | Pending signoffs or approvals | "Engineering approval pending — blocked by design review" |
| `RELEASE` | Release readiness checklist items | "QA signoff incomplete — cannot release to production" |
| `QUALITY` | Quality inspection or tolerance violations | "Edge band adhesion test failed — 2 cabinets affected" |
| `SAFETY` | Safety-related constraints | "Load capacity exceeded — requires structural review" |
| `LOGISTICS` | Shipping, packaging, or delivery constraints | "Packaging specification missing — cannot schedule shipment" |
| `UNKNOWN` | Cannot determine category from available facts | "Unidentified issue — requires manual inspection" |

New categories may be added by future ADRs. Categories are not exhaustive — they are a stable starting point.

---

## 5. Human Message Rules

Every `human_message` and `operational_impact` field must answer at least one of:

| Question | When Required | Example |
|----------|---------------|---------|
| What is the problem? | Always | "Corner joint gap exceeds tolerance" |
| Why does it block or delay production? | When severity is BLOCKED or ERROR | "Machine cannot cut radius smaller than 5mm" |
| What is the impact on the factory? | When severity is WARNING or above | "3 cabinets must be reworked — adds 45 minutes to line" |
| Who should review it? | When alerting a role | "Requires engineering design review" |
| Is it a production blocker or just a warning? | Always | Explicitly state "BLOCKER" or "WARNING" in context |

### 5.1 Examples of Good Messages

| Category | Good Message |
|----------|-------------|
| ENGINEERING | "Cabinet-003 width (612mm) exceeds CNC maximum (600mm). 1 cabinet blocked. Requires design review." |
| MANUFACTURING | "Edge band peeling on 2 doors. Rework time: ~20 minutes. Not a production blocker but requires QA check." |
| COST | "Hardware cost ($1,250) is 35% over estimate ($925). Requires cost manager approval to proceed." |
| RELEASE | "QA signoff pending for 3 cabinets. This is the only release blocker." |

### 5.2 Examples of Bad Messages

| Bad Message | Problem |
|-------------|---------|
| `"Error: Tolerance_exceeded(True)"` | Technical identifier without human context |
| `"KeyError: 'width' not found in panel_data"` | Stack trace or exception exposed to user |
| `"BLOCKED"` | No explanation of what, why, or impact |
| `"Cost too high"` | No threshold, no amount, no comparison |
| `"Validation rule #442 failed"` | Rule number without human-readable label |

---

## 6. Forbidden in FOI

The following are **strictly forbidden** in any FOI module, read model, or output:

| Forbidden | Why |
|-----------|-----|
| Exposing stack traces or exception messages as operational messages | Users are factory operators, not debuggers |
| Exposing Python attribute names, variable names, or internal identifiers without explanation | Confusing and non-actionable |
| Making decisions without clear facts | FOI diagnoses and recommends — it does not decide |
| Calculating cost, manufacturing, commercial, or optimization values | FOI projects existing facts; calculation belongs in domain layers |
| Modifying original ReviewPanelReadModel or domain data | FOI is read-only; it produces new read models, never mutates sources |
| Using AI or LLM as the decision maker | FOI outputs must be deterministic and auditable. AI may assist translation in future, never as the authority. |
| Creating a new Engine, Workflow, or Service without an ADR | Every architectural abstraction must be reviewed and documented |
| Using generic "service", "engine", "workflow", "controller", "store", "event_bus", "renderer", "registry" naming | FOI uses "ReadModel", "Builder", "Analysis", "Recommendation" |

---

## 7. Boundary

FOI modules **read** existing facts. FOI modules **never modify** existing facts.

| Component | Read? | Write? |
|-----------|-------|--------|
| ReviewPanelReadModel | Yes | No |
| FactoryReadinessReadModel | Yes | No |
| Engineering facts | No | No |
| Manufacturing facts | No | No |
| Cost facts | No | No |
| Commercial facts | No | No |
| Release facts | No | No |
| CV2 workspace | No | No |
| Domain modules | No | No |

FOI translates facts into:

- **Diagnosis** — what is the nature of the issue?
- **Operational impact** — what does it mean for factory operations?
- **Recommendations** — what actions could resolve it?
- **Future decisions** — what conditions would change the status?

FOI does **not** produce:

- New domain facts
- Modified ReviewPanelReadModel objects
- Side effects on any CV2 or domain module

---

## 8. FOI Layering

```
┌─────────────────────────────────────────────────────────────────┐
│                        Domain Facts                              │
│  Validation, Manufacturing, Cost, Commercial, Release            │
│  (ReviewPanelReadModel objects)                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-1: Factory Readiness                                      │
│  build_factory_readiness_read_model(review_panels)               │
│  → FactoryReadinessReadModel(status, reasons, counts, ...)      │
│  Status: READY / NOT_READY / NEEDS_REVIEW / BLOCKED / UNKNOWN   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-2: Blocking Analysis (future)                              │
│  build_blocking_analysis(readiness, review_panels)               │
│  → BlockingAnalysis(blockers: list[OperationalBlockingItem])     │
│  Each blocker has operational_category, impact, human_message   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-3: Action Recommendation (future)                          │
│  build_action_recommendation(analysis)                           │
│  → ActionRecommendation(actions: list[OperationalRecommendation])│
│  Each action has owner, priority, suggested resolution           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-4: Factory Decision (future)                               │
│  build_factory_decision(readiness, analysis, recommendations)    │
│  → FactoryDecision(proceed: bool, conditions: [...])            │
│  Decision: PROCEED / PROCEED_WITH_CONDITIONS / HALT / DEFER     │
└─────────────────────────────────────────────────────────────────┘
```

Each layer reads only from the layer above. No layer reads directly from `ReviewPanelReadModel` except FOI-1.

---

## 9. Business Value

| Benefit | Stakeholder | Impact |
|---------|-------------|--------|
| Reduced root-cause search time | Factory operator | "Tolerance exceeded" → immediate understanding vs. "ERROR — Item 442" |
| Better design-to-factory communication | Designer, production manager | Common language ("CNC capacity blocked") replaces domain jargon |
| Fewer production errors | Production | Clear "BLOCKER" vs "WARNING" distinction prevents mis-prioritization |
| Faster supervisor decisions | Shift supervisor | "3 cabinets affected, 45 min rework" enables go/no-go judgment |
| Software understandable to non-programmers | All factory roles | Messages answer "what/why/impact/who" instead of exposing code internals |
| Auditable deterministic output | QA, management | No AI-as-decision-maker; rules are explicit and testable |
| Layered architecture | Engineering | Each FOI layer builds on the previous one; no layer bypasses or duplicates |

---

## 10. Test Requirements

Any future FOI read model (BlockingAnalysis, ActionRecommendation, FactoryDecision, etc.) must have contract tests proving:

1. **Messages are human-readable** — no technical identifiers, no exception text, no attribute names exposed as primary messages
2. **Source domain is preserved** — every output carries its originating ReviewPanelReadModel `panel_name`
3. **Technical details remain optional** — `technical_detail` field may be empty; `human_message` must never be empty for actionable items
4. **No backend object leakage** — no `Shape`, `all_nodes`, `FreeCAD` attributes on any output object
5. **Deterministic output** — same input produces identical output
6. **No input mutation** — input ReviewPanelReadModel and FactoryReadinessReadModel remain unchanged
7. **No forbidden imports** — source-inspection test asserting absence of `domain.*`, `manufacturing.*`, `cost_intelligence.*`, `commercial_outputs.*`, `optimization.*`, `FreeCAD`, `QtWidgets`, `QtCore`, `QtGui`
8. **No Engine/Workflow/Service naming** — function names, class names, and module names avoid forbidden architectural terms
9. **Empty/null input safety** — None, empty list, or empty readiness returns safe defaults (zero blockers, empty recommendations)
10. **All existing UI and architecture tests pass** — FOI must never break CV2 or existing FOI contracts

---

## 11. Future Extension Path

| Sprint | Deliverable | Reads From |
|--------|-------------|------------|
| FOI-1 | Factory Readiness Read Model | ReviewPanelReadModel |
| **FOI-2** | **Factory Blocking Analysis (next)** | FactoryReadinessReadModel + ReviewPanelReadModel |
| FOI-3 | Action Recommendation | BlockingAnalysis |
| FOI-4 | Factory Decision | Readiness + Analysis + Recommendations |

FOI-2 (Factory Blocking Analysis) will use the Operational Language defined in this ADR to translate `FactoryReadinessReason` entries into `OperationalBlockingItem` objects with categories, impacts, and human-readable messages.

FOI-3 (Action Recommendation) will build on FOI-2, not on raw errors. Each recommendation will reference the blocking item it addresses and will include owner, priority, and suggested resolution.

This layering ensures that each FOI component has a single responsibility and a single data source.

---

## 12. Recommendation

**APPROVED.**

Operational Language is adopted as the standard for all future Factory Operational Intelligence read models. Every blocking item, diagnosis, recommendation, and decision must carry the structured fields defined in this ADR.

### Key Commitments

1. Every `OperationalBlockingItem` (or equivalent) must carry `operational_category`, `severity`, `operational_impact`, `human_message`, and `source_panel`.
2. `human_message` must answer at least one of: what is the problem, why does it block, what is the impact, who should review, is it a blocker or warning.
3. Technical details (`technical_detail`) are optional; human messages are never optional for actionable items.
4. No FOI module may import from domain, manufacturing, cost_intelligence, commercial_outputs, optimization, FreeCAD, or Qt.
5. No FOI module may calculate, infer, or derive business decisions — it projects, diagnoses, and recommends.
6. No FOI module may modify its input.
7. No FOI module may use "Engine", "Workflow", "Service", "Controller", "Store", "EventBus", "Renderer", or "Registry" in its naming.
8. No AI or LLM may serve as the decision authority for FOI outputs.
9. Every new FOI read model must pass the 10-point test contract.
10. All existing CV2 and FOI tests must pass before any FOI delivery.

---

## Appendix A: Change History

| Date | Change | Author |
|------|--------|--------|
| 2026-07-05 | Initial ADR — Operational Language standard for Factory Intelligence | FOI Architecture Gate |
