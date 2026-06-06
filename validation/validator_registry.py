from validation.panel_spec_validator import (
    PanelSpecValidator
)

from validation.manufacturing_feasibility_validator import (
    ManufacturingFeasibilityValidator
)

from validation.unified_operation_validation_adapter import (
    UnifiedOperationValidationAdapter
)

VALIDATORS = [
    PanelSpecValidator(),
    ManufacturingFeasibilityValidator(),
    UnifiedOperationValidationAdapter(),
]
