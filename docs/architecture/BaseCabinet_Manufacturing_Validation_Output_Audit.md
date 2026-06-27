# Base Cabinet Manufacturing Validation Output Audit

## Purpose

This audit reviews the existing manufacturing validation path to determine the official reusable validation output that should be considered next beside `BaseCabinetManufacturingOutputsEntry`.

The audit is documentation only. No code changes are made.

## Files Inspected

- `services/manufacturing_validation_service.py`
- `validation/__init__.py`
- `validation/validator_registry.py`
- `validation/panel_spec_validator.py`
- `validation/manufacturing_feasibility_validator.py`
- `manufacturing/manufacturing_validation_builder.py`
- `manufacturing/manufacturing_validation_report.py`
- `manufacturing/manufacturing_validation_summary_builder.py`
- `manufacturing/manufacturing_validation_summary_report.py`
- `manufacturing/manufacturing_production_package_builder.py`
- `manufacturing/manufacturing_production_package.py`
- `manufacturing/manufacturing_release_validator.py`
- `tests/manufacturing/test_manufacturing_validation_builder.py`
- `tests/manufacturing/test_manufacturing_validation_report.py`
- `tests/manufacturing/test_manufacturing_validation_summary_builder.py`
- `tests/manufacturing/test_manufacturing_validation_summary_report.py`
- `tests/manufacturing/test_manufacturing_production_package_contract.py`
- `tests/manufacturing/test_manufacturing_release_validator.py`
- `tests/test_manufacturing_validation_service.py`
- `tests/domain/test_base_cabinet_manufacturing_outputs_entry_contract.py`

## Answers

### 1. Is there an existing Manufacturing Validation Summary report type?

Yes.

`manufacturing.manufacturing_validation_summary_report.ManufacturingValidationSummaryReport` already exists as a dedicated dataclass.

### 2. What input does it expect?

The summary builder expects:

- a `ManufacturingValidationReport`
- a list of `OperationalRuleResult`

The report type itself is just the output container. It does not compute its own values.

### 3. Does it consume Scene Graph, ManufacturingPackage, ProductionPackage, or ValidationReport?

Not directly.

Current consumption is:

- `ManufacturingValidationService` consumes `Scene Graph` and returns `ValidationState`
- `build_manufacturing_validation_report(...)` consumes rule results, not a scene graph or package
- `build_manufacturing_validation_summary_report(...)` consumes `ManufacturingValidationReport` plus rule results
- `ManufacturingProductionPackage` can store a `validation_summary_report`, but the builder does not currently populate it

So the summary output is structurally supported, but the current validation service path does not produce the required intermediate report objects.

### 4. Can it be added to BaseCabinetManufacturingOutputsEntry without new engine/builder?

Not safely with the current audited path.

The existing Base Cabinet manufacturing facade already reuses:

- engineering entry
- scene graph
- manufacturing runtime pipeline
- cut list builder

However, the manufacturing validation service returns `ValidationState`, while the summary builder expects `ManufacturingValidationReport` plus `OperationalRuleResult`. There is no audited bridge from the current service result to the summary builder output.

That means adding `ManufacturingValidationSummaryReport` to `BaseCabinetManufacturingOutputsEntry` would require additional translation logic or a new integration bridge, which is outside the current approved reuse boundary.

### 5. What should be avoided?

- Do not add a parallel validation engine.
- Do not add a new builder just to duplicate existing validation contracts.
- Do not bypass `Scene Graph`.
- Do not force `ValidationState` into a summary report shape without audited translation rules.
- Do not couple manufacturing validation output to FreeCAD or UI behavior.
- Do not expand the outputs entry with unverified validation, BOM, hardware, or CNC branches.

### 6. Should the next output be:

- `ManufacturingValidationSummaryReport`
- `ManufacturingValidationService` result
- `ValidationReport`
- `ProductionPackage` validation summary

**Audit conclusion:** the intended reusable product-level validation artifact is `ManufacturingValidationSummaryReport`, and the closest existing storage location is the `validation_summary_report` field on `ManufacturingProductionPackage`.

**But** the next Base Cabinet output should be postponed until the validation bridge is audited, because the current service returns `ValidationState` and does not directly feed the summary builder contract.

## Decision

**POSTPONED**

The reusable validation output type is already present, but adding it to `BaseCabinetManufacturingOutputsEntry` is not yet safe without a documented bridge from the current validation service output to the summary report contract.

## Summary

Current state:

- validation service exists
- summary report type exists
- production package can hold a validation summary
- Base Cabinet outputs entry currently reaches Cut List only

Next step:

- audit and document the validation translation path before promoting a validation summary into the Base Cabinet outputs facade
