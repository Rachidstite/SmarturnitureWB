# Platform Integration Architecture

## 1. Executive Summary

SmartFurnitureWB is a furniture engineering and manufacturing platform with a verified end-to-end runtime flow that starts from product-family data and proceeds through application services, engineering, construction, manufacturing, factory release, cost, commercial, quotation, and customer outputs.

The repository evidence shows that the platform is already organized around stable boundaries:

- product-family and product-configuration contracts define what the product is
- application services define how a configuration enters the system
- engineering and construction define the cabinet evidence
- manufacturing, factory release, cost, commercial, quotation, and customer outputs consume downstream evidence

The current architecture supports a base-cabinet executable path and a wall-cabinet foundation path. `BASE_CABINET` remains the only application-routed executable family, while `WALL_CABINET` remains catalog-only at routing time and supported only by wall-cabinet domain foundations.

## 2. Platform Layers

The verified platform layers are:

1. Product Family
2. Product Configuration
3. Application Services
4. Engineering
5. Construction
6. Manufacturing
7. Factory Release
8. Cost
9. Commercial
10. Quotation
11. Customer Outputs

These layers are supported by existing repository contracts and application entry points. They form a linear runtime chain, with downstream stages consuming evidence produced by upstream stages.

## 3. End-to-End Runtime Flow

### Product Family

- **Purpose**: define reusable furniture product families.
- **Existing repository components**:
  - `domain/product_family.py`
  - `domain/product_family_registry.py`
  - `domain/product_family_catalog.py`
- **Inputs**: family metadata, default dimensions, engineering defaults, manufacturing defaults, commercial defaults, visual defaults.
- **Outputs**: `ProductFamily` records and a built-in registry of family definitions.
- **Downstream consumer**: `ProductConfiguration`.
- **Upstream dependency**: none; this is the top-level product definition layer.
- **Business responsibility**: describe the product families the platform can represent.
- **Current maturity**: mature as a catalog and registry foundation; only `BASE_CABINET` is executable through application routing.
- **Extension points**: additional product-family catalog entries and registry composition.

### Product Configuration

- **Purpose**: represent a user-selected family plus dimensions and options.
- **Existing repository components**:
  - `domain/product_configuration.py`
  - `domain/product_configuration_family_classifier.py`
- **Inputs**: family_id, dimensions, options, metadata.
- **Outputs**: product-specific configuration data and family classification.
- **Downstream consumer**: application services.
- **Upstream dependency**: `ProductFamily` catalog data.
- **Business responsibility**: capture the chosen family in a runtime-ready form.
- **Current maturity**: mature as a generic contract.
- **Extension points**: new family identifiers and family classification branches.

### Application Services

- **Purpose**: expose the public entry points into the platform.
- **Existing repository components**:
  - `application/engineering_application_service.py`
  - `application/manufacturing_application_service.py`
  - `application/project_application_service.py`
  - `application/application_service_result.py`
- **Inputs**: `ProductConfiguration` or `BaseCabinetSpecification`, depending on service.
- **Outputs**:
  - engineering application result
  - manufacturing application result
  - project application result
- **Downstream consumer**: engineering and workflow layers.
- **Upstream dependency**: product configuration and family routing.
- **Business responsibility**: accept user-facing runtime requests and route them to the correct engineering/workflow path.
- **Current maturity**: mature for `BASE_CABINET`; `WALL_CABINET` remains rejected at routing time.
- **Extension points**: additional executable family routing when supported by engineering contracts.

### Engineering

- **Purpose**: turn product intent into engineering evidence.
- **Existing repository components**:
  - `domain/base_cabinet_engineering_entry.py`
  - `domain/base_cabinet_engineering_model.py`
  - `domain/wall_cabinet_engineering_intent.py`
  - `domain/wall_cabinet_engineering_entry.py`
  - `domain/wall_cabinet_engineering_model.py`
- **Inputs**:
  - base cabinet: `BaseCabinetSpecification`
  - wall cabinet: `WallCabinetSpecification`
- **Outputs**:
  - base cabinet: `Cabinet` with engineering/construction models
  - wall cabinet: engineering intent, entry result, and descriptive engineering model only
- **Downstream consumer**: construction and geometry/runtime layers for base cabinet; wall cabinet remains non-geometric.
- **Upstream dependency**: application routing and family-specific specification contracts.
- **Business responsibility**: produce evidence about how a cabinet is engineered.
- **Current maturity**: base cabinet is executable; wall cabinet is descriptive only.
- **Extension points**: family-specific engineering contracts and descriptive models.

### Construction

- **Purpose**: define structural cabinet evidence from engineering input.
- **Existing repository components**:
  - `domain/construction_resolver.py`
  - `domain/furniture_construction_model.py`
  - `shared/contracts.py`
- **Inputs**: base-cabinet engineering specification.
- **Outputs**: `CabinetConstructionModel`, `CabinetConstructionSpecification`, and related construction dataclasses.
- **Downstream consumer**: `CabinetBuilder` and the manufacturing runtime.
- **Upstream dependency**: base-cabinet engineering entry.
- **Business responsibility**: express construction structure and policy in carrier form.
- **Current maturity**: generic carrier is mature; resolver remains base-specific and mixed.
- **Extension points**: future policy-driven construction separation.

### Manufacturing

- **Purpose**: produce manufacturing evidence and outputs.
- **Existing repository components**:
  - `domain/base_cabinet_manufacturing_outputs_entry.py`
  - `manufacturing/manufacturing_runtime_pipeline_builder.py`
  - `manufacturing/manufacturing_production_package_builder.py`
  - `manufacturing/manufacturing_decision_builder.py`
- **Inputs**: construction/manufacturing evidence from engineering.
- **Outputs**:
  - manufacturing outputs
  - manufacturing package
  - manufacturing production package
  - manufacturing decision
- **Downstream consumer**: factory release.
- **Upstream dependency**: engineering and construction evidence.
- **Business responsibility**: turn construction evidence into manufacturing evidence.
- **Current maturity**: verified and stable for the base cabinet flow.
- **Extension points**: additional family support if upstream evidence is available.

### Factory Release

- **Purpose**: package manufacturing evidence for release.
- **Existing repository components**:
  - `manufacturing/factory_release_package.py`
- **Inputs**: manufacturing decision, cut list, hardware report, CNC report, assembly report, warnings, metadata.
- **Outputs**: `FactoryReleasePackage`.
- **Downstream consumer**: cost.
- **Upstream dependency**: manufacturing.
- **Business responsibility**: create a release-ready manufacturing package.
- **Current maturity**: mature as part of the base cabinet flow.
- **Extension points**: downstream consumers; not additional runtime engines.

### Cost

- **Purpose**: derive cost intelligence from release/manufacturing evidence.
- **Existing repository components**:
  - `cost_intelligence/cost_package_builder.py`
  - `cost_intelligence/cost_package_report.py`
  - `cost_intelligence/manufacturing_cost_pipeline_builder.py`
- **Inputs**: manufacturing evidence / factory release evidence depending on the path.
- **Outputs**: cost package reports and cost intelligence artifacts.
- **Downstream consumer**: commercial.
- **Upstream dependency**: factory release or manufacturing evidence.
- **Business responsibility**: estimate and package cost information.
- **Current maturity**: stable as a downstream foundation.
- **Extension points**: future product-family-aware cost consumers.

### Commercial

- **Purpose**: translate cost evidence into commercial output.
- **Existing repository components**:
  - `commercial_outputs/commercial_package_builder.py`
  - `commercial_outputs/commercial_package_report.py`
  - `cost_intelligence/manufacturing_commercial_pipeline_builder.py`
  - `cost_intelligence/manufacturing_commercial_result.py`
- **Inputs**: cost package / manufacturing cost evidence.
- **Outputs**: commercial package reports and `ManufacturingCommercialResult`.
- **Downstream consumer**: quotation and customer output derivation.
- **Upstream dependency**: cost.
- **Business responsibility**: produce commercial intelligence and pricing-related output.
- **Current maturity**: stable as a downstream contract; `ManufacturingCommercialResult` is the canonical runtime commercial contract.
- **Extension points**: derived reporting and export use cases.

### Quotation

- **Purpose**: generate quotation documents from commercial evidence.
- **Existing repository components**:
  - `cost_intelligence/quotation_report.py`
  - `cost_intelligence/quotation_document.py`
  - `cost_intelligence/quotation_document_builder.py`
  - `exports/quotation_document_export.py`
- **Inputs**: `QuotationReport` and quotation metadata.
- **Outputs**: `QuotationDocumentV1` and exportable quotation documents.
- **Downstream consumer**: customer-facing document export.
- **Upstream dependency**: commercial output.
- **Business responsibility**: present commercial output in quotation form.
- **Current maturity**: stable and derived from the canonical runtime commercial contract.
- **Extension points**: export formats and document rendering.

### Customer Outputs

- **Purpose**: present customer-facing summaries derived from commercial evidence.
- **Existing repository components**:
  - `customer_outputs/customer_package_builder.py`
  - `customer_outputs/customer_package_report.py`
- **Inputs**: commercial package reports.
- **Outputs**: customer package reports.
- **Downstream consumer**: customer-facing output flows.
- **Upstream dependency**: commercial output foundations.
- **Business responsibility**: provide customer-oriented representations of the product/commercial state.
- **Current maturity**: foundation exists; not wired into the public full workflow.
- **Extension points**: later public workflow integration if the commercial contract boundary is resolved.

## 4. Layer Responsibilities

- **Product Family**
  - define reusable family identity and defaults
- **Product Configuration**
  - define the selected family and its runtime configuration
- **Application Services**
  - validate and route runtime requests
- **Engineering**
  - produce cabinet-specific engineering evidence
- **Construction**
  - translate engineering intent into construction carrier data
- **Manufacturing**
  - produce manufacturing outputs and evidence
- **Factory Release**
  - package manufacturing evidence for release
- **Cost**
  - derive cost intelligence
- **Commercial**
  - derive commercial intelligence and pricing output
- **Quotation**
  - produce quotation artifacts
- **Customer Outputs**
  - produce customer-oriented summaries

## 5. Boundary Responsibilities

The platform boundaries are:

- product definitions belong in product family artifacts
- runtime selection belongs in product configuration
- entry routing belongs in application services
- engineering belongs in family-specific engineering contracts and models
- construction belongs in construction carrier models and policy application
- manufacturing belongs in manufacturing runtime and release artifacts
- cost and commercial belong downstream of manufacturing/release evidence
- quotation and customer outputs are derived artifacts, not peer runtime contracts

## 6. Canonical Contracts

The repository establishes the following canonical contracts:

- `ManufacturingCommercialResult`
  - canonical runtime commercial contract
- `CabinetConstructionModel`
  - canonical generic construction carrier
- `ProductConfiguration`
  - canonical product selection contract
- `ProductFamily`
  - canonical product-family definition contract
- `ApplicationServiceResult`
  - canonical application-service wrapper

## 7. Family Extension Points

Verified family extension points include:

- product family catalog entries
- product configuration family classification
- family-specific engineering contracts
- family-specific descriptive engineering models
- passive wall-mount capability/rule vocabulary
- future policy extraction at the construction boundary

`BASE_CABINET` remains the only application-routed executable family. `WALL_CABINET` is present in catalog and domain foundations but is still not routed into the executable application path.

## 8. Verified Runtime Pipeline

The verified runtime pipeline is:

`Product Family`
→ `Product Configuration`
→ `Application Services`
→ `Engineering`
→ `Construction`
→ `Manufacturing`
→ `Factory Release`
→ `Cost`
→ `Commercial`
→ `Quotation`
→ `Customer Outputs`

The pipeline is verified in the repository as a layered flow, but only the base-cabinet path is fully executable end to end through public application routing.

## 9. Deferred Areas

The following are deferred or incomplete:

- executable wall-cabinet application routing
- wall-cabinet geometry generation
- wall-specific construction execution
- policy extraction into a formal construction policy contract
- integration of customer outputs into the public full workflow
- any new resolver-per-family architecture

## 10. References

This document is grounded in existing repository evidence and existing architecture documentation:

- [docs/architecture/Architecture_Baseline_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/Architecture_Baseline_v1.md)
- [docs/product/Product_Architecture_v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/product/Product_Architecture_v1.md)
- [docs/domain/Furniture_Domain_Architecture.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/domain/Furniture_Domain_Architecture.md)
- [docs/architecture/decisions/ADR-0012-canonical-output-contract.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0012-canonical-output-contract.md)
- [docs/architecture/decisions/ADR-0013-construction-policy-boundary.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0013-construction-policy-boundary.md)

The platform integration architecture is consistent with the verified end-to-end flow and with the existing documentation of platform, product, domain, canonical output, and construction-policy boundaries.
