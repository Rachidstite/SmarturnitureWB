# Architecture Baseline v1

## 1. Platform Overview

SmartFurnitureWB is a layered furniture platform centered on a verified
base-cabinet execution path. The current repository supports:

- product family catalog data
- product configuration as a public input contract
- engineering application execution
- manufacturing and factory-release execution
- full product workflow execution
- downstream cost, commercial, and quotation runtime flow
- separate foundation outputs for cost, commercial, and customer-facing summaries

The verified public flow is:

`ProductConfiguration`
→ `ProjectApplicationService`
→ `BaseCabinetProductWorkflow`
→ Engineering
→ Manufacturing
→ Cost
→ Commercial
→ Quotation

## 2. Layered Architecture

### Product

The product layer defines reusable family and configuration contracts:

- `domain.product_family.ProductFamily`
- `domain.product_family_registry.ProductFamilyRegistry`
- `domain.product_family_catalog`
- `domain.product_configuration.ProductConfiguration`

This layer identifies families such as:

- `BASE_CABINET`
- `WALL_CABINET`
- `TALL_CABINET`

### Engineering

The engineering layer is currently implemented through the base-cabinet path:

- `domain.base_cabinet_specification.BaseCabinetSpecification`
- `domain.base_cabinet_specification_adapter.BaseCabinetSpecificationAdapter`
- `domain.base_cabinet_engineering_entry`
- `domain.base_cabinet_engineering_model`
- `domain.construction_resolver`
- `engine.cabinet`
- `engine.cabinet_builder`

### Manufacturing

The manufacturing layer converts engineering scene-graph output into production
evidence:

- `domain.base_cabinet_manufacturing_outputs_entry`
- `manufacturing.manufacturing_runtime_pipeline_builder`
- `manufacturing.manufacturing_production_package_builder`
- `application.manufacturing_application_service`
- `manufacturing.factory_release_package.FactoryReleasePackage`

### Cost

Two cost paths exist in the repository:

1. runtime workflow cost path
   - `cost_intelligence.manufacturing_cost_pipeline_builder`
   - consumes `ManufacturingProductionPackage`
   - produces `ManufacturingCostSummary`

2. foundation cost path
   - `cost_intelligence.cost_package_builder`
   - consumes `FactoryReleasePackage`
   - produces `CostPackageReport`

### Commercial

Two commercial paths exist in the repository:

1. runtime workflow commercial path
   - `cost_intelligence.manufacturing_commercial_pipeline_builder`
   - produces `ManufacturingCommercialResult`

2. foundation commercial path
   - `commercial_outputs.commercial_package_builder`
   - consumes `CostPackageReport`
   - produces `CommercialPackageReport`

## 3. Runtime Flow

The verified full runtime flow is:

1. `ProductConfiguration`
2. `ProjectApplicationService.execute_from_product_configuration(...)`
3. `adapt_product_configuration_to_base_cabinet_specification(...)`
4. `ProjectApplicationService.execute(specification=...)`
5. `build_base_cabinet_product_workflow(...)`
6. engineering:
   - `build_base_cabinet_engineering_cabinet(...)`
7. manufacturing:
   - `build_base_cabinet_manufacturing_outputs_entry(...)`
8. runtime cost:
   - `ManufacturingProductionPackageBuilder().build(...)`
   - `ManufacturingCostPipelineBuilder().build(...)`
9. runtime commercial:
   - `ManufacturingCommercialPipelineBuilder().build(...)`
10. quotation:
   - `QuotationDocumentBuilderV1().build(...)`

## 4. Application Services

The repository exposes three application services:

- `application.engineering_application_service.EngineeringApplicationService`
- `application.manufacturing_application_service.ManufacturingApplicationService`
- `application.project_application_service.ProjectApplicationService`

Their public result wrapper is:

- `application.application_service_result.ApplicationServiceResult`

Verified public entry-point support:

- `EngineeringApplicationService.execute_from_product_configuration(...)`
- `ManufacturingApplicationService.execute_from_product_configuration(...)`
- `ProjectApplicationService.execute_from_product_configuration(...)`

All three follow the same extension pattern:

- adapt `ProductConfiguration` to `BaseCabinetSpecification`
- delegate to existing `execute(specification=...)`

## 5. Canonical Runtime Contract

The canonical downstream runtime contract after the commercial stage is:

- `cost_intelligence.manufacturing_commercial_result.ManufacturingCommercialResult`

Repository evidence shows it is the richest semantic output after commercial
processing. It contains:

- `manufacturing_cost_summary`
- `manufacturing_quotation_input`
- `quotation_report`
- `profitability_report`
- `quotation_intelligence_report`

Derived downstream artifacts include:

- `QuotationReport`
- `QuotationDocumentV1`

Foundation downstream artifacts include:

- `CostPackageReport`
- `CommercialPackageReport`

Customer-facing foundation artifact:

- `CustomerPackageReport`

## 6. Product Family Architecture

The product family layer is passive data:

- `ProductFamily`
- `ProductFamilyRegistry`
- built-in catalog entries

Repository evidence confirms:

- `BASE_CABINET` is the currently implemented executable family path
- `WALL_CABINET` and `TALL_CABINET` exist as catalog data

The catalog records family defaults, including engineering, manufacturing,
visual, and commercial defaults, but does not execute family-specific logic.

## 7. Product Configuration Architecture

`ProductConfiguration` is the current public product input contract:

- `family_id`
- `width`
- `height`
- `depth`
- `material`
- `options`
- `metadata`

The current executable adapter is:

- `domain.product_configuration_base_cabinet_adapter`

It supports:

- `BASE_CABINET`
- `base_cabinet`

It maps supported fields and known safe options into
`BaseCabinetSpecification`.

## 8. Domain Boundaries

Current domain boundaries are explicit:

- base-cabinet engineering and product workflow are family-specific
- product family and product configuration are generic input contracts
- wall-mount vocabulary exists separately in:
  - `domain.wall_mount_capability`

`BaseCabinetSpecification` is a specialized engineering contract, not a proven
root contract for all cabinet families.

## 9. Application Boundaries

Application services orchestrate existing domain/runtime components and return
`ApplicationServiceResult`.

They do not define new engines, builders, or workflow frameworks.

The narrowest public responsibilities are:

- engineering-only: `EngineeringApplicationService`
- manufacturing and factory release: `ManufacturingApplicationService`
- full workflow: `ProjectApplicationService`

## 10. Manufacturing Boundaries

Manufacturing begins from engineering scene-graph output.

Verified path:

- `build_base_cabinet_manufacturing_outputs_entry(specification)`
- internally rebuilds engineering
- extracts `scene_graph`
- `ManufacturingRuntimePipelineBuilder().build(scene_graph)`

Factory release is built in:

- `ManufacturingApplicationService`

Factory release foundation contract:

- `FactoryReleasePackage`

## 11. Cost Boundaries

Runtime workflow cost boundary:

- input: `ManufacturingProductionPackage`
- output: `ManufacturingCostSummary`

Foundation cost boundary:

- input: `FactoryReleasePackage`
- output: `CostPackageReport`

Repository evidence shows these are separate but supported paths.

## 12. Commercial Boundaries

Runtime workflow commercial boundary:

- input:
  - `ManufacturingProductionPackage`
  - `ManufacturingCostSummary`
- output:
  - `ManufacturingCommercialResult`

Foundation commercial boundary:

- input: `CostPackageReport`
- output: `CommercialPackageReport`

The runtime commercial path is the canonical workflow handoff.

## 13. Output Boundaries

Verified downstream output roles:

- runtime contract:
  - `ManufacturingCommercialResult`
- derived runtime report:
  - `QuotationReport`
- export artifact:
  - `QuotationDocumentV1`
- export renderer:
  - `exports.quotation_document_export.QuotationDocumentExport`
- foundation components:
  - `CostPackageReport`
  - `CommercialPackageReport`
- customer artifact:
  - `CustomerPackageReport`

Customer outputs are currently outside the full runtime workflow. They are built
from the foundation commercial path:

- `CommercialPackageReport -> CustomerPackageReport`

## 14. Deferred Technical Debt

The repository currently documents the following deferred technical debt:

- manufacturing rebuilds engineering internally
- foundation output path and runtime output path remain intentionally separate
- customer outputs are not yet integrated into `ProjectApplicationService`
- `BaseCabinetSpecification` is the active engineering specification path, while
  wall-mount semantics exist separately and are not yet part of that executable
  path
- `toe_kick_required` exists in the base-cabinet specification, but the current
  adapter to `CabinetParams` does not map it into `base_height`

## 15. Architecture Principles

The verified repository architecture follows these principles:

- preserve existing APIs
- extend through adapters and application-service methods
- reuse existing engines, builders, workflows, and pipelines
- keep runtime orchestration separate from passive foundation outputs
- use repository evidence, not speculative redesign
- treat richer runtime contracts as canonical handoffs
- keep customer/export artifacts derived from downstream runtime or foundation
  outputs rather than treating them as peer runtime contracts
