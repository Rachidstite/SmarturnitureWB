# Engineering Decision Model

## 1. Purpose

Engineering Decisions are outputs of capabilities built on `EngineeringModel`.
They are not a new architectural layer, not a new engine, and not a new workflow.
Their role is to classify static engineering intelligence into bounded capability outputs that can be compared, reported, and consumed consistently.

## 2. Core Rule

`EngineeringModel` remains the input source for Engineering Intelligence Phase 1.

All Phase 1 engineering capabilities must derive their facts from the engineering model and return a decision through the approved capability template:

`Input Model -> Facts -> Rule -> Decision -> Report`

## 3. Decision Categories

### A. Relationship Decisions

Relationship decisions describe how front-facing or adjacent elements relate to each other in the static model.

- Front Alignment
- Static Door–Drawer Collision
- Front Accessibility Static Feasibility
- Reveal Validation

### B. Integrity Decisions

Integrity decisions describe whether the modeled cabinet structure is internally plausible and consistent.

- Structural Consistency
- Section Consistency
- Cabinet Integrity
- Project Integrity

### C. Behaviour Decisions

Behaviour decisions describe whether a modeled element can behave correctly in motion or dynamic use.

- Opening Envelope
- Motion Validation
- Drawer Extension
- Door Swing

### D. Manufacturing Decisions

Manufacturing decisions describe whether the model is ready for downstream production and shop-floor translation.

- CNC Readiness
- Hardware Readiness
- Assembly Readiness

## 4. Capability Template

The standard capability template is:

`Input Model -> Facts -> Rule -> Decision -> Report`

Meaning:

- `Input Model`: the source engineering representation
- `Facts`: normalized, capability-specific data extracted from the model
- `Rule`: the evaluation logic that inspects facts
- `Decision`: the primary capability output summary
- `Report`: the presentation artifact that packages facts, decision, and violations

## 5. Current Status Table

| Capability | Status |
| --- | --- |
| EDC-1 Front Alignment | Implemented |
| EDC-2 Static Door–Drawer Collision | Implemented |
| EDC-3 Front Accessibility Static Feasibility | Implemented |
| EDC-4 Reveal Validation | Implemented |
| EDC-5 Structural Consistency | Architecture Approved / Planned |

## 6. Non-Negotiable Boundaries

The following boundaries apply to Engineering Decision capabilities in Phase 1:

- No new engine
- No new workflow
- No `GeometryEngine` dependency for EngineeringModel-ready capabilities
- No `SceneGraph` dependency
- No `Manufacturing` dependency inside Engineering capabilities
- No `Cost` dependency inside Engineering capabilities
- No motion simulation inside static decisions

These boundaries exist to keep Phase 1 capabilities small, deterministic, and grounded in static engineering data.

## 7. Purpose of EDC-5

EDC-5, Structural Consistency, belongs to the Integrity Decision category.

It is not a Relationship Decision.
It is not strength validation.
It is not load validation.
It is not shelf sag validation.

Its purpose is to detect obvious structural plausibility problems from `EngineeringModel` only, such as invalid dimensions, missing core components, or components placed outside plausible cabinet bounds.

## 8. Recommendation

Proceed with EDC-5 Structural Consistency implementation after this document is adopted.
Keep the implementation small, static, and model-only so future capabilities do not overlap or drift.
