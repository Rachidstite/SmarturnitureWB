# Cost Intelligence Contract V1

## Purpose

Define the minimal cost intelligence contract for SmartFurnitureWB without introducing duplicate engines or replacing existing manufacturing systems.

## Strategic Flow

CabinetProject
↓
ManufacturingExtractor
↓
PanelSpec
↓
CutListEngine
↓
IndustrialNestingEngine
↓
Cost Intelligence
↓
Commercial Outputs

## Non-Goals

- Do not replace EngineeringCostEngine.
- Do not merge Engineering ROI with actual production cost.
- Do not replace CostImpactEngine.
- Do not create a quotation system yet.
- Do not change CabinetProject.
- Do not change ManufacturingCompiler.
- Do not change Nesting algorithms.

## Cost Concepts

### Actual Production Cost

Cost required to manufacture the project.

Includes:
- material cost
- sheet cost
- waste cost
- hardware cost
- edge banding cost
- machining cost
- labor/setup cost

### Engineering Remediation Cost

Cost estimate for fixing engineering problems.

This remains owned by EngineeringCostEngine.

### Optimization Savings

Potential savings from removing waste or unused operations.

This remains owned by CostImpactEngine.

### ROI Ranking

Qualitative priority ranking.

This remains owned by EngineeringROIEngine.

## Required V1 Outputs

CostReport:
- material_cost
- sheet_cost
- waste_cost
- hardware_cost
- edge_banding_cost
- machining_cost
- labor_cost
- total_cost
- currency
- warnings

## Required V1 Inputs

- CutListItem list
- Nesting result
- Material pricing catalog
- Resolved stock dimensions
- Optional operation counts
- Optional hardware quantities

## Minimum Pricing Contract

PricingCatalog item:
- stock_key
- material
- thickness
- sheet_width
- sheet_height
- price_per_sheet
- price_per_m2
- currency

## Required Safety Rules

- If material price is missing, report warning.
- If nesting rejected parts are unavailable, report warning.
- If sheet dimensions are inferred, report warning.
- If currency is missing, report warning.
- Do not silently calculate total cost from incomplete pricing.

## Recommended First Implementation

Start with MaterialCostCalculator only.

Inputs:
- CutListItem list
- PricingCatalog

Outputs:
- material_cost
- warnings

Do not include:
- quotation
- margin
- tax
- discounts
- customer pricing

## Status

Architecture proposal only.
No production implementation yet.
