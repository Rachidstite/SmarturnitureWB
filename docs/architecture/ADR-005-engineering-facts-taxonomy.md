# ADR-005: Engineering Facts Taxonomy

## Status
Approved

## 1. Context

The repository now has a confirmed architectural path for project-level engineering concerns:

`FurnitureProject`
↓
`Project Geometry`
↓
`Project Engineering`
↓
`Manufacturing Intelligence`
↓
`Cost Intelligence`
↓
`Commercial Outputs`

Project Engineering now contains DTO-only engineering facts, engineering fact extractors, and operational rule inputs/outputs that are reused across furniture components.

These facts are intended to support doors, drawers, shelves, sliding systems, lift systems, and future furniture components without duplicating geometry ownership, rules, decisions, manufacturing behavior, or cost behavior.

## 2. Problem

Project Engineering needs a clear taxonomy for what kinds of engineering facts belong in the layer.

Without a taxonomy, the layer can drift into:

- manufacturing facts
- cost facts
- commercial facts
- geometry ownership
- rule engines
- decision engines
- component-specific logic

That drift would blur ownership boundaries, create duplicate abstractions, and make the engineering vocabulary harder to reuse across future furniture components.

## 3. Decision

Engineering Facts inside `project_engineering` are limited to the following approved categories:

- Spatial Facts
- Structural Facts
- Installation Facts

Rejected inside `project_engineering` are:

- Manufacturing Facts
- Cost Facts
- Commercial Facts

Engineering Facts are:

- derived engineering facts
- not Geometry owners
- not Rules
- not Decisions
- not Manufacturing
- not Cost
- not UI
- reusable across doors, drawers, shelves, sliding systems, lift systems, and future furniture components

## 4. Approved Engineering Fact Categories

### Spatial Facts

Spatial facts describe available, required, derived, or risk-related spatial conditions relevant to component operation and placement.

Approved examples:

- `AvailableOperationalClearanceFact`
- `RequiredOperationalClearanceFact`
- `MotionEnvelopeFact`
- `AccessibilitySpaceFact`
- `CollisionRiskFact`

### Structural Facts

Structural facts describe load, support, and stability conditions relevant to component or project integrity.

Approved examples:

- `LoadCapacityFact`
- `SupportSpanFact`
- `SagRiskFact`
- `RackingRiskFact`
- `StabilityFact`

### Installation Facts

Installation facts describe access, sequencing, clearance, or service conditions relevant to assembly and installation.

Approved examples:

- `InstallationAccessFact`
- `AssemblySequenceFact`
- `WallClearanceFact`
- `ServiceAccessFact`
- `FixingAccessFact`

## 5. Rejected Categories inside Project Engineering

The following categories are rejected as Project Engineering fact families:

### Manufacturing Facts

Examples rejected from `project_engineering`:

- `CutlistFact`
- `CNCOperationFact`
- `EdgeBandingFact`
- `DrillingFact`
- `MaterialYieldFact`

### Cost Facts

Examples rejected from `project_engineering`:

- `MaterialCostFact`
- `HardwareCostFact`
- `LaborCostFact`
- `WasteCostFact`
- `ProfitabilityFact`

### Commercial Facts

Commercial facts are also rejected inside `project_engineering`.
Commercial outputs belong downstream in the commercial layer, not in the engineering fact taxonomy.

## 6. Ownership Rules

The following ownership rules are approved:

1. Engineering facts are derived facts, not geometry owners.
2. Engineering facts do not own project geometry, envelope, bounds, footprint, or collision logic.
3. Engineering facts do not own manufacturing data.
4. Engineering facts do not own pricing data.
5. Engineering facts do not own commercial outputs.
6. Engineering facts do not own UI behavior.
7. Engineering facts may be reused by multiple component families.
8. Engineering facts must remain generic enough to support current and future furniture systems.

## 7. Dependency Rules

The following dependency rules are approved:

1. Engineering facts may be derived from upstream geometry or other engineering input facts.
2. Engineering facts must not calculate geometry ownership.
3. Engineering facts must not become rules.
4. Engineering facts must not become decisions.
5. Engineering facts must not become manufacturing logic.
6. Engineering facts must not become cost logic.
7. Engineering facts must not depend on UI behavior.
8. Engineering facts must not depend on FreeCAD-specific APIs.
9. Engineering facts must not duplicate each other across categories.

This taxonomy is intentionally broad enough to support reusable engineering vocabulary while remaining narrow enough to prevent cross-layer leakage.

## 8. Consequences

The following consequences are approved:

- Project Engineering has a bounded taxonomy for future fact extraction and fact storage.
- Spatial, structural, and installation facts can grow without collapsing into manufacturing or cost logic.
- Domain language stays reusable across doors, drawers, shelves, sliding systems, lift systems, and future furniture components.
- Reviewers can classify new fact types before implementation begins.
- Manufacturing, cost, and commercial concerns remain downstream consumers, not fact taxonomy owners.

## 9. Future Extensions

Future extensions may include:

- additional spatial facts when new reusable engineering evidence appears
- additional structural facts when load or stability needs are proven
- additional installation facts when assembly or service needs are proven
- a future fact registry only if it can remain DTO-only and category-bounded
- future validation or decision steps that consume facts without taking ownership of them

Any future extension must preserve:

- the approved category boundary
- the rejection of manufacturing, cost, and commercial facts inside `project_engineering`
- the no-duplicate-engine rule
- the no-duplicate-abstraction rule
- backward compatibility

