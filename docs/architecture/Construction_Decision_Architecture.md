# Construction Decision Architecture

## 1. Problem Statement

SmartFurnitureWB currently has duplicated construction authority in the back-panel path.

- `ConstructionResolver` defines a single grooved full-cabinet back panel as part of the construction model.
- `GeometryEngine` and `SceneGraphBuilder` also make back-panel decisions from section resolution and emit per-section back panels.

That split creates inconsistent geometry contracts, an incorrect visible model in FreeCAD, and unreliable downstream manufacturing visualization.

This document defines the official ownership boundary for construction decisions in SmartFurnitureWB.

## 2. Evidence From Current Back Panel Conflict

Repository evidence shows two different sources of back-panel authority:

- `domain/construction_resolver.py`
  - Builds `CabinetConstructionModel`
  - Sets `back_panel.placement = "Inside rear groove behind side/top/bottom panels"`
  - Sets `back_panel.installation_mode = "GROOVED"`
  - Sets the back panel dimensions to the cabinet-level construction contract

- `domain/base_cabinet_engineering_model.py`
  - Converts the construction model into engineering coordinates
  - Places the back panel at a single cabinet-level position

- `engine/geometry_engine.py`
  - Resolves section openings and section geometry
  - Does not own construction decisions

- `scene_graph/builder.py`
  - Builds one `BACK_PANEL` node per resolved section in the GeometryEngine path
  - Uses `resolve_back_panel_geometry(...)` to derive back-panel dimensions from section geometry

- `tests/domain/test_construction_resolver_contract.py`
  - Expects a single construction-model back panel

- `tests/manufacturing/test_scene_graph_back_panel_geometry.py`
  - Expects the scene graph to reflect the geometry path’s current back-panel behavior

The conflict is not a renderer bug alone. It is an ownership mismatch across layers.

## 3. Definition Of Construction Decision

A construction decision is a product-level structural choice that determines how the cabinet is physically built before geometry and rendering.

Examples:

- whether the back panel is grooved, overlay, rabbeted, or full-span
- whether shelves are fixed or adjustable
- whether dividers are structural or optional
- whether the door system is inset, overlay, or sliding
- whether drawers use a box-based or face-based strategy
- whether plinth/base is structural or decorative

Construction decisions are not render instructions.
They are not manufacturing Boolean operations.
They are not layout-only dimensions.

They are the authoritative source for downstream engineering, manufacturing, and cost translation.

## 4. Differences Between Core Layers

### Product Parameters

Product parameters are user-facing inputs.

Examples:

- cabinet width, height, depth
- section count
- shelf count
- drawer count
- door count
- back panel type preference

Product parameters describe intent, not the final construction method.

### Construction Decisions

Construction decisions are the resolved product structure produced from product parameters and rules.

Examples:

- grooved back panel
- adjustable shelf with side-panel support
- divider strategy
- door strategy

Construction decisions determine the cabinet’s actual architecture.

### Engineering Geometry

Engineering geometry is the coordinate-ready representation of the resolved construction model.

It answers:

- where each physical component is placed
- what dimensions each component has
- how the resolved structure maps into 3D space

Engineering geometry must not invent the construction strategy.

### Manufacturing Operations

Manufacturing operations are process instructions derived from the resolved engineering model.

Examples:

- grooves
- drilling
- cuts
- hardware placements

Manufacturing operations must consume construction and geometry decisions, not create them.

## 5. Ownership Rule

`ConstructionResolver` owns construction decisions.

It is the authoritative place where SmartFurnitureWB decides:

- what cabinet structure is being built
- which construction strategy applies to each major component
- which structural features exist at all

The construction model is the source of truth for all downstream layers.

## 6. Do-Not-Own Rule

The following components must not invent construction decisions:

- `GeometryEngine`
- `SceneGraphBuilder`
- `Renderer`
- `ManufacturingCompiler`

These layers may:

- interpret construction decisions
- convert them into coordinates
- render them
- compile them into manufacturing outputs

They must not:

- decide the back-panel strategy
- decide whether a shelf is structural or adjustable
- decide whether a divider exists as a construction choice
- decide whether a door is overlay or inset
- decide whether a groove is the construction strategy or only a machining feature

## 7. Decision Dictionary

| Decision | Current Owner(s) | Final Owner | Outputs | Consumed By | Current Duplication Risk | Migration Priority |
|---|---|---|---|---|---|---|
| Back Panel Strategy | `ConstructionResolver`, `GeometryEngine`, `SceneGraphBuilder`, `ManufacturingExtractor`, `Renderer` | `ConstructionResolver` | `BackPanelConstruction`, engineering placement, back-panel nodes, groove operations | Engineering model, scene graph, renderer, manufacturing pipeline | High | Highest |
| Shelf Support Strategy | `ConstructionResolver`, `GeometryEngine`, `SceneGraphBuilder` | `ConstructionResolver` | shelf ownership, support style, shelf geometry | engineering model, scene graph, manufacturing | Medium | High |
| Divider Strategy | `ConstructionResolver`, `GeometryEngine`, `SceneGraphBuilder` | `ConstructionResolver` | divider count, divider locations, divider nodes | engineering model, scene graph, manufacturing | High | High |
| Door Strategy | `ConstructionResolver`, `GeometryEngine`, `SceneGraphBuilder`, `ManufacturingCompiler` | `ConstructionResolver` | overlay/inset/sliding intent, door geometry, hinge strategy | engineering model, renderer, compiler | High | High |
| Drawer Box Strategy | `ConstructionResolver`, `GeometryEngine`, `SceneGraphBuilder`, `ManufacturingCompiler` | `ConstructionResolver` | drawer face/box contract, slide strategy, machining inputs | engineering model, renderer, compiler | High | High |
| Plinth/Base Strategy | `ConstructionResolver`, `SceneGraphBuilder` | `ConstructionResolver` | base/plinth structure, clearance, placement | engineering model, scene graph, renderer | Medium | Medium |
| Wall Mount Strategy | `ConstructionResolver`, `ManufacturingExtractor`, `Rules Engine` | `ConstructionResolver` | wall-mount intent, anchor model, clearance model | engineering model, manufacturing, validation | High | High |
| Hardware Joinery Strategy | `ConstructionResolver`, `Rules Engine`, `ManufacturingCompiler` | `ConstructionResolver` | joinery method, connectors, hardware intent | engineering model, manufacturing, cost | High | High |

## 8. Decision Ownership Details

### Back Panel Strategy

- Current owners:
  - `ConstructionResolver`
  - `GeometryEngine`
  - `SceneGraphBuilder`
  - `ManufacturingExtractor`
  - `Renderer`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - `BackPanelConstruction`
  - engineering back-panel placement
  - scene graph back-panel node
  - groove machining operations
- Consumed by:
  - engineering model
  - scene graph
  - renderer
  - manufacturing compiler
- Current duplication risk:
  - High
- Migration priority:
  - Highest

### Shelf Support Strategy

- Current owners:
  - `ConstructionResolver`
  - `GeometryEngine`
  - `SceneGraphBuilder`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - shelf ownership
  - fixed vs adjustable contract
  - shelf placement intent
- Consumed by:
  - engineering model
  - scene graph
  - manufacturing
- Current duplication risk:
  - Medium
- Migration priority:
  - High

### Divider Strategy

- Current owners:
  - `ConstructionResolver`
  - `GeometryEngine`
  - `SceneGraphBuilder`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - divider strategy
  - divider count
  - divider placement intent
- Consumed by:
  - engineering model
  - scene graph
  - manufacturing
- Current duplication risk:
  - High
- Migration priority:
  - High

### Door Strategy

- Current owners:
  - `ConstructionResolver`
  - `GeometryEngine`
  - `SceneGraphBuilder`
  - `ManufacturingCompiler`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - door strategy
  - overlay / inset / sliding intent
  - hinge-side and door-opening contract
- Consumed by:
  - engineering model
  - scene graph
  - renderer
  - manufacturing compiler
- Current duplication risk:
  - High
- Migration priority:
  - High

### Drawer Box Strategy

- Current owners:
  - `ConstructionResolver`
  - `GeometryEngine`
  - `SceneGraphBuilder`
  - `ManufacturingCompiler`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - drawer face/box strategy
  - slide contract
  - drawer manufacturing geometry
- Consumed by:
  - engineering model
  - scene graph
  - manufacturing compiler
- Current duplication risk:
  - High
- Migration priority:
  - High

### Plinth/Base Strategy

- Current owners:
  - `ConstructionResolver`
  - `SceneGraphBuilder`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - plinth/base height
  - base clearance
  - structural base placement
- Consumed by:
  - engineering model
  - scene graph
  - renderer
- Current duplication risk:
  - Medium
- Migration priority:
  - Medium

### Wall Mount Strategy

- Current owners:
  - `ConstructionResolver`
  - `Rules Engine`
  - `ManufacturingExtractor`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - wall-mount strategy
  - anchor compatibility intent
  - clearance intent
- Consumed by:
  - engineering model
  - validation
  - manufacturing
- Current duplication risk:
  - High
- Migration priority:
  - High

### Hardware Joinery Strategy

- Current owners:
  - `ConstructionResolver`
  - `Rules Engine`
  - `ManufacturingCompiler`
- Final owner:
  - `ConstructionResolver`
- Outputs:
  - joinery method
  - connector selection
  - hardware intent
- Consumed by:
  - engineering model
  - manufacturing compiler
  - cost model
- Current duplication risk:
  - High
- Migration priority:
  - High

## 9. Back Panel Strategy Target Model

The target model for back panels is:

- full back panel
- grooved back

The repository evidence supports a grooved full-cabinet back panel as the authoritative construction contract.

Not selected as the target model:

- per-section back panels
  - this is a geometry-path artifact
  - it duplicates construction authority
- overlay back
  - not the current construction contract
- rabbeted back
  - not the current construction contract

The contract target should be a single grooved back panel defined by `ConstructionResolver`, then translated into engineering coordinates, then rendered, then machined.

## 10. Migration Rules

- No big rewrite.
- Migrate one construction decision at a time.
- Preserve legacy paths until equivalent behavior exists.
- Add contract tests before switching render paths.
- Do not move construction decisions into geometry or renderer layers.
- Keep existing APIs stable while the ownership boundary is clarified.

## 11. First Recommended Implementation Sprint

### Back Panel Strategy Unification

Objective:

- make the Configurator, engineering, scene graph, renderer, and manufacturing layers consume one back-panel construction contract

Scope:

- align back-panel ownership
- remove per-section back-panel invention from geometry and scene-graph decision making
- preserve current API surfaces
- add or update contract tests before switching any render behavior

This is the first required follow-on sprint after documenting the architecture.

## 12. Final Classification

APPROVED as architecture documentation only.

