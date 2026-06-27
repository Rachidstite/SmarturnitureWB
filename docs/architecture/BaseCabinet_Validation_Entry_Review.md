# Base Cabinet Validation Entry Review

## Scope Reviewed

- [domain/base_cabinet_specification_validation.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_specification_validation.py)
- [domain/base_cabinet_specification_adapter.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/base_cabinet_specification_adapter.py)
- [domain/constraint_engine.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/constraint_engine.py)
- [domain/furniture_project_builder.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/furniture_project_builder.py)
- [domain/rules_engine.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/domain/rules_engine.py)
- [engine/cabinet_builder.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/engine/cabinet_builder.py)
- [services/manufacturing_validation_service.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/services/manufacturing_validation_service.py)
- [validation/manufacturing_feasibility_validator.py](/home/rachid/.local/share/FreeCAD/v1-1/Mod/SmartFurnitureWB/validation/manufacturing_feasibility_validator.py)

## Review Questions

### 1. Is `_validation_project_from_adapter_result()` duplicating an existing adapter?

No existing project-adapter component was found that creates the validation project shape for `BaseCabinetSpecification`.

The reviewed codebase has:

- `FurnitureProjectBuilder`, which builds `FurnitureProject`
- `CabinetBuilder`, which consumes `Cabinet`
- `CabinetConstraintValidator`, which expects a project-like object

There is no dedicated `RuntimeProjectAdapter`, `ProjectAdapter`, or `FurnitureProject` adapter that already performs the specific validation-project shaping used by the new entry point.

### 2. Is there an existing component that should create the validation project shape?

Not currently.

The nearest candidates are:

- `FurnitureProjectBuilder`
- `domain.constraint_engine.CabinetConstraintValidator`

But neither one provides a purpose-built validation project adapter for `BaseCabinetSpecification`.

### 3. Should the validation entry keep this helper, move it, or reuse an existing adapter?

Keep the helper for now.

Reason:

- It is narrow.
- It does not introduce a new engine.
- It does not modify runtime or builders.
- It only creates the minimal project-like shape needed by the existing validator.

If a future shared project adapter is introduced, this helper should be moved there rather than duplicated again.

### 4. Is the current `SimpleNamespace` approach acceptable as a temporary contract?

Yes.

It is acceptable as a temporary contract because:

- it is minimal,
- it is explicit,
- it preserves the adapter result metadata,
- it avoids inventing a new model,
- it keeps the validation entry isolated from runtime and geometry code.

## Decision

**APPROVED AS IS**

## Notes

- The helper is not duplicating an existing adapter because no equivalent adapter exists today.
- The helper is still a temporary contract-level shim and should be revisited only if a shared project-adapter layer is added later.
- The current validation entry can be committed if the goal is to preserve the minimal contract entry point without introducing new runtime behavior.
