# Decision Builder Rule

## 1. Purpose

Decision Builders are evidence aggregators, not validators.

Their job is to consume existing domain evidence and convert it into one stable decision object for downstream use.

## 2. Core Rule

Decision Builders must never generate new domain evidence.

They do not create new validation facts, new calculations, or new rule outcomes.
They only aggregate evidence that has already been produced elsewhere.

## 3. Allowed Responsibilities

Decision Builders may:

- consume existing reports
- consume existing validation summaries
- consume existing readiness reports
- normalize statuses
- aggregate blocking reasons
- aggregate warning reasons
- produce one decision object

## 4. Forbidden Responsibilities

Decision Builders must not:

- add new validation logic
- perform geometry reasoning
- perform manufacturing calculation
- perform cost calculation
- perform optimization logic
- recompute Engineering Decisions
- call Engineering capability rules directly

They are not validators, not calculators, and not engines.

## 5. Reference Implementation

The reference implementation for this rule is:

`MI-2 ManufacturingDecisionBuilder`

This builder proves the pattern:

- consume existing evidence
- normalize decision semantics
- produce one manufacturing decision

without introducing new validation or new runtime behavior.

## 6. Future Applicability

This rule should apply to future decision builders such as:

- `CostDecisionBuilder`
- `OptimizationDecisionBuilder`
- `CommercialDecisionBuilder`

## 7. Status Vocabulary Note

`PASS / WARNING / FAIL` currently remain plain strings.

A shared `DecisionStatus` enum is backlog only.
It is not implemented now.

## 8. Recommendation

Use this rule for all future decision builders.

If a component needs to create new evidence, it is not a Decision Builder and should live in the appropriate validation, intelligence, or domain layer instead.
