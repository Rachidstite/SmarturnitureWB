# Full Product Pipeline Architecture Audit

## Purpose

This audit reviews the complete SmartFurnitureWB product pipeline from product definition to commercial outputs, using the current Base Cabinet workflow as evidence.

The audit is documentation only. No code changes are made.

## Files Inspected

- `domain/base_cabinet_product_workflow.py`
- `domain/base_cabinet_product_result.py`
- `domain/base_cabinet_manufacturing_outputs_entry.py`
- `domain/base_cabinet_specification.py`
- `domain/base_cabinet_scenario.py`
- `domain/base_cabinet_engineering_entry.py`
- `domain/base_cabinet_specification_validation.py`
- `manufacturing/`
- `cost_intelligence/`
- `exports/`
- `docs/architecture/`
- `docs/product/`

## Pipeline

Product Definition  
↓  
Engineering  
↓  
Validation  
↓  
Manufacturing Outputs  
↓  
Cost  
↓  
Optimization / Nesting  
↓  
Commercial Outputs

## 1. Product Definition

### Current status

`IMPLEMENTED_AND_CONNECTED`

### Existing reusable components

- `BaseCabinetSpecification`
- `BaseCabinetScenario`
- `BaseCabinetProductResult`
- `build_base_cabinet_product_workflow()`
- `FurnitureProject`
- `FurnitureProjectBuilder`
- `docs/product/Cabinet_Manufacturing_Capability_V1.md`

### Current Base Cabinet integration status

The Base Cabinet workflow already accepts `BaseCabinetSpecification`, creates `BaseCabinetScenario`, and returns a product result object that preserves the specification as the pipeline source of truth.

### Missing bridge

- Generalized product contracts for future product families
- Shared product-specification abstraction across cabinet types

### Business value

- preserves product meaning
- keeps downstream stages anchored to a stable source of truth
- enables repeatable product-level workflows

### Recommendation

- Keep the Base Cabinet product definition path explicit and stable.
- Generalize only after multiple product workflows need the same contract shape.

## 2. Engineering

### Current status

`IMPLEMENTED_AND_CONNECTED`

### Existing reusable components

- `build_base_cabinet_engineering_cabinet()`
- `BaseCabinetSpecificationAdapter`
- `CabinetBuilder`
- `Cabinet`
- `SceneGraph`

### Current Base Cabinet integration status

The Base Cabinet workflow calls the engineering entry and receives the engineering cabinet result that exposes the scene graph used downstream.

### Missing bridge

- A product-agnostic engineering entry abstraction for future furniture types

### Business value

- converts product definition into geometry
- creates the shared engineering handoff artifact
- keeps manufacturing dependent on engineered structure, not raw product spec

### Recommendation

- Reuse the engineering entry pattern for future products.
- Do not bypass engineering when adding downstream outputs.

## 3. Validation

### Current status

`PARTIAL`

### Existing reusable components

- `validate_base_cabinet_specification()`
- `ManufacturingValidationService`
- `ManufacturingValidationReport`
- `ManufacturingValidationSummaryBuilder`
- `ManufacturingValidationSummaryReport`
- `ValidationState`

### Current Base Cabinet integration status

Validation is present in the Base Cabinet workflow, but it is split across engineering validation and manufacturing validation paths. The product workflow currently calls the engineering validation entry, while the manufacturing validation summary bridge remains documented but not yet integrated into the Base Cabinet facade.

### Missing bridge

- A single product-level validation bridge that connects validation service output to the summary-ready manufacturing validation artifact

### Business value

- catches geometric and manufacturing issues earlier
- supports manufacturing readiness decisions
- reduces rework and downstream uncertainty

### Recommendation

- Preserve the existing validation layers.
- Add a dedicated bridge only when the product workflow needs a unified validation summary contract.

## 4. Manufacturing Outputs

### Current status

`PARTIAL`

### Existing reusable components

- `build_base_cabinet_manufacturing_outputs_entry()`
- `ManufacturingRuntimePipelineBuilder`
- `ManufacturingCutlistBuilder`
- `ManufacturingPackage`
- `ManufacturingProductionPackageBuilder`
- `ManufacturingProductionPackage`
- `HardwareUsageBuilder`
- `HardwareBomBuilder`

### Current Base Cabinet integration status

The Base Cabinet workflow already reaches the manufacturing outputs entry. That entry currently returns the cut list, manufacturing package, and metadata, making Cut List the first connected product output.

### Missing bridge

- Additional product-level output bridges for hardware BOM, validation summary, CNC export, and later commercial artifacts

### Business value

- turns engineering geometry into manufacturing-ready outputs
- provides the first reusable production artifact
- creates a stable handoff for later cost and commercial stages

### Recommendation

- Keep Cut List as the first supported output.
- Add further outputs only through audited translation bridges.

## 5. Cost

### Current status

`IMPLEMENTED_NOT_CONNECTED`

### Existing reusable components

- `ManufacturingCostPipelineBuilder`
- `ManufacturingCostSummaryBuilder`
- `ManufacturingCostCalculator`
- `ManufacturingCostContextBuilder`
- `ManufacturingCostInsightsBuilder`
- `ManufacturingCostRiskReportBuilder`
- `ManufacturingQuotationInputBuilder`
- `ManufacturingQuotationReportBuilder`
- `ManufacturingCommercialPipelineBuilder`
- `ManufacturingCommercialResult`
- `FurnitureProjectQuotationBuilder`
- `FurnitureProjectBusinessReportBuilder`

### Current Base Cabinet integration status

The cost stack exists and is well populated, but the current Base Cabinet product workflow does not connect into it yet. The repo already supports cost and quotation flows through manufacturing production packages and furniture project pipelines.

### Missing bridge

- A Base Cabinet cost entry that consumes the approved product workflow outputs or manufacturing production package

### Business value

- supports pricing
- supports profitability analysis
- supports cost control and margin protection

### Recommendation

- Reuse the existing cost pipeline rather than duplicating it.
- Introduce a bridge only when Base Cabinet cost outputs are officially required.

## 6. Optimization / Nesting

### Current status

`IMPLEMENTED_NOT_CONNECTED`

### Existing reusable components

- `ManufacturingOptimizationPipelineBuilder`
- `ManufacturingOptimizationResult`
- `NestingIntelligenceBuilder`
- `OffcutExtractionService`
- `OffcutReportBuilder`
- `OffcutIntelligenceBuilder`
- `WasteIntelligenceBuilder`
- `SheetUtilizationBuilder`
- `ManufacturingProjectIntelligencePipelineBuilder`
- `IndustrialNestingEngine`
- `SVGNestingExporter`

### Current Base Cabinet integration status

The repo already implements optimization and nesting pipelines, including a scene-graph-driven project intelligence path, but the Base Cabinet product workflow does not currently connect to those outputs.

### Missing bridge

- A Base Cabinet optimization bridge from the product workflow or manufacturing production package to the nesting/optimization pipeline

### Business value

- reduces waste
- improves material utilization
- improves production planning
- strengthens manufacturing economics

### Recommendation

- Keep optimization and nesting as downstream consumers of approved manufacturing artifacts.
- Avoid placing nesting logic inside the product workflow itself.

## 7. Commercial Outputs

### Current status

`IMPLEMENTED_NOT_CONNECTED`

### Existing reusable components

- `QuotationDocumentBuilderV1`
- `QuotationDocumentExport`
- `ManufacturingCommercialPipelineBuilder`
- `FurnitureProjectQuotationBuilder`
- `FurnitureProjectQuotationBreakdownBuilder`
- `FurnitureProjectProfitabilityBuilder`
- `FurnitureProjectExecutiveReportBuilder`
- `FurnitureProjectBusinessReportBuilder`
- `QuotationReport`
- `ProfitabilityReport`
- `CommercialAcceptanceContract`

### Current Base Cabinet integration status

Commercial outputs are implemented in the repo, but the current Base Cabinet workflow does not yet connect to quotation generation, profitability reporting, or customer-facing export artifacts.

### Missing bridge

- A Base Cabinet commercial bridge from validated manufacturing outputs into the cost/commercial pipeline

### Business value

- enables quoting
- supports profitability and margin review
- produces customer-facing deliverables
- closes the product-to-commercial loop

### Recommendation

- Keep commercial outputs downstream of validated manufacturing and cost artifacts.
- Do not expose commercial outputs directly from engineering or product-definition stages.

## Stage Classifications

| Stage | Classification |
| --- | --- |
| Product Definition | `IMPLEMENTED_AND_CONNECTED` |
| Engineering | `IMPLEMENTED_AND_CONNECTED` |
| Validation | `PARTIAL` |
| Manufacturing Outputs | `PARTIAL` |
| Cost | `IMPLEMENTED_NOT_CONNECTED` |
| Optimization / Nesting | `IMPLEMENTED_NOT_CONNECTED` |
| Commercial Outputs | `IMPLEMENTED_NOT_CONNECTED` |

## Architectural Conclusions

1. The Base Cabinet workflow proves that the product-definition, engineering, and manufacturing-outputs stages can be orchestrated as a stable product pipeline.
2. Validation is present but still split across multiple contracts, so the validation stage is not yet fully unified at the product-workflow boundary.
3. Manufacturing outputs are intentionally thin today: Cut List is the first connected artifact, while additional outputs remain translation-bridge work.
4. Cost, optimization, and commercial layers are present and reusable, but they are not yet connected to the Base Cabinet product workflow.
5. The repo already has enough downstream machinery to support a full lifecycle pipeline; the remaining work is primarily bridge design and contract alignment, not new engines.

## Recommendation Summary

- Keep the current Base Cabinet workflow as the reference orchestration pattern.
- Connect downstream stages through explicit translation bridges rather than direct duplication.
- Reuse existing cost, optimization, and commercial modules instead of rebuilding them inside the product workflow.
- Delay a generalized universal product workflow until more than one product family proves the same bridge structure.

## Decision

**APPROVED_PIPELINE_DIRECTION**

The architecture direction is sound: product definition flows into engineering, validation, manufacturing outputs, cost, optimization, and commercial outputs. The current Base Cabinet workflow validates the front half of that pipeline, while the back half remains implemented in the repository but not yet connected to the Base Cabinet product workflow.
