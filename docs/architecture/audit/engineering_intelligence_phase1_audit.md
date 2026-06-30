# Engineering Intelligence Phase 1 Audit

## Scope

Reviewed capabilities:

- Front Alignment
- Static Door–Drawer Collision
- Front Accessibility Static Feasibility
- Reveal Validation
- Structural Consistency

This audit is read-only. No implementation files and no tests were modified.

## Strengths

- The five capabilities follow the same high-level architecture: `EngineeringModel -> Facts -> Rule -> Decision -> Report`.
- All five capabilities are model-driven and do not require a new engine or workflow.
- The capability boundaries are mostly coherent:
  - Relationship decisions are separated from integrity decisions.
  - Static decisions are separated from motion-oriented concerns.
  - Structural plausibility is kept distinct from strength/load/sag validation.
- `ConstraintViolation` is used consistently as the shared structured diagnostic primitive.
- The capability reports are uniformly data-first and suitable for downstream presentation.
- Dependency purity is strong in the capability layer:
  - no `GeometryEngine`
  - no `SceneGraph`
  - no `Manufacturing`
  - no `Cost`
- Test coverage is directionally good:
  - each capability has fact/rule/report coverage
  - tests assert banned dependencies are absent
  - tests verify PASS/WARNING/FAIL behavior for the relevant static cases

## Weaknesses

- Fact extraction is repeated across capabilities with similar adapter code for doors and drawer faces.
- Bounds computation is repeated in several rule modules:
  - front alignment computes edges
  - static collision computes axis-aligned bounds
  - front accessibility computes overlap boxes
  - reveal validation computes reveal gaps
  - structural consistency computes enclosure checks
- Decision schemas are not normalized:
  - `aligned_component_count`
  - `checked_pair_count`
  - `checked_component_count`
  - `checked_gap_count`
  - these all mean “work done” but are not structurally consistent
- Report schemas are close but not identical:
  - some include `tolerance_mm`
  - some include `target_reveal_mm`
  - structural consistency does not need tolerance in the same way
- `Front Alignment` still contains a `__GLOBAL__` fallback for missing `section_id`, while later capabilities skip unscoped facts. That is a small boundary inconsistency.
- Static checks are conservative by design, but that means some results are heuristic rather than exhaustive.

## Technical Debt

- Repeated axis-aligned geometry math across four capabilities.
- Repeated extraction patterns for `door`, `drawer_face`, `drawer_box`, `shelf`, and `divider`.
- Slightly divergent terminology in decision counters and report fields.
- Inconsistent treatment of unscoped facts:
  - later capabilities generally skip empty `section_id`
  - front alignment still groups them under a synthetic key
- Structural Consistency currently derives cabinet bounds from existing construction/specification data rather than reading a dedicated bounds object.
- Some current checks are deliberately conservative and may need future tuning when product-family policy becomes explicit.

## Duplicate Logic

The following logic is duplicated across capabilities:

- Door fact extraction
- Drawer-face fact extraction
- Section grouping by `section_id`
- Axis-aligned overlap checks
- Boundary/enclosure checks
- PASS/WARNING/FAIL aggregation
- `ConstraintViolation` creation patterns

This duplication is acceptable for Phase 1 because each capability is still small and domain-specific, but it is already becoming the main source of technical debt.

## Refactoring Recommendations

Phase 2 only. Do not apply these changes now.

- Introduce shared geometric helper functions for:
  - edge computation
  - overlap computation
  - enclosure checks
- Introduce a shared fact extraction helper for door and drawer-face projections.
- Standardize decision field naming where possible:
  - use a common “checked item count” concept across capabilities
  - keep capability-specific names only when the unit of work is materially different
- Normalize report shapes where the fields are conceptually shared.
- Decide whether `Front Alignment` should continue using `__GLOBAL__` or should align with the later skip-unscoped-facts behavior.
- If more tolerance-based capabilities are added, revisit whether local default tolerances should be centralized.
- If more capability categories are added, introduce a shared documentation table for category-to-capability mapping.

## Capability Boundary Review

### Front Alignment

- Boundary is clear: edge alignment of front components.
- Risk: synthetic grouping of missing `section_id` facts is a weak spot and could cause drift.

### Static Door–Drawer Collision

- Boundary is clear: direct physical overlap between door and drawer-face geometry.
- Good separation from accessibility and reveal validation.

### Front Accessibility Static Feasibility

- Boundary is mostly clear: static access plausibility and obvious front-zone blockers.
- It remains distinct from collision because it reasons about practical blockage, not only overlap.

### Reveal Validation

- Boundary is clear: visible gap/reveal quality.
- It is distinct from alignment because it checks spacing, not alignment.

### Structural Consistency

- Boundary is conceptually clear: structural plausibility only.
- It is not strength, load, sag, CNC, or manufacturing validation.
- The main risk is future scope creep if “integrity” starts absorbing manufacturing readiness semantics.

## Decision Consistency

- All five capabilities use a simple tri-state status model:
  - PASS
  - WARNING
  - FAIL
- That is consistent and easy to consume.
- The metrics used to derive the decision differ by capability, which is expected, but the vocabulary is not standardized.

## Report Consistency

- The report pattern is consistent across the capability family:
  - `facts`
  - `decision`
  - `violations`
  - source metadata
- Capability-specific extras are reasonable:
  - `tolerance_mm`
  - `target_reveal_mm`
- Reports remain presentation artifacts rather than decision engines.

## ConstraintViolation Usage

- `ConstraintViolation` is used consistently across the five capabilities.
- The shared structure is beneficial:
  - code
  - message
  - severity
  - node_id
  - current_value
  - required_value
  - suggestion
- The message style is not fully normalized, but the data shape is stable enough for Phase 1.

## Dependency Purity

- The capability layer is cleanly isolated from geometry, manufacturing, cost, and UI dependencies.
- Tests explicitly guard against unwanted imports in multiple capability modules.
- Structural Consistency remains model-only and does not require engine or workflow changes.

## EngineeringModel-Only Compliance

- All five capabilities consume `EngineeringModel` as the source of truth.
- Fact extraction uses data already present in the engineering model:
  - doors
  - drawer faces
  - drawer boxes
  - shelves
  - dividers
  - carcass panels
- No capability requires a new runtime source or a dynamic simulation layer.

## Test Coverage Consistency

- Coverage is good at the capability level:
  - fact extraction tests exist
  - rule behavior tests exist
  - report shape tests exist
  - banned dependency checks exist
- Coverage is weaker at the cross-capability contract level:
  - no shared contract tests enforce consistent decision/report field conventions
  - no shared helper tests enforce identical geometric semantics
  - no shared regression suite checks boundary overlap between capabilities

## Readiness Assessment

Phase 1 is functionally ready.

The architecture is stable enough to support additional static engineering capabilities without introducing a new engine or workflow. The main issue is technical debt from repeated fact extraction and repeated geometric helper logic, not architectural failure.

## Final Classification

**APPROVED WITH TECHNICAL DEBT**

The capability family is ready for Phase 1 use, but the duplicated extraction and geometry logic should be addressed in Phase 2 only, after more capabilities exist and the shared patterns are clearer.
