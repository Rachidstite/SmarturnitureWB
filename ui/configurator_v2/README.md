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

Integration is still pending:

- Application Services are not called yet
- preview remains a placeholder
- manufacturing, cost, commercial, and release panels remain read-only containers

Future sprints will connect the shell to existing Application Services and backend projections.
