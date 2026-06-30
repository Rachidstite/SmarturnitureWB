# Manufacturing Decision Model

## 1. Purpose

Manufacturing Decisions are structured outputs of manufacturing validation and readiness logic.

They are not a new engine.
They are not a new workflow.

Their purpose is to convert manufacturing-specific evidence into a business decision that can be consumed consistently by downstream factory, cost, optimization, and commercial layers.

## 2. Platform Flow

The platform flow is:

`CabinetProject`
`-> EngineeringModel`
`-> Engineering Decisions`
`-> Manufacturing Runtime Package`
`-> Manufacturing Validation`
`-> Manufacturing Readiness`
`-> Manufacturing Decision`
`-> Cost Model`
`-> Optimization`
`-> Commercial Outputs`

This keeps engineering intelligence upstream and manufacturing intelligence downstream.

## 3. Manufacturing Decision Pipeline

The manufacturing decision pipeline is:

`Manufacturing Knowledge`
`-> Manufacturing Validation`
`-> Manufacturing Readiness`
`-> Manufacturing Decision`
`-> Manufacturing Report`

Meaning:

- `Manufacturing Knowledge`: manufacturing-specific rules, reports, package data, and validation sources
- `Manufacturing Validation`: rule-level checks and validation summaries
- `Manufacturing Readiness`: aggregated business readiness state for production
- `Manufacturing Decision`: the primary manufacturing output
- `Manufacturing Report`: the presentation artifact for downstream consumers

## 4. Ownership

### Engineering owns

- alignment
- collision
- accessibility
- reveal
- structural consistency

### Manufacturing owns

- material readiness
- hardware readiness
- operations readiness
- CNC readiness
- assembly readiness
- packaging/release readiness

## 5. Boundary Rules

- Manufacturing must not recompute Engineering Decisions.
- Manufacturing may consume Engineering Decision status as gates.
- Manufacturing decisions must be based on manufacturing-specific validation and readiness outputs.
- Reports are presentation artifacts; decisions are the primary outputs.

These rules preserve the MI-1 boundary:

`EngineeringModel -> Engineering Decisions -> Manufacturing Runtime Package -> Manufacturing Decisions`

## 6. Decision Contract

A manufacturing decision should expose:

- `status`: `PASS` / `WARNING` / `FAIL`
- `blocking_reasons`
- `warning_reasons`
- `recommended_action`
- `source`

This decision is the primary manufacturing business output.

## 7. Current Evidence

The repository already contains manufacturing readiness and validation families that support this decision model:

- panel material readiness
- panel thickness readiness
- hinge readiness
- minifix readiness
- confirmat readiness
- drawer slide readiness
- manufacturing validation summary
- project manufacturing readiness

These existing components show that the manufacturing layer already reasons in validation and readiness terms and does not require a new engine.

## 8. First Implementation Target

The first manufacturing decision implementation target should be:

`MI-2 Manufacturing Readiness Decision`

Its job is to aggregate manufacturing validation and readiness outputs into one primary production decision.

## 9. Non-goals

- no new engine
- no new workflow
- no replacement of existing manufacturing validators
- no recomputation of engineering logic
- no cost logic
- no optimization logic

This document defines the decision model only.
