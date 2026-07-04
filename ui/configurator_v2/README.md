# Configurator V2 Shell

This package contains the navigable workspace shell for Configurator V2.

It follows:

- ADR-0014 Product Architecture V1
- ADR-0015 Configurator Interaction Model
- ADR-0016 Workspace Layout & Navigation Model

This is a shell only:

- no backend logic
- no manufacturing or cost computation
- no commercial pricing
- no CNC generation
- no new renderer

Current state:

- workspace regions exist
- navigation metadata exists
- project context state exists
- product state indicator exists
- selection model exists
- action bar exists
- message center exists
- review containers exist

Read Models:

- the UI consumes read models instead of domain internals
- read models are passive and read-only
- backend adapters will be connected in a later sprint
- the UI must not read FreeCAD, SceneGraph, manufacturing, cost, or commercial internals directly

Projection Adapters:

- adapters convert backend outputs into read models
- adapters do not call services
- adapters do not compute backend truth
- UI consumers receive read models only

Service Integration:

- services are called only through the integration controller
- UI widgets consume read models only
- unsupported capabilities become messages, not fake data
- future sprints will wire real actions gradually

Inspector:

- InspectorRegion consumes InspectorReadModel only
- selection changes flow through the projection adapter layer
- Inspector rendering is read-model driven and read-only
- unsupported selections are shown as messages and display metadata, not exceptions

Preview:

- PreviewRegion consumes PreviewReadModel only
- preview data comes from projection adapters and service integration
- the widget renders titles, scene availability, bounds, node counts, state, representations, warnings, and placeholder messages
- selection highlighting remains as a compatibility hook, but no geometry is accessed directly

Visual Component Library:

- SceneProjection is translated into presentation-only visual components before preview consumption
- visual components expose furniture concepts such as Cabinet, Door, Drawer, Shelf, Divider, Back Panel, Hardware, and Feature Marker
- visual components contain style-ready metadata only: labels, colors, icons, visibility, state, bounds, warnings, and theme keys
- visual components do not contain geometry, SceneNode instances, FreeCAD objects, or renderer-specific objects
- this keeps preview logic independent from both SceneGraph internals and any future rendering backend

Scene Projection Layer:

- SceneGraph is projected into SceneProjection before the UI sees it
- SceneProjection contains only safe presentation data
- SceneProjection flows into Visual Components, then into PreviewReadModel, then into PreviewRegion
- Projection adapters reuse SceneProjection and do not duplicate SceneGraph traversal
- PreviewRegion stays renderer-agnostic and does not touch geometry objects
- this keeps the UI compatible with a future standalone renderer

Integration is still pending:

- Application Services are not called yet
- preview remains a placeholder
- manufacturing, cost, commercial, and release panels remain read-only containers

Future sprints will connect the shell to existing Application Services and backend projections.

## Furniture Visual Styles

Visual Components describe *what* furniture element exists.
Furniture Visual Styles describe *how* that element should appear.

The style layer sits between Visual Components and the PreviewReadModel:

    SceneProjection
         ↓
    Visual Components
         ↓
    Furniture Visual Styles  ← (this layer)
         ↓
    PreviewReadModel
         ↓
    PreviewRegion

### Design Rules

- **Presentation-only**: styles carry colour, finish, texture, door type, handle position, etc. — never geometry, machining logic, CNC data, or cost.
- **No backend objects**: styles contain no FreeCAD, SceneNode, or backend geometry references.
- **No renderer**: styles prepare hints for a future renderer, but do not render anything.
- **Backward compatible**: VisualComponent subclasses remain unchanged. Style metadata is added via `display_metadata` pairs on `PreviewItemReadModel`.

### Style Types

| Style | Component Type | Fields |
|---|---|---|
| `DoorVisualStyle` | `DoorVisualComponent` | door_type (slab/shaker/glass/framed/flush), overlay_inset, handle_position |
| `DrawerVisualStyle` | `DrawerVisualComponent` | front_type (slab/framed), internal_box, slide_type, handle_position |
| `PanelVisualStyle` | `PanelVisualComponent` | material_finish, color_name, texture_descriptor, edge_banding_appearance |
| `BackPanelVisualStyle` | `BackPanelVisualComponent` | thin_panel, recessed_panel, groove_indicator |
| `HardwareVisualStyle` | `HardwareVisualComponent` | hinge, handle, drawer_slide, shelf_pin, minifix, confirmat |
| `FeatureMarkerVisualStyle` | `FeatureMarkerComponent` | drilling, groove, cutout, edge_band_feature, machining_marker |

### Builder API

```python
from .furniture_visual_styles import build_furniture_visual_style, apply_furniture_visual_styles

style = build_furniture_visual_style(door_component)
# -> DoorVisualStyle(door_type="shaker", overlay_inset="overlay", ...)

styles = apply_furniture_visual_styles(components)
# -> tuple[FurnitureVisualStyle, ...]
```

### Metadata Flow

When `build_preview_read_model` processes visual components, it calls `build_furniture_visual_style` for each component and flattens the result into `display_metadata` pairs on `PreviewItemReadModel`. The `PreviewRegion` can then display style summaries via `style_summary_label()`.

### Rendering

Rendering Furniture Visual Styles into actual 3D or 2D visuals remains **future work**. This layer only captures what a renderer *would* need to know to display furniture elements correctly.

## Interactive Furniture Components

Visual Components define *what* furniture element exists.
Furniture Visual Styles describe *how* that element should appear.
Interactive Components define *how the user interacts* with each element.

The interactive layer sits between Visual Styles and the PreviewReadModel:

    SceneProjection
         ↓
    Visual Components
         ↓
    Furniture Visual Styles
         ↓
    Interactive Components    ← (this layer)
         ↓
    PreviewReadModel
         ↓
    PreviewRegion

### Design Rules

- **Presentation-only**: interaction state carries booleans (selected, highlighted, expanded, visible) and strings (state label, motion hint) — never geometry, transforms, positions, or backend objects.
- **Renderer independent**: toggles like `door_swing_visible` and `drawer_open_visible` are hints for a future renderer. No swing arcs or open indicators are actually drawn.
- **No geometry**: no hit-testing, no spatial queries, no bounds computation.
- **No FreeCAD dependency**: the layer imports only `VisualComponent` from the same package.
- **No SceneGraph dependency**: the builder works from `VisualComponent` state, not from `SceneProjection` or `SceneGraph`.

### Interaction State Types

| Type | Data |
|---|---|
| `ComponentInteractionOverlay` | selected, highlighted, expanded (all bool) |
| `ComponentVisibilityState` | visible, hardware_visible, feature_markers_visible, door_swing_visible, drawer_open_visible (all bool) |
| `ComponentMotionIndicator` | motion_hint: str (e.g. "swing", "slide") |
| `ComponentInteractionState` | aggregates overlay + visibility + motion + state_label + tooltip + warnings |
| `InteractiveVisualComponent` | component_id, component_type, display_name + ComponentInteractionState |

### Interaction States

| State | Description |
|---|---|
| `NORMAL` | Default resting state |
| `SELECTED` | User has clicked/selected the component |
| `HIGHLIGHTED` | Component is under cursor or programmatically targeted |
| `EXPANDED` | Sub-structure is revealed (e.g. opened cabinet) |
| `COLLAPSED` | Sub-structure is hidden |
| `HIDDEN` | Component is not visible |
| `UNSUPPORTED` | Component cannot be interacted with |
| `STALE` | Component data is out of date |

### Builder API

```python
from .interactive_components import build_interactive_visual_components

interactives = build_interactive_visual_components(
    components,
    selected_component_id="door-1",
    highlighted_component_id="door-1",
    show_hardware=True,
    show_feature_markers=True,
    show_door_swing=False,
    show_drawer_open=False,
)
# -> tuple[InteractiveVisualComponent, ...]
```

### Toggle Rules

- `hardware_visible`: only applies to HARDWARE, DOOR, DRAWER, and CABINET types.
- `feature_markers_visible`: only applies to FEATURE_MARKER type.
- `door_swing_visible`: forced False for non-DOOR types.
- `drawer_open_visible`: forced False for non-DRAWER types.
- `motion_hint` is derived automatically: "swing" for DOOR with swing enabled, "slide" for DRAWER with open enabled.

### Metadata Flow

When `build_preview_read_model` receives `interactive_components` in its source dict, it builds `PreviewItemReadModel` items from the interactive components, embedding `interaction_state`, `selected`, `highlighted`, `visible`, `hardware_visible`, `feature_markers_visible`, `door_swing_visible`, `drawer_open_visible`, and `motion_hint` as display metadata pairs.

### Service Integration

`ConfiguratorV2ServiceIntegration.refresh_preview()` accepts the same four toggle keyword arguments (`show_hardware`, `show_feature_markers`, `show_door_swing`, `show_drawer_open`). When any toggle is provided, the integration builds interactive components from the scene-projected visual components and routes them through the interactive pipeline. When no toggles are provided, the original visual-components-only path is used.

### Rendering

Rendering Interactive Components — swing arcs, drawer-open indicators, highlight glows, selection rings — remains **future work**. This layer captures the interaction *state* that a renderer would use, but does not render anything.
