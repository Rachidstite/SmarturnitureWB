# Manufacturing Optimization Audit

## Scope

This audit covers `exports/`, `manufacturing/`, `validation/`, and `runtime/`.
It documents current manufacturing bottlenecks, duplicate paths, duplicate
representations, and architectural hotspots. It does not propose a new
architecture and does not change current production behavior.

## Executive Summary

The validated runtime pipeline is intact, but manufacturing data is repeatedly
re-derived into several overlapping representations. The main optimization
opportunity is not a new aggregate or a new pipeline. It is reducing repeated
extraction and clarifying which existing representation owns each downstream
manufacturing concern.

The highest-risk findings are:

1. `HybridManufacturingExtractor` performs a panel-by-operation ownership join
   with nested loops.
2. Multiple services independently repeat the same SceneGraph-to-PanelSpec
   extraction.
3. `PanelSpec` has a declared `cnc_operations` path while hybrid extraction
   dynamically adds `unified_operations`.
4. Legacy direct CNC export and canonical CNC export remain parallel.
5. Costing is split across manufacturing cost impacts, engineering costing, and
   unused material pricing data.
6. Nesting reduces cut-list data to a second input model that loses identity and
   thickness, while stock assumptions are duplicated elsewhere.

## Findings

### F01 - Hybrid extraction performs a nested panel/operation ownership join

**Category:** Manufacturing bottleneck

**Evidence**

- `manufacturing/hybrid_extractor.py:13-22` extracts all panel specs and all
  unified operations separately.
- `manufacturing/hybrid_extractor.py:24-64` loops over every operation for every
  panel, then copies each matching operation to enrich its metadata.
- `manufacturing/canonical_operation_collector.py:12-46` already determines and
  stores `panel_id` while collecting operations.

**Files involved**

- `manufacturing/hybrid_extractor.py`
- `manufacturing/canonical_operation_collector.py`
- `manufacturing/unified_manufacturing_operation.py`

**Duplication risk**

Ownership is discovered once by the collector and then resolved again by the
hybrid extractor. With `P` panels and `O` operations, enrichment is currently
`O(P * O)` and recreates immutable operation objects.

**Manufacturing impact**

Large projects with dense drilling patterns will spend increasing time in
extraction before validation, reporting, dashboard generation, or CNC export.
Repeated object copying also increases memory use.

**Recommended future refactor**

Within the existing extraction boundary, index collected operations by
`metadata["panel_id"]` once, then enrich each panel from its indexed list.
Preserve `HybridManufacturingExtractor` and its output contract.

---

### F02 - SceneGraph manufacturing extraction is repeated across services and exports

**Category:** Duplicate extraction paths

**Evidence**

- `manufacturing/hybrid_extractor.py:13-22` runs both panel extraction and
  operation collection.
- `services/manufacturing_dashboard_service.py:61-65`,
  `services/canonical_manufacturing_export_service.py:31-35`,
  `services/manufacturing_validation_service.py:15-19`, and
  `services/project_intelligence_service.py:21-25` each independently call
  `HybridManufacturingExtractor.extract(scene_graph)`.
- `exports/cutlist_engine.py:23` and `exports/bom_engine.py:40` independently
  call `ManufacturingExtractor.extract(scene_graph)`.

**Files involved**

- `manufacturing/extractor.py`
- `manufacturing/hybrid_extractor.py`
- `services/manufacturing_dashboard_service.py`
- `services/canonical_manufacturing_export_service.py`
- `services/manufacturing_validation_service.py`
- `services/project_intelligence_service.py`
- `exports/cutlist_engine.py`
- `exports/bom_engine.py`

**Duplication risk**

The same SceneGraph can be traversed and mapped multiple times during one user
workflow. Consumers can also observe different snapshots if the graph or
operations change between calls.

**Manufacturing impact**

Dashboard, validation, export, BOM, and cut-list workflows repeat manufacturing
face-size resolution, metadata copying, and operation adaptation.

**Recommended future refactor**

Allow orchestration code to reuse an already-extracted list of existing
`PanelSpec` objects during one workflow. Keep SceneGraph-based entry points for
backward compatibility; do not introduce a new aggregate.

---

### F03 - Panel data is represented repeatedly for adjacent manufacturing outputs

**Category:** Duplicate panel representations

**Evidence**

- `manufacturing/panel_spec.py:8-40` defines the manufacturing panel model.
- `exports/cutlist_engine.py:6-17` defines `CutListItem`, repeating identity,
  dimensions, thickness, material, group, role, quantity, and grain direction.
- `exports/bom_engine.py:7-20` defines `BOMItem`, repeating the same core panel
  fields plus edge fields.
- `exports/nesting_engine.py:5-10` defines `NestingPart`, repeating dimensions
  and rotation state while dropping identity, thickness, quantity, and material.
- `exports/assembly_exporter.py:14-40` directly reconstructs a simple part list
  from SceneGraph nodes instead of using a manufacturing representation.

**Files involved**

- `manufacturing/panel_spec.py`
- `exports/cutlist_engine.py`
- `exports/bom_engine.py`
- `exports/nesting_engine.py`
- `exports/assembly_exporter.py`

**Duplication risk**

Field propagation must be maintained manually. The recently repaired
`grain_direction` and quantity contract demonstrates the drift risk. Loss of
identity and thickness at the nesting boundary limits traceability.

**Manufacturing impact**

Cut-list, BOM, assembly documentation, and nesting can disagree about panel
dimensions, quantities, edges, or stock classification.

**Recommended future refactor**

Keep output-specific DTOs, but centralize their mapping from existing
`PanelSpec` in small explicit mapper functions. Add parity tests for identity,
dimensions, thickness, material, quantity, grain direction, and edges.

---

### F04 - Manufacturing face dimensions are not used consistently by all exports

**Category:** Duplicate extraction path / dimensional hotspot

**Evidence**

- `manufacturing/extractor.py:8-53` resolves manufacturing face dimensions by
  `NodeRole`, using depth/height for vertical panels and width/depth for
  horizontal panels.
- `exports/cutlist_engine.py:23-36` and `exports/bom_engine.py:40-55` consume
  those resolved dimensions.
- `exports/assembly_exporter.py:36-40` directly displays node `width`, `height`,
  and `thickness`.

**Files involved**

- `manufacturing/extractor.py`
- `exports/cutlist_engine.py`
- `exports/bom_engine.py`
- `exports/assembly_exporter.py`

**Duplication risk**

Direct node dimensions and manufacturing face dimensions are both treated as
panel dimensions, but they are not equivalent for every role.

**Manufacturing impact**

Assembly labels can show dimensions that differ from the BOM and cut list,
creating shop-floor ambiguity.

**Recommended future refactor**

Keep the assembly export workflow, but source displayed panel dimensions from
the existing manufacturing face-size mapping or extracted `PanelSpec`.

---

### F05 - Operation representations and ownership paths overlap

**Category:** Duplicate operation representations

**Evidence**

- SceneGraph nodes expose `machining_ops`, consumed by
  `manufacturing/canonical_operation_collector.py:18-27`.
- `manufacturing/machining_operation_adapter.py:8-40` adapts multiple operation
  shapes into `UnifiedManufacturingOperation`.
- `manufacturing/panel_spec.py:40` declares `cnc_operations`.
- `manufacturing/hybrid_extractor.py:64` dynamically attaches
  `spec.unified_operations`, which is not declared on `PanelSpec`.
- `validation/panel_spec_validator.py:43` and
  `validation/manufacturing_feasibility_validator.py:13` validate
  `cnc_operations`.
- `validation/unified_operation_validation_adapter.py:20-26` and
  `validation/intelligence/manufacturing_rule_engine.py:54-57` consume
  `unified_operations`.

**Files involved**

- `manufacturing/panel_spec.py`
- `manufacturing/canonical_operation_collector.py`
- `manufacturing/machining_operation_adapter.py`
- `manufacturing/unified_manufacturing_operation.py`
- `manufacturing/hybrid_extractor.py`
- `validation/panel_spec_validator.py`
- `validation/manufacturing_feasibility_validator.py`
- `validation/unified_operation_validation_adapter.py`
- `validation/intelligence/manufacturing_rule_engine.py`

**Duplication risk**

Two operation-list names exist on the same conceptual panel. Some validators can
inspect an empty `cnc_operations` list while intelligence and canonical export
inspect dynamically attached `unified_operations`.

**Manufacturing impact**

Validation coverage can differ by entry point. An operation may reach canonical
CNC export while bypassing validators that still read `cnc_operations`.

**Recommended future refactor**

First document and test which existing operation list is canonical for each
stage. Then migrate validators incrementally through adapters, preserving
current public contracts until all consumers use one declared operation path.

---

### F06 - Legacy direct CNC export and canonical CNC export are parallel

**Category:** Duplicate operation representation / export hotspot

**Evidence**

- `exports/cnc_exporter.py:15-29` directly reads node `machining_ops` and emits
  CSV-shaped rows from `local_x` and `local_y`.
- `exports/canonical_cnc_exporter.py:13-27` reads panel
  `unified_operations` and maps them through `CanonicalCNCMapper`.
- `manufacturing/canonical_cnc_row.py:4-17` defines the canonical CNC row.
- `services/canonical_manufacturing_export_service.py:57-66` uses the canonical
  path.

**Files involved**

- `exports/cnc_exporter.py`
- `exports/canonical_cnc_exporter.py`
- `exports/canonical_csv_exporter.py`
- `manufacturing/canonical_cnc_mapper.py`
- `manufacturing/canonical_cnc_row.py`

**Duplication risk**

The two exporters differ in headers, coordinate fields, operation type,
operation source, and input model. Fixes applied to one path may not reach the
other.

**Manufacturing impact**

Different export entry points can produce different CNC programs for the same
SceneGraph.

**Recommended future refactor**

Keep the canonical service as the target path. Characterize legacy exporter
behavior, identify remaining callers, and route compatible legacy entry points
through canonical rows before considering deprecation.

---

### F07 - Panel and operation validation rules overlap

**Category:** Duplicate validation work / architectural hotspot

**Evidence**

- `validation/panel_spec_validator.py:43-115` validates operation diameter,
  depth, bounds, and a minifix panel-size condition through `cnc_operations`.
- `validation/manufacturing_feasibility_validator.py:13-29` repeats the minifix
  panel-size condition.
- `validation/hybrid_manufacturing_validator.py:29-167` validates unified
  operation types, dimensions, coordinates, axes, faces, and depth against panel
  thickness metadata.
- `validation/intelligence/manufacturing_rule_engine.py:31-67` executes another
  panel/operation rule pass.

**Files involved**

- `validation/panel_spec_validator.py`
- `validation/manufacturing_feasibility_validator.py`
- `validation/hybrid_manufacturing_validator.py`
- `validation/unified_operation_validation_adapter.py`
- `validation/intelligence/manufacturing_rule_engine.py`

**Duplication risk**

Similar conditions can emit different issue codes or run against different
operation representations. Rule corrections can be applied inconsistently.

**Manufacturing impact**

The same manufacturing defect may be reported twice, reported differently, or
missed depending on service entry point.

**Recommended future refactor**

Build a validation coverage matrix before changes. Consolidate exact duplicate
conditions behind existing adapters and preserve issue codes and service
contracts with characterization tests.

---

### F08 - Manufacturing and engineering costing paths are disconnected

**Category:** Duplicate costing paths

**Evidence**

- `validation/intelligence/cost_impact.py:4-11` models manufacturing savings as
  category, amount, and description.
- `validation/intelligence/unused_operation_cost_impact.py:21-37` assigns a
  fixed `1.0` saving per unused operation.
- `validation/intelligence/engineering/cost/engineering_cost_impact.py:4-13`
  models material sheets, machining minutes, and hardware cost.
- `validation/intelligence/engineering/cost/engineering_cost_estimator.py:1-20`
  applies fixed MDF-sheet and machining-minute prices.
- `manufacturing/material_spec.py:4-19` separately defines sheet dimensions and
  `price_per_m2`, but current material entries leave price at its default.

**Files involved**

- `validation/intelligence/cost_impact.py`
- `validation/intelligence/cost_impact_engine.py`
- `validation/intelligence/unused_operation_cost_impact.py`
- `validation/intelligence/engineering/cost/engineering_cost_impact.py`
- `validation/intelligence/engineering/cost/engineering_cost_engine.py`
- `validation/intelligence/engineering/cost/engineering_cost_estimator.py`
- `manufacturing/material_spec.py`

**Duplication risk**

Three independent pricing concepts exist: fixed savings, fixed engineering
rates, and material-library pricing. Units and currency are implicit.

**Manufacturing impact**

Optimization savings, engineering estimated cost, and actual material
consumption cannot be reconciled reliably.

**Recommended future refactor**

Define shared cost units and currency metadata first. Then make existing cost
engines consume one pricing source while preserving their current report
models. Do not merge manufacturing and engineering rules.

---

### F09 - Nesting input loses stock-critical panel information

**Category:** Duplicate nesting inputs

**Evidence**

- `exports/cutlist_engine.py:6-17` carries identity, dimensions, thickness,
  material, quantity, and grain direction.
- `exports/nesting_engine.py:25-47` accepts both current `width`/`height` and
  legacy `cut_width`/`cut_height`, expands quantity, and converts each item into
  `NestingPart`.
- `exports/nesting_engine.py:5-10` stores only semantic name, dimensions, and
  rotation permission.
- `exports/nesting_engine.py:26-28` groups only by material, not thickness.

**Files involved**

- `exports/cutlist_engine.py`
- `exports/nesting_engine.py`

**Duplication risk**

The nesting boundary supports two dimension contracts and creates a second DTO
that drops panel identity and thickness. Same-material panels with different
thicknesses currently share a basket.

**Manufacturing impact**

Nesting output cannot reliably trace a placed part back to a cut-list identity,
and incompatible stock thicknesses may be combined.

**Recommended future refactor**

Before algorithm improvements, define and test a stock grouping key and
traceability fields for the existing nesting input boundary. Preserve legacy
dimension compatibility until callers are audited.

---

### F10 - Stock dimensions and utilization assumptions are duplicated

**Category:** Architectural hotspot / nesting input duplication

**Evidence**

- `manufacturing/material_spec.py:9-10` defines stock sheet dimensions, with
  current defaults of `1830 x 3660`.
- `exports/nesting_engine.py:16` independently defaults to `2440 x 1220`.
- `exports/svg_exporter.py:10` independently defaults to `2440 x 1220`.
- `exports/svg_exporter.py:19` calculates yield using exporter arguments rather
  than dimensions stored with `SheetResult`.
- `exports/strategies.py:21-26` stores no stock dimensions or rejected parts in
  `SheetResult`.

**Files involved**

- `manufacturing/material_spec.py`
- `exports/nesting_engine.py`
- `exports/strategies.py`
- `exports/svg_exporter.py`

**Duplication risk**

Material definitions, nesting, and SVG reporting can use different stock sizes.
The exporter cannot verify which dimensions produced a result.

**Manufacturing impact**

Yield percentages and cutting maps may not match the stock sheet actually used
for nesting.

**Recommended future refactor**

Pass resolved stock dimensions explicitly through the existing nesting/export
workflow and characterize current defaults first. Avoid changing the placement
algorithm as part of that work.

---

### F11 - An alternative free-rectangle optimization subsystem is disconnected

**Category:** Architectural hotspot

**Evidence**

- `exports/space_manager.py:23-80` implements free-rectangle placement state.
- `exports/heuristics.py:5-67` implements BAF, BSSF, and BLF placement
  heuristics.
- No production caller outside those two files references `SpaceManager` or
  `PlacementHeuristics`.
- Active nesting uses `GuillotineStripStrategy` in `exports/strategies.py`.

**Files involved**

- `exports/space_manager.py`
- `exports/heuristics.py`
- `exports/strategies.py`
- `exports/nesting_engine.py`

**Duplication risk**

Two optimization approaches exist, but only one is integrated. The disconnected
path can be mistaken for active behavior and may diverge without tests.

**Manufacturing impact**

Maintenance effort can be spent on code that does not affect generated cutting
plans. Future integration attempts could unintentionally change established
nesting behavior.

**Recommended future refactor**

Classify the free-rectangle subsystem as experimental or inactive in
documentation and tests. Do not integrate or remove it until a separate nesting
algorithm decision is approved.

---

### F12 - Report builders repeat rule-derived projections

**Category:** Manufacturing bottleneck / reporting hotspot

**Evidence**

- `validation/intelligence/manufacturing_intelligence_report_builder.py:41-45`
  calculates aggregated rule results once.
- The builder repeatedly filters those results for errors, warnings,
  optimizations, export eligibility, and structural warnings while constructing
  the score input and final report (`:73-110`).
- `ManufacturingRuleEngine.errors`, `warnings`, `recommendations`,
  `optimizations`, and `infos` each scan the complete result list.

**Files involved**

- `validation/intelligence/manufacturing_intelligence_report_builder.py`
- `validation/intelligence/manufacturing_rule_engine.py`
- `validation/intelligence/result_aggregator.py`

**Duplication risk**

Repeated projections increase work and can drift if report construction paths
are updated independently.

**Manufacturing impact**

This is a smaller bottleneck than extraction, but it compounds on large result
sets and makes report consistency harder to reason about.

**Recommended future refactor**

Compute existing result projections once inside the report builder and reuse
them for score calculation and final report construction. Preserve all report
and rule-engine contracts.

## Prioritized Future Work

### Priority 1 - Correctness and traceability

1. Characterize and align `cnc_operations` versus `unified_operations`
   consumption.
2. Add nesting stock-group and placed-part traceability contracts.
3. Characterize legacy versus canonical CNC export parity.
4. Align assembly displayed dimensions with manufacturing face dimensions.

### Priority 2 - Performance

1. Replace the hybrid extractor nested ownership join with a panel-id index.
2. Reuse extracted `PanelSpec` lists within individual workflows.
3. Reuse report result projections during report construction.

### Priority 3 - Cost and optimization readiness

1. Define cost units, currency, and pricing ownership.
2. Connect stock dimensions to nesting and SVG reporting explicitly.
3. Classify the free-rectangle subsystem before any nesting algorithm work.

## Audit Constraints Observed

- No production code was changed.
- No architecture was redesigned.
- `CabinetProject`, `NodeRole`, `ManufacturingCompiler`, runtime adapters, rule
  engines, and engineering intelligence rules were not modified.
- Recommendations are future refactor candidates only.
