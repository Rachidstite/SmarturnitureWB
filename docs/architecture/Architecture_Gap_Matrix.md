# Architecture Gap Matrix

## Purpose

This matrix consolidates the current SmartFurnitureWB architecture into one view of what is complete, what needs only a bridge, and what still requires future implementation.

The matrix is documentation only. No code changes are made.

## Source Documents Reviewed

- `docs/architecture/SmartFurnitureWB_Platform_Architecture_V2.md`
- `docs/architecture/Full_Product_Pipeline_Architecture_Audit.md`
- `docs/architecture/Manufacturing_Outputs_Roadmap.md`
- `docs/architecture/Validation_Translation_Layer_Architecture.md`
- `docs/architecture/Cost_Translation_Layer_Audit.md`
- `docs/architecture/Product_Workflow_Architecture_Review.md`
- `docs/architecture/Product_Validation_Bridge_Audit.md`
- `docs/architecture/SceneGraph_Engineering_Manufacturing_Boundary.md`
- `docs/architecture/BaseCabinet_Product_Pipeline_Contract.md`

## Status Legend

- `COMPLETE`
- `IMPLEMENTED_NEEDS_BRIDGE`
- `PARTIAL`
- `MISSING`
- `POSTPONED`

## 1. Product Definition

### Status

`COMPLETE`

### Existing components

- `BaseCabinetSpecification`
- `BaseCabinetScenario`
- `BaseCabinetProductResult`
- `BaseCabinetProductWorkflow`
- `FurnitureProject`
- `FurnitureProjectBuilder`

### Missing bridge or missing implementation

- generalized product-specification contract for all future furniture families

### Business priority

- highest

### Recommendation

- Keep the current product-definition workflow stable.
- Generalize only after multiple product families need the same contract shape.

### Risk if built too early

- product semantics will drift into a one-size-fits-all contract and force later breaking changes.

## 2. Engineering

### Status

`COMPLETE`

### Existing components

- `build_base_cabinet_engineering_cabinet()`
- `BaseCabinetSpecificationAdapter`
- `CabinetBuilder`
- `Cabinet`
- `SceneGraph`

### Missing bridge or missing implementation

- product-agnostic engineering entry abstraction for future product families

### Business priority

- highest

### Recommendation

- Reuse the engineering entry pattern for future products.
- Keep engineering as the authority for geometry creation.

### Risk if built too early

- bypassing engineering would couple downstream layers to raw product spec and increase geometry defects.

## 3. Validation

### Status

`IMPLEMENTED_NEEDS_BRIDGE`

### Existing components

- `validate_base_cabinet_specification()`
- `ValidationReport`
- `ConstraintViolation`
- `ManufacturingValidationService`
- `ValidationState`
- `ManufacturingValidationReport`
- `ManufacturingValidationSummaryBuilder`
- `ManufacturingValidationSummaryReport`

### Missing bridge or missing implementation

- explicit product-to-manufacturing validation bridge
- explicit translation bridge from engineering validation artifacts to manufacturing summary artifacts when required

### Business priority

- high

### Recommendation

- Keep engineering validation and manufacturing validation separate.
- Add translation only where a product workflow requires manufacturing-readiness summary semantics.

### Risk if built too early

- engineering constraint checks and manufacturing readiness checks will be conflated, making validation harder to reason about.

## 4. Manufacturing Outputs

### Status

`IMPLEMENTED_NEEDS_BRIDGE`

### Existing components

- `build_base_cabinet_manufacturing_outputs_entry()`
- `ManufacturingRuntimePipelineBuilder`
- `ManufacturingCutlistBuilder`
- `ManufacturingPackage`
- `ManufacturingProductionPackageBuilder`
- `ManufacturingProductionPackage`
- `HardwareUsageBuilder`
- `HardwareBomBuilder`

### Missing bridge or missing implementation

- translation bridges for hardware BOM
- translation bridges for manufacturing validation summary
- future bridges for CNC export and other product outputs

### Business priority

- highest

### Recommendation

- Keep Cut List as the first connected output.
- Add further outputs only through explicit translation bridges.

### Risk if built too early

- the outputs facade will become a dumping ground for unverified manufacturing semantics.

## 5. Cost Intelligence

### Status

`IMPLEMENTED_NEEDS_BRIDGE`

### Existing components

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

### Missing bridge or missing implementation

- Base Cabinet-facing cost entry
- explicit product workflow to cost-pipeline orchestration

### Business priority

- high

### Recommendation

- Treat `ManufacturingProductionPackage` as the cost entry point.
- Keep cost logic downstream from validated manufacturing outputs.

### Risk if built too early

- pricing logic will be embedded into product orchestration before the manufacturing contract is stable.

## 6. Optimization / Nesting

### Status

`IMPLEMENTED_NEEDS_BRIDGE`

### Existing components

- `ManufacturingOptimizationPipelineBuilder`
- `ManufacturingOptimizationResult`
- `ManufacturingProjectIntelligencePipelineBuilder`
- `NestingIntelligenceBuilder`
- `OffcutExtractionService`
- `OffcutReportBuilder`
- `OffcutIntelligenceBuilder`
- `WasteIntelligenceBuilder`
- `SheetUtilizationBuilder`
- `IndustrialNestingEngine`
- `SVGNestingExporter`

### Missing bridge or missing implementation

- Base Cabinet-facing optimization bridge
- explicit integration from approved manufacturing outputs into nesting/optimization workflows

### Business priority

- medium to high

### Recommendation

- Keep optimization as a downstream consumer of approved manufacturing artifacts.
- Do not place nesting logic inside product workflow orchestration.

### Risk if built too early

- optimization semantics will leak into product definition and manufacturing-output layers.

## 7. Commercial Outputs

### Status

`IMPLEMENTED_NEEDS_BRIDGE`

### Existing components

- `ManufacturingCommercialPipelineBuilder`
- `ManufacturingCommercialResult`
- `QuotationDocumentV1`
- `QuotationDocumentBuilderV1`
- `FurnitureProjectQuotationBuilder`
- `FurnitureProjectBusinessReportBuilder`
- `FurnitureProjectProfitabilityBuilder`
- `FurnitureProjectQuotationBreakdownBuilder`

### Missing bridge or missing implementation

- Base Cabinet cost/commercial bridge
- explicit product workflow handoff into quotation and profitability artifacts

### Business priority

- high

### Recommendation

- Keep commercial outputs downstream of cost summary and manufacturing validation.
- Use the existing commercial pipeline rather than duplicating it.

### Risk if built too early

- customer-facing quotation logic will be coupled directly to engineering and manufacturing internals.

## 8. SaaS Readiness

### Status

`POSTPONED`

### Existing components

- platform boundary docs
- product workflow contracts
- manufacturing, cost, optimization, and commercial pipelines

### Missing bridge or missing implementation

- productized multi-user SaaS architecture
- service boundaries
- deployment/runtime tenancy model

### Business priority

- later

### Recommendation

- Keep SaaS as a future platform layer, not a current implementation target.
- Stabilize the product pipeline before productizing it.

### Risk if built too early

- architectural seams will be forced open before the domain contracts are stable enough for service boundaries.

## 9. AI / Agent Features

### Status

`POSTPONED`

### Existing components

- domain and pipeline contracts
- structured validation and commercial artifacts

### Missing bridge or missing implementation

- agent orchestration layer
- product-aware reasoning loop
- decision/action approval model

### Business priority

- later

### Recommendation

- Treat AI/agent features as consumers of stable contracts, not as the source of those contracts.

### Risk if built too early

- agents will be forced to reason over incomplete or shifting contracts and will amplify architectural noise.

## Consolidated Matrix

| Layer | Status | Business Priority | Risk if Built Too Early |
| --- | --- | --- | --- |
| Product Definition | `COMPLETE` | Highest | Contract drift across product families |
| Engineering | `COMPLETE` | Highest | Geometry coupling to downstream layers |
| Validation | `IMPLEMENTED_NEEDS_BRIDGE` | High | Conflated engineering and manufacturing validation semantics |
| Manufacturing Outputs | `IMPLEMENTED_NEEDS_BRIDGE` | Highest | Outputs facade becomes a dumping ground |
| Cost Intelligence | `IMPLEMENTED_NEEDS_BRIDGE` | High | Pricing embedded too early into orchestration |
| Optimization / Nesting | `IMPLEMENTED_NEEDS_BRIDGE` | Medium-High | Optimization logic leaks into product workflow |
| Commercial Outputs | `IMPLEMENTED_NEEDS_BRIDGE` | High | Customer-facing logic couples to engineering internals |
| SaaS Readiness | `POSTPONED` | Later | Premature service boundaries |
| AI / Agent Features | `POSTPONED` | Later | Agents reason over unstable contracts |

## Architectural Conclusions

1. The front half of the pipeline is complete or nearly complete: product definition, engineering, and the first manufacturing output are in place.
2. Validation, cost, optimization, and commercial layers are implemented in the repository but still require explicit bridges before they become Base Cabinet product outputs.
3. SaaS and AI/agent capabilities are intentionally later-stage concerns and should not drive the current contract design.
4. The best next work is bridge work, not new engines or new builders.

## Decision

**APPROVED_GAP_MATRIX**

This matrix reflects the current architecture accurately: the core product pipeline is established, the downstream intelligence layers are reusable, and the remaining work is explicit translation and orchestration bridges rather than new foundational systems.
