# ADR-001: Project Spatial Conventions Policy

## Status
Approved

## 1. Context

SmartFurnitureWB has completed the Project Engineering Contracts P1:

- Placement Boundary
- Placement Semantic Boundary
- Adjacency Contract
- Alignment Contract
- Installation Clearance Contract
- Collision Contract

The completed audits show the following evidence-based boundaries:

- `FurnitureProject` owns `cabinets`, `placements`, and `metadata`.
- `CabinetPlacement` owns pose only: `cabinet_id`, `x`, `y`, `z`, `rotation_z`.
- `SceneGraph` / `SceneNode` own cabinet-internal geometry.
- `Topology` / `Section` own cabinet subdivision geometry.
- `Layout` owns cabinet-internal layout zones.

The same audits also show that no current owner exists for project-level:

- envelope
- bounds
- footprint
- adjacency relation
- alignment relation
- clearance relation
- collision relation

The canonical spatial conventions audit further established:

- cabinet-internal coordinates are used consistently by `SceneGraph`, `Topology`, and `Layout`
- `rotation_z` exists on `CabinetPlacement` but has no defined unit or direction in production geometry code
- bounds are implicit but not canonical
- envelope is missing as a convention
- project-global coordinate semantics are not formalized

This policy records the current architectural position before any future work on project geometry ownership or project engineering reports.

## 2. Current Geometry Ownership

### Approved current ownership boundaries

- `FurnitureProject` remains the project aggregate and placement owner.
- `CabinetPlacement` remains pose-only.
- `SceneGraph` remains the cabinet-internal geometry owner.
- `Topology` remains the cabinet subdivision geometry owner.
- `Layout` remains the cabinet-internal layout owner.

### Not owned today

The repository does not currently evidence a project-level owner for:

- project cabinet envelope
- project cabinet bounds
- project cabinet footprint
- project adjacency relation
- project alignment relation
- project clearance relation
- project collision relation

## 3. Current Spatial Conventions

### Cabinet-local conventions

The repository already uses cabinet-local conventions for internal geometry:

- `SceneNode` stores local `x`, `y`, `z`, `width`, `depth`, and `height`.
- `Section` stores `origin_x`, `origin_y`, `origin_z`, `width`, `height`, and `depth`.
- `LayoutContext` and `LayoutResult` operate inside cabinet-local space.
- `SpatialQueryEngine` computes collisions from cabinet-node transforms and node dimensions.

### Project-placement conventions

The repository also stores project-level pose data:

- `CabinetPlacement.x`
- `CabinetPlacement.y`
- `CabinetPlacement.z`
- `CabinetPlacement.rotation_z`

However, the repository does not define a canonical project-space convention for:

- origin meaning
- coordinate handedness
- rotation units
- rotation direction
- project-to-cabinet transform semantics

### Bounds and envelope conventions

- `BoundingBox` exists as a generic geometric primitive.
- No canonical project-level bounds owner or envelope owner exists.
- Envelope is not a first-class convention in the repository evidence.

## 4. Known Gaps

The following are still missing as conventions, not merely as implementations:

- project-global coordinate semantics
- `rotation_z` unit and direction
- canonical project envelope definition
- canonical project bounds definition
- canonical project footprint definition
- project-level spatial relation ownership
- project-level tolerance / minimum-distance convention

These gaps prevent deterministic project geometry ownership and prevent project engineering reports from resting on stable spatial conventions.

## 5. Approved Decisions

The following decisions are approved by evidence and audit:

1. `FurnitureProject` remains a placement aggregate only.
2. `CabinetPlacement` remains pose-only.
3. `SceneGraph` remains cabinet-local and cabinet-internal.
4. `Topology` remains cabinet subdivision geometry.
5. `Layout` remains cabinet-internal.
6. Project engineering facts are not yet owned at the project geometry level.
7. Project engineering contracts P1 are complete as boundary contracts, not as ownership contracts.

## 6. Postponed Decisions

The following remain postponed until spatial conventions are formally defined:

- Project Geometry Ownership
- Project Engineering Reports
- Project Engineering Builders
- project-level collision implementation
- project-level alignment implementation
- project-level clearance implementation
- project-level adjacency implementation

## 7. Non-Goals

This policy explicitly does not:

- introduce new engines
- define room engines
- define kitchen engines
- define collision behavior
- define report behavior
- define builder behavior
- move geometry ownership into `FurnitureProject`
- move project decisions into `SceneGraph`
- move project decisions into `Layout`
- move project decisions into `Manufacturing`
- move project decisions into `Cost`

## 8. Impact

### Project Engineering

Project Engineering remains blocked from moving beyond boundary contracts until spatial conventions are explicit. The current evidence supports separation, not ownership.

### Manufacturing Intelligence

Manufacturing intelligence remains downstream of cabinet geometry and project placements. It can consume current facts, but it should not be treated as the owner of project spatial conventions.

### Kitchen Engineering

Kitchen engineering is the clearest future pressure point for project spatial conventions. The current repository evidence does not yet provide a stable project geometry boundary for multi-cabinet kitchen decisions.

### Future Room Engineering

Room engineering is not ready under the current evidence because wall, room, and appliance geometry are not owned project facts and no canonical project spatial convention exists for them.

## 9. Exit Criteria

Before proceeding to each next stage, the following must be clarified:

### Before Project Geometry Ownership

- project coordinate scope
- cabinet placement origin meaning
- `rotation_z` unit
- `rotation_z` direction
- envelope convention
- bounds convention
- footprint convention

### Before Project Engineering Reports

- project-level geometry ownership boundary
- deterministic project spatial conventions
- project-level spatial relation ownership
- project/global coordinate semantics

### Before Project Engineering Builders

- stable project geometry conventions
- stable project geometry ownership boundary
- stable separation from cabinet-internal geometry

## 10. Final Status

**APPROVED**

This policy is approved as the current architectural position:

- Project Engineering Contracts P1 are complete.
- The repository still lacks canonical project spatial conventions.
- Project Geometry Ownership remains postponed until those conventions are formally defined.
- Project Engineering Reports remain postponed for the same reason.

