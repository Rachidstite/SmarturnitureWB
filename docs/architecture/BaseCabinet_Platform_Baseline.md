# BaseCabinet Platform Baseline

## Purpose

This document states the Base Cabinet pipeline as the official reference implementation for future furniture product families in SmartFurnitureWB.

The baseline is documentation only. No code changes are made.

## 1. Product Lifecycle

The current Base Cabinet lifecycle is:

Product Specification
↓
Engineering
↓
Validation Bridge
↓
Manufacturing Outputs Bridge
↓
Cost Bridge
↓
Commercial Bridge
↓
Product Result

This lifecycle is now the approved shape for product-level orchestration in the repository.

## 2. Reference Architecture

Base Cabinet is the reference implementation because it demonstrates:

- a stable product source contract
- a thin workflow orchestrator
- explicit bridge boundaries
- reuse of the manufacturing runtime and cut list pipeline
- reuse of the cost pipeline
- reuse of the commercial / quotation pipeline

The reference architecture is centered on:

- `BaseCabinetSpecification`
- `BaseCabinetScenario`
- `BaseCabinetProductWorkflow`
- `BaseCabinetProductResult`
- `BaseCabinetManufacturingOutputsEntry`

## 3. Completed Bridges

The following bridge layers are already implemented and connected in the Base Cabinet workflow:

- Validation Bridge
- Manufacturing Outputs Bridge
- Cost Bridge
- Commercial Bridge

These bridges reuse existing components and keep product orchestration thin.

## 4. Reusable Components

The following components are suitable for reuse by future product families:

- `BaseCabinetProductWorkflow`
- `BaseCabinetProductResult`
- `BaseCabinetScenario`
- `build_base_cabinet_engineering_cabinet()`
- `validate_base_cabinet_specification()`
- `build_base_cabinet_manufacturing_outputs_entry()`
- `ManufacturingRuntimePipelineBuilder`
- `ManufacturingCutlistBuilder`
- `ManufacturingProductionPackageBuilder`
- `ManufacturingCostPipelineBuilder`
- `ManufacturingCostSummaryBuilder`
- `ManufacturingCommercialPipelineBuilder`
- `ManufacturingQuotationInputBuilder`
- `ManufacturingQuotationReportBuilder`
- `QuotationDocumentBuilderV1`

## 5. Stable APIs

The following APIs are now stable baseline contracts:

- `BaseCabinetSpecification`
- `BaseCabinetScenario`
- `BaseCabinetProductResult`
- `build_base_cabinet_product_workflow()`
- `build_base_cabinet_manufacturing_outputs_entry()`

These contracts provide the product-source, orchestration, manufacturing-output, cost, and commercial handoff structure.

## 6. Components Intended for Reuse

Future product families should reuse the Base Cabinet pattern for:

- product-level workflow orchestration
- result aggregation
- validation translation
- manufacturing outputs translation
- cost translation
- commercial translation
- quotation document generation

The intended reuse target is architectural structure, not Base Cabinet-specific business data.

## 7. Components That Remain Product-Specific

These components remain Base Cabinet specific and should be swapped for product-specific equivalents in future families:

- `BaseCabinetSpecification`
- `BaseCabinetScenario`
- `BaseCabinetSpecificationAdapter`
- `build_base_cabinet_engineering_cabinet()`
- `validate_base_cabinet_specification()`
- `build_base_cabinet_manufacturing_outputs_entry()`

The bridge pattern is reusable, but the underlying product semantics remain family-specific.

## 8. Requirements for Future Product Families

Future product families such as Wall Cabinet, Tall Cabinet, Wardrobe, Kitchen Cabinet, and Office Furniture must:

- keep the same top-level workflow order
- preserve a thin orchestrator
- reuse approved bridge boundaries instead of duplicating pipeline logic
- continue to consume engineering output before manufacturing or commercial stages
- keep cost and commercial logic downstream from manufacturing outputs
- avoid introducing new engines or builders when existing ones already satisfy the contract
- keep product-specific source contracts separate from shared bridge semantics

## Reference Declaration

Base Cabinet is the official reference implementation for:

- Wall Cabinet
- Tall Cabinet
- Wardrobe
- Kitchen Cabinet
- Office Furniture

## Decision

**APPROVED_PLATFORM_BASELINE**

Base Cabinet is now the baseline reference implementation for future product families in SmartFurnitureWB.
