# Scene Graph Engineering-Manufacturing Boundary

## Purpose

This document confirms the integration boundary between Engineering and Manufacturing for the Base Cabinet product flow.

The inspected code shows that the Scene Graph is the shared handoff artifact between the engineering pipeline and the manufacturing pipeline. Engineering creates it, and manufacturing reads it.

## Files Inspected

- `engine/cabinet_builder.py`
- `engine/cabinet.py`
- `scene_graph/`
- `manufacturing/extractor.py`
- `manufacturing/manufacturing_runtime_pipeline_builder.py`
- `services/manufacturing_validation_service.py`
- `manufacturing/furniture_project_manufacturing_package_builder.py`
- `tests/manufacturing/test_manufacturing_runtime_pipeline_builder.py`
- `tests/manufacturing/test_furniture_project_manufacturing_package_builder.py`
- `tests/manufacturing/test_manufacturing_validation_service.py`
- `tests/manufacturing/test_engineering_component_inventory_builder.py`
- `tests/manufacturing/test_drawer_slide_runtime_package_contract.py`
- `tests/manufacturing/test_shelf_pin_runtime_package_contract.py`
- `tests/manufacturing/test_confirmat_runtime_package_contract.py`
- `tests/manufacturing/test_back_panel_groove_emission_contract.py`
- `tests/manufacturing/test_hardware_semantic_identity_runtime_contract.py`

## Findings

### 1. What creates the Scene Graph?

`engine.cabinet_builder.CabinetBuilder` creates the Scene Graph.

Observed flow:

- `CabinetBuilder.build(cabinet)`
- resolves geometry
- creates `SceneGraphBuilder(cabinet, self.mat)`
- stores the result in `self.scene_graph`

This is the engineering-side creation point.

### 2. What consumes the Scene Graph?

The following existing components consume the Scene Graph:

- `manufacturing.manufacturing_runtime_pipeline_builder.ManufacturingRuntimePipelineBuilder`
- `services.manufacturing_validation_service.ManufacturingValidationService`
- `manufacturing.furniture_project_manufacturing_package_builder.FurnitureProjectManufacturingPackageBuilder`
- downstream manufacturing extraction and packaging components

The runtime pipeline reads the Scene Graph through `ManufacturingExtractor.extract(scene_graph)`.

### 3. Does ManufacturingRuntimePipelineBuilder depend on Scene Graph?

Yes.

`ManufacturingRuntimePipelineBuilder.build(scene_graph)` takes a `scene_graph` as its direct input and passes it to `ManufacturingExtractor.extract(scene_graph)`.

It then derives:

- `panel_specs`
- `manufacturing_package`
- `manufacturing_production_package`

### 4. Does ManufacturingValidationService depend on Scene Graph?

Yes.

`ManufacturingValidationService.validate(scene_graph)` takes a `scene_graph` as input, extracts panel specs, and runs validation over those extracted specs.

### 5. Should Scene Graph be treated as the integration boundary?

Yes.

The inspected code supports Scene Graph as the official integration boundary between Engineering and Manufacturing.

Reasoning:

- Engineering constructs the Scene Graph.
- Manufacturing reads the Scene Graph.
- Manufacturing runtime derives packages from the Scene Graph.
- Validation also reads the Scene Graph.
- No manufacturing component needs to recreate engineering geometry from product specification directly.

## Boundary Rules

- Engineering owns Scene Graph creation.
- Manufacturing reads Scene Graph.
- Manufacturing must not mutate product geometry.
- Product Specification must not bypass Engineering to feed Manufacturing directly.
- Cut List must come from `ManufacturingPackage` derived from Scene Graph.

## Decision

**APPROVED_BOUNDARY**

The Scene Graph is the correct integration boundary for the current Base Cabinet flow.

## Summary

For Base Cabinet:

- product specification is resolved by Engineering
- Engineering produces the Scene Graph
- Manufacturing consumes the Scene Graph
- Manufacturing outputs are derived from the resulting ManufacturingPackage

This boundary is already reflected in the existing code and tests.

