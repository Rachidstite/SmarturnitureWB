# Product Validation Bridge Audit

## Purpose

This audit reviews the existing validation stack and determines the correct bridge from `BaseCabinetProductWorkflow` to the existing validation summary artifacts.

The audit is documentation only. No code changes are made.

## Files Inspected

- `domain/base_cabinet_product_workflow.py`
- `domain/base_cabinet_specification_validation.py`
- `services/manufacturing_validation_service.py`
- `manufacturing/manufacturing_validation_summary_builder.py`
- `manufacturing/manufacturing_validation_summary_report.py`
- `manufacturing/manufacturing_validation_builder.py`
- `manufacturing/manufacturing_validation_report.py`
- `validation/`
- `tests/`

## Existing Validation Flow

### Engineering validation flow

`BaseCabinetProductWorkflow` currently calls:

- `validate_base_cabinet_specification()`

That function:

- adapts `BaseCabinetSpecification`
- creates an engineering validation project shape
- calls `CabinetConstraintValidator.validate_all()`
- returns `ValidationReport`

This is the current validation path used by the Base Cabinet product workflow.

### Manufacturing validation flow

`ManufacturingValidationService.validate(scene_graph)` currently:

- accepts a `scene_graph`
- extracts manufacturing specs with `ManufacturingExtractor`
- runs each validator in `VALIDATORS`
- returns `ValidationState`

This is a separate manufacturing validation path and is not yet connected to the Base Cabinet product workflow.

## Validation Artifacts

Existing validation artifacts include:

- `ValidationReport`
- `ValidationState`
- `ManufacturingValidationReport`
- `OperationalRuleResult`

### Recommendation: keep both validation artifact families

- Status: **APPROVED**
- Reason: the engineering validation and manufacturing validation contracts serve different purposes and should not be collapsed into one object.

## Validation Summary Artifacts

Existing summary artifacts include:

- `ManufacturingValidationSummaryReport`
- `build_manufacturing_validation_summary_report()`

The summary builder expects:

- a `ManufacturingValidationReport`
- a list of `OperationalRuleResult`

This means the summary artifact is not a direct consumer of `ValidationReport` or `ValidationState`.

### Recommendation: treat the summary report as a downstream manufacturing artifact

- Status: **APPROVED**
- Reason: the summary report is already designed as a manufacturing readiness summary, not a generic product-validation object.

## Current Base Cabinet Integration

Current Base Cabinet workflow behavior:

- product workflow creates `BaseCabinetScenario`
- product workflow runs engineering
- product workflow runs `validate_base_cabinet_specification()`
- product workflow runs manufacturing outputs entry
- product workflow stores diagnostics from engineering validation violations

Current Base Cabinet workflow does **not** yet:

- call `ManufacturingValidationService`
- build `ManufacturingValidationReport`
- build `ManufacturingValidationSummaryReport`
- attach a manufacturing validation summary to `BaseCabinetProductResult`

### Recommendation: keep the current workflow unchanged until the bridge contract is explicit

- Status: **APPROVED**
- Reason: the workflow currently has a valid engineering validation path; it should not be forced to consume manufacturing validation artifacts prematurely.

## Missing Bridge

The missing bridge is:

- a documented translation path from the Base Cabinet product workflow into the manufacturing validation summary contract

In practical terms, the current stack is missing:

- a bridge from product workflow to manufacturing validation service output
- a bridge from `ValidationState` to the manufacturing validation report family, if the engineering-side result is intended to inform manufacturing readiness
- a bridge from manufacturing validation report to `ManufacturingValidationSummaryReport`

The important constraint is that the summary builder expects a manufacturing validation report plus rule results, not the engineering `ValidationReport` returned by `validate_base_cabinet_specification()`.

### Recommendation: use an explicit validation bridge rather than direct reuse of engineering validation output

- Status: **APPROVED**
- Reason: the contract mismatch is architectural, not cosmetic.

### Recommendation: do not force `ValidationReport` into the manufacturing summary builder

- Status: **REJECTED**
- Reason: the summary builder contract does not accept `ValidationReport`, and forcing that reuse would blur the engineering/manufacturing boundary.

## Reusable Components

Reusable validation components already present in the repository:

- `BaseCabinetSpecificationAdapter`
- `CabinetConstraintValidator`
- `ValidationReport`
- `ManufacturingValidationService`
- `ValidationState`
- `ManufacturingValidationBuilder`
- `ManufacturingValidationReport`
- `ManufacturingValidationSummaryBuilder`
- `ManufacturingValidationSummaryReport`
- `ManufacturingProductionPackage.validation_summary_report`

### Recommendation: reuse the existing validation layers instead of introducing a third validation family

- Status: **APPROVED**
- Reason: the repository already has the necessary contracts; the missing work is connection and translation, not new validation engines.

## Business Value

This bridge matters because it would:

- separate engineering correctness from manufacturing readiness
- support consistent product-level readiness reporting
- enable later commercial and release workflows to depend on a validated manufacturing state
- reduce rework by making validation outputs explicit and stage-specific

## Recommendation

### Recommended bridge shape

1. Keep `validate_base_cabinet_specification()` as the engineering validation entry.
2. Use `ManufacturingValidationService` as the manufacturing validation entry when scene-graph-level readiness is required.
3. Convert manufacturing validation results into `ManufacturingValidationReport` through the existing manufacturing validation builder.
4. Convert that report plus rule results into `ManufacturingValidationSummaryReport`.
5. Attach the summary only when a product workflow explicitly needs manufacturing readiness summary semantics.

### Recommendation: add the bridge only through a documented stage translation path

- Status: **APPROVED**
- Reason: this keeps the product workflow clean and prevents validation semantics from being conflated.

### Recommendation: postpone attaching the manufacturing validation summary to Base Cabinet product workflow until the bridge is wired by contract

- Status: **POSTPONED**
- Reason: the current Base Cabinet workflow has no manufacturing-validation summary contract yet, and the summary builder input shape does not match engineering validation output.

## Stage Classification

| Stage | Classification |
| --- | --- |
| Engineering validation (`validate_base_cabinet_specification`) | `IMPLEMENTED_AND_CONNECTED` |
| Manufacturing validation service (`ManufacturingValidationService`) | `IMPLEMENTED_NOT_CONNECTED` |
| Manufacturing validation report (`ManufacturingValidationReport`) | `IMPLEMENTED_NOT_CONNECTED` |
| Manufacturing validation summary (`ManufacturingValidationSummaryReport`) | `IMPLEMENTED_NOT_CONNECTED` |
| Product workflow to manufacturing validation summary bridge | `MISSING` |

## Decision

**APPROVED_VALIDATION_BRIDGE**

The correct direction is to preserve the engineering validation path in `BaseCabinetProductWorkflow` and connect manufacturing validation summary artifacts through an explicit translation bridge rather than forcing the current engineering validation result into the manufacturing summary contract.
