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
