# ADR-006: Engineering Evaluation Pattern

## Status
Approved

## 1. Context

Project Engineering has evolved into a reusable intelligence layer with:

- engineering fact extractors
- engineering facts
- engineering rules
- operational rule results
- decision reduction
- cabinet readiness reports
- project readiness reports

The repository now has examples of this flow for operational clearance and operational readiness.

The architecture needs a stable evaluation pattern so future engineering intelligence features can be added without introducing duplicate engines, component-specific rule systems, or hidden geometry ownership.

## 2. Problem

Without an explicit evaluation pattern, engineering intelligence can drift into:

- rules that read geometry directly
- facts that start behaving like rules
- extractors that become engines
- readiness reports that become manufacturing or cost reports
- component-specific engines such as DoorEngine or DrawerEngine
- FreeCAD-specific logic inside project_engineering

That drift would reduce reuse across doors, drawers, sliding systems, lift systems, shelves, and future furniture components.

## 3. Decision

All future engineering intelligence features should follow this pattern:

`Project Geometry`
↓
`Engineering Fact Extractor`
↓
`Engineering Facts`
↓
`Engineering Rule`
↓
`OperationalRuleResult`
↓
`OperationalDecisionReport`
↓
`CabinetOperationalReadinessReport`
↓
`ProjectOperationalReadinessReport`

The pattern is approved as the default evaluation path for reusable engineering intelligence.

## 4. Approved Evaluation Pattern

The approved pattern has the following responsibilities:

1. Project Geometry owns geometry.
2. Engineering Fact Extractors derive facts only.
3. Engineering Facts carry derived engineering data only.
4. Engineering Rules evaluate facts only.
5. Rules return `OperationalRuleResult`.
6. Decision reducers aggregate rule results only.
7. Cabinet reports aggregate cabinet-level readiness only.
8. Project reports aggregate project-level readiness only.

This pattern is an evaluation pipeline, not an engine hierarchy.

## 5. Layer Responsibilities

### Project Geometry

Project Geometry owns canonical spatial facts, envelope, bounds, footprint, and other geometry-related ownership concerns.

### Engineering Fact Extractor

Extractors derive engineering facts from already available engineering input.
They do not calculate geometry, make decisions, or execute rule logic.

### Engineering Facts

Facts carry derived engineering data only.
They are reusable across components and remain generic.

### Engineering Rule

Rules evaluate facts only and return `OperationalRuleResult`.
Rules are small and focused.

### OperationalRuleResult

`OperationalRuleResult` captures the result of a single rule evaluation.

### OperationalDecisionReport

`OperationalDecisionReport` aggregates rule results into project-level operational decision flags and messages.

### CabinetOperationalReadinessReport

`CabinetOperationalReadinessReport` aggregates cabinet-level readiness and cabinet-level warnings or violations.

### ProjectOperationalReadinessReport

`ProjectOperationalReadinessReport` aggregates project-level readiness and project-level cabinet counts, warnings, and violations.

## 6. Dependency Rules

The following dependency rules are approved:

1. Rules must not read Project Geometry directly.
2. Decisions must not calculate geometry.
3. Facts must not become rules.
4. Extractors must not become engines.
5. Readiness reports must not become manufacturing reports.
6. Readiness reports must not become cost reports.
7. Readiness reports must not become commercial reports.
8. Manufacturing, Cost, and Commercial remain downstream layers.
9. No FreeCAD-specific dependencies are allowed inside the engineering evaluation pattern.
10. No component-specific engines such as DoorEngine or DrawerEngine are approved.

These rules preserve the separation between geometry ownership, derived engineering data, rule evaluation, and readiness aggregation.

## 7. Non-Goals

This ADR explicitly does not:

- create new implementation
- create new DTOs
- create new rules
- create new engines
- refactor existing modules
- move files
- define component-specific engines
- move manufacturing intelligence into Project Engineering
- move cost intelligence into Project Engineering
- replace Project Geometry ownership

## 8. Consequences

The following consequences are approved:

- Future engineering intelligence features can reuse the same structure.
- Engineering features remain generic across doors, drawers, sliding systems, lift systems, shelves, and future components.
- Geometry ownership remains in Project Geometry.
- Project Engineering stays focused on derived engineering intelligence.
- Operational results can be reduced into cabinet and project readiness without mixing in manufacturing or cost concerns.

## 9. Future Extensions

Future extensions may include:

- Motion Intelligence
- Accessibility Intelligence
- Structural Intelligence
- Installation Intelligence
- Door, Drawer, Sliding, and Lift systems consuming the same pattern

Any future extension must preserve:

- geometry ownership boundaries
- fact extraction as a derivation step only
- rule evaluation as a fact-consumption step only
- readiness aggregation as a downstream step only
- the no-duplicate-engine rule
- the no-FreeCAD-in-project_engineering rule

