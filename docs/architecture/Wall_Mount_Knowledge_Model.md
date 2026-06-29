# Wall Mount Knowledge Model

## Scope

This document defines the official wall-mount knowledge model for SmartFurnitureWB.

It is documentation and domain modelling only.

It does not define runtime behavior, builders, validation algorithms, UI behavior, or rendering.

The model is intentionally declarative so future wall-mounted cabinet work can reuse the existing product pipeline without duplicating Base Cabinet logic.

## Architectural Grounding

This knowledge model is aligned with the existing architecture boundary rules:

- engineering facts may be structural or installation-oriented
- manufacturing must remain downstream of engineering
- validation may consume engineering facts, but must not own geometry
- wall-specific concerns belong in reusable contracts, not in duplicate engines
- project spatial conventions remain separate from cabinet-local geometry

Relevant reusable evidence already exists in the repository:

- `docs/architecture/ADR-005-engineering-facts-taxonomy.md`
- `docs/architecture/ADR-004-project-engineering-capability-architecture.md`
- `docs/architecture/SceneGraph_Engineering_Manufacturing_Boundary.md`
- `manufacturing/cabinet_structural_builder.py`
- `manufacturing/cabinet_stability_builder.py`
- `manufacturing/back_panel_validation_builder.py`
- `manufacturing/cabinet_manufacturing_knowledge_report.py`
- `domain/wall_mount_capability.py`

## 1. Mounting Strategies

### 1.1 Concealed suspension rail
- **Business Reason**: Supports clean visible design for wall cabinets and simplifies leveling.
- **Engineering Reason**: Transfers load through a continuous rail and spreads forces across multiple fixings.
- **Manufacturing Impact**: Requires rail-compatible back structure, hole pattern consistency, and kit selection.
- **Validation Target**: Mounting support, rail compatibility, load distribution, and installation clearance.
- **Future Capability Dependencies**: Wall mount capability, suspension hardware family catalog, wall load validation.

### 1.2 Point-fixed bracket mounting
- **Business Reason**: Useful for compact cabinets and lower-cost configurations.
- **Engineering Reason**: Concentrates load into discrete anchors and requires strong local reinforcement.
- **Manufacturing Impact**: Requires defined bracket positions, reinforcement zones, and accurate hole placement.
- **Validation Target**: Anchor spacing, local load limit, and bracket clearance.
- **Future Capability Dependencies**: Mounting validation bridge, structural report, anchor rule contract.

### 1.3 French cleat style mounting
- **Business Reason**: Supports easier installation and repeatable hanging alignment.
- **Engineering Reason**: Provides a self-locating load path with a broad contact interface.
- **Manufacturing Impact**: Requires mating cleat geometry and dedicated machining or attachment steps.
- **Validation Target**: Cleat engagement, wall compatibility, and anti-lift retention.
- **Future Capability Dependencies**: Suspension hardware family registry, installation sequence contract.

### 1.4 Hybrid rail-plus-safety-retention mounting
- **Business Reason**: Improves safety for larger wall cabinets.
- **Engineering Reason**: Combines primary load support with secondary retention against lift-off or slip.
- **Manufacturing Impact**: Requires both primary and secondary hardware definitions.
- **Validation Target**: Redundancy, retention engagement, and installation completeness.
- **Future Capability Dependencies**: Safety rules, suspension hardware families, product workflow bridge.

## 2. Wall Types

### 2.1 Concrete wall
- **Business Reason**: Common high-strength support surface for heavy wall cabinets.
- **Engineering Reason**: Provides strong substrate for anchors and high load capacity when fixings are correct.
- **Manufacturing Impact**: Drives anchor kit selection and installation instructions, not cabinet geometry changes.
- **Validation Target**: Wall compatibility, anchor suitability, and maximum supported load.
- **Future Capability Dependencies**: Wall type contract, anchor rules, installation clearance checks.

### 2.2 Masonry wall
- **Business Reason**: Common durable mounting substrate.
- **Engineering Reason**: Can support high loads but requires appropriate anchor type and embedment strategy.
- **Manufacturing Impact**: Requires wall-specific fixings and possibly alternate drill/anchor instructions.
- **Validation Target**: Fixing method compatibility and load limit compliance.
- **Future Capability Dependencies**: Suspension hardware family, mounting validation.

### 2.3 Timber stud wall
- **Business Reason**: Common residential construction type.
- **Engineering Reason**: Load must transfer to studs or verified structural members.
- **Manufacturing Impact**: May require adjustable mounting points and stud-aligned hole patterns.
- **Validation Target**: Stud alignment, fastener compatibility, and clearance for access.
- **Future Capability Dependencies**: Wall load constraints, anchor rules, installation method contract.

### 2.4 Steel stud wall
- **Business Reason**: Common in commercial interiors.
- **Engineering Reason**: Requires fasteners and load assumptions specific to thin-gauge steel members.
- **Manufacturing Impact**: Hardware family and installation instructions may differ from timber walls.
- **Validation Target**: Member compatibility and pull-out / tear-out resistance.
- **Future Capability Dependencies**: Suspension hardware families, failure modes, safety rules.

### 2.5 Plasterboard over stud wall
- **Business Reason**: Common finish surface that often hides the true structure.
- **Engineering Reason**: Finish board alone is insufficient for load transfer; structural members must carry the load.
- **Manufacturing Impact**: Requires installation guidance to locate and use the structural member.
- **Validation Target**: Structural member presence and load transfer path.
- **Future Capability Dependencies**: Installation considerations, wall load constraints.

### 2.6 Hollow masonry / block wall
- **Business Reason**: Common building substrate that may support specialized anchors.
- **Engineering Reason**: Load capacity depends on block type and anchor system.
- **Manufacturing Impact**: Must support alternate anchor families and installation warnings.
- **Validation Target**: Anchor selection and load limit verification.
- **Future Capability Dependencies**: Anchor rules, safety rules, wall type catalog.

## 3. Suspension Hardware Families

### 3.1 Wall rail family
- **Business Reason**: Provides a standardized productized wall support system.
- **Engineering Reason**: Spreads load and improves leveling and installation repeatability.
- **Manufacturing Impact**: Requires rail length, rail holes, and compatible hanger interfaces.
- **Validation Target**: Rail compatibility and load rating.
- **Future Capability Dependencies**: Wall mount capability, manufacturing outputs, commercial packaging.

### 3.2 Adjustable hanger family
- **Business Reason**: Enables fine adjustment after installation.
- **Engineering Reason**: Supports leveling correction and cabinet-to-wall tolerance management.
- **Manufacturing Impact**: Requires hanger mounting points and access zones.
- **Validation Target**: Adjustment range and clearance.
- **Future Capability Dependencies**: Installation clearance, product workflow bridge.

### 3.3 Concealed bracket family
- **Business Reason**: Supports hidden mounting where the visual front must remain clean.
- **Engineering Reason**: Loads are carried through hidden structural interfaces and need reinforcement.
- **Manufacturing Impact**: Requires bracket pockets, insert points, or reinforced back structure.
- **Validation Target**: Bracket engagement, structural support, and anti-drop retention.
- **Future Capability Dependencies**: Structural report, stability report, failure mode checks.

### 3.4 Cleat family
- **Business Reason**: Useful for installable, repeatable hanging systems.
- **Engineering Reason**: Self-locating support path with strong shear transfer.
- **Manufacturing Impact**: Requires matching cabinet-side and wall-side geometry.
- **Validation Target**: Cleat engagement and retention against lift-off.
- **Future Capability Dependencies**: Suspension hardware catalog, safety rules.

### 3.5 Anti-lift / retention hardware family
- **Business Reason**: Prevents accidental disengagement after hanging.
- **Engineering Reason**: Adds secondary retention against vertical lift or vibration.
- **Manufacturing Impact**: Adds hardware items and installation steps.
- **Validation Target**: Retention engagement and completeness.
- **Future Capability Dependencies**: Safety rules, installation method contract.

## 4. Load Constraints

### 4.1 Static distributed load
- **Business Reason**: Ensures the cabinet can safely hold contents over time.
- **Engineering Reason**: Base support load must remain within wall and suspension capacity.
- **Manufacturing Impact**: Influences hardware selection and reinforcement requirements.
- **Validation Target**: Load within limit.
- **Future Capability Dependencies**: Wall mount validation, stability report, manufacturing knowledge.

### 4.2 Cantilever moment load
- **Business Reason**: Accounts for load extending away from the wall face.
- **Engineering Reason**: Creates additional moment at the suspension interface and wall anchors.
- **Manufacturing Impact**: May require stronger hardware or deeper support geometry.
- **Validation Target**: Moment / lever-arm compatibility.
- **Future Capability Dependencies**: Structural report, anchor rules.

### 4.3 Door-open and access load
- **Business Reason**: Opening cabinet doors changes the effective load path and can stress mount points.
- **Engineering Reason**: Door motion and access forces can amplify wall interface loads.
- **Manufacturing Impact**: May require local reinforcement around mounting points.
- **Validation Target**: Mount integrity under operational load.
- **Future Capability Dependencies**: Opening system reuse, stability validation.

### 4.4 Shelf-content load transfer
- **Business Reason**: Shelf loads are part of the wall cabinet operating envelope.
- **Engineering Reason**: Shelf loads transfer into cabinet structure and then into wall fixings.
- **Manufacturing Impact**: May require additional internal reinforcement or hardware selection.
- **Validation Target**: Total supported load and load distribution.
- **Future Capability Dependencies**: Shelf system reuse, cabinet structural report.

### 4.5 Dynamic disturbance load
- **Business Reason**: Cabinets can be subject to bumps, vibration, or repeated use.
- **Engineering Reason**: Dynamic loading can loosen fixings and reduce retention over time.
- **Manufacturing Impact**: Influences retention hardware and fastener selection.
- **Validation Target**: Retention robustness and warning generation.
- **Future Capability Dependencies**: Safety rules, failure mode model.

## 5. Anchor Rules

### 5.1 Anchor must match wall type
- **Business Reason**: Prevents unsafe or invalid installation combinations.
- **Engineering Reason**: Different wall substrates require different anchor behaviors.
- **Manufacturing Impact**: Forces wall-specific hardware families and kit definitions.
- **Validation Target**: Mounting supported / not supported.
- **Future Capability Dependencies**: Wall type contract, suspension hardware family registry.

### 5.2 Structural member preference
- **Business Reason**: Improves safety and load capacity where wall construction permits.
- **Engineering Reason**: Direct load transfer into structural members is more reliable than finish surfaces.
- **Manufacturing Impact**: May alter bracket placement or installation instructions.
- **Validation Target**: Structural attachment path verified.
- **Future Capability Dependencies**: Installation considerations, clearance rules.

### 5.3 Minimum anchor spacing
- **Business Reason**: Prevents concentrated failure at a single fixation region.
- **Engineering Reason**: Load distribution improves pull-out and shear behavior.
- **Manufacturing Impact**: Drives mounting hole spacing and bracket layout.
- **Validation Target**: Anchor spacing acceptable.
- **Future Capability Dependencies**: Manufacturing knowledge, mounting validation.

### 5.4 Edge distance and embedment sufficiency
- **Business Reason**: Reduces wall damage and fastener failure.
- **Engineering Reason**: Proper embedment and edge distance are required for real load capacity.
- **Manufacturing Impact**: Constrains hole placement and hardware instructions.
- **Validation Target**: Anchor depth and edge clearance.
- **Future Capability Dependencies**: Wall load constraints, installation method contract.

### 5.5 Redundant retention where load risk is elevated
- **Business Reason**: Improves safety for larger or heavier cabinets.
- **Engineering Reason**: Secondary retention reduces catastrophic failure risk.
- **Manufacturing Impact**: Adds hardware and installation steps.
- **Validation Target**: Anti-lift / anti-drop retention present.
- **Future Capability Dependencies**: Safety rules, failure mode model.

## 6. Installation Clearances

### 6.1 Top installation clearance
- **Business Reason**: Allows mounting, hanging, and final adjustment.
- **Engineering Reason**: Clearance is needed for positioning and rail engagement.
- **Manufacturing Impact**: May affect cabinet height assumptions and packaging instructions.
- **Validation Target**: Required clearance available.
- **Future Capability Dependencies**: Wall mount validation, installation method contract.

### 6.2 Side installation clearance
- **Business Reason**: Prevents interference with adjacent cabinets or walls.
- **Engineering Reason**: Needed for access, alignment, and tolerances.
- **Manufacturing Impact**: May influence module width and side finish requirements.
- **Validation Target**: Clearance maintained at sides.
- **Future Capability Dependencies**: Product workflow, spatial facts.

### 6.3 Rear service clearance
- **Business Reason**: Allows mounting hardware and wall irregularity accommodation.
- **Engineering Reason**: The cabinet must not bind against the wall or concealment hardware.
- **Manufacturing Impact**: Can require recesses or spacer allowance.
- **Validation Target**: Wall interface clearance is sufficient.
- **Future Capability Dependencies**: Suspension hardware family, structural report.

### 6.4 Leveling and adjustment clearance
- **Business Reason**: Supports post-install alignment.
- **Engineering Reason**: Adjustability is necessary because walls are rarely perfectly plumb.
- **Manufacturing Impact**: Requires accessible adjustment zones.
- **Validation Target**: Adjustment access available.
- **Future Capability Dependencies**: Installation considerations, wall-specific result contract.

### 6.5 Door and opening clearance at installation state
- **Business Reason**: Ensures the cabinet remains usable immediately after installation.
- **Engineering Reason**: Doors and openable components must clear nearby surfaces.
- **Manufacturing Impact**: Might alter hinge or opening system assumptions.
- **Validation Target**: Opening path unobstructed.
- **Future Capability Dependencies**: Opening system reuse, product workflow bridge.

## 7. Failure Modes

### 7.1 Anchor pull-out
- **Business Reason**: Catastrophic failure mode that must be prevented.
- **Engineering Reason**: Insufficient wall fixation can detach the cabinet from the wall.
- **Manufacturing Impact**: Drives stronger hardware and explicit installation rules.
- **Validation Target**: Load and anchor compatibility.
- **Future Capability Dependencies**: Safety rules, wall load validation.

### 7.2 Anchor shear failure
- **Business Reason**: Prevents mount collapse under sustained or accidental lateral loads.
- **Engineering Reason**: Shear load can exceed fastener or substrate capacity.
- **Manufacturing Impact**: May require multiple anchors or rail distribution.
- **Validation Target**: Load distribution and anchor selection.
- **Future Capability Dependencies**: Mounting strategy, suspension hardware family.

### 7.3 Bracket or rail deformation
- **Business Reason**: Maintains alignment and long-term safety.
- **Engineering Reason**: Overloaded hardware can deform and lose support capacity.
- **Manufacturing Impact**: Affects material selection and hardware rating.
- **Validation Target**: Hardware load rating.
- **Future Capability Dependencies**: Suspension hardware catalog, load constraints.

### 7.4 Wall substrate crushing or cracking
- **Business Reason**: Prevents property damage and unsafe mounting.
- **Engineering Reason**: Some substrates cannot support high point loads without proper anchors.
- **Manufacturing Impact**: Requires wall-type-specific installation guidance.
- **Validation Target**: Wall type compatibility.
- **Future Capability Dependencies**: Anchor rules, safety rules.

### 7.5 Cabinet sagging or tilt after installation
- **Business Reason**: Affects usability and customer perception.
- **Engineering Reason**: Uneven load transfer or inadequate stiffness can produce visible tilt.
- **Manufacturing Impact**: Requires reinforcement or leveling support.
- **Validation Target**: Stability and clearance checks.
- **Future Capability Dependencies**: Cabinet stability reuse, installation clearance.

### 7.6 Anti-lift failure
- **Business Reason**: A hanging cabinet must not slip off the support system.
- **Engineering Reason**: Secondary retention must remain engaged.
- **Manufacturing Impact**: Drives retention hardware selection and inspection steps.
- **Validation Target**: Retention engagement.
- **Future Capability Dependencies**: Safety rules, installation method contract.

## 8. Manufacturing Considerations

### 8.1 Reinforced mounting zone
- **Business Reason**: Improves support for wall-mounted loads.
- **Engineering Reason**: Wall fixings need a structurally adequate load path.
- **Manufacturing Impact**: May require thicker back structure, inserts, or dedicated reinforcement.
- **Validation Target**: Structural adequacy at mounting points.
- **Future Capability Dependencies**: Cabinet structural builder reuse, wall capability result.

### 8.2 Hardware kit definition
- **Business Reason**: Simplifies assembly, ordering, and installation.
- **Engineering Reason**: Hardware must be matched to cabinet load and wall substrate.
- **Manufacturing Impact**: Requires kit selection and packaging content definition.
- **Validation Target**: Hardware family compatibility.
- **Future Capability Dependencies**: Commercial pipeline, manufacturing outputs.

### 8.3 Fastener hole pattern
- **Business Reason**: Ensures repeatable installation and manufacturing consistency.
- **Engineering Reason**: Mounting geometry must align with the chosen suspension family.
- **Manufacturing Impact**: Drives machining instructions and tolerances.
- **Validation Target**: Hole pattern suitability.
- **Future Capability Dependencies**: Mounting strategy, anchor rules.

### 8.4 Installation documentation / kit labeling
- **Business Reason**: Reduces installation errors.
- **Engineering Reason**: Wall-mount systems depend on correct installation sequence.
- **Manufacturing Impact**: Requires clear labels and part grouping.
- **Validation Target**: Installation method completeness.
- **Future Capability Dependencies**: Installation considerations, commercial outputs.

### 8.5 Factory packaging for wall hardware
- **Business Reason**: Ensures all installation-critical parts are present.
- **Engineering Reason**: Missing anchors or retention parts can invalidate the mount.
- **Manufacturing Impact**: Adds packaging checks and kit completeness validation.
- **Validation Target**: Kit completeness and hardware family match.
- **Future Capability Dependencies**: Manufacturing pipeline, commercial pipeline.

## 9. Installation Considerations

### 9.1 Wall condition verification
- **Business Reason**: Installation must be safe on the actual wall, not only on paper.
- **Engineering Reason**: Wall condition controls load transfer and anchor suitability.
- **Manufacturing Impact**: Needs clear instructions and suitability warnings.
- **Validation Target**: Wall type and support verification.
- **Future Capability Dependencies**: Wall type contract, safety rules.

### 9.2 Level reference setup
- **Business Reason**: Supports accurate cabinet alignment.
- **Engineering Reason**: Wall cabinets need a stable reference for mounting.
- **Manufacturing Impact**: May influence rail-based systems and adjustment hardware.
- **Validation Target**: Installation alignment achievable.
- **Future Capability Dependencies**: Installation clearance, suspension hardware family.

### 9.3 Temporary support during installation
- **Business Reason**: Reduces risk while positioning the cabinet.
- **Engineering Reason**: Wall units need safe handling before final fixation.
- **Manufacturing Impact**: May require helper procedures or installation sequence notes.
- **Validation Target**: Installation method supportability.
- **Future Capability Dependencies**: Installation method contract, product workflow.

### 9.4 Verification after hanging
- **Business Reason**: Confirms the cabinet is secure and usable.
- **Engineering Reason**: Post-install checks catch loosening, tilt, and incomplete retention.
- **Manufacturing Impact**: Can drive instruction cards and inspection points.
- **Validation Target**: Retention and clearance confirmed.
- **Future Capability Dependencies**: Validation bridge, commercial outputs.

### 9.5 Removal and service access
- **Business Reason**: Allows safe maintenance and future adjustment.
- **Engineering Reason**: A wall-mounted unit must remain serviceable without damaging the wall.
- **Manufacturing Impact**: Influences hardware access and adjustment points.
- **Validation Target**: Service access available.
- **Future Capability Dependencies**: Installation clearance, serviceability facts.

## 10. Safety Rules

### 10.1 Do not exceed rated wall load
- **Business Reason**: Prevents injury and property damage.
- **Engineering Reason**: Wall and hardware capacity is finite and must not be exceeded.
- **Manufacturing Impact**: Sets hardware selection and product load rating.
- **Validation Target**: Load within limit.
- **Future Capability Dependencies**: Wall load constraints, safety rules.

### 10.2 Use compatible anchors only
- **Business Reason**: Prevents unsafe or unstable installations.
- **Engineering Reason**: Anchor behavior depends on wall substrate and load type.
- **Manufacturing Impact**: Requires explicit hardware family matching.
- **Validation Target**: Mounting supported and anchor compatible.
- **Future Capability Dependencies**: Wall type contract, suspension hardware family.

### 10.3 Provide secondary retention for elevated risk cases
- **Business Reason**: Reduces severity of accidental disengagement.
- **Engineering Reason**: Redundancy improves fault tolerance in wall installations.
- **Manufacturing Impact**: Adds kit and assembly steps.
- **Validation Target**: Retention present.
- **Future Capability Dependencies**: Failure mode model, installation method contract.

### 10.4 Require adequate clearance for safe installation
- **Business Reason**: Prevents rushed or forced assembly.
- **Engineering Reason**: Clearance is needed for positioning, fastening, and adjustment.
- **Manufacturing Impact**: May require dimensional allowances or warnings.
- **Validation Target**: Clearance available.
- **Future Capability Dependencies**: Installation clearance, wall capability validation.

### 10.5 Require explicit installation method
- **Business Reason**: Reduces ambiguity and installer error.
- **Engineering Reason**: Different wall systems require different installation sequences.
- **Manufacturing Impact**: Requires documentation and part kit alignment.
- **Validation Target**: Installation method defined.
- **Future Capability Dependencies**: Product workflow, commercial outputs.

### 10.6 Do not mix load-bearing and decorative hardware
- **Business Reason**: Avoids unsafe assumptions about what actually carries the load.
- **Engineering Reason**: Decorative components must not be treated as structural support.
- **Manufacturing Impact**: Prevents incorrect kit composition.
- **Validation Target**: Structural support path verified.
- **Future Capability Dependencies**: Structural report, anchor rules.

## Summary

The wall-mount knowledge model is a declarative, reusable domain model that organizes the engineering knowledge required for wall-mounted cabinets without introducing runtime behavior or duplicate builders.

It is intended to support future wall cabinet work by reusing:

- existing structural knowledge
- existing stability knowledge
- existing validation translation paths
- existing manufacturing and cost pipelines
- existing product workflow patterns

It also preserves the architecture rule that wall-specific capability must remain additive and independent until a future implementation phase is approved.
