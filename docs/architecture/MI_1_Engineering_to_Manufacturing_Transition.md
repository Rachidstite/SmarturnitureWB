# MI-1 Engineering to Manufacturing Transition

## Problem Statement

Determine how Manufacturing Intelligence should consume Engineering Intelligence outputs in Phase 1.

The engineering side already produces five static Engineering Decisions:

- Front Alignment
- Static Door–Drawer Collision
- Front Accessibility Static Feasibility
- Reveal Validation
- Structural Consistency

The question is whether Manufacturing should consume `EngineeringModel`, Engineering Decisions, or both.

## Existing Evidence

### Engineering side

- `EngineeringApplicationService` returns a real cabinet with `construction_model`, `engineering_model`, and `scene_graph` attached. See [`application/engineering_application_service.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/engineering_application_service.py).
- `build_base_cabinet_engineering_cabinet()` builds the cabinet, attaches the engineering model, and then attaches the scene graph through `CabinetBuilder`. See [`domain/base_cabinet_engineering_entry.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_engineering_entry.py).
- Engineering decisions are implemented as `EngineeringModel -> Facts -> Rule -> Decision -> Report` capabilities in `project_engineering/`.

### Manufacturing side

- `ManufacturingApplicationService` calls `build_base_cabinet_manufacturing_outputs_entry(spec)` and returns manufacturing outputs. See [`application/manufacturing_application_service.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/manufacturing_application_service.py).
- `build_base_cabinet_manufacturing_outputs_entry()` builds the engineering cabinet, reads the scene graph from the cabinet, and passes that scene graph into `ManufacturingRuntimePipelineBuilder`. See [`domain/base_cabinet_manufacturing_outputs_entry.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_manufacturing_outputs_entry.py).
- `ManufacturingRuntimePipelineBuilder` consumes `scene_graph` and produces manufacturing package data from extracted panel specs and operations. See [`manufacturing/manufacturing_runtime_pipeline_builder.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_runtime_pipeline_builder.py).
- Manufacturing model builders and validation builders consume manufacturing package and manufacturing rule results, not engineering decision objects. See [`manufacturing/manufacturing_model_builder.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_model_builder.py), [`manufacturing/manufacturing_validation_builder.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_validation_builder.py), and [`manufacturing/manufacturing_validation_summary_builder.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_validation_summary_builder.py).
- The manufacturing layer already consumes `OperationalRuleResult`-style outputs in several readiness rules, showing a precedent for decision-like inputs. See [`manufacturing/door_hinge_engineering_readiness_rule.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/door_hinge_engineering_readiness_rule.py), [`manufacturing/minifix_validation_readiness_rule.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/minifix_validation_readiness_rule.py), and [`manufacturing/panel_material_readiness_rule.py`](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/panel_material_readiness_rule.py).

## Current Architecture

The current repository architecture is:

`CabinetProject -> EngineeringModel -> scene_graph -> Manufacturing runtime/package -> Manufacturing model -> Cost -> Commercial outputs`

At present, Manufacturing does **not** recompute the engineering decision capabilities from scratch.

Instead, Manufacturing reads the derived scene graph / manufacturing package layer and uses its own manufacturing validation and readiness rules.

## Transition Architecture

The clean boundary for MI-1 is:

`CabinetProject`
`-> EngineeringModel`
`-> Engineering Decisions`
`-> Manufacturing Model / Manufacturing Runtime Package`
`-> Manufacturing Decisions`
`-> Cost Model`
`-> Optimization`
`-> Commercial Outputs`

This should be interpreted as follows:

- Engineering owns the static decision logic for alignment, collision, accessibility, reveal, and structural plausibility.
- Manufacturing owns fabrication-oriented derivation from the engineered cabinet into panels, operations, packages, and manufacturing readiness signals.
- Manufacturing may consume Engineering Decision outputs as gates or preconditions, but it should not recompute those same engineering decisions.
- Manufacturing should continue to consume the derived manufacturing data path it already owns, rather than reading raw `EngineeringModel` for relationship logic.

## Ownership Matrix

### Engineering owns

- Static geometry and placement facts in `EngineeringModel`
- Relationship decisions
- Integrity decisions
- Engineering decision reports and violations
- Static plausibility checks before manufacturing

### Manufacturing owns

- Scene-graph-to-manufacturing extraction
- Panel specification and machining package generation
- Cut list generation
- Manufacturing readiness rules
- Manufacturing validation summary
- Manufacturing production package generation

### Shared boundary

- Engineering Decision results may be consumed by Manufacturing orchestration as gate inputs
- Manufacturing does not own the engineering decision algorithms
- Engineering does not own the manufacturing package generation algorithms

## Boundary Rules

The official boundary rules for Phase 1 are:

- Manufacturing must not recompute Front Alignment, Static Door–Drawer Collision, Front Accessibility, Reveal Validation, or Structural Consistency.
- Manufacturing must not introduce duplicate reasoning for geometry relationships already covered by Engineering Decisions.
- Manufacturing may consume Engineering Decision outputs as a pass/fail/review gate.
- Manufacturing may continue to consume scene graph or manufacturing-package data for fabrication extraction because that is a different concern from engineering decisions.
- EngineeringModel remains the source of truth for engineering intelligence, but Manufacturing is not required to re-read it directly when the existing manufacturing bridge already provides derived manufacturing data.

## Business Value

- Prevents duplicate reasoning across layers.
- Keeps engineering checks upstream and fabrication logic downstream.
- Preserves a single source of truth for static engineering decisions.
- Allows Manufacturing to focus on buildability, packaging, cut lists, and production metrics instead of re-solving engineering geometry.

## Architectural Impact

- The architecture becomes easier to reason about because Engineering and Manufacturing have different responsibilities.
- Engineering Decision outputs become reusable quality gates for downstream workflows.
- Manufacturing remains free to evolve its own readiness, validation, and production models without inheriting engineering rule logic.

## Technical Risk

- If Manufacturing begins recomputing alignment, collision, reveal, accessibility, or structural plausibility, the boundary will drift and duplicate logic will accumulate.
- If Engineering Decision outputs are treated as manufacturing truth rather than gates, the layers may become semantically coupled in the wrong direction.
- The existing architecture still depends on a scene graph bridge for manufacturing package generation, so the transition should preserve that bridge rather than forcing raw `EngineeringModel` reuse.
- A future risk is category drift if manufacturing readiness rules start to absorb engineering decision semantics.

## Maintenance Cost

- Lower than recomputing the same checks in both layers.
- Moderate only where bridging code has to pass Engineering Decision outputs into downstream orchestration.
- Without a clean boundary, maintenance cost grows quickly because each new manufacturing capability would duplicate engineering reasoning.

## ROI

- High.
- This boundary avoids repeated implementation of the five engineering decisions in downstream manufacturing code.
- It preserves a clean ownership line between static engineering intelligence and fabrication intelligence.
- It keeps the current system scalable as more manufacturing and cost capabilities are added.

## Recommendation

Adopt the boundary:

`EngineeringModel -> Engineering Decisions -> Manufacturing Model / Runtime Package -> Manufacturing Decisions -> Cost -> Optimization`

Do **not** make Manufacturing recompute engineering relationship or integrity decisions.

Manufacturing should consume Engineering Decision outputs as gating inputs where helpful, but its primary data path should remain the derived manufacturing package / manufacturing runtime path that already exists.

## Final Classification

**APPROVED**

The repository supports a clean Engineering-to-Manufacturing boundary without duplicate reasoning, provided Manufacturing does not recompute the five Engineering Intelligence decisions.
