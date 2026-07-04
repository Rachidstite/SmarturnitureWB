# ADR-0015
Configurator Interaction Model

## Status

Accepted

## Context

ADR-0014 establishes the product boundary:

- Configurator is the primary user interface.
- Application Services are the only gateway from UI to business logic.
- FreeCAD is the engineering, geometry, and preview backend.
- Manufacturing, cost, commercial, and release remain backend services.
- UI must not duplicate backend logic.

The current repository evidence shows that the backend is already richer than the GUI:

- `ProductConfiguration` and `ProductFamily` exist.
- `ProjectApplicationService`, `EngineeringApplicationService`, and `ManufacturingApplicationService` exist.
- `FactoryReleasePackage`, `FactoryDecisionProjection`, `CommercialPackageReport`, and `QuotationDocumentV1` exist.
- The current GUI is still a narrow two-tab `QMainWindow`.

The missing decision is not a new engine. The missing decision is how the Configurator behaves as a product experience while staying inside the boundary defined by ADR-0014.

## Evidence

Repository evidence used for this decision:

- `ui/main_window.py`
  - narrow two-tab configurator shell
- `application/project_application_service.py`
  - current orchestration gateway for product workflow
- `application/engineering_application_service.py`
  - engineering gateway
- `application/manufacturing_application_service.py`
  - manufacturing gateway
- `domain/product_configuration.py`
  - canonical editable product input
- `domain/product_family.py`
  - canonical product family definition
- `manufacturing/factory_release_package.py`
  - release package boundary
- `manufacturing/factory_decision_projection.py`
  - read-only release review projection
- `manufacturing/manufacturing_decision.py`
  - manufacturing readiness decision object
- `manufacturing/manufacturing_production_package.py`
  - production evidence and release readiness flags
- `commercial_outputs/commercial_package_report.py`
  - passive commercial summary boundary
- `cost_intelligence/manufacturing_commercial_pipeline_builder.py`
  - existing commercial pipeline fed by manufacturing evidence
- `cost_intelligence/quotation_document.py`
  - customer-facing quotation artifact
- `docs/product/Decision_Projection_Contract.md`
  - release-review projection is read-only and must not recompute decisions
- `docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md`
  - commercial approval must precede production release

## Decision

The Configurator is the primary product experience layer and owns the user journey, transient UI state, visual organization, and presentation of backend evidence.

The Configurator does not own business truth. It must remain a client of application services and read-only backend projections.

The Configurator owns:

- user input flow
- UI state
- visual organization
- user decisions
- preview requests
- warning presentation
- workflow progression

The Configurator does not own:

- engineering calculation
- manufacturing generation
- cost calculation
- commercial pricing
- CNC generation
- release decision
- validation rules

## Product State Model

Configurator UI state is separate from backend truth, but state transitions must be backed by application service results.

| State | Meaning | Entry criteria | Owner / source of truth | Allowed user actions | Forbidden transitions |
|---|---|---|---|---|---|
| `Draft` | User is entering or editing project and product inputs. | A project context exists in the Configurator, but derived backend results are not yet authoritative. | Configurator transient state. | Edit customer/project context, choose family, edit parameters, request preview. | Cannot claim validated, released, or manufactured status. |
| `Configured` | A product configuration is materially defined. | Product family selected and a valid `ProductConfiguration` draft exists. | Configurator draft state backed by `ProductConfiguration`. | Edit configuration, request preview, request validation. | Cannot claim manufacturing readiness without backend results. |
| `Validated` | Engineering validation has produced a non-blocking result. | Application service returns engineering validation with no blocking issues for the current draft. | `ProjectApplicationService` / `EngineeringApplicationService` result. | Review warnings, proceed to manufacturing evidence request. | Cannot skip to release if downstream evidence is stale or missing. |
| `Manufacturing Ready` | Manufacturing evidence and readiness have been generated. | `ManufacturingApplicationService` returns production evidence and readiness is not blocked. | `ManufacturingDecision` plus `ManufacturingProductionPackage.release_ready`. | Review manufacturing evidence, review cost, review commercial output. | Cannot claim release approval without commercial review. |
| `Cost Reviewed` | Cost evidence has been refreshed and viewed. | Cost outputs are generated from the current manufacturing evidence. | Cost pipeline outputs reached through application workflow. | Review cost breakdown, revise draft inputs, proceed to commercial review. | Cannot treat cost as final if upstream configuration changed after the last refresh. |
| `Commercial Approved` | Quotation and commercial summary have been reviewed and accepted. | `CommercialPackageReport` and `QuotationDocumentV1` exist for the current manufacturing evidence and the user has accepted them. | Commercial output boundary plus Configurator approval state. | Approve or reject release request, revise commercial inputs if permitted. | Cannot claim factory release without release approval. |
| `Released` | The product has been formally approved for factory release. | Factory release decision is produced from current manufacturing and commercial evidence. | `FactoryReleasePackage` / `FactoryDecisionProjection` / release decision source. | Generate production documents, inspect release package, archive. | Cannot silently mutate upstream configuration without invalidating release. |
| `Manufactured` | Factory execution feedback confirms production completion. | External factory feedback or execution evidence marks the job complete. | Future factory execution feedback, not UI inference. | Review completion documents and final records. | Cannot be faked by the Configurator; it is a downstream fact only. |

UI may not fake state transitions. If the required application service result is absent, the UI must remain in the prior state and show stale or incomplete data.

## Interaction Flow

The official interaction flow is:

1. Select or create customer.
2. Create project.
3. Select product family.
4. Configure product dimensions and options.
5. Request preview.
6. Run engineering validation.
7. Generate manufacturing evidence.
8. Review manufacturing readiness.
9. Review cost.
10. Review commercial package and quotation.
11. Approve factory release.
12. Generate production documents.

| Step | UI responsibility | Application service used | Outputs consumed | Errors / warnings shown |
|---|---|---|---|---|
| 1. Customer | Capture customer context and associate it with the project. | `ProjectApplicationService` when persistence or orchestration is available; otherwise transient UI context only. | Customer/project draft context. | Missing customer context, incomplete project metadata. |
| 2. Project | Create or select the project workspace and keep it active. | `ProjectApplicationService`. | Project result, document name when a document is created. | Missing project context, stale project state. |
| 3. Product Family | Select the family and check whether it is supported. | `ProjectApplicationService` or `EngineeringApplicationService` via family routing. | `ProductFamily`, `ProductConfiguration`, routing result. | Unsupported family, catalog-only family, routing rejection. |
| 4. Configuration | Edit dimensions, sections, materials, and hardware intent. | No backend computation beyond draft synchronization; service calls may be debounced. | Local draft state and normalized parameter snapshot. | Invalid parameter combinations, incomplete draft inputs. |
| 5. Preview | Request preview from current draft and show only current geometry truth. | `EngineeringApplicationService` and backend preview path through FreeCAD/SceneGraph. | Cabinet geometry, scene graph, visible geometry plan. | Preview stale, preview unavailable, unsupported family preview gap. |
| 6. Validation | Request engineering validation and surface blocking issues. | `ProjectApplicationService` or `EngineeringApplicationService`. | Validation report and diagnostics. | Validation errors, warnings, unsupported family path. |
| 7. Manufacturing Evidence | Request manufacturing outputs from validated geometry. | `ManufacturingApplicationService`. | Manufacturing package, production package, release decision inputs. | Manufacturing blockers, missing evidence, stale upstream draft. |
| 8. Manufacturing Review | Present manufacturing readiness and evidence completeness. | `ManufacturingApplicationService`. | `ManufacturingDecision`, `ManufacturingProductionPackage`, `FactoryReleasePackage`. | Blocking manufacturing issues, missing CNC/assembly/hardware evidence. |
| 9. Cost | Refresh cost from current manufacturing evidence. | `ProjectApplicationService` via the full product workflow. | Cost summary, cost report, cost warnings. | Stale cost, missing upstream evidence, incomplete cost coverage. |
| 10. Commercial | Refresh quotation and commercial summary from current cost/manufacturing evidence. | `ProjectApplicationService` via the full product workflow. | `CommercialPackageReport`, `QuotationDocumentV1`. | Commercial warnings, stale quotation, unsupported family gap. |
| 11. Release | Approve or reject factory release using backend evidence only. | `ManufacturingApplicationService` and decision projection consumers. | Release package, release decision, blocker summary. | Release blockers, unresolved warnings, stale upstream evidence. |
| 12. Production Documents | Generate or display output documents for shop and customer use. | `ProjectApplicationService` and downstream exporters only. | Release package references, quotation document, production documents. | Missing document artifacts, stale outputs, incomplete handoff. |

## Service Call Rules

The Configurator may cache draft inputs, but it may not cache final truth.

Rules:

- On configuration draft change, the UI updates local state immediately and marks downstream outputs stale.
- On preview refresh, the UI requests backend geometry/preview outputs rather than recomputing them.
- On validation request, the UI calls application services and renders the returned validation result.
- On manufacturing review or release request, the UI calls `ManufacturingApplicationService`.
- On cost review request, the UI refreshes cost through the existing product workflow path and must not calculate cost locally.
- On quotation request, the UI uses the existing commercial path and must not format or price orders itself.
- On factory release approval, the UI consumes backend release evidence and must not infer approval from preview or cost alone.
- Any upstream change invalidates preview, manufacturing, cost, commercial, and release outputs below that point.
- The UI must show stale-output warnings whenever displayed data is older than the current draft.

## Preview Modes

Preview must use the existing SceneGraph / renderer / backend outputs. No new renderer is approved by this ADR.

| Mode | Purpose | Data source | Allowed overlays | Forbidden logic | Refresh trigger |
|---|---|---|---|---|---|
| Customer View | Show the product in customer-friendly form. | `CommercialPackageReport`, `QuotationDocumentV1`, product summary outputs. | Family label, dimensions, finish, price summary. | Manufacturing drill detail, release logic, internal validation math. | Draft change when customer-facing data is stale; commercial refresh. |
| Design View | Show the editable product structure. | FreeCAD preview backend, SceneGraph, engineering outputs. | Dimensions, section labels, editable parameters. | Pricing, release, commercial approval logic. | Configuration change or explicit preview request. |
| Manufacturing Detail View | Show production evidence. | Manufacturing runtime outputs, visible geometry plan, production package. | Drill holes, edge banding, grooves, hardware markers. | Cost computation, quotation formatting, release inference. | Manufacturing evidence refresh. |
| Assembly View | Show assembly sequence and part relationships. | Assembly package and production package. | Part labels, hardware callouts, assembly sequence markers. | Pricing, manufacturing recomputation, release logic. | Manufacturing or assembly output refresh. |
| Cost View | Show cost summary and margin visibility. | Cost pipeline outputs and commercial summary. | Cost breakdown, warnings, margin summary. | Geometry edits, manufacturing generation, release approval. | Cost refresh or upstream invalidation. |
| Quality Review View | Show blockers, warnings, and readiness. | `FactoryDecisionProjection`, validation summary, manufacturing decision. | Blockers, warnings, readiness badges, stale-data notices. | Changing backend verdicts or hiding blockers. | Validation, manufacturing, cost, or commercial refresh. |

## Error And Warning Model

The UI must present backend truth faithfully.

| Signal type | Presentation rule | Source of truth | UI behavior |
|---|---|---|---|
| Validation errors | Always visible before further progression. | Engineering validation results. | Block progression, show error state, keep current product state. |
| Manufacturing blockers | Always visible before release. | `ManufacturingDecision` and production package evidence. | Prevent release approval and mark the release state as blocked. |
| Commercial warnings | Visible and dismissible only after acknowledgment, not hidden. | `CommercialPackageReport` and quotation output. | Allow review, but do not silently promote to approval. |
| Release blockers | Always dominant over warnings. | `FactoryDecisionProjection` and release decision inputs. | Prevent release, surface the exact blocker source. |
| Stale data | Explicitly marked on all downstream panes. | UI draft timestamp versus last backend refresh. | Show stale warning, require refresh before release. |
| Unsupported family gaps | Shown as unsupported, not forced through another path. | Family routing result. | Disable unsupported operations and explain the routing gap. |

Blocking issues must remain visible before release. The UI may not downgrade backend blockers into warnings.

## Module Boundaries

Configurator V2 should be organized as product-experience modules, not as backend engines.

| Module | Responsibility | Allowed inputs | Service outputs consumed | Forbidden responsibilities |
|---|---|---|---|---|
| Project Context | Hold customer and project context. | Customer metadata, project metadata, current draft state. | Project result, document name, active specification. | Manufacturing, cost, commercial, release computation. |
| Product Family Selector | Choose supported product families. | Catalog data, family availability, routing info. | `ProductFamily`, family classification, routing result. | Inventing families or forcing unsupported routing. |
| Product Parameters | Edit dimensions and option inputs. | Draft configuration, dimension fields, option fields. | Draft configuration snapshots. | Validation math, geometry generation, cost math. |
| Structure Editor | Edit sections, doors, drawers, shelves, and dividers. | Product draft structure, section configuration. | Engineering and preview outputs. | Manufacturing or pricing logic. |
| Materials / Hardware | Select materials and hardware intent. | Catalog data, draft selection, SKU options. | Material/hardware evidence from backend workflows. | Calculating BOM, cost, or CNC. |
| Preview | Display geometry and overlay modes. | Scene graph, preview outputs, visibility preferences. | Engineering and manufacturing preview outputs. | Generating geometry or recomputing manufacturing truth. |
| Validation | Show validation status and blockers. | Draft configuration and refresh requests. | Validation reports, warnings, diagnostics. | Changing validation rules or verdicts. |
| Manufacturing Review | Review machining, hardware, assembly, and release evidence. | Manufacturing evidence and refresh requests. | `ManufacturingDecision`, production package, release package. | Creating manufacturing truth locally. |
| Cost Review | Show cost and margin from current evidence. | Manufacturing outputs and cost refresh requests. | Cost pipeline outputs and commercial summaries. | Pricing logic, tax logic, discount logic in UI. |
| Commercial Review | Show quotation and commercial readiness. | Cost outputs, commercial refresh requests. | `CommercialPackageReport`, `QuotationDocumentV1`. | Replacing commercial logic or formatting rules with UI rules. |
| Release Review | Present go/no-go decision and next actions. | Decision projection, release package, refresh requests. | `FactoryDecisionProjection`, release decision inputs. | Computing release approval independently. |

## Non-Goals

This ADR explicitly excludes:

- SaaS
- ERP
- MES
- inventory planning
- FreeCAD removal
- a new geometry backend
- a new renderer engine
- direct CNC authoring in the UI
- pricing logic inside the UI
- manufacturing logic inside the UI

## Risks

The main risks are:

- a narrow GUI can continue to underrepresent the real product
- the Configurator can drift into duplicate backend logic if service boundaries are relaxed
- stale preview or cost data can mislead users if invalidation is weak
- unsupported families can be forced through the wrong path if routing is obscured
- release confidence can be overstated if the UI invents transitions not backed by backend results
- overbuilding the experience before Wall Cabinet and Tall Cabinet are stable would dilute product focus

## Consequences

This decision makes the Configurator a stateful experience layer, but not a business-logic owner.

The Configurator:

- owns transient UI state
- requests backend truth through application services
- renders read-only projections and reports
- invalidates downstream outputs when upstream inputs change
- presents blockers and warnings without altering them

Backend truth remains in application services and downstream report objects.

## References

- [docs/architecture/decisions/ADR-0014-product-architecture-v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0014-product-architecture-v1.md)
- [ui/main_window.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/ui/main_window.py)
- [application/project_application_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/project_application_service.py)
- [application/engineering_application_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/engineering_application_service.py)
- [application/manufacturing_application_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/manufacturing_application_service.py)
- [domain/product_configuration.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/product_configuration.py)
- [domain/product_family.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/product_family.py)
- [manufacturing/factory_release_package.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/factory_release_package.py)
- [manufacturing/factory_decision_projection.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/factory_decision_projection.py)
- [manufacturing/manufacturing_decision.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_decision.py)
- [manufacturing/manufacturing_production_package.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_production_package.py)
- [commercial_outputs/commercial_package_report.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/commercial_outputs/commercial_package_report.py)
- [cost_intelligence/manufacturing_commercial_pipeline_builder.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/cost_intelligence/manufacturing_commercial_pipeline_builder.py)
- [cost_intelligence/quotation_document.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/cost_intelligence/quotation_document.py)
- [docs/product/Decision_Projection_Contract.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/product/Decision_Projection_Contract.md)
- [docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md)
