# Base Cabinet Product Semantics Audit

This document audits each field in `BaseCabinetSpecification` and defines the intended domain ownership, current consumer, and adapter treatment before any adapter changes are made.

## Sources Inspected

- [domain/base_cabinet_specification.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_specification.py)
- [domain/base_cabinet_specification_adapter.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_specification_adapter.py)
- [shared/contracts.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/shared/contracts.py)
- [domain/rules_engine.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/rules_engine.py)
- [engine/cabinet.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/engine/cabinet.py)
- [engine/cabinet_builder.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/engine/cabinet_builder.py)
- [engine/geometry_engine.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/engine/geometry_engine.py)
- [manufacturing/](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing)
- [cost_intelligence/](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/cost_intelligence)

## Field Audit Table

| Field | Meaning | Domain Owner | Correct Consumer | Current Adapter Mapping | Status | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| `width_mm` | Canonical cabinet width in millimeters | Engineering / Product Specification | `CabinetParams.width` and any geometry consumers of cabinet width | Mapped directly to `CabinetParams.width` | DIRECT_ENGINEERING_INPUT | Keep as direct mapping |
| `height_mm` | Canonical cabinet height in millimeters | Engineering / Product Specification | `CabinetParams.height` and any geometry consumers of cabinet height | Mapped directly to `CabinetParams.height` | DIRECT_ENGINEERING_INPUT | Keep as direct mapping |
| `depth_mm` | Canonical cabinet depth in millimeters | Engineering / Product Specification | `CabinetParams.depth` and any geometry consumers of cabinet depth | Mapped directly to `CabinetParams.depth` | DIRECT_ENGINEERING_INPUT | Keep as direct mapping |
| `door_count` | Product structure definition for number of doors | Product Structure / Engineering | Future product structure resolver or section/door configuration layer | Mapped to `CabinetParams.sec_count` | PRODUCT_STRUCTURE_INPUT | Remove direct mapping; keep in metadata until a dedicated product-structure consumer exists |
| `shelf_count` | Product structure definition for internal shelves | Product Structure / Engineering | Future product structure resolver or section/shelf configuration layer | Preserved in adapter metadata | PRODUCT_STRUCTURE_INPUT | Keep in metadata until a dedicated consumer exists |
| `has_back_panel` | Whether the cabinet includes a back panel | Product Structure / Manufacturing Intent | A future structure resolver or back-panel intent consumer | Mapped to `CabinetParams.back_thickness` via zero/non-zero thickness | PRODUCT_STRUCTURE_INPUT | Treat as intent, not thickness; keep in metadata until a dedicated back-panel consumer exists |
| `edge_banding_required` | Whether edge banding is required | Manufacturing Intent / Manufacturing Knowledge | Manufacturing knowledge and edge-finishing consumers | Mapped to `CabinetParams.hw_mode` | MANUFACTURING_INTENT_INPUT | Remove direct mapping; preserve in metadata until a proper edge-band consumer exists |
| `toe_kick_required` | Whether a toe kick is required | Product Structure / Engineering | Future product structure resolver | Preserved in adapter metadata | PRODUCT_STRUCTURE_INPUT | Keep in metadata until a dedicated toe-kick consumer exists |
| `hinge_family` | Selected hinge family / hardware intent | Hardware Selection / Manufacturing Intent | `CabinetParams.hinge_sku`, then `domain.rules_engine.build_rule_context_from_params` | Mapped directly to `CabinetParams.hinge_sku` | HARDWARE_SELECTION_INPUT | Keep as direct mapping; current consumer is evidence-based |
| `drawer_family` | Selected drawer family / product intent | Hardware Selection / Product Configuration | No clear current consumer in `CabinetParams` or rule context | Mapped to `CabinetParams.handle_sku` | UNSUPPORTED_BY_CURRENT_ADAPTER | Remove or correct mapping; keep in metadata until a drawer-family consumer exists |

## Answers to the Audit Questions

### 1. Which fields may safely map to `CabinetParams` now?

Based on the current codebase, only these fields have direct, evidence-based consumers:

- `width_mm` -> `CabinetParams.width`
- `height_mm` -> `CabinetParams.height`
- `depth_mm` -> `CabinetParams.depth`
- `hinge_family` -> `CabinetParams.hinge_sku`

These mappings are semantically aligned with the current consumers in the geometry and rules layers.

### 2. Which fields must stay in metadata until a proper consumer exists?

These fields should remain in adapter metadata because the current `CabinetParams` contract does not provide a correct semantic destination:

- `shelf_count`
- `toe_kick_required`

`has_back_panel` also belongs here if the goal is to preserve product intent rather than encode it as thickness.

### 3. Which fields require future dedicated resolvers/builders?

The following fields represent product structure or manufacturing intent that should be consumed by dedicated resolvers/builders rather than forced into the current `CabinetParams` shape:

- `door_count`
- `shelf_count`
- `has_back_panel`
- `edge_banding_required`
- `toe_kick_required`
- `drawer_family`

### 4. Which existing adapter mappings should be removed or corrected?

The current adapter contains mappings that are not semantically correct:

- `door_count` -> `sec_count` should be removed or replaced with a dedicated structure resolver
- `edge_banding_required` -> `hw_mode` should be removed
- `has_back_panel` -> `back_thickness` should be revised; thickness is a material parameter, not a back-panel presence flag
- `drawer_family` -> `handle_sku` should be removed or replaced with a proper drawer-family consumer
- `drawer_depth` and `drawer_bottom_thickness` are hard-coded in the adapter and do not come from `BaseCabinetSpecification`; they should not be treated as specification mappings
- `cnc_mode` is execution-oriented and should not be driven by the base cabinet specification adapter

## Status Summary

- `DIRECT_ENGINEERING_INPUT`: `width_mm`, `height_mm`, `depth_mm`
- `PRODUCT_STRUCTURE_INPUT`: `door_count`, `shelf_count`, `has_back_panel`, `toe_kick_required`
- `MANUFACTURING_INTENT_INPUT`: `edge_banding_required`
- `HARDWARE_SELECTION_INPUT`: `hinge_family`
- `UNSUPPORTED_BY_CURRENT_ADAPTER`: `drawer_family`

## Conclusion

The current adapter should not be treated as semantically final.

Only the engineering dimensions and hinge-family selection are currently justified as direct adapter mappings. The remaining product-structure and manufacturing-intent fields should stay in metadata or be routed through future dedicated resolvers/builders so the adapter does not overload `CabinetParams` with incorrect meaning.
