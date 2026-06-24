# ADR-003: Project Geometry Ownership Boundary

## Status
Approved

## 1. Context

Repository evidence establishes the following current ownership boundaries:

- `FurnitureProject` owns `cabinets`, `placements`, and `metadata`.
- `CabinetPlacement` owns pose only.
- `SceneGraph` owns cabinet-local geometry.
- `Topology` owns cabinet subdivision geometry.
- `Layout` owns cabinet-internal layout.

ADR-002 defined canonical spatial conventions for project coordinates, cabinet placement origin meaning, `rotation_z`, envelope, bounds, and footprint. Those conventions define how project spatial facts must be interpreted, but they do not assign ownership.

This ADR assigns ownership boundaries for project geometry facts and clarifies what remains outside that boundary.

## 2. Ownership Decision

### A. Project Geometry Facts

The following facts belong to the **Project Geometry boundary**:

- envelope
- bounds
- footprint

These are project-level spatial facts and are not owned by `FurnitureProject`, `SceneGraph`, `Topology`, or `Layout`.

### B. Project Engineering Facts

The following facts belong to the **Project Engineering boundary**, which remains later than project geometry:

- adjacency
- alignment
- clearance
- collision

These facts depend on project geometry facts plus higher-level project decision logic.

### C. External Environmental Facts

The following facts remain outside the current ownership boundary:

- wall geometry
- room geometry
- appliance geometry

These are environmental facts, not current project-owned facts.

## 3. Boundary Rules

The following boundary rules are approved:

1. `FurnitureProject` must not own envelope, bounds, or footprint.
2. `CabinetPlacement` must remain pose-only.
3. `SceneGraph` must remain cabinet-local.
4. `Topology` must remain cabinet subdivision geometry.
5. `Layout` must remain cabinet-internal.
6. Manufacturing and Cost layers must consume downstream facts, not own project geometry.

These rules preserve the separation already evidenced in the repository:

- project aggregate ownership remains in `FurnitureProject`
- cabinet geometry remains in `SceneGraph` and `Topology`
- cabinet layout remains in `Layout`
- downstream manufacturing and cost layers remain consumers of geometry-derived facts

## 4. Architecture Flow

The intended architecture flow is:

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

This flow reflects the boundary order established by the audits:

- project placements are upstream of project geometry
- project geometry is upstream of project engineering
- project engineering is upstream of manufacturing and cost intelligence

## 5. Consequences

The following consequences are approved:

- Project Geometry Ownership is now approved as an architecture boundary.
- Project Engineering Reports remain postponed until Project Geometry contracts exist.
- Project Engineering Builders remain postponed.
- Collision, alignment, clearance, and adjacency implementations remain postponed.

This ADR does not change implementation status. It only establishes the ownership boundary.

## 6. Non-goals

This ADR explicitly does not:

- define implementations
- define algorithms
- define engines
- define builders
- define reports
- move project geometry into `FurnitureProject`
- move project geometry into `SceneGraph`
- move project geometry into `Manufacturing`
- move project geometry into `Cost`
- introduce a room engine
- introduce a kitchen engine

## 7. Exit Criteria

Before Project Engineering Reports may proceed, the following must exist:

- Project Geometry boundary contracts
- envelope contract
- bounds contract
- footprint contract
- boundary tests proving separation from:
  - `FurnitureProject`
  - `SceneGraph`
  - `Layout`
  - `Manufacturing`
  - `Cost`

These exit criteria are about verified separation and ownership, not implementation detail.

## 8. Final Classification

- ADR-003: **APPROVED**
- Project Geometry Ownership Boundary: **APPROVED**
- Project Geometry Implementation: **POSTPONED**
- Project Engineering Reports: **POSTPONED**
- Project Engineering Builders: **POSTPONED**

## 9. Summary

This ADR formally establishes the project geometry boundary:

- `FurnitureProject` remains the project aggregate owner.
- `CabinetPlacement` remains pose-only.
- `SceneGraph`, `Topology`, and `Layout` remain cabinet-scoped.
- Project geometry facts are owned by a distinct project geometry boundary.
- Project engineering facts are later and remain postponed until project geometry contracts exist.

