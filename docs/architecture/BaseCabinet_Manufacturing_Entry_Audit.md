# Base Cabinet Manufacturing Entry Audit

## Purpose

This audit identifies the smallest existing manufacturing path that can consume a cabinet-like engineering result and produce manufacturing outputs without introducing a new engine, builder, runtime layer, or execution model.

The current repository already has a usable bridge:

- `BaseCabinetSpecification` -> `BaseCabinetSpecificationAdapter`
- engineering cabinet creation via `build_base_cabinet_engineering_cabinet()`
- existing scene-graph-based manufacturing pipeline

The goal of this audit is to document the safest reuse path and the boundaries that must stay intact.

## Files Inspected

- `domain/base_cabinet_specification.py`
- `domain/base_cabinet_specification_adapter.py`
- `domain/base_cabinet_specification_validation.py`
- `domain/base_cabinet_engineering_entry.py`
- `domain/constraint_engine.py`
- `domain/rules_engine.py`
- `engine/cabinet.py`
- `engine/cabinet_builder.py`
- `manufacturing/extractor.py`
- `manufacturing/manufacturing_runtime_pipeline_builder.py`
- `manufacturing/manufacturing_package_builder.py`
- `manufacturing/manufacturing_production_package_builder.py`
- `manufacturing/manufacturing_cutlist_builder.py`
- `manufacturing/manufacturing_edge_builder.py`
- `manufacturing/manufacturing_machining_builder.py`
- `manufacturing/manufacturing_summary_builder.py`
- `manufacturing/hardware_usage_builder.py`
- `manufacturing/hardware_bom_builder.py`
- `manufacturing/manufacturing_validation_summary_builder.py`
- `manufacturing/manufacturing_model_builder.py`
- `manufacturing/engineering_component_inventory_builder.py`
- `manufacturing/furniture_project_manufacturing_package_builder.py`
- `manufacturing/manufacturing_project_intelligence_pipeline_builder.py`
- `services/manufacturing_validation_service.py`
- `tests/domain/test_base_cabinet_specification_contract.py`
- `tests/domain/test_base_cabinet_scenario_contract.py`
- `tests/domain/test_base_cabinet_specification_adapter_contract.py`
- `tests/domain/test_base_cabinet_specification_validation_contract.py`
- `tests/domain/test_base_cabinet_engineering_entry_contract.py`

## Questions and Findings

### 1. What existing manufacturing component is closest to consuming an engineering cabinet?

The closest existing manufacturing component is:

- `manufacturing.manufacturing_runtime_pipeline_builder.ManufacturingRuntimePipelineBuilder`

It consumes a `scene_graph` and produces:

- `ManufacturingPackage`
- `ManufacturingProductionPackage`

The closest cabinet-like project aggregator is:

- `manufacturing.furniture_project_manufacturing_package_builder.FurnitureProjectManufacturingPackageBuilder`

It consumes a `FurnitureProject`, iterates `cabinet.graph`, and aggregates the runtime pipeline output.

For validation-only use, the narrowest existing component is:

- `services.manufacturing_validation_service.ManufacturingValidationService`

It also consumes `scene_graph`.

### 2. What input does it expect?

The runtime manufacturing path expects a `scene_graph`.

The higher-level project aggregator expects a `FurnitureProject` whose cabinets expose `graph`.

That means the practical handoff is:

- `BaseCabinetSpecification` -> existing engineering cabinet entry -> `CabinetBuilder`-produced `scene_graph` -> manufacturing runtime pipeline

### 3. Can BaseCabinetSpecification -> Engineering Cabinet be adapted to that input without new engine?

Yes, with the existing engineering pipeline.

The current engineering entry already adapts the specification and reuses `CabinetBuilder`. `CabinetBuilder` already resolves geometry and produces `scene_graph`.

So no new manufacturing engine is needed.
What is still required is a narrow bridge from the engineering cabinet result to the manufacturing runtime input shape, namely the `scene_graph`.

### 4. Which manufacturing output should be first?

Recommended first output: `Cut List`

Reason:

- it is already produced from `ManufacturingPackage`
- it depends on the existing runtime pipeline only
- it does not require hardware-intent extraction to be correct
- it is less speculative than BOM or hardware list generation

Secondary note:

- `ManufacturingValidationSummary` is the safest validation gate
- `Hardware List` and `BOM` should come later, after the hardware-intent path is explicit and verified

### 5. What should be explicitly avoided?

Avoid:

- introducing a new manufacturing engine
- introducing a new builder for the manufacturing path
- treating `CabinetParams` as the product model
- forcing unsupported product semantics into engineering parameters
- making BOM or hardware-list generation depend on guessed metadata
- moving into runtime execution, scheduling, jobs, queues, workers, or machine assignment
- coupling manufacturing outputs to FreeCAD/UI behavior

## Decision

**APPROVED_REUSE_EXISTING_PATH**

The existing scene-graph-based manufacturing pipeline is reusable. The correct implementation boundary is to reuse the engineering cabinet build result and then hand its `scene_graph` into the existing manufacturing runtime path. No new engine is required.

## Boundary Summary

- Engineering creates the cabinet and scene graph.
- Manufacturing reads the scene graph.
- Validation can consume the scene graph directly.
- Cut list is the first safe manufacturing output.
- BOM and hardware list should remain downstream until the hardware extraction path is explicit.

