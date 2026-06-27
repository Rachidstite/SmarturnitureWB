# CabinetParams Mapping Audit

This audit reviews the field mapping performed by `BaseCabinetSpecificationAdapter` against the actual `CabinetParams` contract and its current use sites.

## Evidence Reviewed

- `shared/contracts.py`
- `engine/cabinet.py`
- `engine/cabinet_builder.py`
- `engine/geometry_engine.py`
- `domain/rules_engine.py`
- `domain/base_cabinet_specification_adapter.py`

## Findings Table

| Adapter Field | CabinetParams Field | Evidence | Status |
| --- | --- | --- | --- |
| `width_mm` | `width` | `CabinetParams.width` is the geometry width consumed by `engine.geometry_engine` and `engine.cabinet_builder`. Direct mapping from the specification width is consistent with current use. | VERIFIED |
| `height_mm` | `height` | `CabinetParams.height` is the geometry height consumed by `engine.geometry_engine` and `engine.cabinet_builder`. Direct mapping from the specification height is consistent with current use. | VERIFIED |
| `depth_mm` | `depth` | `CabinetParams.depth` is the cabinet depth consumed by `engine.geometry_engine` and `engine.cabinet_builder`. Direct mapping from the specification depth is consistent with current use. | VERIFIED |
| `door_count` | `sec_count` | `sec_count` drives cabinet section count in `engine.geometry_engine`, not door count. The current adapter uses `door_count` as a proxy for section count, but the codebase does not establish that these concepts are equivalent. | INCORRECT |
| `edge_banding_required` | `hw_mode` | `hw_mode` is consumed in `engine.cabinet_builder` to gate carcass joinery behavior. It is not an edge banding flag. The semantic intent does not match the field purpose. | INCORRECT |
| `has_back_panel` | `back_thickness` | `engine.geometry_engine` and `engine.cabinet_builder` use `back_thickness` as a material thickness parameter. Mapping presence of a back panel to a nonzero thickness is a reasonable representation for current engine consumption. | VERIFIED |
| `toe_kick_required` | `metadata` | `CabinetParams` has no dedicated toe kick field. Preserving this in adapter metadata avoids loss of product information without changing APIs. | VERIFIED |
| `hinge_family` | `hinge_sku` | `domain.rules_engine.build_rule_context_from_params` reads `hinge_sku` and maps it into the hardware profile. This is evidence-based and semantically aligned. | VERIFIED |
| `drawer_family` | `handle_sku` | `CabinetParams.handle_sku` is an existing handle SKU field. Mapping `drawer_family` into `handle_sku` is not semantically supported by the current contract and is therefore not evidence-based. | INCORRECT |
| `shelf_count` | `metadata` | `CabinetParams` has no shelf count field. Preserving this in adapter metadata avoids loss of product information without changing APIs. | VERIFIED |
| `drawer_depth` | `drawer_depth` | `CabinetParams.drawer_depth` is consumed by `engine.geometry_engine` and `engine.cabinet_builder` for drawer geometry calculations. The adapter sets a fixed constant rather than deriving it from specification data, so the mapping is not evidence-based from the specification contract alone. | QUESTIONABLE |
| `drawer_bottom_thickness` | `drawer_bottom_thickness` | `CabinetParams.drawer_bottom_thickness` is consumed by `engine.cabinet_builder`. The adapter sets a fixed constant rather than deriving it from specification data, so the mapping is not evidence-based from the specification contract alone. | QUESTIONABLE |
| `cnc_mode` | `cnc_mode` | `CabinetParams.cnc_mode` is an execution-oriented flag used in `engine.cabinet_builder`. The adapter forces it to `False`, which avoids execution behavior but does not arise from the product specification. | QUESTIONABLE |
| `slide_sku` | `slide_sku` | `domain.rules_engine.build_rule_context_from_params` consumes `slide_sku`, but the adapter assigns a fixed default unrelated to the specification contract. It is a placeholder rather than a specification-derived mapping. | QUESTIONABLE |

## Summary

Not all mappings are verified.

Verified mappings:

- `width_mm` -> `width`
- `height_mm` -> `height`
- `depth_mm` -> `depth`
- `has_back_panel` -> `back_thickness`
- `toe_kick_required` -> metadata
- `hinge_family` -> `hinge_sku`
- `shelf_count` -> metadata

Questionable mappings:

- `drawer_depth` -> `drawer_depth`
- `drawer_bottom_thickness` -> `drawer_bottom_thickness`
- `cnc_mode` -> `cnc_mode`
- `slide_sku` -> `slide_sku`

Incorrect mappings:

- `door_count` -> `sec_count`
- `edge_banding_required` -> `hw_mode`
- `drawer_family` -> `handle_sku`

## Notes

- The adapter preserves unmapped product configuration values in metadata to avoid API changes.
- The audit did not change any runtime behavior, builder behavior, or public APIs.
