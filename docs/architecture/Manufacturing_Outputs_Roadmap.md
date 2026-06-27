# Manufacturing Outputs Roadmap

## Purpose

This roadmap defines the official implementation sequence for `BaseCabinetManufacturingOutputsEntry` based only on the completed architecture audits:

- Base Cabinet Product Pipeline Contract
- Base Cabinet Manufacturing Entry Audit
- Scene Graph Engineering-Manufacturing Boundary
- Base Cabinet Manufacturing Validation Output Audit
- Base Cabinet BOM Output Audit

The roadmap is documentation only and does not change code.

## Current Outputs

### 1. Cut List

- Current status: implemented
- Existing reusable components:
  - `build_base_cabinet_engineering_cabinet()`
  - `ManufacturingRuntimePipelineBuilder`
  - `ManufacturingCutlistBuilder`
- Missing bridge:
  - none for the current approved cut list path
- Business priority:
  - highest
  - first safe reusable manufacturing output
- Recommended implementation order:
  - already complete

## Outputs Requiring Translation Bridges

### 2. Hardware BOM

- Current status: reusable hardware BOM artifact exists, but it is not yet a product-level Base Cabinet output
- Existing reusable components:
  - `HardwareUsageBuilder`
  - `HardwareUsageReport`
  - `HardwareBomBuilder`
  - `HardwareBomReport`
  - `ManufacturingPackage`
  - `ManufacturingRuntimePipelineBuilder`
- Missing bridge:
  - a documented translation bridge from `BaseCabinetManufacturingOutputsEntry` to `HardwareUsageReport`
  - then from `HardwareUsageReport` to `HardwareBomReport`
- Business priority:
  - medium
  - useful for downstream commercial and purchasing workflows, but still hardware-only
- Recommended implementation order:
  - after validation summary translation is designed, and before any product BOM work, if hardware purchasing output is desired

### 3. Manufacturing Validation Summary

- Current status: reusable report type exists, but it is not yet safely connected to the Base Cabinet outputs facade
- Existing reusable components:
  - `ManufacturingValidationService`
  - `ManufacturingValidationReport`
  - `ManufacturingValidationSummaryBuilder`
  - `ManufacturingValidationSummaryReport`
  - `ManufacturingProductionPackage`
- Missing bridge:
  - a documented translation bridge from the current validation service output to the validation report / rule-result shape expected by the summary builder
- Business priority:
  - medium to high
  - valuable as an early manufacturing readiness gate
- Recommended implementation order:
  - first among the translation-bridge outputs, because it clarifies validation readiness before broader commercial outputs are added

## Outputs Requiring Additional Architecture

### 4. Product BOM

- Current status: not implemented
- Existing reusable components:
  - hardware-only BOM path exists
  - no audited product BOM contract exists
- Missing bridge:
  - a product-level BOM architecture
  - explicit product-item semantics beyond hardware SKU counts
- Business priority:
  - medium
  - important for commercial completeness, but not safe to infer from the current hardware BOM
- Recommended implementation order:
  - after validation summary and hardware BOM work, once a product-level contract is defined

### 5. CNC Export

- Current status: not implemented as a Base Cabinet output facade artifact
- Existing reusable components:
  - scene graph
  - manufacturing runtime pipeline
  - machining operations already exist in runtime packaging
- Missing bridge:
  - an audited CNC export contract and output format
  - explicit mapping from runtime machining data to export artifacts
- Business priority:
  - high for factory execution
  - still requires dedicated export architecture
- Recommended implementation order:
  - after validation and BOM-related outputs, unless the factory specifically needs export sooner

### 6. Cost Summary

- Current status: not implemented as a Base Cabinet manufacturing output facade artifact
- Existing reusable components:
  - manufacturing runtime package
  - cost-intelligence builders exist elsewhere in the repository
- Missing bridge:
  - an audited product-to-cost translation path for Base Cabinet outputs
- Business priority:
  - medium
  - useful for planning and quoting, but not needed to prove the core manufacturing path
- Recommended implementation order:
  - after BOM and validation outputs, unless commercial planning becomes the primary objective

### 7. Quotation Draft

- Current status: not implemented as a Base Cabinet manufacturing output facade artifact
- Existing reusable components:
  - cost-intelligence layer
  - manufacturing-related summary artifacts
- Missing bridge:
  - a documented commercial pipeline from manufacturing outputs into a quotation draft
- Business priority:
  - high for sales operations
  - downstream of technical manufacturing readiness
- Recommended implementation order:
  - after cost summary

## Recommended Implementation Sequence

1. Manufacturing Validation Summary
2. Hardware BOM
3. Product BOM
4. CNC Export
5. Cost Summary
6. Quotation Draft

Rationale:

- Validation summary should come first because it clarifies readiness before commercial or production outputs expand.
- Hardware BOM is already supported by reusable lower-level artifacts, but needs a translation bridge before it can sit beside Cut List in the Base Cabinet facade.
- Product BOM requires a different contract than hardware BOM and should not be inferred from SKU counts.
- CNC export depends on manufacturing runtime data but needs an explicit export contract.
- Cost summary should follow a stable manufacturing output model.
- Quotation draft is the most downstream and should be built from already-validated outputs.

## Output Status Table

| Output | Status | Reusable Components | Missing Bridge | Business Priority | Recommended Order |
| --- | --- | --- | --- | --- | --- |
| Cut List | Implemented | Engineering Entry, Runtime Pipeline, Cutlist Builder | None | Highest | 1 |
| Manufacturing Validation Summary | Reusable but not yet connected | Validation Service, Validation Report, Summary Builder, Summary Report | Validation translation bridge | Medium-High | 1 |
| Hardware BOM | Reusable hardware-only artifact | Hardware Usage Builder, Hardware Usage Report, Hardware Bom Builder, Hardware Bom Report | Hardware usage bridge from Base Cabinet facade | Medium | 2 |
| Product BOM | Not implemented | Hardware BOM only, no product BOM contract | Product BOM architecture | Medium | 3 |
| CNC Export | Not implemented | Scene Graph, Runtime Package, machining operations | Export contract and formatter | High | 4 |
| Cost Summary | Not implemented | Runtime package, cost-intelligence layer | Base Cabinet cost bridge | Medium | 5 |
| Quotation Draft | Not implemented | Cost and summary layers | Commercial drafting pipeline | High | 6 |

## Decision

**APPROVED_ROADMAP**

This roadmap reflects the current audited state and orders the next manufacturing outputs by reuse safety, bridge complexity, and business value.
