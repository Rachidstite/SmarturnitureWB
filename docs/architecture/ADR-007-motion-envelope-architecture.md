# ADR-007: Motion Envelope Architecture

## Status
Approved

## 1. Context

Project Engineering now includes DTO-only engineering facts and reusable evaluation patterns.

The repository has a new motion-oriented engineering fact:

- `MotionEnvelopeFact`

The architecture needs a clear definition of how motion-related spatial data fits into the overall engineering evaluation path without creating duplicate engines or moving geometry ownership out of Project Geometry.

## 2. Problem

Moving furniture components such as doors, drawers, sliding systems, and lift systems occupy more space while in motion than they do at rest.

Without an explicit architecture, this can lead to:

- motion being modeled as geometry ownership
- motion simulation being embedded into rules
- collision logic being duplicated inside motion extraction
- component-specific engines such as DoorEngine or DrawerEngine
- FreeCAD-specific motion logic inside `project_engineering`

This would weaken reuse and make it difficult to reason about operational clearances, accessibility, and serviceability.

## 3. Decision

`MotionEnvelopeFact` is approved as the derived spatial envelope occupied by a component during its possible motion.

It is:

- an engineering fact
- derived from geometry and motion input
- reusable across doors, drawers, sliding systems, lift systems, and future moving furniture components
- consumed by rules and decisions

It is not:

- a geometry owner
- a collision engine
- a motion simulator
- a time-step animation
- a FreeCAD renderer
- a manufacturing, cost, or commercial object

## 4. Definition of Motion Envelope

The motion envelope is the total spatial region that may be occupied by a component while it moves through its allowed motion.

It is distinct from the static occupied space of the component when it is at rest.

The motion envelope may be represented as a derived spatial range or bounding region with motion metadata such as motion type and direction.

## 5. Difference between Static Bounds and Motion Envelope

### Static Bounds

Static bounds describe the occupied space of a component at rest.

They are derived from the component's fixed pose and dimensions.

### Motion Envelope

Motion envelope describes the total space that may be occupied during movement.

It includes all spatial positions the component may traverse during motion.

### Distinction

Static bounds answer:

- "What space does this component occupy now?"

Motion envelope answers:

- "What space might this component occupy while operating?"

## 6. Ownership Rules

The following ownership rules are approved:

1. Project Geometry owns static geometry.
2. Motion extraction derives `MotionEnvelopeFact`.
3. Rules evaluate `MotionEnvelopeFact`.
4. Decisions aggregate rule results.
5. Motion facts do not own geometry.
6. Motion facts do not own collision behavior.
7. Motion facts do not own manufacturing data.
8. Motion facts do not own pricing data.
9. Motion facts do not own UI behavior.
10. Motion facts remain reusable across component families.

## 7. Dependency Rules

The following dependency rules are approved:

1. Motion rules must not read Project Geometry directly.
2. Motion facts must not calculate collision.
3. Motion extractors must not become motion engines.
4. No DoorEngine, DrawerEngine, SlidingDoorEngine, or LiftEngine is approved.
5. No FreeCAD dependency is allowed inside project_engineering motion intelligence.
6. Manufacturing, Cost, and Commercial remain downstream consumers.
7. Motion-envelope logic must stay DTO-first and rule-driven.

## 8. Non-Goals

This ADR explicitly does not:

- define a motion simulator
- define time-step animation
- define collision resolution algorithms
- define rendering logic
- define new motion engines
- define door-specific or drawer-specific implementations
- move static geometry ownership out of Project Geometry
- move manufacturing or cost behavior into Project Engineering

## 9. Consequences

The following consequences are approved:

- Motion envelope data can be reused across multiple moving furniture systems.
- Static bounds and motion envelope remain distinct concepts.
- Rules can evaluate motion-related space without owning geometry.
- Accessibility and serviceability logic can consume motion facts later.
- Motion intelligence can grow without creating duplicate engines.

## 10. Future Extensions

Future extensions may include:

- door swing envelope extraction
- drawer pull envelope extraction
- sliding door envelope extraction
- lift-system envelope extraction
- motion envelope collision rules
- accessibility and serviceability consumption of motion envelopes

Any future extension must preserve:

- static geometry ownership in Project Geometry
- motion extraction as derivation only
- rule evaluation as fact consumption only
- decision aggregation as a downstream step only
- the no-duplicate-engine rule
- the no-FreeCAD-in-project_engineering rule

