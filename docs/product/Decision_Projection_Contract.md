# Decision Projection Contract

## Purpose

This contract defines the official read-only projection for release review.

Its job is to organize existing manufacturing, release, and commercial objects into a single decision surface so a user can answer:

- Is the project ready for production?
- If not, why?
- What warnings exist?
- Are manufacturing outputs complete?
- Are assembly outputs complete?
- Are commercial outputs ready?
- What should the user do next?

This is not backend capability. It is a stable contract for future report generation or UI presentation.

## Scope

Included in this contract:

- release review projection
- readiness summarization
- blocker and warning grouping
- manufacturing output status projection
- assembly output status projection
- commercial output status projection
- visualization status projection
- recommended next actions projection

The projection must only use existing source objects and must preserve their references whenever available.

## Non-goals

This contract does not:

- compute manufacturing validity
- compute commercial profitability
- recompute warnings
- modify release status
- add a new workflow layer
- add a new engine
- duplicate validation logic
- duplicate decision logic
- replace existing manufacturing or commercial objects

## Inputs

Approved inputs:

- `ManufacturingDecision`
- `ManufacturingValidationSummaryReport`
- `ManufacturingProductionPackage`
- `FactoryReleasePackage`
- `CommercialPackageReport`
- `QuotationDocumentV1`

Optional inputs, only if already available from the existing pipeline:

- production visualization evidence
- production visualization coverage summary

No new source objects are introduced by this contract.

## Outputs

The projection should present the following sections:

1. Readiness Summary
2. Blocking Issues
3. Warning Summary
4. Manufacturing Output Status
5. Assembly Status
6. Commercial Status
7. Visualization Status
8. Recommended Next Actions
9. Release Decision

The projection output is expected to be a passive view model with normalized display fields, not a decision engine.

## Field Mapping

| Section | Field name | Source object | Source field | Meaning | User decision supported |
|---|---|---|---|---|---|
| Readiness Summary | `ready_for_production` | `ManufacturingDecision` | `ready_for_production` | Whether the project is production-ready | Go / no-go |
| Readiness Summary | `decision_status` | `ManufacturingDecision` | `status` | Compact readiness state | Approve / hold / reject |
| Blocking Issues | `blocking_reasons` | `ManufacturingDecision` | `blocking_reasons` | Reasons that must be fixed first | Fix-first decision |
| Blocking Issues | `blocking_messages` | `ManufacturingValidationSummaryReport` | `blocking_messages` | Validation blockers reported upstream | Fix-first decision |
| Warning Summary | `warning_reasons` | `ManufacturingDecision` | `warning_reasons` | Non-blocking concerns | Review / accept with warnings |
| Warning Summary | `warning_messages` | `ManufacturingValidationSummaryReport` | `warning_messages` | Validation warnings reported upstream | Review / accept with warnings |
| Manufacturing Output Status | `cut_list` | `FactoryReleasePackage` | `cut_list` | Panel cutting evidence is present | Output completeness |
| Manufacturing Output Status | `hardware_bom` | `FactoryReleasePackage` | `hardware_bom` | Hardware evidence is present | Output completeness |
| Manufacturing Output Status | `cnc_package` | `FactoryReleasePackage` | `cnc_package` | CNC evidence is present | Output completeness |
| Assembly Status | `assembly_package` | `FactoryReleasePackage` | `assembly_package` | Workshop-readable assembly content is present | Workshop readiness |
| Assembly Status | `assembly_rows` | `ManufacturingProductionPackage` | `assembly_report.rows` | Assembly package has structured rows | Workshop readiness |
| Commercial Status | `commercial_report` | `CommercialPackageReport` | `estimated_price`, `margin_amount`, `margin_percent`, `warnings` | Commercial boundary summary | Quotation / release proceed |
| Commercial Status | `quotation_document` | `QuotationDocumentV1` | `total_amount`, `currency`, `quotation_number` | Customer-facing quotation is present | Quote approval |
| Visualization Status | `visualization_evidence` | optional visualization evidence | existing evidence summary | Production-backed visualization is available | Visual fidelity check |
| Recommended Next Actions | `recommended_action` | `ManufacturingDecision` | `recommended_action` | The next action already recommended by the system | Fix / release / quote |
| Release Decision | `release_ready` | `ManufacturingProductionPackage` | `release_ready` | Production package readiness | Release / hold |

## Rules

- The projection is read-only.
- The projection does not compute manufacturing validity.
- The projection does not compute commercial profitability.
- The projection does not recompute warnings.
- The projection does not modify release status.
- The projection may normalize existing values for display.
- The projection may group existing warnings and blockers.
- The projection must preserve source references when available.
- The projection must be safe for future UI or report generation.

## Exclusions

The contract explicitly excludes:

- ERP logic
- MES logic
- inventory planning
- procurement planning
- scheduling
- shop-floor dispatch
- new quotation engines
- new validation engines
- new dashboard systems
- customer portal behavior

These belong to later phases after pilot validation.

## Gap Classification

The remaining gaps are classified as follows:

- Presentation-only
  - no single release-review surface exists yet
  - information is present but not unified for the user
- Passive summary
  - a read-only projection can safely organize the existing objects
- Real backend gap
  - none proven for the release-review decision itself
- Post-pilot gap
  - scheduling, ERP, MES, procurement, and dispatch concerns

The current evidence does not justify backend work for release review.

## Future Implementation Shape

If approved later, the implementation should be a passive report/view model such as:

- `FactoryDecisionWorkspaceReport`

Its shape should:

- be read-only
- be built from existing release/commercial/manufacturing objects
- avoid new engines
- avoid duplicate decision logic
- avoid duplicate validation logic
- preserve backward compatibility

The projection may later support UI, document generation, or export surfaces without changing the source objects.
