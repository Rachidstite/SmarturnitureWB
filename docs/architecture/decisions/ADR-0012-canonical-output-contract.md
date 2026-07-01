# ADR-0012
Canonical Output Contract

## Status

Accepted

## Context

The verified downstream workflow in SmartFurnitureWB is:

`ProductConfiguration`
→ `ProjectApplicationService`
→ `BaseCabinetProductWorkflow`
→ Engineering
→ Manufacturing
→ Cost
→ Commercial
→ Quotation

Architecture Gate Phase 5 audited the downstream contracts produced after the
full product workflow in order to determine which object is the canonical
runtime handoff and which objects are derived reports, exports, or foundation
artifacts.

## Evidence

The following downstream objects are present in the repository and were
verified during the architecture audit.

### `ManufacturingCommercialResult`

Produced by:

- `cost_intelligence.manufacturing_commercial_pipeline_builder`

How it is produced:

- `BaseCabinetProductWorkflow._build_commercial_bridge(...)` calls
  `ManufacturingCommercialPipelineBuilder().build(...)`
- the builder returns `ManufacturingCommercialResult`

Contents verified in repository:

- `manufacturing_cost_summary`
- `manufacturing_quotation_input`
- `quotation_report`
- `profitability_report`
- `quotation_intelligence_report`

### `QuotationReport`

Produced by:

- `cost_intelligence.manufacturing_quotation_report_builder`
- inside `ManufacturingCommercialPipelineBuilder`

How it is produced:

- `ManufacturingCommercialPipelineBuilder` builds a
  `ManufacturingQuotationInput`
- `ManufacturingQuotationReportBuilder().build(...)` returns `QuotationReport`

### `QuotationDocumentV1`

Produced by:

- `cost_intelligence.quotation_document_builder.QuotationDocumentBuilderV1`

How it is produced:

- `BaseCabinetProductWorkflow._build_commercial_bridge(...)` reads
  `commercial_result.quotation_report`
- `QuotationDocumentBuilderV1().build(...)` transforms the `QuotationReport`
  plus quotation metadata into `QuotationDocumentV1`

It is exported by:

- `exports.quotation_document_export.QuotationDocumentExport`

### `CommercialPackageReport`

Produced by:

- `commercial_outputs.commercial_package_builder.CommercialPackageBuilder`

How it is produced:

- `CommercialPackageBuilder().build(cost_report)` transforms
  `CostPackageReport` into `CommercialPackageReport`

Repository evidence shows this is a passive foundation component with no
pricing policy, quotation formatting, tax, discount, or currency logic.

### `CustomerPackageReport`

Produced by:

- `customer_outputs.customer_package_builder.CustomerPackageBuilder`

How it is produced:

- `CustomerPackageBuilder().build(commercial_report)` transforms
  `CommercialPackageReport` into `CustomerPackageReport`

Repository evidence shows this customer-facing artifact is built from the
foundation commercial path, not from the runtime commercial workflow.

### `CostPackageReport`

Produced by:

- `cost_intelligence.cost_package_builder.CostPackageBuilder`

How it is produced:

- `CostPackageBuilder().build(package)` transforms `FactoryReleasePackage`
  into `CostPackageReport`

Repository evidence shows this is a passive foundation component for
cost-relevant evidence available from `FactoryReleasePackage`.

## Decision

Canonical Runtime Contract:

- `ManufacturingCommercialResult`

Derived runtime report:

- `QuotationReport`

Export artifact:

- `QuotationDocumentV1`

Foundation components:

- `CostPackageReport`
- `CommercialPackageReport`

Customer artifact:

- `CustomerPackageReport`

Internal DTOs:

- `ManufacturingQuotationInput`
- `ManufacturingCostSummary`

## Rationale

`ManufacturingCommercialResult` is the canonical runtime contract because it is
the richest semantic representation produced by the full product workflow after
commercial processing. Repository evidence shows that it carries the runtime
commercial state required for downstream work:

- cost summary
- quotation input
- quotation report
- profitability
- quotation intelligence

`QuotationReport` is narrower than `ManufacturingCommercialResult` and is
produced inside the commercial runtime pipeline. It is therefore a derived
runtime report, not the primary workflow handoff.

`QuotationDocumentV1` must remain a derived export artifact because repository
evidence shows it is created by transforming `QuotationReport` together with
external quotation metadata. It is then consumed by `QuotationDocumentExport`.
It is a document-facing artifact, not the runtime orchestration contract.

`CustomerPackageReport` is currently outside the runtime workflow because
repository evidence shows it is produced from `CommercialPackageReport`, while
the full product workflow produces `ManufacturingCommercialResult` and
`QuotationDocumentV1`. The customer package foundation therefore exists on a
separate downstream path.

`CostPackageReport` and `CommercialPackageReport` remain foundation components
because they are produced by passive builders over narrower upstream contracts:

- `FactoryReleasePackage -> CostPackageReport`
- `CostPackageReport -> CommercialPackageReport`

They are valid supported artifacts, but they are not the canonical runtime
handoff of the full product workflow.

## Consequences

Future integrations should consume `ManufacturingCommercialResult`.

Quotation, PDF, Excel, REST, SaaS, and customer-facing exports should derive
from the canonical runtime contract instead of becoming peer runtime contracts.

The foundation path remains supported but is not the runtime workflow handoff.

## Deferred Technical Debt

- Manufacturing rebuilds engineering internally.
- Foundation output path and runtime output path remain intentionally separate.
- Customer outputs are not yet integrated into `ProjectApplicationService`.

## References

Relevant modules inspected during Architecture Gates 3–5:

- `application/project_application_service.py`
- `application/engineering_application_service.py`
- `application/manufacturing_application_service.py`
- `application/application_service_result.py`
- `domain/base_cabinet_product_workflow.py`
- `domain/base_cabinet_product_result.py`
- `domain/product_configuration.py`
- `domain/product_configuration_base_cabinet_adapter.py`
- `cost_intelligence/manufacturing_cost_pipeline_builder.py`
- `cost_intelligence/manufacturing_commercial_pipeline_builder.py`
- `cost_intelligence/manufacturing_commercial_result.py`
- `cost_intelligence/manufacturing_cost_summary.py`
- `cost_intelligence/manufacturing_quotation_input.py`
- `cost_intelligence/quotation_report.py`
- `cost_intelligence/quotation_document_builder.py`
- `cost_intelligence/quotation_document.py`
- `cost_intelligence/cost_package_builder.py`
- `cost_intelligence/cost_package_report.py`
- `commercial_outputs/commercial_package_builder.py`
- `commercial_outputs/commercial_package_report.py`
- `customer_outputs/customer_package_builder.py`
- `customer_outputs/customer_package_report.py`
- `exports/quotation_document_export.py`
- `tests/integration/test_end_to_end_pipeline.py`
- `tests/cost_intelligence/test_quotation_document_builder.py`
- `tests/test_commercial_outputs/test_commercial_package_foundation.py`
- `tests/test_customer_outputs/test_customer_package_foundation.py`
- `tests/application/test_project_application_service_product_configuration_contract.py`
