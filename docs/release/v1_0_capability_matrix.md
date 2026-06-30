# V1.0 Capability Matrix

Release-control artifact for the current repository state.

Scope: documentation only. Evidence is taken from existing files and tests. Status is strict: a capability is only `COMPLETE` when the repository evidence supports a realistic factory workflow for V1.0.

Status values:

- `COMPLETE`: usable as-is for the documented V1.0 workflow.
- `NEEDS_IMPROVEMENT`: present, tested, or modeled, but not sufficient for a real factory workflow without manual interpretation or missing bridges.
- `CRITICAL_GAP`: absent from the V1.0 product path, unsafe to rely on, or not factory-executable.

Priority values:

- `P0`: blocks factory-ready V1.0.
- `P1`: required for controlled release after the blocking path exists.
- `P2`: important hardening or expansion.

## 1. Engineering Accuracy

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Base cabinet specification validation | `domain/base_cabinet_product_workflow.py` calls `validate_base_cabinet_specification`; `tests/domain/test_base_cabinet_product_workflow_contract.py` asserts validation is used and diagnostics are returned. | NEEDS_IMPROVEMENT | Validation is wired, but factory-level acceptance remains separate from a full production gate. | Reduces invalid designs but does not independently certify production readiness. | P1 |
| Static panel engineering model for base cabinet carcass | `domain/base_cabinet_engineering_model.py` creates side, top, bottom, back, and shelf placements with dimensions and materials. | NEEDS_IMPROVEMENT | Door, drawer, divider, and section-specific resolved components are not produced by the base builder in this file. | Core carcass data exists, but front systems can be missing from the factory package. | P0 |
| Back panel strategy and groove metadata | `domain/base_cabinet_engineering_model.py` maps installation mode/strategy and groove dimensions; `manufacturing/extractor.py` can append a groove operation for back panels. | NEEDS_IMPROVEMENT | Needs verified end-to-end factory output for back-panel machining across supported strategies. | Back panel can be represented, but machining confidence depends on runtime extraction coverage. | P1 |
| Project engineering readiness signals | `project_engineering/` contains operational clearance, collision, alignment, accessibility, reveal, and structural consistency reports/rules; `tests/project_engineering/` covers several of these contracts. | NEEDS_IMPROVEMENT | Needs a single release gate that combines these signals into product readiness for the base cabinet workflow. | Engineering risks can be detected, but factory operators need one authoritative go/no-go result. | P1 |

## 2. Door System

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Door layout and hinge-side modeling | `domain/layout_engine.py`, `domain/front_layout.py`, and `scene_graph/metadata.py` contain door width, position, door type, and hinge-side concepts. | NEEDS_IMPROVEMENT | Promote resolved door geometry into the V1.0 base cabinet engineering/product path consistently. | Door information exists in parts of the system, but release output may not include real door production data. | P0 |
| Door panels in base cabinet engineering model | `domain/base_cabinet_engineering_model.py` defines `EngineeringDoorPlacement` but returns `doors=()` in `BaseCabinetEngineeringModelBuilder.build`. | CRITICAL_GAP | Build and validate door placements from the base cabinet specification into the engineering model and scene graph. | A two-door V1.0 base cabinet cannot be treated as factory-ready if the canonical model omits doors. | P0 |
| Hinge CNC/drilling export support | `exports/cnc_exporter.py` exports drilling map rows; `tests/test_cnc_export_hinge.py` verifies 35 mm and 2.5 mm hinge drilling rows, face, and depth. | NEEDS_IMPROVEMENT | Connect hinge drilling to the V1.0 base cabinet product path and produce machine-specific or clearly accepted shop output. | Hinge machining can be represented, but a real shop still needs reliable product-path generation and machine handoff. | P0 |
| Door operational clearance | `project_engineering/door_operational_clearance_requirement.py`, `simple_door_swing_motion_envelope_extractor.py`, and related tests cover clearance/motion facts. | NEEDS_IMPROVEMENT | Integrate clearance failures into the V1.0 release package decision. | Reduces collision risk, but disconnected findings can be missed before production. | P1 |

## 3. Drawer System

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Drawer box and face data structures | `domain/base_cabinet_engineering_model.py` defines `EngineeringDrawerBox` and `EngineeringDrawerFace`. | NEEDS_IMPROVEMENT | Ensure the canonical V1.0 base builder emits drawer systems when specified. | Data structures alone do not create a manufacturable drawer package. | P1 |
| Drawer projection bridge from resolved geometry | `tests/domain/test_engineering_drawer_box_projection_contract.py` and `tests/domain/test_engineering_drawer_face_projection_contract.py` cover transitional projection into engineering model and scene graph. | NEEDS_IMPROVEMENT | Replace transitional bridge dependency with a stable product-path contract and release gate. | Drawer geometry can be projected, but the path is transitional and not enough for factory release control. | P1 |
| Drawer slide drilling export | `tests/test_cnc_export.py` verifies drawer slide drilling rows in the neutral drilling map. | NEEDS_IMPROVEMENT | Connect drawer slides to product package, hardware BOM, and assembly sequence for release. | Drill data may exist, but slide purchasing and installation remain incomplete as a unified workflow. | P1 |
| Drawer validation/intelligence reports | `manufacturing/drawer_validation_report.py`, `drawer_intelligence_report.py`, and related tests establish report contracts. | NEEDS_IMPROVEMENT | Convert reports into actionable release blockers and product package outputs. | Useful diagnostics exist, but not enough to run production without interpretation. | P1 |

## 4. Hardware

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Hardware catalog loading | `domain/hardware_catalog_loader.py`, `domain/hardware_library.py`, and `data/hardware/drawer_slides.json` show catalog and SKU concepts. | NEEDS_IMPROVEMENT | Expand catalog coverage and enforce SKU resolution for every required V1.0 hardware item. | Hardware can be modeled, but purchasing completeness is not guaranteed. | P1 |
| Hardware placement compilation into machining operations | `domain/manufacturing_compiler.py` maps hardware placements through hardware specs into host/target holes. | NEEDS_IMPROVEMENT | Ensure every V1.0 hardware placement is generated from canonical product data. | CNC marks can be produced, but missing placements cause silent factory omissions. | P0 |
| Hardware report | `exports/hardware_report.py` counts minifix, dowel, hinge, confirmat, shelf pin, drawer slide, and handles from assembly/project placements. | NEEDS_IMPROVEMENT | Promote to release package output and reconcile counts with hardware BOM/cost reports. | Operators and purchasing may receive inconsistent or incomplete hardware quantities. | P1 |
| Hardware BOM | `manufacturing/hardware_bom_builder.py`, `manufacturing/hardware_usage_builder.py`, and `docs/architecture/BaseCabinet_BOM_Output_Audit.md` show hardware BOM exists but is hardware-only. | NEEDS_IMPROVEMENT | Add an audited bridge from base cabinet outputs to hardware usage/BOM, without calling it a product BOM. | Hardware purchasing support exists downstream but is not yet a V1.0 base output. | P1 |

## 5. Manufacturing Outputs

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Manufacturing runtime package | `manufacturing/manufacturing_runtime_pipeline_builder.py` extracts panel specs, machining operations, edge operations, and builds a package. | NEEDS_IMPROVEMENT | Populate materials and guarantee all required V1.0 panels/hardware operations enter the package. | Package exists, but incomplete inputs can make readiness false or misleading. | P0 |
| Production package reports | `manufacturing/manufacturing_production_package_builder.py` builds cutlist, edge, machining, summary, and release validation reports. | NEEDS_IMPROVEMENT | Include validation summary and connect warnings to a release-control decision. | Good reporting structure, but not yet a complete factory release artifact. | P1 |
| Release readiness validator | `manufacturing/manufacturing_release_validator.py`, `manufacturing/manufacturing_warnings_analyzer.py`, and `tests/test_project_release_end_to_end_contract.py` show warning-based readiness. | NEEDS_IMPROVEMENT | Replace generic missing-data warnings with capability-specific blocking checks for V1.0. | Prevents obviously empty packages but does not certify production completeness. | P0 |

## 6. CNC Outputs

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Neutral drilling map CSV | `exports/cnc_exporter.py` writes `Panel_ID`, `Role`, `Face`, `X`, `Y`, `Diameter`, `Depth`, `Axis`, and `Is_Through`; CNC tests cover minifix, hinge, drawer slide, handle, and axis fields. | NEEDS_IMPROVEMENT | Promote export into production package and define shop-accepted format/version. | Useful drill map exists, but it is not a controlled V1.0 deliverable. | P0 |
| Machine-ready CNC files | Repository evidence shows neutral CSV and operation models; `manufacturing/operation_realizer.py` and related operation requirement files mention `gcode`, but no exporter proves machine-ready programs. | CRITICAL_GAP | Produce verified machine-ready CNC output or explicitly define the accepted CAM handoff contract. | Factory cannot run CNC directly from the current release package. | P0 |
| CNC operation extraction | `manufacturing/extractor.py` merges node machining ops with generated panel operations and back-panel grooves. | NEEDS_IMPROVEMENT | Add coverage that every V1.0 required operation survives extraction into the release package. | Missing operation extraction creates scrap or manual rework risk. | P0 |

## 7. BOM / Cut List

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Base cabinet cut list entry | `domain/base_cabinet_cutlist_entry.py`, `domain/base_cabinet_manufacturing_outputs_entry.py`, and `tests/domain/test_base_cabinet_manufacturing_outputs_entry_contract.py` show cut list generation from the manufacturing package. | NEEDS_IMPROVEMENT | Verify cut list includes all V1.0 panels including doors, drawer parts when present, backs, shelves, and edge deductions. | Cut list can be generated, but completeness depends on upstream model coverage. | P0 |
| CSV BOM/cut list export | `exports/bom_engine.py` and `exports/csv_exporter.py` write CSV-style shop outputs. | NEEDS_IMPROVEMENT | Connect exports to V1.0 product workflow and define one canonical cut list/BOM output. | Shop data exists but can be fragmented across exporters. | P1 |
| Product-level BOM | `docs/architecture/BaseCabinet_BOM_Output_Audit.md` concludes the reusable path is hardware-only and not a product-level BOM for base cabinet outputs. | CRITICAL_GAP | Add product BOM contract covering panels, hardware, edging, and consumables. | Purchasing and production cannot rely on a complete BOM. | P0 |

## 8. Assembly Instructions

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| HTML assembly manual exporter | `exports/assembly_exporter.py` creates part labels, drilling/marking tables, and assembly steps from scene graph plus joinery graph. | NEEDS_IMPROVEMENT | Connect exporter to V1.0 production package and ensure generated steps match all required hardware/panels. | Manual can be produced, but release package does not guarantee it is complete. | P1 |
| Assembly graph primitives | `assembly/assembly_graph.py`, `assembly/assembly_graph_builder.py`, and `assembly/joint_rules.py` support joinery/sequence concepts. | NEEDS_IMPROVEMENT | Validate sequence quality and dependency ordering for the V1.0 base cabinet. | Assembly sequence may require shop interpretation. | P1 |
| Factory-ready assembly instructions | No test proves a V1.0 production package contains final assembly instructions. | CRITICAL_GAP | Add production-package assembly instruction artifact and acceptance tests. | Operators lack controlled assembly guidance. | P0 |

## 9. Cost Intelligence

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Manufacturing cost pipeline | `cost_intelligence/manufacturing_cost_pipeline_builder.py` builds metrics, context, insights, risk, cost report, and summary. | NEEDS_IMPROVEMENT | Feed complete product BOM, hardware cost, labor, waste, CNC, and assembly costs from one release package. | Cost estimate exists but can be under-scoped if upstream package is incomplete. | P1 |
| Pricing catalog | `data/pricing/default_pricing_catalog.json` and pricing catalog tests support configurable costs. | NEEDS_IMPROVEMENT | Ensure catalog values are complete for all V1.0 materials, hardware, processes, and currency assumptions. | Missing catalog coverage causes inaccurate pricing. | P1 |
| Waste/offcut intelligence | `cost_intelligence/offcut_*`, `waste_*`, and tests cover waste/offcut reports and calculators. | NEEDS_IMPROVEMENT | Connect real nesting/cut list data from V1.0 package into the commercial output. | Waste risk can be modeled, but quote accuracy depends on integration. | P2 |

## 10. Quotation / Commercial Outputs

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Manufacturing commercial pipeline | `cost_intelligence/manufacturing_commercial_pipeline_builder.py` builds quotation input, quotation report, profitability report, and quotation intelligence. | NEEDS_IMPROVEMENT | Ensure quote is based on complete production package and release readiness status. | Quote may be generated from incomplete manufacturing data. | P1 |
| Quotation document | `cost_intelligence/quotation_document_builder.py`, `cost_intelligence/quotation_document.py`, and `exports/quotation_document_export.py` support a text quotation document. | NEEDS_IMPROVEMENT | Add controlled customer-facing export format and complete terms/line breakdown. | Sales output exists, but may not meet commercial release expectations. | P2 |
| Product workflow commercial bridge | `domain/base_cabinet_product_workflow.py` builds commercial result and quotation document when cost bridge exists; contract tests assert bridge calls. | NEEDS_IMPROVEMENT | Pass user-provided quotation metadata correctly and block quote release when factory readiness is blocked. | Commercial output can be produced before production confidence is sufficient. | P1 |

## 11. Factory Decisions

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Factory decision reports/builders | `cost_intelligence/factory_decision_builder.py`, `furniture_project_factory_decision_builder.py`, and related tests exist. | NEEDS_IMPROVEMENT | Use complete V1.0 production package and readiness findings as mandatory decision inputs. | Decision intelligence exists but depends on input quality. | P1 |
| Blocked readiness translation | `tests/test_project_release_end_to_end_contract.py` verifies blocked readiness becomes blocked factory decision. | NEEDS_IMPROVEMENT | Add non-mocked end-to-end test using actual V1.0 base cabinet outputs. | Concept is correct, but actual release data path needs proof. | P1 |
| Factory capacity/resource/time intelligence | `manufacturing/factory_*`, `data/factory/factory_time_catalog.json`, and `data/factory/factory_resource_catalog.json` show capacity and resource models. | NEEDS_IMPROVEMENT | Connect capacity decisions to release package quantities and actual shop calendars. | Useful estimates exist, but factory planning remains advisory. | P2 |

## 12. Production Package

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Manufacturing production package dataclass | `manufacturing/manufacturing_production_package.py` has cutlist, edge, machining, summary, validation summary, release flag, and warnings; tests lock the contract. | NEEDS_IMPROVEMENT | Fill all fields consistently from the V1.0 workflow, especially validation summary. | Package shape exists, but content completeness is not guaranteed. | P0 |
| Base cabinet product workflow aggregation | `domain/base_cabinet_product_workflow.py` returns engineering, validation, manufacturing outputs, cost, commercial, quotation document, metadata, and diagnostics. | NEEDS_IMPROVEMENT | Include controlled production package artifact and block release on critical gaps. | Good aggregation point, but not yet a full release package. | P0 |
| Factory-executable production package | No inspected file proves one artifact contains cut list, CNC, BOM, hardware, assembly instructions, readiness, cost, and quote for V1.0. | CRITICAL_GAP | Create a release package contract and tests using existing builders. | Factory must assemble outputs manually, increasing error and omission risk. | P0 |

## 13. UX / Product Readiness

| Capability | Current evidence from repository | Status | Missing work | Factory impact | Priority |
|---|---|---|---|---|---|
| Application service entry points | `application/engineering_application_service.py`, `manufacturing_application_service.py`, `project_application_service.py`, and `tests/application/test_application_services_contract.py` show service-layer access to real components. | NEEDS_IMPROVEMENT | Expose a single V1.0 product action that returns release-ready status and artifacts. | Users can call services, but production readiness is not presented as one workflow. | P1 |
| Product use case documentation | `docs/product/Cabinet_Manufacturing_Capability_V1.md` defines the V1 scenario and expected outputs. | NEEDS_IMPROVEMENT | Align implementation evidence with every required output in the document. | Product promise exceeds confirmed factory-executable capability. | P0 |
| FreeCAD workbench commands | `commands/workbench_commands.py`, `InitGui.py`, and `tests/test_workbench_commands_legacy_contract.py` indicate workbench integration exists. | NEEDS_IMPROVEMENT | Ensure UI surfaces release blockers and generated artifacts without manual inspection of internals. | Factory-facing users may not know when outputs are incomplete. | P1 |

## Top 5 Critical Gaps

1. Door panels are absent from the canonical base cabinet engineering model (`doors=()`), while V1.0 requires a two-door base cabinet.
2. No machine-ready CNC export is proven; current CNC evidence is neutral drilling-map CSV, not executable machine programs.
3. No product-level BOM exists; current audited BOM capability is hardware-only or fragmented.
4. No factory-ready assembly instruction artifact is proven inside the V1.0 production package.
5. No single factory-executable production package contains all required release outputs and release blockers.

## Top 5 Next Implementation Sprints

1. Sprint P0: Promote doors into the canonical base cabinet engineering/product path, including scene graph, cut list, hardware placement, and validation.
2. Sprint P0: Define and test the V1.0 production package contract as the single release artifact containing cut list, machining, edge, hardware, BOM, assembly, readiness, cost, and quote references.
3. Sprint P0: Add product-level BOM output using existing cut list, hardware BOM, edge, material, and pricing data without duplicating engines.
4. Sprint P0: Convert neutral CNC drilling output into a controlled factory handoff: either accepted CAM-ready CSV contract or machine-ready exporter with tests.
5. Sprint P1: Add factory-ready assembly instructions to the production package and validate sequence/part/hardware completeness for the V1.0 base cabinet.
