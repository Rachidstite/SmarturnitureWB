# ADR-HFG-1 — Rendering Ownership Decision

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Date** | 2026-07-05 |
| **Author** | HFG Architecture Gate |
| **Supersedes** | — |

---

## 1. Problem Statement

The rendering pipeline audit (HFG-1) identified two active rendering systems in the codebase, both capable of generating FreeCAD `Part::Feature` objects from `SceneGraph` data:

1. **SceneRenderer** (`scene_graph/renderer.py`) — the primary renderer with per-role strategy dispatch and overlay pipeline
2. **GeometryRenderer** (`gui/renderer.py`) — a standalone display renderer that creates separate additive feature geometry

Both renderers can produce manufacturing visualization output. Neither has explicit ownership of manufacturing rendering. Before High-Fidelity Manufacturing Visualization can be implemented, architectural ownership must be assigned to prevent:

- Duplicate renderer development (forbidden by project constitution)
- Divergent feature classification sets
- Conflicting extension mechanisms
- Architectural drift

This ADR does not mandate implementation, refactoring, migration, or deprecation. It establishes architectural ownership only.

---

## 2. Existing Evidence

### 2.1 SceneRenderer (scene_graph/renderer.py — 405 lines)

- **Location**: `scene_graph/renderer.py`
- **Input**: `SceneGraph.all_nodes()` → per-node dispatch via `RendererRegistry`
- **Output**: FreeCAD `Part::Feature` objects in grouped `App::DocumentObjectGroup` containers
- **Architecture**: Per-role strategy registration (`RendererRegistry.register(role, strategy_fn)`)
- **Panel geometry**: `Part.makeBox()` → `process_panel_shape()` for subtractive manufacturing cuts
- **Manufacturing overlays**: 4 overlay types (`edge_banding`, `drill_hole`, `groove`, `hardware_marker`) via `build_visual_overlays()` and `build_viewport_overlay_commands()`
- **Overlay pipeline**: 3-step pattern: `VisualMetadata` dataclass → overlay dict → viewport command dict
- **Strategies registered**: SHELF, DIVIDER, DRAWER_FACE, DOOR_PANEL
- **Default fallback**: `_render_simple_panel()` — applies `process_panel_shape()` for BACK_PANEL, SIDE_PANEL, TOP_PANEL, BOTTOM_PANEL, DIVIDER roles
- **Manufacturing link**: `self.panel_features` → `process_panel_shape()`; `build_visual_metadata()` → reads CNC/edge/hardware reports
- **Extension mechanism**: New role strategy via `RendererRegistry.register()`; new overlay type via new method in `_<type>_overlays()` + `_<type>_viewport_command()` pipeline
- **RendererRegistry**: `scene_graph/registry.py` (19 lines) — singleton registry mapping roles to strategy functions
- **FreeCAD dependency**: YES — `Part`, `App`

### 2.2 GeometryRenderer (gui/renderer.py — 206 lines)

- **Location**: `gui/renderer.py`
- **Input**: `project` object with `project.graph.physical_nodes` + `build_visible_geometry_plan(project)`
- **Output**: FreeCAD `Part::Feature` objects in two groups: panel group + `Manufacturing_Geometry` group
- **Architecture**: Standalone static method `render()` — calls `_render_cabinet_panel()` and `_render_manufacturing_geometry()` independently
- **Panel geometry**: `Part.makeBox()` → `process_panel_shape()` for subtractive cuts (same as SceneRenderer)
- **Feature geometry**: `_make_feature_shape()` creates Part boxes/cylinders per feature kind — **additive display geometry**, NOT solid cuts
- **Feature kinds**: `back_panel_groove`, `drawer_slide_line`, `edge_banding_strip`, `wall_mount_prototype` (as boxes), `hinge_plate_position` (as boxes), `hinge_cup_hole`, `shelf_pin_hole`, `drilling_indicator` (as cylinders)
- **Data source**: `build_visible_geometry_plan(project)` → `VisibleGeometryFeatureSpec[]` with placement, size, color, prototype flags
- **Extension mechanism**: None — `_make_feature_shape()` is a hardcoded switch on `feature.kind`
- **Feature rendering**: Separate additive objects in `Manufacturing_Geometry` group — features sit BESIDE panels, not cut INTO them
- **Transparency**: Prototype features get Transparency=35; production features get Transparency=10
- **FreeCAD dependency**: YES — `Part`, `App`, `FreeCADGui`

### 2.3 Additional Rendering Components

| Component | Location | Role | Active? |
|-----------|----------|------|---------|
| `RendererRegistry` | `scene_graph/registry.py` | Per-role strategy dispatch | YES — consumed by SceneRenderer |
| `VisualMetadata` | `scene_graph/metadata.py` | Manufacturing overlay data (frozen dataclass) | YES — consumed by SceneRenderer |
| `ManufacturingMarker` | `scene_graph/manufacturing_marker.py` | Operation-based marker dataclass | YES — consumed by SceneRenderer |
| `ManufacturingMarkerBuilder` | `scene_graph/manufacturing_marker_builder.py` | Operation→ManufacturingMarker mapping | YES |
| `process_panel_shape` | `manufacturing/panel_shape_processor.py` | Boolean cut of features into panel solid | YES — shared by both renderers |
| `build_visible_geometry_plan` | `manufacturing/visible_geometry_plan.py` | Feature spec list from project | YES — consumed by GeometryRenderer |
| `BaseRenderer` | `engine/base_renderer.py` | Abstract shape builder | NO — stale |
| `IncrementalRenderer` | `engine/incremental_renderer.py` | Diff-driven incremental update | NO — stale |
| `ShelfRenderer` | `renderers/shelf_renderer.py` | Single BaseRenderer implementation | NO — stale, CNC commented out |
| `SceneProjection` | `ui/configurator_v2/scene_projection.py` | SceneGraph→CV2 frozen read model | YES — CV2 boundary |

### 2.4 Pipeline Flow Comparison

**SceneRenderer pipeline:**
```
SceneGraph.all_nodes()
  → RendererRegistry.render(node, renderer)
    → strategy_fn(node, renderer) | renderer._render_simple_panel(node)
      → Part.makeBox()
      → process_panel_shape() — manufacturing cuts into panel
      → Placement, Color, Transparency
  → build_visual_metadata() — from CNC/edge/hardware reports
  → build_visual_overlays() → overlay dicts
  → build_viewport_overlay_commands() → command dicts
```

**GeometryRenderer pipeline:**
```
project → build_visible_geometry_plan(project)
  → VisibleGeometryPlan(features=VisibleGeometryFeatureSpec[])
  → GeometryRenderer.render(project, plan)
    → _render_cabinet_panel() per physical node
      → Part.makeBox() → process_panel_shape()
    → _render_manufacturing_geometry(plan.features)
      → _render_feature() per feature
        → _make_feature_shape() — Part.makeBox or Part.makeCylinder
        → Placement (additive, beside panel)
```

### 2.5 Key Architectural Difference

**SceneRenderer** cuts manufacturing features **into** panels (subtractive/Boolean). Overlays are viewport commands (dicts) that annotate the existing panel — they do not create separate FreeCAD objects.

**GeometryRenderer** creates manufacturing features as **separate** FreeCAD objects in a dedicated group. Features are additive display elements rendered beside the panels, not modifications of them.

This is not a bug. Both approaches are valid for different purposes. But for High-Fidelity Manufacturing Visualization, one approach must own the canonical representation.

---

## 3. Existing Rendering Components

### SceneRenderer ownership chain:
```
SceneGraph
  └── RendererRegistry (scene_graph/registry.py)
        ├── _shelf_strategy → _render_simple_panel → process_panel_shape
        ├── _divider_strategy → _render_simple_panel → process_panel_shape
        ├── _drawer_strategy → DrawerBuilder | _render_simple_panel
        ├── _door_strategy → DoorBuilder + process_panel_shape
        └── [default] → _render_simple_panel → process_panel_shape
              └── VisualMetadata
                    ├── build_visual_overlays
                    │     ├── _edge_band_overlays
                    │     ├── _drill_hole_overlays
                    │     ├── _groove_overlays
                    │     └── _hardware_marker_overlays
                    └── build_viewport_overlay_commands
                          ├── _edge_viewport_command
                          ├── _drill_viewport_command
                          ├── _groove_viewport_command
                          └── _hardware_viewport_command
```

### GeometryRenderer ownership chain:
```
project
  └── build_visible_geometry_plan → VisibleGeometryPlan
        └── GeometryRenderer.render
              ├── _render_cabinet_panel → process_panel_shape
              └── _render_manufacturing_geometry
                    └── _render_feature
                          └── _make_feature_shape
                                ├── Part.makeBox (groove, slide, edge, wall_mount, hinge_plate)
                                └── Part.makeCylinder (hinge_cup, shelf_pin, drilling)
```

---

## 4. Ownership Analysis

### 4.1 Implicit Ownership

Current implicit ownership, as evidenced by integration depth:

| Metric | SceneRenderer | GeometryRenderer |
|--------|--------------|-----------------|
| Connected to main render pipeline (`render_graph()`) | YES | NO |
| Connected to SceneGraph | YES (directly) | YES (via project.graph) |
| Has extension mechanism | YES (RendererRegistry + overlay pipeline) | NO (hardcoded feature switch) |
| Connected to CV2 SceneProjection | YES (via `_iter_scene_nodes` / `build_scene_projection`) | NO (standalone only) |
| Has overlay command format for UI | YES (4 viewport command types) | NO (FreeCAD objects only) |
| Shared with panel_shape_processor | YES | YES |
| Has per-feature color/transparency control | NO (per-role only) | YES (per feature color from spec) |
| Creates separate Manufacturing_Geometry group | NO | YES |

**Conclusion**: SceneRenderer is already the implicit owner of manufacturing visualization. GeometryRenderer is a secondary/pathfinder renderer that demonstrates additive feature display but is not integrated into the main pipeline.

### 4.2 Feature Kind Coverage

| Feature | SceneRenderer | GeometryRenderer |
|---------|--------------|-----------------|
| Edge banding | overlay (edge_banding) | additive (boxes in Manufacturing_Geometry) |
| Drill holes | overlay (drill_hole with x,y,z,diameter,depth) | additive (cylinders) |
| Back panel groove | overlay (groove) + solid cut (process_panel_shape) | additive (boxes) + solid cut |
| Minifix holes | NOT rendered | additive (inferred via drilling_indicator) |
| Confirmat holes | NOT rendered | additive (inferred via drilling_indicator) |
| Hinge cup holes | NOT rendered | additive (cylinders) |
| Hinge plate positions | NOT rendered | additive (boxes) |
| Shelf pin holes | NOT rendered | additive (cylinders) |
| Drawer slide holes | NOT rendered | additive (boxes) |
| Hardware markers | overlay (hardware_marker with HINGE/DRAWER/SHELF_PIN symbols) | NOT rendered |

**Conclusion**: Neither renderer currently covers all manufacturing features. SceneRenderer has the overlay infrastructure but only 4 overlay types. GeometryRenderer has more feature kinds hardcoded but lacks the overlay command pipeline. SceneRenderer's extension mechanism (add new overlay type) requires less new code per feature than GeometryRenderer's hardcoded switch.

---

## 5. Options Considered

### Option A: SceneRenderer owns all manufacturing visualization

SceneRenderer is the canonical renderer for all manufacturing features. New feature types are added as new overlay types in the existing `build_visual_overlays()` → `build_viewport_overlay_commands()` pipeline. `VisualMetadata` is extended with new dataclass fields. `ManufacturingMarker` is used for operation-level annotations. `RendererRegistry` is extended with new strategies if role-specific rendering is needed.

**Evidence supporting this option:**
- SceneRenderer is already connected to the main `render_graph()` pipeline (`scene_graph/renderer.py:249`)
- SceneRenderer already has the overlay extension mechanism (`build_visual_overlays()`, lines 22-47)
- SceneRenderer already has the viewport command dispatch (`build_viewport_overlay_commands()`, lines 50-66)
- SceneRenderer's `_hardware_visual_type()` (lines 160-176) already classifies HINGE, DRAWER_SLIDE, SHELF_PIN — the exact features needed
- SceneRenderer is connected to SceneGraph directly (not via project intermediate)
- SceneRenderer's overlay architecture is FreeCAD-free at the command level — overlay commands are plain dicts
- SceneRenderer feeds into SceneProjection which feeds CV2 PreviewRegion

### Option B: GeometryRenderer owns manufacturing visualization

GeometryRenderer becomes the canonical renderer. `_make_feature_shape()` is extended with new feature kinds. `_render_feature()` becomes the primary mechanism for displaying manufacturing details. Additional feature types are added to `build_visible_geometry_plan()` and `GeometryRenderer` is connected to the main render pipeline.

**Evidence against this option:**
- GeometryRenderer is standalone — not connected to `render_graph()` or `SceneRenderer`'s `render_graph()` (`gui/renderer.py:17`)
- GeometryRenderer has no extension mechanism — `_make_feature_shape()` is a hardcoded switch (`gui/renderer.py:140-161`)
- GeometryRenderer creates additive objects — features as separate FreeCAD objects in `Manufacturing_Geometry` group (`gui/renderer.py:104-113`). This creates duplicates of panel geometry that SceneRenderer already produces
- GeometryRenderer has no overlay command pipeline — all output is FreeCAD Part objects only
- GeometryRenderer is not connected to SceneProjection or CV2 — no path to the UI presentation layer
- `_make_feature_shape()` classifies features by kind string only (4 groups), which would require expansion for each new feature
- `process_panel_shape()` is shared with SceneRenderer — establishing GeometryRenderer as primary would create dual ownership of `process_panel_shape()` outputs

### Option C: Split ownership

SceneRenderer handles panel rendering with subtractive manufacturing cuts. GeometryRenderer handles standalone additive feature visualization. Both coexist as first-class renderers with distinct responsibilities.

**Evidence against this option:**
- Directly violates the project constitution rule: "No duplicate renderer"
- Creates two authoritative paths for manufacturing features — a feature added to one must be added to the other
- `process_panel_shape()` is already shared, demonstrating that feature processing is not cleanly split
- The overlay pipeline in SceneRenderer already serves the additive role (viewport commands annotate panels without creating objects) — GeometryRenderer's additive Part objects duplicate what overlays already communicate
- Maintenance burden doubles: every new feature requires changes in both renderers
- CV2 integration path is unclear — SceneProjection understands overlay commands but not GeometryRenderer's Part objects

### Option D: Existing ownership is already correct

The current state — SceneRenderer as main renderer with overlays, GeometryRenderer as standalone experimental renderer — is accepted as-is. No ownership is formally assigned.

**Evidence supporting this option:**
- Both renderers currently produce correct output in their respective use cases
- GeometryRenderer does not interfere with SceneRenderer's pipeline
- SceneRenderer's overlay mechanism is already sufficient for the 4 existing types

**Evidence against this option:**
- Leaves the dual-path ambiguity unresolved for new features
- Without formal ownership, new manufacturing features may be added to the wrong renderer
- Creates risk of divergent classification sets (feature kind strings, hardware intent mappings)
- Violates the project constitution principle of "evidence before conclusions" — evidence of dual paths exists and must be resolved

---

## 6. Risks

| Risk | Level | Mitigation (ADR only) |
|------|-------|----------------------|
| SceneRenderer overlay pipeline may need expansion for complex feature shapes | LOW | Overlay pipeline already handles arbitrary position/diameter/depth data. Complex shapes may need new visual_type values but not architecture changes. |
| GeometryRenderer's additive Part objects already work and may be more intuitive for debugging | MODERATE | This ADR does not remove GeometryRenderer. It remains available as a secondary/experimental display path. Only canonical manufacturing rendering ownership is assigned. |
| SceneRenderer has no per-feature color control (only per-role) | LOW | VisualMetadata can carry per-feature color data. Overlay dicts already include optional style fields. |
| SceneRenderer currently ignores most feature types (minifix, confirmat, hinge, etc.) | MODERATE | This is the gap HFG implementation fills. The overlay pipeline is designed for extension — each new feature is ~15 lines of extraction + ~15 lines of overlay conversion. |
| Overlay commands are dicts — no type safety | LOW | VisualMetadata dataclasses provide type safety at the data layer. Overlay commands are intentionally dicts for serialization. |

---

## 7. Business Impact

| Factor | Impact | Rationale |
|--------|--------|-----------|
| Implementation speed | POSITIVE | SceneRenderer's existing overlay pipeline reduces new feature cost to ~30 lines each |
| Learning curve | LOW | Adding a new overlay type follows the exact same pattern as the 4 existing types |
| Dual-path cleanup cost | NONE | This ADR does not mandate cleanup, only ownership. Existing GeometryRenderer continues working. |
| Future maintenance | POSITIVE | Single canonical path eliminates "which renderer?" decisions for new features |
| CV2 integration | POSITIVE | SceneRenderer → SceneProjection path is already established |

---

## 8. Architectural Impact

| Component | Impact |
|-----------|--------|
| `scene_graph/renderer.py` | Gains ownership of manufacturing visualization. Extended with new overlay methods. |
| `scene_graph/metadata.py` | Gains new dataclass fields (minifix_holes, confirmat_holes, etc.) |
| `scene_graph/registry.py` | Unchanged — existing strategy mechanism sufficient. |
| `gui/renderer.py` | Unchanged — remains as secondary/experimental display path. No ownership change. |
| `manufacturing/visible_geometry_plan.py` | Feature classification logic extracted into metadata.py; visible_geometry_plan remains for GeometryRenderer. |
| `manufacturing/panel_shape_processor.py` | Shared between both renderers — unchanged. |
| `ui/configurator_v2/scene_projection.py` | Extended with visible_features field carrying manufacturing feature projections. |
| `engine/` renderer family | Unchanged — remains stale. No ownership impact. |

---

## 9. Maintenance Cost

| Action | Cost |
|--------|------|
| Ownership documentation | ZERO — this ADR establishes it |
| Per-feature implementation | ~30 lines each (15 extraction + 15 overlay) in existing files |
| Per-feature tests | ~50-100 lines each following existing overlay test patterns |
| GeometryRenderer maintenance | Unchanged — continues at current level |

---

## 10. ROI Assessment

| Factor | Rating | Detail |
|--------|--------|--------|
| Decision clarity | HIGH | Single canonical renderer eliminates ambiguity |
| Implementation cost | ZERO for decision, LOW per feature | ADR is documentation only; ~30 lines per feature |
| Dual-path risk | ELIMINATED by ownership assignment | New features go to SceneRenderer |
| GeometryRenderer value | PRESERVED | Remains available for standalone/experimental preview |
| CV2 integration path | CLEAR | SceneProjection extends from SceneRenderer data |
| Architectural drift | PREVENTED | Ownership is explicit, not implicit |

---

## 11. Final Decision

### APPROVED — Option A: SceneRenderer owns all manufacturing visualization

**Effective immediately.** SceneRenderer (`scene_graph/renderer.py`) is the canonical renderer for High-Fidelity Manufacturing Visualization. All new manufacturing feature rendering uses the existing `build_visual_overlays()` → `build_viewport_overlay_commands()` pipeline in SceneRenderer, extended with:

1. New `VisualMetadata` dataclass fields for each feature type (mirroring existing `drill_holes`, `grooves`, `edge_banding`, `hardware_markers`)
2. New SceneRenderer static methods `_<feature>_overlays()` and `_<feature>_viewport_command()` for each feature type (mirroring existing `_drill_hole_overlays()`, `_drill_viewport_command()`, etc.)
3. New extraction functions in `scene_graph/metadata.py` for each feature type (mirroring existing `_drill_holes_from_cnc()`, `_grooves_from_node()`, etc.)

Supporting evidence:
- SceneRenderer is connected to the main `render_graph()` pipeline
- SceneRenderer already has the overlay extension mechanism with 4 working types
- SceneRenderer's `_hardware_visual_type()` already classifies HINGE, DRAWER_SLIDE, SHELF_PIN
- SceneRenderer feeds SceneProjection → CV2 PreviewRegion
- SceneRenderer's overlay dicts are FreeCAD-free — testable without `Part` module
- The 3-step overlay pattern (dataclass → overlay dict → viewport command) requires zero new architecture

---

## 12. Consequences

### Positive
- Single canonical path for manufacturing visualization
- Existing `build_visual_overlays()` pipeline reused without modification
- RendererRegistry strategy registration available for role-specific extensions
- SceneProjection extends naturally with visible_features field
- Overlay commands remain FreeCAD-free for CV2 consumption

### Neutral
- GeometryRenderer (`gui/renderer.py`) continues to exist but is not the manufacturing rendering owner. It remains available for standalone/experimental preview and does not require changes.
- `engine/` renderer family remains stale. This ADR does not affect it.

### Negative
- Manufacturing features require overlay methods even for features that could be displayed via raw Part objects
- Per-feature color/transparency must be carried through VisualMetadata if needed

---

## 13. Future Work

The following implementation tasks are identified but NOT mandated by this ADR:

1. **Extend `VisualMetadata`** (scene_graph/metadata.py): Add `minifix_holes`, `confirmat_holes`, `hinge_cup_holes`, `drawer_slide_holes`, `shelf_pin_features`, `hinge_plate_positions` tuple fields. Add extraction functions `_minifix_from_cnc()`, `_confirmat_from_cnc()`, `_hinge_cup_from_cnc()`, `_drawer_slide_from_cnc()`, `_shelf_pin_from_cnc()`, `_hinge_plate_from_cnc()`.

2. **Extend `SceneRenderer`** (scene_graph/renderer.py): Add `_minifix_overlays()`, `_confirmat_overlays()`, `_hinge_cup_overlays()`, `_drawer_slide_overlays()`, `_shelf_pin_overlays()`, `_hinge_plate_overlays()` static methods. Add corresponding `_minifix_viewport_command()`, `_confirmat_viewport_command()` etc. Wire into `build_visual_overlays()` and `build_viewport_overlay_commands()`.

3. **Extend `process_panel_shape()`** (manufacturing/panel_shape_processor.py): Add new feature kinds to `_feature_supported_for_panel()` if subtractive solid cutting is desired per feature type.

4. **Extend `SceneProjection`** (ui/configurator_v2/scene_projection.py): Add `visible_features` field carrying manufacturing feature projections as frozen dataclasses.

5. **Extend CV2 Viz adapters**: Create `manufacturing_feature_adapter` module converting scene_graph overlay data to CV2-native read models.

6. **Contract tests**: Mirror existing `test_overlay_renderer_contract.py` pattern for each new feature type.

---

*This ADR establishes architectural ownership only. No code, no renderers, no engines, no migrations, and no refactoring are mandated.*
