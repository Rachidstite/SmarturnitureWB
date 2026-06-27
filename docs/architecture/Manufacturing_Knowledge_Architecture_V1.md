# Manufacturing Knowledge Architecture V1

## Purpose

The Manufacturing Knowledge Layer exists to represent manufacturing knowledge in a declarative, product-centered form before any execution concerns appear.

It defines the vocabulary, semantics, requirements, instances, links, and logical structure needed to describe how a product should be understood from a manufacturing perspective.

This layer is intentionally non-executable. It preserves traceability from product intent to logical manufacturing representation without introducing runtime behavior, scheduling behavior, or factory control behavior.

## Core Principles

- Product is the source of truth
- Operation model is derived
- Knowledge before execution
- No duplicate engines
- No runtime concepts inside knowledge layer
- No machine, worker, queue, job, cost, CNC, or scheduling logic

## Architecture Flow

FurnitureProject  
↓  
Engineering Model  
↓  
Manufacturing Model  
↓  
Manufacturing Validation  
↓  
Operation Vocabulary  
↓  
Operation Semantics  
↓  
Operation Requirements  
↓  
Requirement Builder  
↓  
Operation Definitions  
↓  
Operation Instances  
↓  
Operation Links  
↓  
Dependency Graph  
↓  
Logical Execution Plan

## Layer Responsibility Matrix

### Manufacturing Validation
- Responsibility: Confirm the product model is manufacturable at a knowledge level
- Input: Manufacturing model data
- Output: Validation outcome and validation summary
- Forbidden responsibilities: Execution planning, runtime control, machine assignment, job creation

### Operation Vocabulary
- Responsibility: Define the canonical set of manufacturing operation categories and operation identifiers
- Input: Domain language and approved manufacturing concepts
- Output: Stable operation vocabulary
- Forbidden responsibilities: Requirement derivation, instance creation, execution logic, machine logic

### Operation Semantics
- Responsibility: Define what each operation means in declarative terms
- Input: Operation vocabulary
- Output: Semantic contract for each operation
- Forbidden responsibilities: Product analysis, geometry calculation, task execution, scheduling

### Operation Requirement
- Responsibility: Represent that a product element requires a semantic manufacturing transformation
- Input: Product element identity, operation identity, reason, source
- Output: Declarative operation requirement
- Forbidden responsibilities: Execution steps, jobs, queues, runtime state, machine assignment

### Requirement Builder
- Responsibility: Derive atomic operation requirements from simple product-like input data
- Input: Product element identifiers and requirement flags
- Output: Tuple of operation requirements
- Forbidden responsibilities: Execution tasks, graph construction, geometry calculation, scheduling

### Operation Realizer
- Responsibility: Convert operation requirements into declarative operation records
- Input: Operation requirements
- Output: Declarative manufacturing operations
- Forbidden responsibilities: Operation ordering, machine assignment, job creation, runtime behavior

### Operation Instance
- Responsibility: Represent a semantic operation instance item with optional reference fields
- Input: Operation and instance identity context
- Output: Declarative operation instance
- Forbidden responsibilities: Placement calculation, execution status, job modeling, queue modeling

### Operation Instantiator
- Responsibility: Convert a realized operation into one or more declarative operation instances
- Input: Realized operation and known instance labels/references
- Output: Tuple of operation instances
- Forbidden responsibilities: Geometry calculation, placement inference, execution planning

### Operation Link
- Responsibility: Represent a semantic relationship between operation instances
- Input: Predecessor and successor instance identifiers
- Output: Declarative operation link
- Forbidden responsibilities: Dependency inference, execution ordering, runtime control

### Dependency Graph
- Responsibility: Hold structural relations between operation instances and operation links
- Input: Operation instances and operation links
- Output: Graph representation with adjacency and reverse adjacency
- Forbidden responsibilities: Manufacturing inference, execution order, batching, scheduling, machine logic

### Logical Execution Plan
- Responsibility: Provide a logical projection of graph states such as roots, blocked nodes, and terminal nodes
- Input: Dependency graph
- Output: Logical execution plan representation
- Forbidden responsibilities: Scheduler behavior, time assignment, priority assignment, job creation, runtime execution

## Boundary Rules

- Graph must not infer manufacturing knowledge
- Instantiator must not calculate geometry
- Realizer must not analyze product
- Requirement Builder must not create execution tasks
- Logical Plan must not become scheduler
- Factory Runtime must not modify product knowledge

## Future Layers

The following domains are reserved for future work and are intentionally not part of Manufacturing Knowledge Layer V1:

- Production Release Domain
- Factory Execution Domain
- Execution Model
- Job Model
- Queue Model
- Machine Model
- Production Intelligence

## Architecture Decision

Manufacturing Knowledge Layer V1 is architecturally stable and approved as the foundation for future execution layers.

It is the declarative manufacturing source of truth for downstream release, execution, and intelligence domains, but it remains separate from them by design.
