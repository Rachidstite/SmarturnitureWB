# Validation Translation Layer Architecture

## Purpose

This document reviews the architectural translation layer between engineering validation and manufacturing validation, and defines the official translation pattern for future product pipelines.

The review is documentation only. No code changes are made.

## Files Inspected

- `domain/diagnostics.py`
- `domain/base_cabinet_specification_validation.py`
- `services/manufacturing_validation_service.py`
- `manufacturing/manufacturing_validation_builder.py`
- `manufacturing/manufacturing_validation_report.py`
- `manufacturing/manufacturing_validation_summary_builder.py`
- `manufacturing/manufacturing_validation_summary_report.py`
- `domain/base_cabinet_product_workflow.py`
- `docs/product/Cabinet_Manufacturing_Capability_V1.md`
- `tests/domain/test_base_cabinet_specification_validation_contract.py`
- `tests/domain/test_base_cabinet_product_workflow_contract.py`
- `tests/test_manufacturing_validation_service.py`
- `tests/manufacturing/test_manufacturing_validation_builder.py`
- `tests/manufacturing/test_manufacturing_validation_report.py`
- `tests/manufacturing/test_manufacturing_validation_summary_builder.py`
- `tests/manufacturing/test_manufacturing_validation_summary_report.py`

## 1. Engineering Validation Artifacts

Engineering validation currently uses:

- `ValidationReport`
- `ConstraintViolation`

`validate_base_cabinet_specification()` adapts `BaseCabinetSpecification`, builds an engineering validation project shape, and returns `ValidationReport`.

### Recommendation: keep engineering validation artifacts distinct

- Status: **APPROVED**
- Reason: engineering validation is a structural/constraint-level contract and should remain separate from manufacturing readiness contracts.

## 2. Manufacturing Validation Artifacts

Manufacturing validation currently uses:

- `ValidationState`
- `ManufacturingValidationReport`
- `OperationalRuleResult`

`ManufacturingValidationService.validate(scene_graph)` returns `ValidationState`.

`build_manufacturing_validation_report(rule_results)` converts rule results into `ManufacturingValidationReport`.

### Recommendation: keep manufacturing validation artifacts distinct from engineering validation artifacts

- Status: **APPROVED**
- Reason: manufacturing validation describes rule outcomes and readiness counts, not engineering constraint violations.

## 3. Validation Summary Artifacts

The summary layer currently uses:

- `ManufacturingValidationSummaryReport`
- `build_manufacturing_validation_summary_report(validation_report, rule_results)`

This summary layer is a downstream manufacturing readiness summary, not a direct engineering validation container.

### Recommendation: treat the summary report as the final manufacturing validation artifact

- Status: **APPROVED**
- Reason: the summary layer is intended to aggregate manufacturing validation into a compact readiness view.

## 4. Translation Boundaries

There are two important boundaries:

1. Engineering validation boundary
   - input: `BaseCabinetSpecification`
   - output: `ValidationReport`

2. Manufacturing validation boundary
   - input: `scene_graph`
   - output: `ValidationState`, then `ManufacturingValidationReport`, then `ManufacturingValidationSummaryReport`

### Recommendation: do not collapse the two boundaries into one artifact

- Status: **APPROVED**
- Reason: the two validation domains answer different questions and have different consumers.

## 5. Translation Responsibilities

The translation layer should be responsible for:

- preserving the engineering validation result untouched
- preserving the manufacturing validation result untouched
- converting rule-level results into manufacturing report counts
- converting manufacturing counts into a summary report
- preserving source provenance in the `source` field where applicable

### Recommendation: keep translation responsibility narrow and explicit

- Status: **APPROVED**
- Reason: translation should normalize shape, not redefine meaning.

## 6. Allowed Data Flow

Allowed flows are:

- `BaseCabinetSpecification` -> `ValidationReport`
- `scene_graph` -> `ValidationState`
- `OperationalRuleResult` -> `ManufacturingValidationReport`
- `ManufacturingValidationReport` + `OperationalRuleResult` -> `ManufacturingValidationSummaryReport`
- product workflow -> engineering validation -> manufacturing validation -> summary artifact

### Recommendation: allow only staged, contract-based validation flow

- Status: **APPROVED**
- Reason: this keeps the architecture composable and avoids hidden coupling.

## 7. Forbidden Direct Conversions

Forbidden direct conversions are:

- `ValidationReport` -> `ManufacturingValidationSummaryReport`
- `ValidationState` -> `ManufacturingValidationSummaryReport`
- `ValidationReport` -> `ManufacturingValidationReport` without an explicit translation contract
- `scene_graph` -> `ManufacturingValidationSummaryReport`
- product workflow -> summary report without passing through a manufacturing validation contract

### Recommendation: reject direct cross-family validation conversions

- Status: **REJECTED**
- Reason: direct conversion would blur engineering and manufacturing semantics and bypass the translation layer.

## 8. Product Workflow Implications

`BaseCabinetProductWorkflow` currently uses engineering validation (`validate_base_cabinet_specification`) and stores diagnostics from that result.

It does not yet call the manufacturing validation service or materialize a manufacturing validation summary artifact.

### Recommendation: keep `BaseCabinetProductWorkflow` using engineering validation as its current validation contract

- Status: **APPROVED**
- Reason: the product workflow should not invent a summary bridge until the manufacturing validation path is intentionally wired.

### Recommendation: add a separate manufacturing validation bridge only when a product workflow explicitly needs readiness summary semantics

- Status: **POSTPONED**
- Reason: the bridge is architecturally valid but not yet required by the current Base Cabinet workflow contract.

## 9. Future Reuse

### Cost

The translation-layer pattern should be reused by cost pipelines as:

- validated manufacturing inputs -> cost summary inputs -> cost summary outputs

### Commercial Outputs

The translation-layer pattern should be reused by commercial pipelines as:

- validated manufacturing/cost outputs -> quotation inputs -> quotation reports -> documents

### Optimization

The translation-layer pattern should be reused by optimization pipelines as:

- manufacturing outputs -> utilization/offcut/waste/nesting inputs -> optimization reports

### Recommendation: reuse the staged translation model for cost, commercial, and optimization layers

- Status: **APPROVED**
- Reason: these downstream domains already work as pipelines and benefit from explicit contract translation.

### Recommendation: do not let cost or commercial layers consume raw engineering validation artifacts directly

- Status: **REJECTED**
- Reason: cost and commercial pipelines should depend on normalized manufacturing-ready outputs, not raw engineering diagnostics.

## 10. Architectural Conclusions

1. Engineering validation and manufacturing validation are separate artifact families.
2. Manufacturing validation summary is a downstream artifact of the manufacturing validation family.
3. The correct architecture is translation, not substitution.
4. `ValidationReport`, `ValidationState`, `ManufacturingValidationReport`, and `ManufacturingValidationSummaryReport` each serve a different level of the pipeline.
5. The Base Cabinet workflow should preserve the current engineering validation contract until a manufacturing validation bridge is intentionally introduced.

## Decision

**APPROVED_TRANSLATION_LAYER**

The official pattern is a staged translation layer: engineering validation remains engineering-specific, manufacturing validation remains manufacturing-specific, and the summary layer consumes the manufacturing validation family rather than raw engineering validation artifacts.
