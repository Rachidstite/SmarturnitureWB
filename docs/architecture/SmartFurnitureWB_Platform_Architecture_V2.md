# SmartFurnitureWB Platform Architecture V2

## 1. Platform Vision

SmartFurnitureWB is a furniture engineering, manufacturing, costing, optimization, commercial, and future factory execution platform.

It exists to connect product definition with manufacturing knowledge, commercial readiness, and eventual execution in a way that keeps the product model coherent across the full lifecycle.

## 2. Core Business Goal

The platform is designed to:

- design faster
- manufacture faster
- reduce mistakes
- reduce waste
- reduce cost
- generate outputs automatically
- increase profitability

## 3. Platform Domains

### Engineering Domain

Defines the product intent, structure, geometry, and engineering rules for furniture design.

### Manufacturing Domain

Transforms the engineering model into manufacturing-oriented representations, validation summaries, and manufacturing knowledge.

### Manufacturing Knowledge Layer

Provides the declarative vocabulary, semantics, requirements, instances, links, dependency graphs, and logical execution planning needed to represent manufacturing knowledge without execution.

### Cost Intelligence Domain

Evaluates cost-related impact, cost risk, and pricing implications from product and manufacturing inputs.

### Optimization Domain

Improves manufacturability, waste reduction, and decision quality by analyzing and refining derived platform outputs.

### Commercial Domain

Converts engineering and manufacturing readiness into commercial decision support, release readiness, and customer-facing outputs.

### Production Release Domain

Controls the formal approval boundary between commercial readiness and factory execution.

### Factory Execution Domain

Represents the future execution-side domain for factory operations, runtime control, and execution-side coordination.

### Production Intelligence Domain

Consumes feedback from manufacturing and execution outcomes to improve rules, recommendations, and decision quality.

### SaaS Domain future

Represents the later platform direction for multi-user, service-oriented, and productized deployment capabilities.

## 4. Canonical Flow

Customer Intent  
↓  
FurnitureProject  
↓  
Engineering Model  
↓  
Manufacturing Model  
↓  
Manufacturing Knowledge Layer  
↓  
Cost Intelligence  
↓  
Optimization  
↓  
Commercial Decision  
↓  
Production Release  
↓  
Factory Execution  
↓  
Production Feedback  
↓  
Knowledge Improvement

## 5. Domain Responsibilities

### Engineering Domain
- Responsibility: Define the product and its engineering intent
- Input: Customer intent, design constraints, product requirements
- Output: Engineering model
- Forbidden responsibilities: Factory runtime, execution control, queue logic, machine control

### Manufacturing Domain
- Responsibility: Convert engineering knowledge into manufacturing-oriented representations and validation outputs
- Input: Engineering model
- Output: Manufacturing model and validation artifacts
- Forbidden responsibilities: Factory runtime, job scheduling, worker assignment, machine assignment

### Manufacturing Knowledge Layer
- Responsibility: Represent manufacturing knowledge declaratively
- Input: Manufacturing model and validation context
- Output: Vocabulary, semantics, requirements, instances, links, graphs, and logical plans
- Forbidden responsibilities: Scheduling, runtime execution, machine assignment, job creation

### Cost Intelligence Domain
- Responsibility: Evaluate cost impact, cost signals, and pricing implications
- Input: Engineering and manufacturing outputs
- Output: Cost intelligence and commercial cost context
- Forbidden responsibilities: Geometry modification, runtime execution, release control

### Optimization Domain
- Responsibility: Improve decision quality, waste reduction, and manufacturability recommendations
- Input: Engineering, manufacturing, and cost intelligence
- Output: Optimization guidance and improved decision support
- Forbidden responsibilities: Direct factory execution, job assignment, commercial approval

### Commercial Domain
- Responsibility: Convert readiness into commercial decision support and customer-facing outcomes
- Input: Manufacturing validation, cost intelligence, optimization context
- Output: Commercial approval or commercial decision artifacts
- Forbidden responsibilities: Factory runtime control, machine assignment, execution scheduling

### Production Release Domain
- Responsibility: Gate the transition from commercial approval to factory execution
- Input: Engineering validation, manufacturing validation, cost, optimization, commercial approval
- Output: Release authorization
- Forbidden responsibilities: Execution control, geometry changes, runtime coordination

### Factory Execution Domain
- Responsibility: Execute approved production work in the factory
- Input: Released production intent and execution context
- Output: Factory execution outcomes
- Forbidden responsibilities: Product knowledge mutation, engineering changes, commercial approval

### Production Intelligence Domain
- Responsibility: Learn from production feedback and improve rules through controlled review
- Input: Production feedback, manufacturing outcomes, execution outcomes
- Output: Improved rules, recommendations, and insights
- Forbidden responsibilities: Unreviewed product mutation, direct execution control

### SaaS Domain future
- Responsibility: Support future hosted, scalable, and service-oriented product delivery
- Input: Platform capabilities and product strategy
- Output: SaaS-ready platform capabilities
- Forbidden responsibilities: Replacing domain boundaries, collapsing knowledge and execution layers

## 6. Boundary Rules

- Engineering must not know factory runtime
- Manufacturing Knowledge must not schedule
- Cost must not modify product geometry
- Commercial approval must precede production release
- Factory execution must not modify product knowledge
- Production feedback improves rules through controlled review only

## 7. Production Release Rule

Factory execution starts only after:

- engineering validation passed
- manufacturing validation passed
- cost calculated
- optimization reviewed
- commercial approval completed

## 8. Current Completion Status

- Engineering Foundation: completed
- Manufacturing Knowledge Layer: completed
- Cost Intelligence: active/existing
- Optimization: active/future expansion
- Commercial Product Readiness: next major priority
- Production Release: future
- Factory Execution: future
- SaaS: later

## 9. Architecture Decision

SmartFurnitureWB Platform Architecture V2 is the strategic reference for future development.

It defines the domain boundaries, flow, and release rules that should guide future platform work without collapsing knowledge, commercial, and execution responsibilities into a single layer.
