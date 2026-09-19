# Contributing to SmartFurnitureWB

Thank you for helping improve SmartFurnitureWB.

## Before making changes

1. Read the architecture documentation in `docs/Architecture.md`.
2. Understand whether the change belongs to the domain/manufacturing layer or the FreeCAD GUI layer.
3. Prefer the smallest change that preserves existing contracts and behavior.
4. Add or update tests for behavior that can be tested automatically.

## Development principles

### Manufacturing correctness first

Changes affecting dimensions, topology, joinery, machining operations, CNC output, BOMs, cut lists, or validation should be treated as manufacturing-critical.

Avoid silently changing manufacturing behavior.

### Keep domain logic isolated

Where practical, keep manufacturing and domain rules independent from FreeCAD GUI concerns. The architecture is intentionally structured around domain objects, rules, compilation, validation, and export.

### Preserve identity and state

The Scene Graph, domain identities, serialization, and object registry are part of the system's consistency model. Changes to these areas should include regression coverage.

### Test before merging

Run:

```bash
python3 run_tests.py
```

For focused development, run the relevant test module(s) directly as well.

Do not mark a change as production-safe when the relevant tests are failing.

## Pull requests

A useful pull request should explain:

- What changed
- Why it changed
- Which manufacturing behavior is affected
- Tests added or executed
- Any known limitations or follow-up work

Keep pull requests focused. Avoid mixing unrelated refactors with manufacturing behavior changes.

## Bug reports

When reporting a bug, include:

- FreeCAD version
- SmartFurnitureWB revision/branch
- Minimal reproduction steps
- Expected behavior
- Actual behavior
- Relevant test output or error message
- Whether the issue affects geometry, manufacturing data, validation, export, or UI

## Manufacturing changes

For changes involving CNC or machining data, include concrete examples whenever possible:

- Panel dimensions
- Material/thickness
- Hardware/joinery type
- Expected machining operation
- Expected coordinates or export result

This helps reviewers validate the change against real workshop requirements.
