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

Scene Projection Layer:

- SceneGraph is projected into SceneProjection before the UI sees it
- SceneProjection contains only safe presentation data
- Projection adapters convert SceneProjection into PreviewReadModel
- PreviewRegion stays renderer-agnostic and does not touch geometry objects
- this keeps the UI compatible with a future standalone renderer

Integration is still pending:

- Application Services are not called yet
- preview remains a placeholder
- manufacturing, cost, commercial, and release panels remain read-only containers

Future sprints will connect the shell to existing Application Services and backend projections.
