# Furniture Domain Architecture

## 1. Purpose

This document defines the furniture domain concepts behind SmartFurnitureWB.
It is written in factory and domain language, not software-class language.

The goal is to describe the reusable furniture knowledge that SmartFurnitureWB
models across product families.

## 2. Domain Vision

SmartFurnitureWB should model furniture as a chain of reusable knowledge:

`Product`
→ `Engineering`
→ `Manufacturing`
→ `Cost`
→ `Commercial`
→ `Customer Output`

The repository evidence shows this chain already exists in executable form for
the base-cabinet path and in foundation form for downstream cost/commercial
outputs.

## 3. Core Domain Objects

The following objects are domain concepts in factory language:

- Furniture Project
- Cabinet
- Product Family
- Product Configuration
- Cabinet Section
- Opening
- Panel
- Carcass
- Back Panel
- Shelf
- Door
- Drawer
- Hardware
- Material
- Assembly
- Manufacturing Operation
- Factory Release
- Quotation
- Customer Output

These concepts describe the furniture business domain independently of the
software implementation.

## 4. Engineering Knowledge Areas

The engineering domain for furniture includes:

- Geometry Knowledge
- Construction Knowledge
- Support Strategy
- Mounting Strategy
- Opening Strategy
- Storage Strategy
- Movement Strategy
- Hardware Strategy
- Material Strategy
- Validation Knowledge

Repository evidence shows that the executable engineering path already carries
construction, joinery, panel, shelf, door, back-panel, and validation
knowledge for the base-cabinet family.

## 5. Manufacturing Knowledge Areas

Manufacturing knowledge in the furniture domain includes:

- Cutting
- Edge Banding
- Drilling
- CNC Machining
- Assembly
- Packaging
- Quality Control
- Waste / Offcut handling

The current repository demonstrates that manufacturing evidence is produced
from engineering output and then converted into manufacturing packages and
factory release evidence.

## 6. Commercial Knowledge Areas

Commercial knowledge in the furniture domain includes:

- Material Cost
- Hardware Cost
- Manufacturing Cost
- Waste Cost
- Profitability
- Quotation
- Customer-facing output

The repository currently distinguishes between:

- runtime commercial/quotation evidence
- passive commercial foundation output
- customer-facing foundation output

## 7. Product Family Interpretation

Product families should be understood as compositions of domain knowledge, not
as isolated software systems.

### Base Cabinet

Repository evidence shows the base-cabinet family as:

- floor support
- optional toe kick
- carcass
- doors / drawers / shelves
- manufacturing outputs

### Wall Cabinet

Repository evidence shows wall-cabinet catalog knowledge as:

- wall mounting
- no toe kick
- suspension hardware
- reduced depth
- mounting validation

The wall-cabinet family is currently catalog data only and not yet wired into
the executable product workflow.

### Tall Cabinet

Repository evidence shows tall-cabinet catalog knowledge as:

- vertical storage
- stability / overturn risk
- multiple sections
- possibly wall fixing

The tall-cabinet family is currently catalog data only and not yet wired into
the executable product workflow.

## 8. Current Repository Mapping

The following repository objects map to domain concepts:

- `ProductFamily`
  - product family knowledge and defaults
- `ProductConfiguration`
  - a user-selected product intent and dimension contract
- `BaseCabinetSpecification`
  - a specialized engineering contract for the executable base-cabinet path
- `CabinetParams`
  - an execution-oriented cabinet contract broader than `BaseCabinetSpecification`
- `WallMountCapability`
  - an existing extension vocabulary for mounting semantics
- `ManufacturingCommercialResult`
  - the canonical runtime commercial contract
- `FactoryReleasePackage`
  - the factory-release evidence contract
- `CostPackageReport`
  - the passive cost foundation report
- `CommercialPackageReport`
  - the passive commercial foundation report
- `CustomerPackageReport`
  - the passive customer-facing foundation report

Clarifications supported by repository evidence:

- `BaseCabinetSpecification` is a specialized engineering contract.
- `CabinetParams` is an execution-oriented contract.
- `WallMountCapability` is existing extension vocabulary.
- `ManufacturingCommercialResult` is the canonical runtime commercial contract.

## 9. Boundary Rules

The furniture domain follows these boundary rules:

- Domain knowledge must not be hidden only inside execution parameters.
- Product families must not duplicate engines.
- Family-specific contracts may exist, but they must reuse shared domain
  concepts.
- New product families must extend through existing application and product
  boundaries.
- Manufacturing, cost, and commercial layers should remain downstream of
  engineering and manufacturing evidence.

## 10. Deferred Domain Gaps

The repository currently shows the following domain gaps as deferred:

- no named root cabinet engineering contract yet
- wall cabinet is catalog-only
- tall cabinet is catalog-only
- wall mounting is not wired into the executable workflow
- `toe_kick_required` is not currently mapped into
  `CabinetParams.base_height`
- customer outputs are not yet wired into `ProjectApplicationService`

These are documented as current repository state, not as implementation
proposals.

## 11. Relationship to Existing Documents

This document should be read together with:

- [docs/product/Product_Architecture_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/product/Product_Architecture_v1.md)
- [docs/architecture/Architecture_Baseline_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/Architecture_Baseline_v1.md)
- [docs/architecture/decisions/ADR-0012-canonical-output-contract.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0012-canonical-output-contract.md)

The roles of the documents are:

- Product Architecture defines why the platform exists.
- Architecture Baseline defines how the current software is structured.
- Furniture Domain Architecture defines what the furniture domain means.
- ADR-0012 defines the downstream runtime output contract.
