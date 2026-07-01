# Product Architecture v1

## 1. Product Vision

SmartFurnitureWB is a Furniture Engineering and Manufacturing Platform.
It exists to help furniture companies:

- design faster
- manufacture faster
- reduce mistakes
- reduce waste
- reduce cost
- generate manufacturing outputs
- improve quotation and commercial output quality
- increase profitability

The repository evidence shows a platform centered on a verified furniture
product workflow, not just a generic FreeCAD workbench.

## 2. Core Product Value

The product value chain is:

`Product Family`
→ `Product Configuration`
→ Engineering
→ Manufacturing
→ Factory Release
→ Cost
→ Commercial
→ Quotation
→ Customer Outputs

This value chain is supported by the current verified application services and
downstream output contracts.

## 3. Product Scope

In scope:

- cabinet and furniture engineering
- manufacturing outputs
- factory release
- cost intelligence
- commercial and quotation outputs
- future customer outputs

Explicitly out of scope for now:

- generic CAD replacement
- generic FreeCAD workbench features
- AI or agent features without measurable factory value
- SaaS features before product readiness

## 4. Product Layers

These are product and business layers, not software implementation layers:

- Product Definition
- Engineering
- Manufacturing
- Factory Release
- Cost Intelligence
- Commercial Intelligence
- Customer Output
- Optimization
- Platform Independence

## 5. Current Verified Product Capabilities

The repository currently verifies the following:

- `ProductFamily` exists
- `ProductConfiguration` exists
- `EngineeringApplicationService` supports `ProductConfiguration`
- `ManufacturingApplicationService` supports `ProductConfiguration`
- `ProjectApplicationService` supports `ProductConfiguration`
- Base Cabinet is the executable product family
- Wall Cabinet and Tall Cabinet exist as catalog data only
- `docs/architecture/Architecture_Baseline_v1.md` exists
- `ManufacturingCommercialResult` is the canonical runtime commercial contract

## 6. Product Governance

Every future feature must answer these questions:

- Does it make the software more valuable for a furniture manufacturer?
- Does it strengthen the domain model?
- Does it reuse existing architecture?
- Does it avoid duplicate engines, builders, workflows, and pipelines?
- Does it improve priorities 1 through 7 before SaaS, AI, or agent features?

## 7. Product Roadmap

Phase I - Platform Foundations

- Status: Completed

Phase II - Product Experience

- Status: Completed for Base Cabinet

Phase III - Furniture Domain Architecture

- Status: Next

Phase IV - Product Family Expansion

- Status: Planned

Phase V - Manufacturing Intelligence

- Status: Planned

Phase VI - Commercial Product Readiness

- Status: Planned

Phase VII - Platform Independence / Standalone

- Status: Future

Phase VIII - SaaS Readiness

- Status: Future

Phase IX - AI and Agent Features

- Status: Deferred until measurable business value exists

## 8. Non-Negotiable Product Rules

- no feature without manufacturing or commercial value
- no duplicate engines
- no duplicate workflows
- no duplicate abstractions
- preserve existing APIs
- preserve backward compatibility
- prefer extension over replacement
- business value before technical novelty

## 9. Relationship to Existing Architecture Documents

This document must be read together with:

- [docs/architecture/Architecture_Baseline_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/Architecture_Baseline_v1.md)
- [docs/architecture/decisions/ADR-0012-canonical-output-contract.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0012-canonical-output-contract.md)

The documents have different roles:

- Product Architecture defines why the platform exists.
- Architecture Baseline defines how the software is currently structured.
- ADR-0012 defines the canonical downstream runtime output contract.

## 10. Deferred Product Areas

These areas are deferred, not rejected:

- Wall Cabinet executable support
- Tall Cabinet executable support
- Wardrobe / Pantry / Vanity
- CustomerPackage workflow integration
- Nesting optimization
- standalone desktop UI
- REST API
- SaaS
- AI and agents

The repository evidence shows these areas are either catalog-only, separate
foundation components, or future-facing product areas that are not yet wired
into the verified full product workflow.
