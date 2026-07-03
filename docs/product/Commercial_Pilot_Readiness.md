# Commercial Pilot Readiness

## 1. Purpose

This document defines the minimum product scope required before the first paying furniture manufacturer can use SmartFurnitureWB on real cabinet projects.

It is a product-planning document, not an implementation plan.

## 2. Commercial Pilot Scope

Commercial Pilot means the platform can support a real cabinet project from configuration to release-ready commercial output:

- define a cabinet family and project configuration
- generate engineering geometry for the project
- generate manufacturable panels, doors, drawers, shelves, and joinery evidence
- produce cut list, CNC, machining, hardware, edge banding, and assembly documentation
- produce quotation, profitability, and commercial warning outputs
- produce production-backed visualization that matches manufacturing evidence
- allow a user to review the project before release

## 3. What Is Included

Included in Phase 1:

- base cabinet complete workflow
- wall cabinet complete workflow
- tall cabinet complete workflow
- wardrobe complete workflow
- cabinet-level assembly output
- production documentation
- commercial quotation package
- profitability summary
- production visualization for release review
- project review and warning review steps

Included later in Commercial Pilot only if they strengthen the cabinet workflow:

- corner cabinet support
- blind corner cabinet support
- TV unit support
- office cabinet / desk support

## 4. What Is Excluded

Excluded from Commercial Pilot:

- ERP integration
- MES integration
- inventory planning
- multi-factory SaaS
- enterprise customer management
- shop-floor dispatch orchestration
- procurement automation
- production scheduling system replacement
- broad generic CAD replacement
- AI or agent features without measured factory value

These belong after pilot validation.

## 5. Success Criteria

Commercial Pilot is successful when:

- a real cabinet project can be configured and reviewed by a paying manufacturer
- engineering outputs are consistent and repeatable
- manufacturing outputs are complete enough for workshop use
- quotation outputs are generated without manual rework
- production visualization matches manufacturing evidence
- warnings are understandable and actionable
- the workflow can be completed on representative cabinet projects without critical blockers

## 6. Risks

Primary risks:

- missing cabinet family coverage
- incomplete production documentation
- incomplete release-ready assembly guidance
- insufficient confidence in quotation/profitability outputs
- insufficient coverage of production-backed visualization
- workflow friction during project review and export

Secondary risks:

- overextending the platform into ERP/MES concerns too early
- introducing duplicate engines or workflows
- weakening backward compatibility while narrowing legacy bridges

## 7. Readiness KPIs

Commercial Pilot readiness should be measured by the KPI contract in `Commercial_Pilot_KPIs.md`.

The key gating idea is simple:

- the product must support real cabinet projects end to end
- the outputs must be complete enough for workshop use
- the user must be able to trust the release package without manual reconstruction

