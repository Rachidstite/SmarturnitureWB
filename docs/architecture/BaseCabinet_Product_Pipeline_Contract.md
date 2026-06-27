# Base Cabinet Product Pipeline Contract

## Purpose

`BaseCabinetSpecification` is the product source for the Base Cabinet flow.

All downstream outputs must flow through the approved pipeline so that product meaning stays anchored to the specification, engineering remains the geometry and scene-graph authority, and manufacturing stays on the existing runtime path.

This contract documents the official boundary for product-level outputs now that the flow reaches Cut List through the Manufacturing Outputs Entry.

## Official Pipeline

BaseCabinetSpecification  
↓  
BaseCabinetSpecificationAdapter  
↓  
Engineering Entry  
↓  
Engineering Cabinet  
↓  
Scene Graph  
↓  
Validation Entry  
↓  
Manufacturing Runtime Pipeline  
↓  
Manufacturing Outputs Entry  
↓  
Cut List

## Current Implemented Outputs

- Cut List

## Future Outputs

Document only:

- BOM
- Hardware List
- Manufacturing Validation Summary
- CNC Export
- Cost Summary
- Quotation Draft

These outputs are not part of the current implemented contract and must remain documented as future work until their existing paths are independently audited and approved.

## Boundary Rules

- No output may bypass `BaseCabinetSpecification`.
- No output may bypass Engineering Entry.
- Manufacturing must consume `Scene Graph` or `ManufacturingPackage`.
- Manufacturing Outputs Entry is the facade for product-level manufacturing outputs.
- Builders remain independent.
- Do not create one entry per output unless there is proven architectural need.
- Do not add BOM, hardware, or CNC until their existing paths are audited.

## Value to Factory

This contract supports a cleaner factory pipeline by keeping the product source, engineering handoff, validation, and manufacturing outputs in a stable order.

That provides:

- faster design
- faster manufacturing preparation
- fewer mistakes
- reusable manufacturing outputs
- future commercial readiness

## Decision

**APPROVED_PIPELINE_CONTRACT**

This document establishes the official Base Cabinet product pipeline contract for the current implemented flow.
