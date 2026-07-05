# ADR-FOI-3 — Recommendation Knowledge Boundary

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Date** | 2026-07-05 |
| **Author** | FOI Architecture Gate |
| **Supersedes** | — |

---

## 1. Context

The Factory Operational Intelligence pipeline has completed three layers:

```
Engineering Facts  →  ReviewPanelReadModel
Manufacturing Facts  →  ReviewPanelReadModel
Cost Facts  →  ReviewPanelReadModel
Commercial Facts  →  ReviewPanelReadModel
Release Facts  →  ReviewPanelReadModel
         │
         ▼
FOI-1: Factory Readiness Read Model
         │
         ▼
FOI-2: Factory Blocking Analysis
         │
         ▼
FOI-3: Action Recommendation  (next layer)
         │
         ▼
Factory Decision
         │
         ▼
Scheduling / Production
```

Each FOI layer reads only from the layer above it.

FOI-3 will recommend actions to resolve blocking items produced by FOI-2. Without an architectural boundary defining where recommendations come from, the system risks evolving into a rule engine, an AI suggestion box, or a cascading set of duplicated business logic.

---

## 2. Problem

Recommendations are dangerous because they appear authoritative even when they are not.

### Bad examples

| Scenario | What Happens | Why It Is Dangerous |
|----------|-------------|---------------------|
| Door collision detected | An LLM suggests increasing cabinet gap | The LLM does not know the machine tolerance or design constraints |
| CNC edge mismatch | A rule recommends reducing feed rate | The rule may conflict with material specifications owned by manufacturing |
| Cost over budget | A generic recommendation suggests switching material | The material switch may violate engineering or commercial agreements |
| Blocked by QA signoff | A recommendation auto-approves the release | Bypasses the human review process that the signoff exists to enforce |

### Good examples

| Scenario | What Happens | Why It Is Safe |
|----------|-------------|----------------|
| Door collision detected | The system references an existing engineering rule: "Door gap must be ≥2mm for hinge clearance" | The knowledge is owned by engineering, not invented by FOI |
| CNC edge mismatch | The system reads the existing CNC capability table and reports the tool radius limit | The fact is already computed; FOI only surfaces it |
| Cost over budget | The system reads the existing cost estimate and budget from the Cost panel | FOI does not decide the budget — it projects the existing comparison |
| Blocked by QA signoff | The system reports "QA signoff blocked by pending review — requires Release Manager" | FOI identifies the blocker and the owner from existing data |

Without a **Knowledge Boundary**, FOI-3 could:

- Duplicate engineering rules in FOI code
- Invent manufacturing constraints from partial data
- Generate AI-suggested fixes that have no engineering basis
- Become a de facto Decision Engine by making recommendations that operators follow blindly
- Create an unowned, untested knowledge base that drifts from the domain sources

---

## 3. Decision

**Recommendations reference existing knowledge. They never invent knowledge.**

Every recommendation produced by FOI-3 must trace back to a knowledge source that already exists in the SmartFurnitureWB codebase. FOI-3 is an **orchestration layer** that surfaces already-owned knowledge — it is not a knowledge base, rule engine, or AI prompt.

### Core Principle

```
Blocking Item (from FOI-2)
         │
         ▼
Lookup: which domain owns this blocker type?
         │
         ▼
Reference: existing knowledge artifact in that domain
         │
         ▼
Recommendation: surface the known resolution
```

If no existing knowledge artifact can be referenced, the recommendation must state **"No automated recommendation available — requires manual review"** rather than inventing a guess.

---

## 4. Recommendation Sources

Every recommendation must reference exactly one **knowledge source** from the following allowed set:

| Source | What It Provides | Example Artifact |
|--------|-----------------|------------------|
| **Engineering** | Design rules, tolerances, geometry constraints | `JoineryIntelligenceBuilder`, `GeometryEngine` constraints |
| **Manufacturing** | CNC capabilities, tool paths, assembly rules | `ManufacturingDecisionBuilder`, CNC capability tables |
| **Cost** | Pricing, budget thresholds, cost estimates | `CostPackageBuilder`, `CostPackageReport` |
| **Commercial** | Pricing policy, discount rules, quotation terms | `CommercialPackageBuilder`, pricing policy tables |
| **Release** | Release checklists, signoff rules, approval chains | Release readiness checklist, signoff state |
| **Future Operational Policy** | Factory-specific rules (e.g., safety, logistics) | Future ADR-defined policies |
| **Unknown** | No known knowledge source | Must produce "No automated recommendation" |

A recommendation that references "Unknown" must **not** propose a concrete action — only a referral to manual review.

---

## 5. Recommendation Structure

Every recommendation should conceptually contain the following fields. These are **architecture-level requirements** — the actual dataclass will be defined when FOI-3 is implemented.

| Field | Purpose | Required |
|-------|---------|----------|
| `recommendation_id` | Unique identifier for traceability | Yes |
| `knowledge_source` | One of the allowed sources from Section 4 | Yes |
| `responsible_domain` | The domain that owns this knowledge (e.g., "Manufacturing") | Yes |
| `recommended_action` | What the system suggests doing | Yes |
| `recommendation_reason` | Why this action is recommended — must reference existing knowledge | Yes |
| `confidence` | High if knowledge source provides exact data; Low if only partial or heuristic | Yes |
| `blocking_reference` | The FactoryBlockingItem this recommendation addresses | Yes |
| `optional_notes` | Additional context from the knowledge source | No |

### Confidence Rules

| Confidence | When to Use |
|------------|-------------|
| `HIGH` | The knowledge source provides a direct, exact resolution (e.g., known tolerance range, known tool capability, known cost threshold) |
| `MEDIUM` | The knowledge source provides a related rule that partially applies (e.g., similar material, similar geometry) |
| `LOW` | The knowledge source provides general guidance but no exact match (e.g., "Contact engineering" with no rule reference) |
| `NONE` | No knowledge source found — produce "No automated recommendation available" |

Confidence `NONE` recommendations must be surfaced clearly to the operator so they know the system has no answer, rather than receiving a misleading low-confidence guess.

---

## 6. Forbidden Patterns

Recommendations **must not**:

| Forbidden | Why |
|-----------|-----|
| Calculate geometry (angles, distances, intersections) | Engineering owns geometry — FOI references, never computes |
| Calculate machining (speeds, feeds, tool paths) | Manufacturing owns machining — FOI references, never computes |
| Calculate cost (sums, estimates, comparisons) | Cost owns pricing — FOI references, never computes |
| Calculate quotation (discounts, margins, taxes) | Commercial owns pricing policy — FOI references, never computes |
| Override engineering facts | Facts are authoritative; FOI is read-only |
| Override manufacturing facts | Same — FOI is read-only |
| Override cost facts | Same — FOI is read-only |
| Override commercial facts | Same — FOI is read-only |
| Invent new engineering rules | Rules belong to domain modules — FOI must not create them |
| Generate AI guesses | LLM-generated fixes are non-deterministic and unauditable |
| Become a Decision Engine | FOI recommends; a human decides |
| Become a Workflow | Workflows sequence production steps; FOI diagnosis is not a workflow |
| Become a Service | FOI is a stateless read-model builder, not a running service |
| Become an Engine | "Engine" implies computation or inference — FOI projects and references |

### Zero-Tolerance Rules

1. **No `sum()`, `len() > 0` is fine but no arithmetic** — recommendations must not compute values
2. **No `if ... then ...` that encodes a new business rule** — business rules live in domain modules
3. **No `import` from domain modules** — FOI imports only from CV2 read models and other FOI modules
4. **No mutable state** — every FOI function is deterministic and input-preserving

---

## 7. Recommendation vs Decision

```
    Blocking Analysis (FOI-2)
           │
           ▼
    Recommendation (FOI-3)
           │
           ▼    ┌──────────────────┐
           │    │  HUMAN REVIEWS   │
           ▼    │  - Supervisor    │
    Condition  │  - Engineer      │
    Met? ──no──►  - Manager       │
           │    │  - Approver      │
           ▼    └──────────────────┘
       PROCEED          │
           │            ▼
           ▼       MODIFY / REJECT
    Production    /  Return to
           │         Design
           ▼
     Scheduling / Execution
```

**Key rule**: Recommendations never start production. A person reviews, decides, and triggers the next step. FOI-3 is a **diagnosis aid**, not a **production trigger**.

---

## 8. Knowledge Ownership

| Knowledge Domain | Owned By | FOI Role |
|-----------------|----------|----------|
| Engineering tolerances | `JoineryIntelligenceBuilder`, `GeometryEngine` | Reference only |
| Manufacturing capabilities | `ManufacturingDecisionBuilder`, CNC tables | Reference only |
| Cost pricing | `CostPackageBuilder`, `CostPackageReport` | Reference only |
| Commercial policy | `CommercialPackageBuilder`, pricing policy | Reference only |
| Release criteria | Release checklists, signoff state | Reference only |
| Recommendation orchestration | FOI-3 | Owns lookup and projection — never owns domain rules |

FOI-3 is a **thin orchestration layer** that maps blocking items to existing knowledge. It owns:

- The mapping table (blocker category → knowledge source)
- The recommendation structure per ADR-FOI-3
- The confidence calculation
- The "No automated recommendation" fallback

FOI-3 does **not** own:

- Engineering rules
- Manufacturing limits
- Cost thresholds
- Commercial policies
- Release criteria

---

## 9. Future Layering

```
┌─────────────────────────────────────────────────────────────────┐
│                        Domain Facts                              │
│  Validation, Manufacturing, Cost, Commercial, Release            │
│  (ReviewPanelReadModel objects)                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-1: Factory Readiness                                       │
│  Is the project ready?                                          │
│  → FactoryReadinessReadModel(status, reasons)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-2: Blocking Analysis                                       │
│  What is blocking production?                                   │
│  → FactoryBlockingAnalysisReadModel(items, counts)              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-3: Action Recommendation  (next)                           │
│  What can resolve it?                                           │
│  → references existing knowledge only                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FOI-4: Production Decision  (future)                           │
│  Can we proceed?                                                │
│  → based on recommendation + human input                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Scheduling / Execution                                         │
│  When does production start?                                    │
└─────────────────────────────────────────────────────────────────┘
```

Each layer reads only from the layer above. No layer reads directly from domain facts except FOI-1. No layer skips a layer.

---

## 10. Business Value

| Benefit | How ADR-FOI-3 Delivers |
|---------|------------------------|
| **Reusable knowledge** | FOI-3 references existing domain modules — no duplicate rules, no drift |
| **No duplicated rules** | Every recommendation traces to one knowledge source owned by one domain |
| **Traceable recommendations** | Each recommendation carries `knowledge_source` and `blocking_reference` |
| **Factory trust** | Operators learn that recommendations are grounded in known facts, not guesses |
| **Explainable decisions** | Every recommendation has a `recommendation_reason` that references a specific knowledge artifact |
| **Low maintenance** | When domain rules change, the recommendation automatically updates because FOI-3 references the current state |
| **Safe fallback** | When no knowledge source exists, "No automated recommendation" prevents misleading guesses |
| **No AI liability** | All outputs are deterministic and auditable — no LLM-generated advice that could cause production errors |

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Knowledge duplication** — recommendation logic copies a domain rule instead of referencing it | Medium | High | Code review must verify every recommendation traces to a domain module import or call. Static analysis can check that `knowledge_source` values match allowed set. |
| **Recommendation drift** — FOI-3 accumulates heuristic rules over time, becoming a de facto rule engine | Medium | High | ADR-FOI-3 explicitly forbids new business rules in FOI code. Periodic architecture gates must enforce this. |
| **Conflicting recommendations** — two knowledge sources suggest different actions for the same blocker | Low | Medium | The mapping table (`blocker category → knowledge source`) ensures exactly one source per blocker type. If overlap occurs, it must be resolved by an ADR amendment. |
| **Domain ownership violations** — FOI-3 accidentally references a knowledge source the caller does not own | Low | Low | Each recommendation carries `responsible_domain` — consumers can filter by ownership. |
| **"No automated recommendation" overload** — too many blockers lack a knowledge source, making FOI-3 useless | Low | High | The first implementation of FOI-3 should start with the most common blocker categories and expand only when knowledge sources exist. Never invent knowledge to fill gaps. |
| **Performance impact of knowledge lookups** — referencing domain modules may be expensive | Low | Low | FOI-3 reads already-computed read models; it never triggers domain computation. Lookups are in-memory dict/attribute reads. |

---

## 12. Recommendation

**APPROVED.**

The Recommendation Knowledge Boundary is adopted as the architectural standard for FOI-3. Every recommendation must reference an existing knowledge source, never invent new knowledge, and clearly signal when no automated recommendation is available.

### Key Commitments

1. Every recommendation carries `knowledge_source` from the allowed set (Engineering, Manufacturing, Cost, Commercial, Release, Future Operational Policy, Unknown).
2. Every recommendation is traceable to a `blocking_reference`.
3. `confidence` is HIGH, MEDIUM, LOW, or NONE — never derived by AI.
4. Recommendations never calculate geometry, machining, cost, or quotation.
5. Recommendations never override domain facts.
6. Recommendations never invent engineering rules.
7. The fallback for unknown blockers is always "No automated recommendation available — requires manual review."
8. FOI-3 is a stateless, deterministic read-model builder — not a service, engine, workflow, or decision system.
9. The mapping from blocker category to knowledge source is a simple table — not a rule engine, not AI, not a decision tree.
10. All existing CV2 and FOI tests must pass before FOI-3 delivery.

---

## Appendix A: Change History

| Date | Change | Author |
|------|--------|--------|
| 2026-07-05 | Initial ADR — Recommendation Knowledge Boundary | FOI Architecture Gate |
