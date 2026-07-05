# ADR-FOI-4 — Production Decision Boundary

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Date** | 2026-07-05 |
| **Author** | FOI Architecture Gate |
| **Supersedes** | — |

---

## 1. Context

The Factory Operational Intelligence pipeline has completed four architectural layers:

```
Review Facts (ReviewPanelReadModel[])
         │
         ▼
FOI-1: Factory Readiness Read Model
    status: READY / NOT_READY / NEEDS_REVIEW / BLOCKED / UNKNOWN
         │
         ▼
FOI-2: Factory Blocking Analysis Read Model
    blocking_items[] with blocking_item_id, category, severity, impact
         │
         ▼
FOI-3: Factory Action Recommendation Read Model
    recommendations[] with blocking_reference, knowledge_source, confidence
         │
         ▼
FOI-4: Production Decision  ← next layer
```

The pipeline transforms raw domain facts (via CV2 Review Panels) into increasingly operational forms: facts → diagnosis → recommendations. The next layer, Production Decision, is the most architecturally sensitive because it determines what a factory supervisor sees as the final go/no-go signal. Without an explicit boundary, FOI-4 risks being mistaken for an automatic production executor.

---

## 2. Problem

Production Decision is dangerous because:

| Risk | Scenario | Consequence |
|------|----------|-------------|
| Recommendation mistaken for approval | A supervisor sees "START_READY" and bypasses manual checks | Quality or safety issues reach production |
| Software appears to execute production | A "PROCEED" status is misinterpreted as an automatic factory command | No human reviews purchased material or scheduled machines |
| Decision ownership unclear | No recorded reason for the decision | Audit cannot determine why production was allowed or blocked |
| FOI becomes a Decision Engine | Decision logic accumulates business rules, becoming opaque and unmaintainable | Violates the core FOI principle: FOI reads, reasons, and recommends — it does not decide |
| BLOCKED status treated as permanent | A BLOCKED decision from an earlier analysis is not updated when conditions change | Production pauses unnecessarily |

Without a documented boundary, FOI-4 could evolve into:

- A production scheduler
- An automatic CNC trigger
- A quotation approver
- A business rule engine
- An AI-based go/no-go oracle

All of these violate the SmartFurnitureWB architecture.

---

## 3. Decision

**Adopt Production Decision as a Read Model / Decision Record, not an Engine.**

FOI-4 produces a `ProductionDecisionReadModel` that summarizes whether production should proceed. It does not execute, schedule, or approve anything. The decision is advisory — a human supervisor reviews it and makes the final call.

### Core Principle

```
Recommendation (FOI-3)  →  Human Review  →  Decision (FOI-4)  →  Production
```

The human review is **outside** FOI-4. FOI-4 produces a decision record summarizing what is known. A human (or future external system) uses that record to make the actual production call.

---

## 4. Allowed Inputs

`build_production_decision_read_model` may consume:

| Input | Source | Purpose |
|-------|--------|---------|
| `FactoryReadinessReadModel` | FOI-1 | Overall readiness status (BLOCKED, READY, etc.) |
| `FactoryBlockingAnalysisReadModel` | FOI-2 | Specific blocking items with IDs and severities |
| `FactoryRecommendationReadModel` | FOI-3 | Actionable recommendations with confidence levels |

These are the **only** allowed inputs. FOI-4 must not consume:

- Domain modules (`domain.*`, `manufacturing.*`, `cost_intelligence.*`, `commercial_outputs.*`, `optimization.*`)
- CV2 modules (`ui/configurator_v2.*`)
- FreeCAD or Qt modules
- Raw backend objects
- Scene graphs, visual components, or geometry data

FOI-4 reads the summary, not the raw data. If information is missing from FOI-1/2/3, it is missing from the decision — FOI-4 never fetches data directly.

---

## 5. Allowed Responsibilities

`build_production_decision_read_model` may:

| Responsibility | Example |
|---------------|---------|
| Summarize decision status | `START_READY`, `HOLD`, `BLOCKED`, etc. |
| List blocking references | `["MANUFACTURING:MANUFACTURING:0", ...]` |
| List required human reviews | `["Engineering review required for tolerance violation"]` |
| List recommendation references | `["REC-0001", "REC-0002"]` |
| Produce explanation text | "2 critical blockers unresolved. 1 high-confidence recommendation available." |
| Produce confidence level | `HIGH`, `MEDIUM`, `LOW` based on recommendation confidences |
| Produce audit-friendly decision reasons | Traceable back to readiness status, blocking item IDs, and recommendation IDs |
| Count items by severity/confidence | Summarize how many blockers, warnings, and recommendations exist |

Everything in FOI-4 must be **derived from FOI-1/2/3 inputs only**. No new facts, no new calculations, no new business rules.

---

## 6. Forbidden Responsibilities

`build_production_decision_read_model` must **not**:

| Forbidden | Why |
|-----------|-----|
| Start production | FOI-4 is advisory — it does not trigger factory equipment or workflows |
| Schedule jobs | Scheduling is an operational concern outside FOI scope |
| Generate CNC code | CNC generation belongs to the manufacturing domain |
| Change engineering facts | Facts are authoritative — FOI is read-only |
| Change manufacturing facts | Same — read-only |
| Change cost facts | Same — read-only |
| Change commercial facts | Same — read-only |
| Approve quotation | Commercial approval is a business process, not a software decision |
| Approve customer order | Same |
| Calculate cost | Cost calculation belongs to `cost_intelligence.*` |
| Calculate manufacturing feasibility | Feasibility belongs to `manufacturing.*` |
| Infer hidden readiness | If FOI-1 says UNKNOWN, FOI-4 must not override to READY |
| Override human review | The decision record must not bypass the human reviewer |
| Use AI as final authority | AI may assist but must not be the sole decision maker |
| Become Engine / Workflow / Service / Controller | Naming must follow FOI conventions — read model builder |

---

## 7. Human Ownership

FOI-4 is **advisory** unless explicitly approved by a human role.

### What FOI-4 produces

```
ProductionDecisionReadModel
    decision_status: str          — START_READY / START_AFTER_REVIEW / HOLD / BLOCKED / UNKNOWN
    blocking_references: [...]    — blocking_item_id values
    required_reviews: [...]       — human-readable review requirements
    recommendation_references: [...] — REC-XXXX ids
    explanation: str              — human-readable summary
    confidence: str               — aggregate confidence
```

### What happens next (outside FOI-4)

A future system or process may record:

| Field | Purpose | Owner |
|-------|---------|-------|
| `reviewer` | Who reviewed the decision | External system / human |
| `approval_timestamp` | When the decision was confirmed | External system / human |
| `decision_note` | Free-text justification | External system / human |
| `human_override` | Whether a human overrode the recommendation | External system / human |

These fields belong **outside FOI-4**. FOI-4 produces the decision record; a human or external wrapper enriches it. This keeps FOI-4 stateless, deterministic, and testable.

---

## 8. Decision Traceability

Every field in `ProductionDecisionReadModel` must trace back to its source:

| Decision Field | Source |
|----------------|--------|
| `decision_status` | Derived from `FactoryReadinessReadModel.status` + blocking/recommendation counts |
| `blocking_references` | Copied from `FactoryBlockingAnalysisReadModel.blocking_items[].blocking_item_id` |
| `required_reviews` | Derived from `FactoryRecommendationReadModel.recommendations[].responsible_domain` — each domain with HIGH confidence recommendations may require review |
| `recommendation_references` | Copied from `FactoryRecommendationReadModel.recommendations[].recommendation_id` |
| `explanation` | Built from FOI-1/2/3 summaries |
| `confidence` | Derived from the lowest confidence among referenced recommendations |

Traceability ensures that an auditor can start from any decision field and follow the chain back to the original review panel fact.

---

## 9. Decision Status Rules

The following **conceptual** rules define how `decision_status` is derived. These are architecture-level guidelines — the actual implementation will be a pure function.

| Status | Conditions | Notes |
|--------|------------|-------|
| `BLOCKED` | `FactoryReadinessReadModel.status == BLOCKED` OR `critical_count > 0` | Production cannot proceed until blockers are resolved |
| `HOLD` | `FactoryReadinessReadModel.status == NOT_READY` OR `high_count > 0` AND `critical_count == 0` | Production should not start; errors need correction first |
| `START_AFTER_REVIEW` | `FactoryReadinessReadModel.status == NEEDS_REVIEW` OR `medium_count > 0` AND `critical_count == 0` AND `high_count == 0` | Production may proceed after warnings are reviewed |
| `START_READY` | `FactoryReadinessReadModel.status == READY` AND `critical_count == 0` AND `high_count == 0` AND `medium_count == 0` | Production can start — no blockers, errors, or warnings |
| `UNKNOWN` | `FactoryReadinessReadModel.status == UNKNOWN` OR insufficient data | Cannot determine — requires data |

**Important**: These rules are pure mappings from FOI-1/2/3 fields. They do not execute production, schedule jobs, or bypass human review. A `START_READY` decision does not automatically start production — it tells a supervisor "the system sees no reason to block production."

---

## 10. Test Requirements for FOI-4

When FOI-4 is implemented, the following tests must exist:

| # | Test | Proves |
|---|------|--------|
| 1 | Deterministic output | Same inputs → same decision |
| 2 | No input mutation | Input FOI models unchanged after call |
| 3 | Frozen dataclasses | `ProductionDecisionReadModel` is frozen |
| 4 | Traceability to blocking item IDs | `blocking_references` matches source `blocking_item_id` values |
| 5 | Traceability to recommendation IDs | `recommendation_references` matches source `recommendation_id` values |
| 6 | No backend imports | Source-inspection test on `factory_production_decision.py` |
| 7 | No decision execution | No calls to scheduling, CNC, or production APIs |
| 8 | No scheduling logic | Function never references time, dates, or schedules |
| 9 | No CNC generation | Function never references CNC paths or machine parameters |
| 10 | No cost calculation | No `sum()`, arithmetic, or cost formulas |
| 11 | No AI final authority | No import or invocation of AI/LLM modules |
| 12 | Status follows rules | Each status (BLOCKED, HOLD, START_AFTER_REVIEW, START_READY, UNKNOWN) is tested |
| 13 | Human reviews derived from recommendations | `required_reviews` matches domain-level recommendations |
| 14 | Empty/None inputs return safe defaults | No crashes on missing data |
| 15 | Existing FOI and UI and architecture tests pass | No regressions |

---

## 11. Business Value

| Benefit | How FOI-4 Delivers |
|---------|--------------------|
| **Reduces production risk** | BLOCKED and HOLD statuses prevent starting projects with unresolved issues |
| **Faster supervisor decisions** | Single decision status with explanation replaces manual cross-referencing of 5 review panels |
| **Preserves accountability** | Every decision traces back to specific blocking_item_id and recommendation_id |
| **Prevents starting incomplete projects** | `START_READY` only when all layers agree — no blockers, errors, or warnings |
| **Auditable decision reasons** | `explanation` field documents why a decision was reached |
| **No automatic production** | FOI-4 is advisory — a human always reviews before production starts |
| **Consistent decision rules** | Pure function — same conditions always produce the same status |
| **Low maintenance** | Decision logic is a simple mapping from FOI-1/2/3; no business rules embedded |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `START_READY` misinterpreted as "start now" | Medium | High | The ADR explicitly documents that FOI-4 is advisory. The output field `decision_status` must never trigger production APIs. |
| Status rules drift from FOI-1/2/3 changes | Low | Medium | Since FOI-4 reads only FOI-1/2/3, changes in those layers automatically propagate. If a new severity level is added to FOI-2, FOI-4 status rules must be updated. |
| `required_reviews` becomes a workflow engine | Medium | High | FOI-4 must **list** required reviews, not **assign** them or **track** their completion. Workflow tracking is an external system concern. |
| Human override field becomes a bypass | Low | Medium | The `human_override` field (if added by an external system) should be logged and auditable, not silent. FOI-4 itself never uses it. |
| Decision confidence is too simplistic | Low | Low | Confidence is derived from the lowest recommendation confidence. If FOI-3 adds more granular confidence, FOI-4 should propagate it. |

---

## 13. Recommendation

**APPROVED.**

The Production Decision Boundary is adopted as the architectural standard for FOI-4. Production Decision is a Read Model / Decision Record, not an Engine. It consumes FOI-1/2/3 only, never domain data directly. It never executes production. It is advisory — a human always reviews before production starts.

### Key Commitments

1. `build_production_decision_read_model` is a pure function — deterministic, side-effect free, input-preserving.
2. It consumes only `FactoryReadinessReadModel`, `FactoryBlockingAnalysisReadModel`, and `FactoryRecommendationReadModel`.
3. It never imports from domain, manufacturing, cost_intelligence, commercial_outputs, optimization, FreeCAD, or Qt.
4. It never starts production, schedules jobs, generates CNC, or approves orders.
5. Every output field traces back to a specific input field (blocking_item_id, recommendation_id, etc.).
6. `decision_status` is one of: `START_READY`, `START_AFTER_REVIEW`, `HOLD`, `BLOCKED`, `UNKNOWN`.
7. Confidence is derived from FOI-3 recommendation confidence — never invented.
8. No AI, LLM, or non-deterministic system serves as final authority.
9. All existing FOI, UI, and architecture tests must pass before FOI-4 delivery.
10. A separate ADR amendment is required if FOI-4 must read any data source beyond FOI-1/2/3.

---

## Appendix A: Status Decision Table

| Readiness Status | Critical Count | High Count | Medium Count | → Decision Status |
|-----------------|----------------|------------|--------------|-------------------|
| BLOCKED | any | any | any | BLOCKED |
| any | ≥1 | any | any | BLOCKED |
| NOT_READY | 0 | ≥1 | any | HOLD |
| any | 0 | 0 | ≥1 | START_AFTER_REVIEW |
| READY | 0 | 0 | 0 | START_READY |
| UNKNOWN | 0 | 0 | 0 | UNKNOWN |

This table is authoritative for FOI-4 implementation. Priority is top-to-bottom: the first matching row determines the status.

## Appendix B: Change History

| Date | Change | Author |
|------|--------|--------|
| 2026-07-05 | Initial ADR — Production Decision Boundary | FOI Architecture Gate |
