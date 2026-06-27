# Cost Translation Layer Audit

## Purpose

This audit reviews the existing cost pipeline and identifies the official translation boundary between Manufacturing Outputs and Cost Intelligence.

The audit is documentation only. No code changes are made.

## Files Inspected

- `cost_intelligence/`
- `manufacturing/`
- `domain/base_cabinet_manufacturing_outputs_entry.py`
- `domain/base_cabinet_product_workflow.py`
- `docs/architecture/`

## 1. Existing Cost Artifacts

Existing cost artifacts include:

- `ManufacturingCostSummary`
- `CostReport`
- `ManufacturingCostContext`
- `ManufacturingCostInsights`
- `ManufacturingCostRiskReport`
- `ManufacturingQuotationInput`
- `QuotationReport`
- `ProfitabilityReport`
- `ManufacturingCommercialResult`
- `QuotationDocumentV1`

### Current status

`IMPLEMENTED_AND_CONNECTED`

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
- `QuotationDocumentBuilderV1`

### Current Base Cabinet integration status

The Base Cabinet manufacturing outputs entry already produces a `ManufacturingPackage`, which is the correct upstream object for the manufacturing cost pipeline. The cost stack itself is implemented and reusable.

### Missing bridge

- A Base Cabinet-specific cost entry that intentionally hands the manufacturing outputs into the cost pipeline

### Business value

- supports pricing
- supports margin analysis
- supports cost risk review
- supports commercial readiness

### Recommendation

- Reuse the cost pipeline as-is.
- Introduce a Base Cabinet cost bridge only when product-level cost outputs are formally required.

## 2. Cost Entry Point

The effective cost entry point is:

- `ManufacturingCostPipelineBuilder.build(production_package, hardware_cost=0.0)`

This builder consumes a `ManufacturingProductionPackage`.

### Current status

`IMPLEMENTED_AND_CONNECTED`

### Existing reusable components

- `ManufacturingProductionPackage`
- `ManufacturingCostPipelineBuilder`

### Current Base Cabinet integration status

`BaseCabinetManufacturingOutputsEntry` returns `manufacturing_package`, and the repository already knows how to convert a production package into cost summaries downstream. The bridge is present at the artifact level, but not yet surfaced as a Base Cabinet product-level cost entry.

### Missing bridge

- an explicit Base Cabinet cost workflow entry

### Business value

- converts manufacturing outputs into monetary analysis
- enables pricing and profitability decisions

### Recommendation

- Treat the manufacturing production package as the official cost entry input.
- Keep the product workflow free of cost calculations until the cost bridge is explicitly needed.

## 3. Translation Boundary

The official translation boundary is:

- `ManufacturingProductionPackage` -> `ManufacturingCostSummary`

Then, for commercial handoff:

- `ManufacturingCostSummary` -> `ManufacturingQuotationInput` -> `QuotationReport` -> `QuotationDocumentV1`

### Current status

`IMPLEMENTED_AND_CONNECTED`

### Existing reusable components

- `ManufacturingProductionPackageBuilder`
- `ManufacturingCostPipelineBuilder`
- `ManufacturingCommercialPipelineBuilder`
- `QuotationDocumentBuilderV1`

### Current Base Cabinet integration status

The Base Cabinet workflow already produces the upstream manufacturing package, which is sufficient for the existing cost pipeline to operate once a cost bridge is invoked.

### Missing bridge

- a Base Cabinet-facing cost entry point

### Business value

- preserves separation between manufacturing and cost intelligence
- enables downstream pricing without polluting product workflow logic

### Recommendation

- Keep the translation boundary at the production-package layer.
- Do not move cost logic into the product workflow.

## 4. Cost Reports

Cost report family includes:

- `ManufacturingCostSummary`
- `CostReport`
- `ManufacturingCostContext`
- `ManufacturingCostInsights`
- `ManufacturingCostRiskReport`
- `QuotationReport`
- `ProfitabilityReport`

### Current status

`IMPLEMENTED_AND_CONNECTED`

### Existing reusable components

- cost calculation and summary builders
- quotation and profitability builders

### Current Base Cabinet integration status

The Base Cabinet product pipeline does not yet produce these reports directly, but the underlying cost stack is already reusable and contract-stable.

### Missing bridge

- explicit Base Cabinet orchestration into the cost report family

### Business value

- provides the numeric basis for quotations and profitability checks
- captures cost risk and warnings

### Recommendation

- Reuse the existing cost report family downstream from manufacturing outputs.
- Avoid duplicating report types for Base Cabinet.

## 5. Commercial Handoff

Commercial handoff currently uses:

- `ManufacturingCommercialPipelineBuilder`
- `ManufacturingCommercialResult`
- `QuotationDocumentBuilderV1`
- `FurnitureProjectQuotationBuilder`
- `FurnitureProjectBusinessReportBuilder`

### Current status

`IMPLEMENTED_NOT_CONNECTED`

### Existing reusable components

- commercial pipeline builders
- quotation and profitability report builders
- quotation document export

### Current Base Cabinet integration status

The commercial pipeline is implemented in the repository, but the current Base Cabinet workflow does not yet hand off into it directly.

### Missing bridge

- a Base Cabinet cost/commercial bridge from manufacturing outputs to the commercial pipeline

### Business value

- creates customer-facing quotations
- supports sales and margin review
- closes the product-to-commercial loop

### Recommendation

- Use the cost summary as the commercial handoff boundary.
- Keep commercial document generation downstream from validated cost artifacts.

## 6. Reusable Components

Reusable components already available:

- `ManufacturingPackage`
- `ManufacturingProductionPackage`
- `ManufacturingCostPipelineBuilder`
- `ManufacturingCommercialPipelineBuilder`
- `ManufacturingCostSummary`
- `ManufacturingQuotationInput`
- `QuotationReport`
- `QuotationDocumentV1`
- `FurnitureProjectQuotationBuilder`
- `FurnitureProjectBusinessReportBuilder`

### Current status

`IMPLEMENTED_AND_CONNECTED`

### Current Base Cabinet integration status

The Base Cabinet manufacturing outputs entry already returns the correct upstream object for cost reuse.

### Missing bridge

- Base Cabinet-specific cost entry and product workflow linkage

### Recommendation

- Reuse the existing cost and commercial components rather than creating product-specific cost builders.

## 7. Missing Bridge

The missing bridge is:

- a documented Base Cabinet cost entry that takes `BaseCabinetManufacturingOutputsEntryResult.manufacturing_package` or a production package and hands it into the existing cost pipeline

### Current status

`PARTIAL`

### Existing reusable components

- manufacturing outputs entry
- manufacturing production package builder
- cost pipeline builder
- commercial pipeline builder

### Business value

- enables product-level pricing
- enables profitability reporting
- enables customer-facing quotation generation

### Recommendation

- Add the bridge only as an explicit orchestration layer, not as new cost logic.

## Stage Classifications

| Stage | Classification |
| --- | --- |
| Existing cost artifacts | `IMPLEMENTED_AND_CONNECTED` |
| Cost entry point | `IMPLEMENTED_AND_CONNECTED` |
| Translation boundary | `IMPLEMENTED_AND_CONNECTED` |
| Cost reports | `IMPLEMENTED_AND_CONNECTED` |
| Commercial handoff | `IMPLEMENTED_NOT_CONNECTED` |
| Reusable components | `IMPLEMENTED_AND_CONNECTED` |
| Missing bridge | `PARTIAL` |

## Decision

**APPROVED_COST_TRANSLATION_LAYER**

The official boundary is the manufacturing production package: product/manufacturing outputs flow into cost intelligence through the existing cost pipeline, and commercial outputs remain downstream of the cost summary. The architecture already supports the translation layer; the remaining work is only Base Cabinet-facing orchestration, not new cost engines or builders.
