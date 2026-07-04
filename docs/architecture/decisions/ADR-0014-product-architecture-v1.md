# ADR-0014
SmartFurnitureWB Product Architecture V1

## Status

Accepted

## Context

SmartFurnitureWB already contains a stronger backend than its current user interface:

- `ProductConfiguration` and `ProductFamily` exist as canonical product inputs.
- `ProjectApplicationService`, `EngineeringApplicationService`, and `ManufacturingApplicationService` already provide layered application entry points.
- `BaseCabinetProductWorkflow` already orchestrates engineering, validation, manufacturing, cost, and commercial bridges.
- `FactoryReleasePackage` and `CommercialPackageReport` already exist as downstream boundary artifacts.
- The current configurator is a narrow two-tab parameter editor, not a commercial product cockpit.
- FreeCAD currently hosts geometry and preview behavior, but it should not be treated as the daily product face.

Repository evidence also shows the current product direction is already expressed in the runtime stack:

- product configuration feeds application services
- application services feed engineering and manufacturing workflows
- manufacturing feeds cost and commercial outputs
- commercial and release artifacts exist as backend outputs

The next product step is therefore not a new engine or a new workflow. The next product step is to formalize the product boundary and declare the Configurator as the primary user interface.

## Evidence

The following repository evidence supports this decision:

- `domain/product_configuration.py`
  - canonical product input contract
- `domain/product_family.py`
  - canonical product family contract
- `domain/product_family_catalog.py`
  - built-in product family definitions
- `application/project_application_service.py`
  - public orchestration entry point for product workflows
- `application/engineering_application_service.py`
  - engineering service gateway
- `application/manufacturing_application_service.py`
  - manufacturing service gateway
- `domain/base_cabinet_product_workflow.py`
  - orchestrates engineering, validation, manufacturing, cost, and commercial bridges
- `manufacturing/factory_release_package.py`
  - release boundary package
- `commercial_outputs/commercial_package_report.py`
  - passive commercial boundary report
- `ui/main_window.py`
  - current narrow configurator shell
- `engine/cabinet_builder.py`
  - geometry backend and preview bridge
- `gui/renderer.py`
  - document-level preview renderer
- `docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md`
  - platform boundary rules already require commercial approval before production release
- `docs/product/Product_Architecture_v1.md`
  - product value chain already treats product configuration, engineering, manufacturing, release, cost, commercial, and quotation as a single platform path

## Decision

SmartFurnitureWB is a furniture manufacturing platform, not a generic FreeCAD workbench.

The official primary user interface is the Configurator.

The product boundary is defined as follows:

- UI layers may present projects, products, preview, manufacturing, cost, commercial, and release.
- UI layers must not contain business logic that belongs in application services or backend layers.
- Application services are the only gateway from UI to business logic.
- FreeCAD is the engineering, geometry, and preview backend.
- Manufacturing, cost, commercial, and factory release remain backend services and reports.
- No UI may duplicate manufacturing, cost, commercial, or release logic.

This ADR freezes the product direction before Configurator V2 is built.

## Product Layers

### 1. Product Experience Layer

The product experience layer is the daily operator surface:

- Dashboard
- Projects
- Customers
- Product Families
- Configurator
- Preview
- Manufacturing
- Cost
- Commercial
- Factory Release
- Settings

### 2. Application Services Layer

The application layer is the only UI gateway into business logic:

- `ProjectApplicationService`
- `EngineeringApplicationService`
- `ManufacturingApplicationService`
- future Configurator orchestration service only if evidence proves it is needed

### 3. Domain / Engineering Layer

The domain layer owns product meaning and engineering truth:

- `ProductConfiguration`
- `ProductFamily`
- engineering models
- construction models

### 4. Manufacturing Layer

The manufacturing layer owns downstream production evidence:

- manufacturing runtime
- materials
- machining
- hardware
- assembly
- factory release

### 5. Cost / Commercial Layer

The cost and commercial layer owns downstream economic evidence:

- cost intelligence
- `CommercialPackageReport`
- quotation
- profitability

### 6. Geometry Backend Layer

The geometry backend is FreeCAD and its preview/rendering path:

- FreeCAD
- SceneGraph rendering
- geometry execution

## UI Rules

The UI rules are strict:

- UI must call application services, not domain internals directly.
- UI must not compute manufacturing data.
- UI must not compute cost.
- UI must not compute commercial pricing.
- UI must not generate CNC directly.
- UI must not bypass validation.
- UI must not duplicate release decisions.
- UI consumes projections, reports, and service outputs.
- Configurator visual improvements remain presentation-only unless source data is missing.
- FreeCAD UI remains secondary and backend-facing.

## Product Workflow

The official product workflow is:

Customer
  ↓
Project
  ↓
Product Family
  ↓
Configuration
  ↓
Live Preview
  ↓
Engineering Validation
  ↓
Manufacturing Evidence
  ↓
Cost
  ↓
Commercial / Quotation
  ↓
Factory Release
  ↓
Production Documents

Release must not bypass manufacturing evidence or commercial evidence.

## Configurator V2 Target

Configurator V2 is the product face of SmartFurnitureWB.

It should present:

- project context
- product family selector
- parameters and dimensions
- doors, drawers, shelves, and dividers
- materials
- hardware
- live preview
- manufacturing detail mode
- assembly view
- cost preview
- commercial summary
- validation and warnings
- release readiness

This ADR does not define specific widgets or layout mechanics.

## FreeCAD Role

Current role:

- FreeCAD is the workbench host and geometry backend.

Target role:

- FreeCAD becomes the backend execution and preview service behind the Configurator.

Long-term role:

- FreeCAD may become replaceable only after Commercial V1 and multiple reference product families are validated.

This ADR does not recommend FreeCAD independence now.

## Risks

The main risks are:

- the current GUI is too narrow for commercial product use
- building Configurator V2 without application services would duplicate logic
- exposing FreeCAD as the primary UX weakens product perception
- overbuilding UI before Wall Cabinet and Tall Cabinet workflows are stable
- mixing presentation with manufacturing truth
- starting SaaS or FreeCAD independence too early

## Consequences

This decision establishes a stable product boundary:

- future UI work must treat the Configurator as the primary product surface
- backend services remain the source of truth
- FreeCAD stays an engineering backend, not the daily business UI
- new product UI must reuse existing application and backend layers
- no parallel GUI architecture should be introduced

## References

- [domain/product_configuration.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/product_configuration.py)
- [domain/product_family.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/product_family.py)
- [domain/product_family_catalog.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/product_family_catalog.py)
- [application/project_application_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/project_application_service.py)
- [application/engineering_application_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/engineering_application_service.py)
- [application/manufacturing_application_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/application/manufacturing_application_service.py)
- [domain/base_cabinet_product_workflow.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_product_workflow.py)
- [manufacturing/factory_release_package.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/factory_release_package.py)
- [commercial_outputs/commercial_package_report.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/commercial_outputs/commercial_package_report.py)
- [ui/main_window.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/ui/main_window.py)
- [engine/cabinet_builder.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/engine/cabinet_builder.py)
- [gui/renderer.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/gui/renderer.py)
- [docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md)
- [docs/product/Product_Architecture_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/product/Product_Architecture_v1.md)
