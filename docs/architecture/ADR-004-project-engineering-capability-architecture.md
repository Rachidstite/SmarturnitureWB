# ADR-004: Project Engineering Capability Architecture

## Status
Approved

## 1. Context

The repository now has a confirmed architectural path:

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

Project Engineering P2 has introduced DTO-only contracts for reusable engineering vocabulary:

- Operational Capability
- Operational Clearance
- Motion
- Accessibility
- Installation Sequence
- Serviceability

These contracts are intentionally generic. They are not component-specific and they are not tied to a single appliance or furniture subtype.

## 2. Problem

Project Engineering needs reusable capability language that can describe engineering constraints without collapsing into component-specific logic, manufacturing logic, or cost logic.

Without an explicit architecture, capability concepts risk fragmenting into duplicate engines, implicit special cases, or component-specific implementations that are difficult to reuse across current and future furniture systems.

## 3. Decision

Project Engineering Capability Architecture is approved as a reusable contract layer within Project Engineering.

Capabilities are:

- reusable engineering vocabulary
- generic across component types
- downstream of Project Geometry
- upstream of Manufacturing Intelligence and Cost Intelligence

Capabilities are not:

- geometry ownership
- manufacturing ownership
- pricing ownership
- UI logic
- new engines

## 4. Capability Hierarchy

The approved capability hierarchy is:

`FurnitureProject`
↓
`Project Geometry`
↓
`Project Engineering`
│
└── `Engineering Capabilities`
    ├── Operational Capability
    ├── Operational Clearance
    ├── Motion
    ├── Accessibility
    ├── Installation Sequence
    └── Serviceability
↓
`Manufacturing Intelligence`
↓
`Cost Intelligence`
↓
`Commercial Outputs`

This hierarchy defines a contract vocabulary, not an execution pipeline.

## 5. Dependency Rules

The following dependency rules are approved:

1. Capabilities may consume project-level facts that arrive from Project Geometry.
2. Capabilities may be referenced by future components such as Door, Drawer, Sliding Door, Lift Systems, and other future assemblies.
3. Capabilities must not depend on SceneGraph internals.
4. Capabilities must not calculate geometry.
5. Capabilities must not calculate motion.
6. Capabilities must not calculate accessibility.
7. Capabilities must not calculate clearances.
8. Capabilities must not calculate collision.
9. Capabilities must not calculate layout.
10. Capabilities must not calculate installation sequence.
11. Capabilities must not introduce duplicate engines.

These rules preserve the separation between geometry facts, engineering requirements, and downstream manufacturing or commercial computation.

## 6. Ownership Rules

The following ownership rules are approved:

1. Capabilities are reusable engineering contracts.
2. Capabilities do not own geometry.
3. Capabilities do not own manufacturing data.
4. Capabilities do not own pricing.
5. Capabilities do not own export or UI behavior.
6. Capabilities do not own component-specific business logic.

Current DTO contracts in this family are temporary peers that share report structure until the full family has been reviewed.

No shared base abstraction is approved yet.

## 7. Non-Goals

This ADR explicitly does not:

- define capability algorithms
- define engines
- define manufacturing behavior
- define cost behavior
- define UI behavior
- define component-specific business rules
- define scheduler behavior
- define task planner behavior
- move project geometry into Project Engineering
- move manufacturing intelligence into Project Engineering
- move cost intelligence into Project Engineering
- create a shared base abstraction for the current DTO family

## 8. Consequences

The following consequences are approved:

- Project Engineering can introduce reusable capability contracts without creating duplicate engines.
- Door, Drawer, Sliding Door, Lift Systems, and future components can consume the same capability vocabulary.
- Future engineering contracts can remain generic and DTO-only until a stable abstraction review is completed.
- Architecture review must continue before any capability family abstraction is extracted.
- Manufacturing Intelligence and Cost Intelligence remain downstream consumers of capability results, not owners of capability definitions.

## 9. Future Extensions

Future extensions may include:

- additional capability contracts when a new reusable engineering need is evidenced
- capability consumption by component-specific engineering models
- capability validation rules once real implementation requirements are proven
- eventual abstraction extraction only after the full capability family is reviewed and stable

Any future extension must preserve:

- backward compatibility
- geometry ownership boundaries
- manufacturing and cost separation
- the no-duplicate-engine rule

