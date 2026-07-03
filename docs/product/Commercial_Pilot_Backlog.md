# Commercial Pilot Backlog

This backlog defines the product work required before SmartFurnitureWB can support the first paying furniture manufacturer on real cabinet projects.

The backlog is organized by epics. It is intentionally scoped to Commercial Pilot and does not include ERP, MES, procurement automation, multi-factory SaaS, or enterprise integration work.

## Epic 1 - Product Family Coverage

Goal: support real cabinet-project variation without breaking the core workflow.

Stories:

- Base cabinet complete workflow
- Wall cabinet complete workflow
- Tall cabinet complete workflow
- Wardrobe complete workflow
- Corner cabinet support
- Blind corner cabinet support
- TV unit support
- Office cabinet / desk support

Acceptance notes:

- each supported family must flow through engineering, manufacturing, cost, commercial, and visualization outputs
- each family must produce predictable release evidence

## Epic 2 - Assembly Excellence

Goal: make the release package readable and executable in a workshop.

Stories:

- assembly sequence
- hardware order
- fastener map
- panel orientation
- installation notes
- workshop-readable instructions

Acceptance notes:

- a workshop user should be able to build the cabinet from the output package without reverse engineering the design intent

## Epic 3 - Production Documentation

Goal: produce the minimum manufacturing packet required for a real cabinet release.

Stories:

- cut list
- CNC file package
- edge banding list
- hardware list
- panel labels
- assembly sheets
- QA checklist
- delivery package

Acceptance notes:

- the packet should be complete enough for production preparation and handoff

## Epic 4 - Commercial Workflow

Goal: make the system useful for technical sales and quoting.

Stories:

- quotation package
- profitability summary
- commercial risk warnings
- customer package
- production release package

Acceptance notes:

- commercial output must remain aligned with the manufacturing release evidence

## Epic 5 - User Workflow

Goal: reduce friction between project setup and release.

Stories:

- new project wizard
- project review step
- manufacturing release step
- commercial release step
- export step
- error/warning review
- decision projection review

Acceptance notes:

- the workflow must stay understandable for non-developer technical users
- warnings must be reviewable before release
- release review should be possible from a single read-only projection over existing objects

## Backlog Priorities

Priority 1:

- Base cabinet complete workflow
- Wall cabinet complete workflow
- Tall cabinet complete workflow
- cut list
- CNC file package
- quotation package
- profitability summary
- project review step
- decision projection contract

Priority 2:

- wardrobe complete workflow
- assembly sequence
- hardware order
- panel labels
- assembly sheets
- QA checklist

Priority 3:

- corner cabinet support
- blind corner cabinet support
- TV unit support
- office cabinet / desk support
- delivery package
- commercial release step
- export step

## Exclusions

Not in this backlog:

- ERP
- MES
- inventory planning
- production scheduling system
- procurement automation
- multi-factory SaaS
- enterprise APIs
- customer portals
