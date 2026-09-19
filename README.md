# SmartFurnitureWB

**Manufacturing-focused FreeCAD Workbench for parametric furniture design and MDF production workflows.**

SmartFurnitureWB is an open-source FreeCAD project focused on connecting furniture design data with manufacturing logic. The project is designed around a production-oriented pipeline rather than geometry alone.

## What it is

SmartFurnitureWB aims to turn a parametric furniture model into structured manufacturing data that can be validated, costed, assembled, and exported for workshop use.

**Design → Topology → Scene Graph → Rules → Manufacturing Compiler → Validation → Export**

## Core capabilities

- Parametric cabinet and furniture structures
- Scene Graph and persistent domain identity
- Spatial and geometric validation
- Furniture constraints and manufacturing rules
- Assembly graph and joinery logic
- Hardware library and placement rules
- Manufacturing operations and drilling data
- CNC-oriented generation and export
- Cut lists and BOM/report generation
- Cost calculation and cost intelligence
- Incremental rendering and object registry
- Automated regression and integration tests

## Architecture

The project separates manufacturing/domain logic from the FreeCAD presentation layer:

```text
User / FreeCAD UI
        │
        ▼
Furniture Builders
        │
        ▼
Topology + Scene Graph
        │
        ▼
Rules / Constraints
        │
        ▼
Manufacturing Compiler
        │
        ├── Hardware / Joinery
        ├── Machining Operations
        └── CNC Data
        │
        ▼
Validation
        │
        ▼
Exports / BOM / Cut List / Reports
```

The repository currently contains dedicated modules for assembly, CNC, constraints, costing, domain modeling, manufacturing, scene graph management, validation, exports, GUI, and tests.

## Manufacturing model

The domain layer represents physical furniture parts and manufacturing intent explicitly. Examples include:

- Side, top, bottom, divider and shelf panels
- Doors and drawer components
- Hardware placements
- MINIFIX / CONFIRMAT / shelf-pin style joinery
- Face and edge drilling
- Grooves and machining operations
- Material and edge-band specifications
- Manufacturing validation constraints

This makes the project suitable for workflows where a furniture model must remain connected to the data required to build it.

## Testing

The repository includes unit, integration, manufacturing, CNC, scene-graph, serialization, topology, and golden-master tests.

The project also provides `run_tests.py` for the FreeCAD development environment.

```bash
python3 run_tests.py
```

The test runner discovers tests from the project's `tests/` directory and exits non-zero when regressions are detected.

## Documentation

- [Architecture](docs/Architecture.md)
- [Vision](docs/Vision.md)
- [Roadmap](docs/Roadmap.md)
- [Domain Model](docs/DomainModel.md)
- [Changelog](docs/Changelog.md)
- [ADR](docs/adr/)

## Project status

SmartFurnitureWB is an actively developed research/engineering project. The architecture and manufacturing pipeline are evolving toward a production-ready FreeCAD workbench.

The roadmap currently identifies CNC/nesting workshop output as a next-stage focus, followed by a future commercial-grade GUI.

## Contributing

Contributions, technical discussion, bug reports, and manufacturing-workflow feedback are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Maintainer

Maintained by **Rachidstite**.

## Scope

SmartFurnitureWB is focused on furniture manufacturing workflows, especially panel-based furniture such as MDF cabinetry. It is not intended to replace general-purpose FreeCAD functionality; it adds domain-specific manufacturing intelligence on top of FreeCAD.
