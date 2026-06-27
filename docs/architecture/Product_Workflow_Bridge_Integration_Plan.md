# Product Workflow Bridge Integration Plan

## Purpose

This plan defines the official integration order for all approved translation and orchestration bridges inside the Product Workflow.

The plan is documentation only. No code changes are made.

## Files Inspected

- `domain/base_cabinet_product_workflow.py`
- `domain/base_cabinet_product_result.py`
- `docs/architecture/`

## 1. Current Product Workflow

`BaseCabinetProductWorkflow` currently performs thin orchestration only:

- accepts `BaseCabinetSpecification`
- creates `BaseCabinetScenario`
- invokes engineering entry
- invokes engineering validation entry
- invokes manufacturing outputs entry
- returns `BaseCabinetProductResult`

### Current status

`APPROVED`

### Responsibility

- orchestration only
- no direct builders
- no direct runtime assembly
- no cost/commercial/optimization logic

## 2. Approved Bridges

Approved bridge categories:

- Validation Bridge
- Manufacturing Outputs Bridge
- Cost Bridge
- Commercial Bridge

These are the only bridge types approved for the product workflow at this stage.

### Current status

`APPROVED`

### Responsibility

- translate stage output from one contract family to the next
- preserve stage ownership
- avoid mixing product logic into bridge code

## 3. Integration Order

The official execution order is:

Product Specification  
↓  
Engineering  
↓  
Validation Bridge  
↓  
Manufacturing Outputs Bridge  
↓  
Cost Bridge  
↓  
Commercial Bridge  
↓  
Product Result

### Current status

`APPROVED`

### Recommendation

- Keep this order stable for Base Cabinet and future furniture products.
- Add new stages only if a new domain boundary is introduced by architecture review.

## 4. ProductResult Evolution

`BaseCabinetProductResult` is the current concrete result contract.

Expected evolution pattern:

- keep `specification`
- keep `scenario`
- keep `engineering`
- keep `validation`
- keep `manufacturing_outputs`
- keep `metadata`
- keep `diagnostics`
- allow future bridge outputs to be attached only when a product workflow explicitly requires them

### Current status

`APPROVED`

### Recommendation

- Preserve the result as a stable aggregation contract.
- Extend only through explicit bridge outputs, not by leaking internal pipeline state.

## 5. Responsibilities of Product Workflow

The product workflow is responsible for:

- owning stage order
- instantiating the scenario
- invoking approved entries/bridges in order
- collecting outputs into `ProductResult`
- preserving metadata and diagnostics as pass-through data

### Current status

`APPROVED`

### Forbidden responsibilities

- direct builder calls
- direct cost logic
- direct commercial logic
- direct optimization logic
- direct runtime engine construction

## 6. Responsibilities of Each Bridge

### Validation Bridge

- translate from engineering validation to manufacturing validation summary semantics when required
- keep engineering and manufacturing validation artifacts distinct

### Manufacturing Outputs Bridge

- translate engineering output into manufacturing outputs
- keep Cut List as the first connected output
- add further outputs only through audited translation paths

### Cost Bridge

- translate manufacturing outputs into cost intelligence inputs
- keep pricing and profitability downstream from manufacturing outputs

### Commercial Bridge

- translate cost outputs into quotation and commercial artifacts
- keep customer-facing documents downstream from validated cost state

### Current status

`APPROVED`

### Recommendation

- Each bridge should own exactly one boundary translation job.
- Bridges should not perform direct engineering or runtime work.

## 7. Forbidden Dependencies

The following dependencies are forbidden inside Product Workflow:

- direct `CabinetBuilder` calls
- direct `ManufacturingRuntimePipelineBuilder` calls
- direct `ManufacturingCutlistBuilder` calls
- direct cost calculations
- direct quotation generation
- direct optimization or nesting execution
- direct commercialization logic

### Current status

`APPROVED`

### Recommendation

- Keep the workflow isolated from implementation detail.
- Let bridges own all translation and orchestration at their respective boundaries.

## 8. Future Reuse

This bridge integration plan should be reused by:

- Wall Cabinet
- Tall Cabinet
- Wardrobe
- Kitchen
- Office Furniture

Reuse rules:

- keep the same stage order
- swap in product-specific specification, scenario, engineering, validation, outputs, and result contracts
- keep bridges boundary-specific rather than product-specific

### Current status

`APPROVED`

### Recommendation

- Reuse the workflow structure across product families.
- Do not duplicate bridge semantics inside each product workflow.

## Decision

**APPROVED_PRODUCT_WORKFLOW_BRIDGES**

The product workflow should remain a thin orchestrator and invoke the approved bridges in the documented order: specification, engineering, validation bridge, manufacturing outputs bridge, cost bridge, commercial bridge, then product result.
