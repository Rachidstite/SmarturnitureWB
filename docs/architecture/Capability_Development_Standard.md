# Capability Development Standard

## Purpose

This standard defines the mandatory development lifecycle for every capability in SmartFurnitureWB.

Capabilities must be introduced in a controlled sequence so the repository avoids duplicate engines, duplicate workflows, duplicate builders, and premature runtime integration.

The standard is documentation-only and applies to all current and future capabilities.

## Mandatory Lifecycle

### Phase 1: Knowledge Model

**Purpose**

Establish the domain knowledge that the capability must represent before any implementation begins.

**Required Inputs**

- engineering knowledge
- manufacturing knowledge
- commercial knowledge
- terminology
- assumptions
- failure modes

**Produced Outputs**

- architecture notes
- concept definitions
- rule candidates
- scope boundaries
- reusable domain language

**Dependencies**

- product architecture evidence
- existing domain boundaries
- approved platform terminology

**Forbidden Changes**

- no runtime logic
- no builders
- no workflow changes
- no validation algorithms
- no duplicate domain models

**Completion Criteria**

- the capability scope is clear
- the capability vocabulary is grounded in repository evidence
- the capability boundary is explicitly separated from runtime behavior

### Phase 2: Vocabulary

**Purpose**

Create stable terminology that can be used consistently by all future contracts.

**Required Inputs**

- knowledge model
- approved domain terms
- reusable naming patterns

**Produced Outputs**

- enums
- value objects
- stable terminology

**Dependencies**

- approved knowledge model
- existing naming conventions
- documented boundary rules

**Forbidden Changes**

- no validation logic
- no manufacturing logic
- no cost logic
- no commercial logic
- no workflow logic

**Completion Criteria**

- the vocabulary is data-only
- the vocabulary is serializable
- the vocabulary is independent of runtime concerns

### Phase 3: Capability Contracts

**Purpose**

Define the data contracts that represent the capability before any integration work begins.

**Required Inputs**

- vocabulary
- knowledge model
- product boundary assumptions

**Produced Outputs**

- specification
- validation contract
- result contract

**Dependencies**

- stable vocabulary
- data-only modeling rules
- frozen dataclass conventions where appropriate

**Forbidden Changes**

- no algorithms
- no workflow logic
- no builder creation
- no engine creation
- no duplicate base product modeling

**Completion Criteria**

- the capability can be represented without runtime behavior
- the contracts are immutable where appropriate
- the contracts can be serialized and compared predictably

### Phase 4: Rule Contracts

**Purpose**

Capture rule-level concerns as data before any validation integration is added.

**Required Inputs**

- capability contracts
- failure modes
- assumptions
- engineering constraints

**Produced Outputs**

- rule contracts
- severity
- diagnostics vocabulary

**Dependencies**

- capability contracts
- vocabulary
- documented failure modes

**Forbidden Changes**

- no rule engines
- no validation algorithms
- no runtime execution
- no manufacturing calculations
- no cost calculations

**Completion Criteria**

- every rule is declarative
- every rule can be referenced by validation without implementing behavior
- diagnostics remain a vocabulary, not an engine

### Phase 5: Validation Integration

**Purpose**

Attach the capability to the existing validation architecture without duplicating validation engines.

**Required Inputs**

- capability contracts
- rule contracts
- existing validation path

**Produced Outputs**

- extended validation coverage
- validation translation outputs
- diagnostics and warnings

**Dependencies**

- existing validation stack
- validation translation layer
- approved boundary between engineering and manufacturing validation

**Forbidden Changes**

- no duplicate validation engines
- no duplicate validation pipelines
- no direct bypass of existing validation flow
- no runtime redesign

**Completion Criteria**

- validation can consume the capability through approved bridges
- existing validation remains the source of execution
- the capability does not own validation runtime behavior

### Phase 6: Manufacturing Integration

**Purpose**

Connect the capability to the existing manufacturing builders and manufacturing pipeline.

**Required Inputs**

- validated capability
- engineering output
- manufacturing knowledge

**Produced Outputs**

- manufacturing-relevant capability outputs
- manufacturing translations
- manufacturing warnings or summaries

**Dependencies**

- existing manufacturing builders
- existing manufacturing runtime pipeline
- scene graph boundary

**Forbidden Changes**

- no duplicate manufacturing pipeline
- no new manufacturing engine
- no bypass of the scene graph boundary
- no direct manufacturing ownership in the capability layer

**Completion Criteria**

- manufacturing consumes the capability through reuse
- no existing builder is duplicated
- manufacturing remains downstream of engineering

### Phase 7: Cost Integration

**Purpose**

Reuse the existing cost pipeline to translate manufacturing outputs into cost intelligence.

**Required Inputs**

- manufacturing outputs
- product-level cost context

**Produced Outputs**

- cost summaries
- cost reports
- cost bridge artifacts

**Dependencies**

- existing cost pipeline
- existing manufacturing outputs
- approved translation boundaries

**Forbidden Changes**

- no duplicate cost engine
- no duplicate cost builder
- no recalculation inside the commercial bridge if cost is already computed

**Completion Criteria**

- the capability can reach cost without introducing a second cost path
- cost remains a downstream reuse of manufacturing outputs

### Phase 8: Commercial Integration

**Purpose**

Reuse the quotation pipeline and commercial pipeline to produce customer-facing artifacts.

**Required Inputs**

- cost outputs
- quotation metadata contract when required
- commercial-ready product context

**Produced Outputs**

- quotation documents
- commercial reports
- commercial summaries

**Dependencies**

- existing commercial pipeline
- existing quotation pipeline
- official metadata contract

**Forbidden Changes**

- no duplicate quotation logic
- no duplicate commercial pipeline
- no inference of commercial metadata from unrelated runtime artifacts

**Completion Criteria**

- commercial outputs reuse existing components
- quotation data comes from an official contract
- no new commercial engine is introduced

### Phase 9: Product Integration

**Purpose**

Attach the capability to the product workflow as a thin, additive layer.

**Required Inputs**

- capability contracts
- validation outputs
- manufacturing outputs
- cost outputs
- commercial outputs

**Produced Outputs**

- product result
- capability-aware orchestration
- final product-level artifact aggregation

**Dependencies**

- product workflow architecture
- existing product result contract
- approved bridge order

**Forbidden Changes**

- no duplicate workflows
- no new product engine
- no bypass of product workflow stages
- no ownership overlap with engineering, validation, manufacturing, cost, or commercial layers

**Completion Criteria**

- the capability is reachable through the product workflow
- orchestration remains thin
- the capability does not create a separate product pipeline

## Capability Readiness Levels (CRL)

Capability Readiness Levels define the minimum maturity required before a capability can advance to the next phase.

### CRL-0: Knowledge

The capability has a documented knowledge model.

**To advance to CRL-1**

- terminology must be stable
- scope must be clear
- assumptions and failure modes must be documented

### CRL-1: Vocabulary

The capability has enums and value objects for stable terminology.

**To advance to CRL-2**

- vocabulary must be data-only
- vocabulary must be serializable
- vocabulary must not depend on runtime behavior

### CRL-2: Contracts

The capability has specification, validation, and result contracts.

**To advance to CRL-3**

- contracts must be immutable where appropriate
- contracts must be isolated from runtime logic
- rule candidates must be represented explicitly

### CRL-3: Rules

The capability has declarative rule contracts and diagnostics vocabulary.

**To advance to CRL-4**

- rules must be data-only
- no validation algorithm may exist yet
- the existing validation path must be identified for reuse

### CRL-4: Validation

The capability is connected to the existing validation architecture through approved translation.

**To advance to CRL-5**

- validation must reuse existing validation infrastructure
- no duplicate validation engine may be introduced
- the capability must remain additive

### CRL-5: Manufacturing

The capability is connected to the existing manufacturing builders and runtime pipeline.

**To advance to CRL-6**

- manufacturing must reuse existing builders
- no duplicate manufacturing pipeline may exist
- the scene graph boundary must remain intact

### CRL-6: Cost

The capability is connected to the existing cost pipeline.

**To advance to CRL-7**

- cost must reuse the existing cost pipeline
- no duplicate cost engine may be introduced
- cost must not be recomputed in commercial logic

### CRL-7: Commercial

The capability is connected to the existing quotation and commercial pipelines.

**To advance to CRL-8**

- quotation metadata must come from an official contract
- commercial outputs must reuse existing pipelines
- no duplicate commercial workflow may be introduced

### CRL-8: Product Integration

The capability is attached to the product workflow as a thin orchestration layer.

**To maintain CRL-8**

- the capability must remain additive
- no duplicate workflow may appear
- product workflow responsibilities must not be absorbed by the capability itself

## Standard Summary

The approved development order for every new capability is:

1. Knowledge Model
2. Vocabulary
3. Capability Contracts
4. Rule Contracts
5. Validation Integration
6. Manufacturing Integration
7. Cost Integration
8. Commercial Integration
9. Product Integration

This sequence is mandatory because it preserves architecture boundaries, prevents duplicate engines and workflows, and keeps future capabilities reusable across product families.
