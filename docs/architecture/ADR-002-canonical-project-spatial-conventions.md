# ADR-002: Canonical Project Spatial Conventions

## Status
Approved

## 1. Project Coordinate Convention

### Decision

The canonical project coordinate system is a **right-handed** 3D coordinate system with:

- **+X** increasing from left to right
- **+Y** increasing from front to back
- **+Z** increasing from bottom to top

### Evidence

Repository evidence is consistent with this convention:

- `SceneGraphBuilder` places cabinet-internal geometry with `x = 0` on the left side, `y = 0` at the front, and `z = 0` at the bottom.
- `SceneGraphBuilder` places the right side at `x = W - T`, the top at `z = H - T`, and the back panel near `y = D`, which is consistent with a depth axis on `Y` and a vertical axis on `Z`.
- `SpatialQueryEngine` treats `x`, `y`, and `z` as the minimum corner of a box and expands by `width`, `depth`, and `height`, which matches an axis-aligned box convention in the same coordinate frame.
- `LayoutContext` and `LayoutResult` use `z_start` and `height` as vertical layout quantities, reinforcing `Z` as the vertical axis.

### Policy Meaning

Project-space coordinates use the same axis semantics as cabinet-local geometry:

- `X` is horizontal width
- `Y` is cabinet depth
- `Z` is vertical height

This policy does not change ownership. It only defines the convention that project-level placement data must follow.

## 2. Cabinet Placement Convention

### Decision

`CabinetPlacement.x`, `CabinetPlacement.y`, and `CabinetPlacement.z` represent the **project-space origin of the placed cabinet**.

The canonical origin point is the **lower-left-front corner of the cabinet envelope** in project space, before any rotation is applied.

### Evidence

- `CabinetPlacement` is pose-only and contains no bounds or size fields.
- `SceneGraphBuilder` uses cabinet-local node coordinates anchored at `(0, 0, 0)` for the cabinet frame.
- Cabinet geometry is built from that cabinet-local corner-based frame.
- The project placement fields are therefore the appropriate project-space location for the cabinet's origin.

### Policy Meaning

`CabinetPlacement` is interpreted as:

- `x`: project-space left-to-right position of the cabinet origin
- `y`: project-space front-to-back position of the cabinet origin
- `z`: project-space bottom-to-top position of the cabinet origin

## 3. `rotation_z` Convention

### Decision

`rotation_z` means **rotation around the project Z axis** of the placed cabinet.

### Units

The canonical unit is **degrees**.

### Direction

Positive rotation is **counterclockwise when viewed from above looking down the +Z axis**.

### Relationship to Project Coordinates

`rotation_z` is applied in the project coordinate system around the cabinet origin defined by `CabinetPlacement.x`, `CabinetPlacement.y`, and `CabinetPlacement.z`.

### Evidence

- `CabinetPlacement` already carries `rotation_z`.
- The repository has no alternative rotation field for project placement.
- Project-level placement tests already use numeric rotation values such as `90.0`, which are consistent with degree-based convention.
- No production geometry code currently consumes `rotation_z`, so the convention must be explicit before project geometry work proceeds.

## 4. Envelope Convention

### Decision

An **envelope** is the canonical 3D occupied extent of a placed cabinet in project space.

It is the spatial volume occupied by the cabinet after applying:

- cabinet-local geometry
- project-space placement origin
- project-space `rotation_z`

### Policy Meaning

Envelope is the primary spatial convention for the placed cabinet's occupied space.

It is not a separate ownership claim. It is the canonical spatial meaning that project geometry must use.

## 5. Bounds Convention

### Decision

`Bounds` are the **axis-aligned min/max extents** of the envelope in project space.

### Relationship to Envelope

- Envelope is the canonical occupied shape.
- Bounds are the normalized project-space axis-aligned extents of that envelope.

### Evidence

- `BoundingBox` already exists as a generic primitive in `domain/topology.py`.
- `SpatialQueryEngine` computes min/max extents from node positions and dimensions.
- The repository does not provide a canonical project bounds owner, so the convention must be defined in relation to envelope.

## 6. Footprint Convention

### Decision

`Footprint` is the **2D projection of the envelope onto the project XY plane**.

### Relationship to Envelope

- Envelope is the full 3D occupied extent.
- Footprint is the project-floor projection of that extent.

### Evidence

- Project placement is expressed in `x`, `y`, `z`.
- Cabinet-local geometry is built in a 3D frame.
- Project engineering contracts P1 concern adjacency, alignment, clearance, and collision, all of which depend on the spatial projection of cabinet occupancy.

## 7. Non-Goals

This ADR does not:

- define collision behavior
- define alignment behavior
- define clearance behavior
- define geometry ownership
- define builders
- define reports
- define engines
- move project geometry into `FurnitureProject`
- move project geometry into `SceneGraph`
- move project geometry into `Topology`
- move project geometry into `Layout`
- move project geometry into `Manufacturing`
- move project geometry into `Cost`

## 8. Exit Criteria

After ADR-002, the following are unblocked as conventions, not as implementations:

- canonical interpretation of `CabinetPlacement`
- canonical project-space meaning of `rotation_z`
- canonical envelope definition
- canonical bounds definition as a derived extent convention
- canonical footprint definition as a derived projection convention

This ADR does **not** unblock project geometry ownership itself, project engineering reports, or project engineering builders.

## 9. Final Classification

- Project Geometry Ownership: **POSTPONED**
- Project Engineering Reports: **POSTPONED**
- Project Engineering Builders: **POSTPONED**

## 10. Summary

This ADR establishes the spatial conventions required for future project geometry work:

- project coordinates are right-handed
- `CabinetPlacement` is the project-space origin of the cabinet
- `rotation_z` is a degree-based project-space orientation around +Z
- envelope is the canonical occupied 3D extent
- bounds are the axis-aligned extents of the envelope
- footprint is the projection of the envelope onto the XY plane

The conventions are now explicit. Ownership and implementation remain postponed.

