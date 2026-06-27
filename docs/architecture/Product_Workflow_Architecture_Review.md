# Product Workflow Architecture Review

## Purpose

This review evaluates `BaseCabinetProductWorkflow` as a candidate foundation for future furniture product workflows.

The review is documentation only. No code changes are made.

## Files Inspected

- `domain/base_cabinet_product_workflow.py`
- `domain/base_cabinet_product_result.py`
- `domain/base_cabinet_scenario.py`
- `domain/base_cabinet_specification.py`
- `domain/base_cabinet_engineering_entry.py`
- `domain/base_cabinet_specification_validation.py`
- `domain/base_cabinet_manufacturing_outputs_entry.py`
- `tests/domain/test_base_cabinet_product_workflow_contract.py`
- `tests/domain/test_base_cabinet_product_result_contract.py`
- `tests/domain/test_base_cabinet_scenario_contract.py`
- `tests/domain/test_base_cabinet_specification_contract.py`
- `tests/domain/test_base_cabinet_engineering_entry_contract.py`
- `tests/domain/test_base_cabinet_specification_validation_contract.py`
- `tests/domain/test_base_cabinet_manufacturing_outputs_entry_contract.py`
- `docs/product/Cabinet_Manufacturing_Capability_V1.md`
- `docs/architecture/Manufacturing_Outputs_Roadmap.md`

## 1. BaseCabinetProductWorkflow Responsibilities

Current responsibilities:

- accept `BaseCabinetSpecification`
- create a `BaseCabinetScenario`
- invoke the engineering entry
- invoke the validation entry
- invoke the manufacturing outputs entry
- collect the results into `BaseCabinetProductResult`
- copy metadata from the manufacturing outputs result
- copy diagnostics from validation violations

### Recommendation: workflow orchestration

- Status: **APPROVED**
- Reason: the workflow is a thin orchestration layer, not a domain engine. This is the correct level for a product workflow entry.

## 2. Generic Responsibilities

The following responsibilities are generic and should be preserved as a reusable workflow pattern:

- orchestration of ordered product stages
- collecting stage outputs into a stable product result
- keeping metadata and diagnostics as pass-through result fields
- avoiding direct builder usage inside the workflow
- avoiding direct runtime construction inside the workflow

### Recommendation: keep orchestration generic

- Status: **APPROVED**
- Reason: future furniture products can reuse the same stage-driven pattern without inheriting Base Cabinet mechanics.

## 3. Base Cabinet Specific Responsibilities

The following responsibilities are Base Cabinet specific:

- `BaseCabinetSpecification`
- `BaseCabinetScenario`
- `build_base_cabinet_engineering_cabinet()`
- `validate_base_cabinet_specification()`
- `build_base_cabinet_manufacturing_outputs_entry()`
- `BaseCabinetProductResult`
- Base Cabinet metadata semantics
- Base Cabinet diagnostics semantics

### Recommendation: keep product-specific entry points explicit

- Status: **APPROVED**
- Reason: product-specific names prevent accidental cross-product coupling and preserve current API clarity.

### Recommendation: create a generic product workflow only through a new abstraction layer

- Status: **POSTPONED**
- Reason: a generalized workflow should be introduced only after multiple products prove the same stage contract shape.

## 4. Reuse Potential for Future Products

Future products considered:

- Wall Cabinet
- Tall Cabinet
- Wardrobe
- Drawer Unit

### Can they reuse the same workflow structure?

Yes, at the structural level:

- a product specification object
- a scenario object
- an engineering entry
- a validation entry
- a manufacturing outputs entry
- a product result object

But they cannot reuse the current Base Cabinet workflow implementation verbatim because the entry functions and result types are product-specific.

### Recommendation: reuse the workflow shape, not the Base Cabinet identifiers

- Status: **APPROVED**
- Reason: the stage sequence is generic, while the concrete domain adapters and entry functions remain product-specific.

## 5. Architectural Duplication Risks

Observed duplication risks:

- one workflow file per product with copied stage ordering
- one result dataclass per product with the same field inventory
- repeated metadata/diagnostics extraction logic
- repeated orchestration of the same stage chain
- parallel product-specific entry names with no shared contract

### Recommendation: avoid copy-paste workflow scaffolding

- Status: **REJECTED**
- Reason: duplicating the whole workflow body per product would create maintenance drift without adding architectural value.

### Recommendation: avoid duplicating stage-extraction logic

- Status: **REJECTED**
- Reason: metadata and diagnostics should come from shared result contracts, not repeated ad hoc extraction code in each workflow.

## 6. Extension Points Instead of Duplication

Recommended extension points:

- product specification contract
- product scenario contract
- product engineering entry
- product validation entry
- product manufacturing outputs entry
- product result contract

### Recommendation: formalize stage contracts before adding a generalized workflow implementation

- Status: **APPROVED**
- Reason: future workflows should plug into well-defined stages rather than new custom execution paths.

### Recommendation: introduce a shared workflow shape only after at least two additional products need it

- Status: **POSTPONED**
- Reason: the current evidence supports the pattern, but not yet a shared implementation.

## 7. Generalized Product Workflow Architecture

Proposed architecture, without implementation:

- `ProductSpecification`
- `ProductScenario`
- `build_<product>_engineering_entry()`
- `validate_<product>_specification()`
- `build_<product>_manufacturing_outputs_entry()`
- `ProductResult`
- `ProductWorkflow`

Expected behavior:

- workflow accepts a product specification
- workflow creates a scenario
- workflow runs engineering
- workflow runs validation
- workflow runs manufacturing outputs
- workflow returns a frozen result object
- result holds specification, scenario, engineering, validation, manufacturing outputs, metadata, and diagnostics

### Recommendation: define a generalized workflow contract now, but do not implement it yet

- Status: **POSTPONED**
- Reason: the contract is architecturally sound, but implementation would be premature until more product workflows exist.

### Recommendation: keep product-specific entry functions as adapters into the shared shape

- Status: **APPROVED**
- Reason: this is the cleanest way to extend future products without contaminating the workflow with product logic.

## 8. Architectural Conclusions

1. `BaseCabinetProductWorkflow` is a valid foundation pattern.
2. The structure is generic enough to be reused by future furniture products.
3. The current implementation is still Base Cabinet specific by design.
4. The workflow should be treated as an orchestration pattern, not a universal engine.
5. A generalized product workflow should be designed as a contract first, then implemented only when more than one product needs it.

## 9. Final Decision Table

| Recommendation | Status |
| --- | --- |
| Workflow orchestration | APPROVED |
| Keep orchestration generic | APPROVED |
| Keep product-specific entry points explicit | APPROVED |
| Reuse the workflow shape, not Base Cabinet identifiers | APPROVED |
| Avoid copy-paste workflow scaffolding | REJECTED |
| Avoid duplicating stage-extraction logic | REJECTED |
| Formalize stage contracts before adding a generalized workflow implementation | APPROVED |
| Introduce a shared workflow shape only after at least two additional products need it | POSTPONED |
| Define a generalized workflow contract now, but do not implement it yet | POSTPONED |
| Keep product-specific entry functions as adapters into the shared shape | APPROVED |

## Decision

**APPROVED**

`BaseCabinetProductWorkflow` is a reasonable foundation pattern for future furniture product workflows, provided it remains a thin orchestrator and future products use their own product-specific entries and result types.
