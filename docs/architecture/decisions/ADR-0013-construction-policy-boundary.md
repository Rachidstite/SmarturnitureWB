# ADR-0013
Construction Policy Boundary

## Status

Accepted conceptually. Implementation postponed.

## Context

Repository evidence shows that SmartFurnitureWB already separates the broad furniture domain from the current executable base-cabinet path, but the engineering boundary is still mixed:

- `CabinetConstructionModel` is a generic construction carrier.
- `ConstructionResolver` currently combines construction model assembly with base-cabinet policy.
- `WallCabinetEngineeringModel` is descriptive only and does not produce geometry.
- Wall cabinet geometry is not implemented.
- `WallMountCapability`, `WallMountRules`, and `WallMountVocabulary` already exist as passive wall-policy vocabulary.
- Creating a `WallCabinetConstructionResolver` is not approved.

The architecture therefore needs a clear conceptual boundary between:

- Construction Model
- Construction Policy
- Construction Execution

## Evidence

The repository establishes the following evidence:

- `domain/furniture_construction_model.py`
  - defines the generic construction carrier types:
    - `CabinetConstructionSpecification`
    - `PanelConstruction`
    - `BackPanelConstruction`
    - `DoorConstruction`
    - `ShelfConstruction`
    - `JoineryConstruction`
    - `HardwareConstruction`
    - `ConstructionValidationIssue`
    - `CabinetConstructionModel`
  - `CabinetConstructionSpecification` already contains `wall_mount_count`, which shows that wall-related construction intent is part of the carrier vocabulary, not the execution layer.

- `domain/construction_resolver.py`
  - currently hard-codes base-cabinet policy values such as thickness, back-panel style, drawer count, wall-mount count, joinery policy, hardware policy, allowed/disallowed details, and validation posture.
  - produces a `CabinetConstructionModel`, which is the generic carrier, but the policy decisions are embedded inside the resolver body.

- `domain/wall_cabinet_engineering_model.py`
  - remains descriptive only.
  - derives wall fields from `WallCabinetSpecification`.
  - does not generate geometry.

- `domain/wall_mount_vocabulary.py`
  - provides wall-mount vocabulary such as mounting type, wall type, anchor type, suspension hardware family, load category, clearance type, and failure mode.

- `domain/wall_mount_rules.py`
  - provides passive wall-mount rule dataclasses.

- `domain/wall_mount_capability.py`
  - provides passive wall-mount capability dataclasses.

- `docs/domain/Furniture_Domain_Architecture.md`
  - already distinguishes shared domain concepts from family-specific specialization axes.

- `docs/architecture/Architecture_Baseline_v1.md`
  - documents the current layered architecture and runtime flow.

- `docs/architecture/decisions/ADR-0012-canonical-output-contract.md`
  - defines the canonical downstream runtime output contract and keeps output contracts separate from engineering policy.

## Decision

Adopt the following conceptual separation:

- **Construction Model**
  - a generic construction carrier
  - represents structural cabinet data in a family-neutral shape

- **Construction Policy**
  - family-specific construction rules and strategies
  - describes how a cabinet family should be built and validated

- **Construction Execution**
  - resolver / builder / geometry generation
  - applies policy to a model and produces executable geometry or scene-graph evidence

This ADR accepts Construction Policy as a concept, but does not introduce a new implementation yet.

## Consequences

- The existing generic construction carrier remains the shared data shape for construction evidence.
- Base-cabinet policy remains in the current resolver for now.
- Wall policy vocabulary remains passive and available for later use.
- The repo can reason about family-specific construction strategy without requiring a new engine, builder, workflow, or pipeline.
- Future policy extraction can happen without changing the canonical output contract or the current application routing.

## Out of Scope

This ADR does not:

- implement `ConstructionPolicy`
- modify `ConstructionResolver`
- create `WallCabinetConstructionResolver`
- add scene graph generation
- add FreeCAD geometry
- add manufacturing logic
- add cost logic
- add commercial logic

## Deferred Implementation

Implementation is postponed for:

- a concrete `ConstructionPolicy` data contract
- policy-driven resolver refactoring
- wall-specific resolver classes
- any geometry-producing wall implementation

The current repository evidence is sufficient to accept the concept, but not sufficient to justify code changes.

## References

- [docs/domain/Furniture_Domain_Architecture.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/domain/Furniture_Domain_Architecture.md)
- [docs/architecture/Architecture_Baseline_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/Architecture_Baseline_v1.md)
- [docs/architecture/decisions/ADR-0012-canonical-output-contract.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0012-canonical-output-contract.md)
- [domain/construction_resolver.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/construction_resolver.py)
- [domain/furniture_construction_model.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/furniture_construction_model.py)
- [domain/wall_cabinet_engineering_model.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/wall_cabinet_engineering_model.py)
- [domain/wall_mount_rules.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/wall_mount_rules.py)
- [domain/wall_mount_capability.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/wall_mount_capability.py)
