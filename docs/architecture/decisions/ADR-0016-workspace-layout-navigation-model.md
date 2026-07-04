# ADR-0016
Workspace Layout & Navigation Model

## Status

Accepted

## Context

ADR-0014 defines SmartFurnitureWB as a product with the Configurator as the primary UI, Application Services as the only gateway, and FreeCAD as the backend engineering and preview layer.

ADR-0015 defines how the Configurator behaves:

- product state model
- interaction flow
- service call rules
- preview modes
- error and warning behavior

The remaining missing decision is the permanent workspace structure: where the user navigates, where the project tree lives, where preview lives, where properties are edited, and where validation, manufacturing, cost, commercial, and release evidence live.

The current repository evidence still shows a narrow two-tab `QMainWindow` in `ui/main_window.py`, which is not yet a multi-role furniture manufacturing workspace. This ADR establishes the long-term workspace layout and navigation model without changing production code.

## Evidence

Repository evidence used for this decision:

- `ui/main_window.py`
  - current narrow parameter-editor shell
- `ui/issue_presenter.py`
  - current inline warning/issue presentation
- `engine/cabinet_builder.py`
  - FreeCAD-backed geometry and scene-graph bridge
- `gui/renderer.py`
  - document-level preview renderer
- `manufacturing/visible_geometry_plan.py`
  - manufacturing-aware preview overlays
- `manufacturing/factory_decision_projection.py`
  - read-only release review projection
- `manufacturing/manufacturing_production_package.py`
  - production evidence container
- `commercial_outputs/commercial_package_report.py`
  - passive commercial summary
- `docs/architecture/decisions/ADR-0014-product-architecture-v1.md`
  - Configurator is the primary UI
- `docs/architecture/decisions/ADR-0015-configurator-interaction-model.md`
  - interaction flow, state model, preview modes, service rules

## Decision

The Configurator workspace is a multi-role furniture manufacturing workspace.

It is not:

- a simple form
- a FreeCAD command window
- a generic CAD canvas
- a standalone renderer
- a business logic layer

It must support the daily work of:

- designer
- sales user
- estimator
- production engineer
- factory manager

The workspace is organized as a single coherent product surface with persistent regions for navigation, project structure, preview, inspection, review, and actions.

## Main Workspace Areas

### 1. Global Navigation

The global navigation surface is the persistent entry point for product-level modules:

- Dashboard
- Projects
- Customers
- Product Families
- Materials / Hardware
- Manufacturing
- Cost
- Commercial
- Factory Release
- Settings

Responsibility:

- move the user across major business areas
- preserve the active project and product context where possible

Allowed actions:

- switch top-level area
- open recent work
- return to the active project workspace

Forbidden logic:

- computing manufacturing truth
- computing cost or commercial truth
- duplicating release decisions

Stale data behavior:

- changing the active project or product invalidates downstream review panes until refreshed

### 2. Project Tree

The project tree is the structural navigation surface for the current workspace:

- Customer
- Project
- Room
- Wall
- Product / Cabinet
- Documents

Responsibility:

- show the active hierarchy and selection path
- make the current project structure navigable

Allowed actions:

- select a project node
- open a product/cabinet node
- open related documents
- jump to a room or wall context

Forbidden logic:

- generating engineering or manufacturing output
- computing pricing or release status

Stale data behavior:

- tree selections remain visible, but downstream review panes must flag stale data after configuration changes

### 3. Central Preview Area

The central area is the live preview and design canvas.

It must provide:

- live 3D preview
- SceneGraph-backed rendering
- FreeCAD backend preview bridge
- preview modes from ADR-0015

Responsibility:

- show the current product truth visually
- present overlays for manufacturing and quality review

Allowed actions:

- change preview mode
- inspect selected geometry
- request refresh

Forbidden logic:

- generating manufacturing truth
- generating cost or commercial truth
- hiding blockers

Stale data behavior:

- preview must visibly indicate when the geometry or evidence is outdated

### 4. Inspector Panel

The inspector is the selected-object and property review area.

It must include:

- selected object properties
- dimensions
- materials
- doors
- drawers
- shelves
- dividers
- hardware

Responsibility:

- display editable or read-only properties depending on selection and state
- support local draft editing of the current selection

Allowed actions:

- edit draft properties where the current state allows it
- inspect selection metadata
- jump to related review modules

Forbidden logic:

- recomputing engineering or manufacturing values
- changing release decisions

Stale data behavior:

- when upstream draft data changes, the inspector must mark derived fields stale until refreshed

### 5. Review Panels

The review panels are dedicated evidence surfaces:

- Validation
- Manufacturing
- Cost
- Commercial
- Release

Responsibility:

- present backend outputs for review
- support decision-making without owning the decision logic

Allowed actions:

- review evidence
- acknowledge warnings
- request refresh
- proceed when the backend state allows it

Forbidden logic:

- generating backend truth locally
- suppressing blockers
- modifying decisions

Stale data behavior:

- each review panel must show stale state when its source data is older than the active draft

### 6. Message Center

The message center is the persistent evidence and alert surface.

It must show:

- validation errors
- manufacturing blockers
- commercial warnings
- stale data warnings
- unsupported family warnings

Responsibility:

- surface the current priority of issues across the workspace
- keep blocking issues visible even when the user is in another area

Allowed actions:

- acknowledge warnings
- open the source panel or selection that produced the message

Forbidden logic:

- downgrading backend blockers
- hiding stale states
- silently dismissing unsupported family warnings

Stale data behavior:

- stale warnings remain visible until the related outputs are refreshed

### 7. Action Bar

The action bar is the explicit workflow control surface.

It must include:

- Save Draft
- Refresh Preview
- Validate
- Generate Manufacturing
- Review Cost
- Generate Quotation
- Approve Release
- Export Production Documents

Responsibility:

- provide deliberate workflow actions
- make progression explicit rather than implicit

Allowed actions:

- request the next backend step
- save the local draft state

Forbidden logic:

- computing manufacturing or commercial truth
- auto-approving release

Stale data behavior:

- disabled or stale actions must explain why they are unavailable

## Navigation Rules

The navigation rules are strict:

- The user enters through Dashboard or Project.
- Project context must be active before product configuration.
- Product Family selection happens before Configurator editing.
- Preview must show stale state if configuration changed.
- Manufacturing, Cost, and Commercial panels are read-only until backend refresh.
- Release panel cannot be active before Manufacturing and Commercial readiness.
- Unsupported product families must be visible but blocked from release.
- FreeCAD document view must not be the primary navigation surface.

## Layout Policy

The preferred layout concept is:

- Left: Global navigation and project tree
- Center: Live preview / design canvas
- Right: Inspector / selected item properties
- Bottom: Messages / validation / warnings
- Secondary tabs or panels: Manufacturing, Cost, Commercial, Release

This ADR defines layout policy only.

It does not define exact Qt widgets, exact docking primitives, or a pixel-level mockup.

## Role-Based Views

### Designer

Emphasis:

- Configurator
- Preview
- Validation

### Sales

Emphasis:

- Customer view
- Cost summary
- Quotation
- Commercial approval

### Estimator

Emphasis:

- Materials
- Hardware
- Cost
- Profitability

### Production Engineer

Emphasis:

- Manufacturing detail
- CNC
- Hardware BOM
- Assembly
- Release blockers

### Factory Manager

Emphasis:

- Project status
- release queue
- risk summary
- profitability
- workload signals

## Panel Responsibilities

| Area | Responsibility | Data source | Allowed actions | Forbidden logic | Stale data behavior |
|---|---|---|---|---|---|
| Global Navigation | Switch major workspace areas and preserve context. | Workspace state, active project, active family. | Navigate, open recent work, return to active workspace. | Manufacturing, cost, commercial, release computation. | Downstream panels stale until refreshed after context changes. |
| Project Tree | Show project hierarchy and current selection path. | Customer/project/room/wall/cabinet/document structure. | Select nodes, open documents, jump context. | Output generation or pricing. | Selection remains valid; derived panes show stale badges after draft changes. |
| Preview | Display current product truth visually. | SceneGraph, FreeCAD backend, visible geometry plan. | Change mode, inspect geometry, refresh preview. | Truth generation or blocker suppression. | Must visibly indicate outdated geometry/evidence. |
| Inspector | Display selected object properties and draft-editable fields. | Current selection, draft state, product properties. | Edit allowed draft values, inspect metadata. | Recomputing backend truth. | Derived fields stale after upstream edits. |
| Validation | Show engineering validation and warnings. | Validation service outputs and diagnostics. | Review, refresh, acknowledge. | Altering validation rules or verdicts. | Must show stale state if draft changed after validation. |
| Manufacturing | Show manufacturing evidence and readiness. | Manufacturing application outputs and production package. | Review evidence, refresh, inspect blockers. | Creating manufacturing truth locally. | Must show stale state if configuration changed. |
| Cost | Show cost and margin evidence. | Cost pipeline outputs, commercial summary. | Review, refresh, compare outputs. | Price computation in UI. | Must show stale state if manufacturing evidence changed. |
| Commercial | Show quotation and commercial readiness. | Commercial package report, quotation document. | Review, refresh, acknowledge warnings. | Commercial logic in UI. | Must show stale state if cost or manufacturing changed. |
| Release | Show release readiness and go/no-go evidence. | Decision projection, release package, release decision. | Approve, reject, inspect blockers. | Computing release truth locally. | Must show stale state if upstream evidence changes. |
| Message Center | Surface blockers, warnings, and stale state. | Validation, manufacturing, cost, commercial, release outputs. | Acknowledge, open source panel. | Hiding or downgrading blockers. | Stale warnings remain until relevant refresh occurs. |
| Action Bar | Trigger the workflow explicitly. | Active draft and current backend status. | Save, refresh, validate, generate, approve, export. | Backend truth computation. | Disabled actions must explain stale or unsupported conditions. |

## Preview Integration

Preview is part of the workspace, not a separate product.

Rules:

- Preview consumes SceneGraph / backend geometry.
- Preview modes are inherited from ADR-0015.
- Manufacturing overlays use existing `VisibleGeometryPlan` and production evidence.
- Preview must not generate manufacturing truth.
- Preview must not hide blockers.
- Preview must show stale state if geometry or evidence is outdated.

## Message Center Model

Message categories:

- Blocking validation errors
- Non-blocking warnings
- Manufacturing blockers
- Commercial warnings
- Release blockers
- Stale output warnings
- Unsupported product family warnings
- System errors

Severity values:

- `BLOCKER`
- `WARNING`
- `INFO`
- `STALE`
- `UNSUPPORTED`

Rules:

- Blockers must always be visible.
- Warnings must remain visible until acknowledged.
- Stale state must be visible wherever outdated outputs are shown.
- UI must not downgrade backend blockers.
- Unsupported families must remain visible as unsupported rather than being routed into the wrong flow.

## Non-Goals

This ADR explicitly excludes:

- SaaS
- ERP
- MES
- inventory planning
- FreeCAD removal
- a new geometry backend
- a new renderer engine
- direct CNC authoring in UI
- pricing logic inside UI
- manufacturing logic inside UI
- exact Qt widget implementation
- visual mockup implementation

## Risks

The main risks are:

- forcing a production workspace into a simple-form mental model
- allowing the project tree to become a second place where business logic leaks in
- confusing navigation with state transitions
- making preview the source of truth instead of a backend-backed view
- hiding release blockers behind visually attractive panels
- turning the message center into an unprioritized log instead of a decision surface
- adding a duplicate GUI structure instead of extending the existing product surface

## Consequences

This decision establishes the permanent workspace shape for Configurator V2:

- the user always has a clear navigation path
- project structure remains visible throughout the workflow
- preview remains central
- properties remain inspectable on the right
- blockers and warnings remain persistent and visible
- manufacturing, cost, commercial, and release evidence are surfaced as dedicated review areas rather than hidden inside forms

The workspace remains a product experience layer, not a backend engine.

## References

- [docs/architecture/decisions/ADR-0014-product-architecture-v1.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0014-product-architecture-v1.md)
- [docs/architecture/decisions/ADR-0015-configurator-interaction-model.md](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/docs/architecture/decisions/ADR-0015-configurator-interaction-model.md)
- [ui/main_window.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/ui/main_window.py)
- [ui/issue_presenter.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/ui/issue_presenter.py)
- [engine/cabinet_builder.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/engine/cabinet_builder.py)
- [gui/renderer.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/gui/renderer.py)
- [manufacturing/visible_geometry_plan.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/visible_geometry_plan.py)
- [manufacturing/factory_decision_projection.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/factory_decision_projection.py)
- [manufacturing/manufacturing_production_package.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/manufacturing/manufacturing_production_package.py)
- [commercial_outputs/commercial_package_report.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/commercial_outputs/commercial_package_report.py)
