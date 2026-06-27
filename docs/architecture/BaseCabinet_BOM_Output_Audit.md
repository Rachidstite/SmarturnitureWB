# Base Cabinet BOM Output Audit

## Purpose

This audit reviews the existing BOM and Hardware BOM paths to determine whether a BOM output can be safely added next to `Cut List` in `BaseCabinetManufacturingOutputsEntry`.

The audit is documentation only. No code changes are made.

## Files Inspected

- `manufacturing/hardware_bom_builder.py`
- `manufacturing/hardware_bom_report.py`
- `manufacturing/hardware_usage_builder.py`
- `manufacturing/hardware_usage_report.py`
- `manufacturing/manufacturing_package.py`
- `manufacturing/manufacturing_runtime_pipeline_builder.py`
- `manufacturing/manufacturing_production_package_builder.py`
- `tests/manufacturing/`
- `tests/domain/test_base_cabinet_manufacturing_outputs_entry_contract.py`

## Answers

### 1. Is there an existing BOM or Hardware BOM report type?

Yes.

The existing report type is `manufacturing.hardware_bom_report.HardwareBomReport`, with rows represented by `HardwareBomRow`.

### 2. What input does it expect?

`HardwareBomBuilder.build(...)` expects a `hardware_usage_report`.

It reads:

- `hardware_usage_report.hardware_sku_counts`

### 3. Does it consume ManufacturingPackage, hardware_sku_counts, Scene Graph, or metadata?

Indirectly, through `HardwareUsageReport`.

Current chain:

- `Scene Graph` is consumed by `ManufacturingRuntimePipelineBuilder`
- `ManufacturingRuntimePipelineBuilder` produces a `ManufacturingPackage`
- `HardwareUsageBuilder` consumes `ManufacturingPackage.machining_operations`
- `HardwareUsageBuilder` derives `hardware_sku_counts`, `hardware_family_counts`, and `hardware_intent_counts`
- `HardwareBomBuilder` consumes `hardware_usage_report.hardware_sku_counts`

So the BOM builder itself does not consume `Scene Graph` or `ManufacturingPackage` directly.
It also does not consume raw metadata directly; it consumes the already-derived SKU counts.

### 4. Can it be added to BaseCabinetManufacturingOutputsEntry without new engine/builder?

Not safely as a product-level BOM.

The current BOM path is not a product BOM path. It is a hardware BOM path derived from runtime metadata via `HardwareUsageReport`.

That means adding a BOM output beside `Cut List` would require a new translation bridge from the existing manufacturing outputs entry result to a `HardwareUsageReport`, and then to `HardwareBomReport`. The audited `BaseCabinetManufacturingOutputsEntry` does not currently expose that bridge.

### 5. Is it product-level BOM or only hardware BOM?

It is only a hardware BOM.

Evidence:

- the builder is named `HardwareBomBuilder`
- the report is named `HardwareBomReport`
- the source of truth is `hardware_sku_counts`
- the upstream usage builder only counts hardware identity metadata on machining operations

There is no audited product-level BOM contract here.

### 6. What should be avoided?

- Do not call this a product BOM.
- Do not introduce a new BOM engine.
- Do not add a new builder to duplicate the existing hardware BOM path.
- Do not bypass `ManufacturingPackage`.
- Do not infer hardware from geometry or scene graph without the existing usage report chain.
- Do not store BOM logic inside `ManufacturingPackage`.
- Do not add BOM to `BaseCabinetManufacturingOutputsEntry` as if it were already a product-level output.

## Reusable BOM Output Found

The reusable existing artifact is:

- `HardwareBomReport`

But it is reusable only as a hardware BOM artifact, not as a product-level BOM for Base Cabinet outputs.

## Decision

**HARDWARE_BOM_ONLY**

The repository already contains a reusable hardware BOM pipeline, but not a product-level BOM contract suitable for promotion into `BaseCabinetManufacturingOutputsEntry` without an additional audited bridge.

## Summary

Current state:

- Cut List is already supported at the Base Cabinet outputs boundary.
- Hardware usage and hardware BOM exist as separate downstream artifacts.
- The BOM path depends on hardware SKU counts derived from manufacturing runtime metadata.

Conclusion:

- A BOM-like output is present.
- It is hardware-only.
- It should not yet be promoted as a next Base Cabinet outputs entry artifact without additional audit of the translation bridge.
