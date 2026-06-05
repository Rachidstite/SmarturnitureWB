from validation.panel_spec_validator import (
    PanelSpecValidator
)

from validation.manufacturing_feasibility_validator import (
    ManufacturingFeasibilityValidator
)

VALIDATORS = [
    PanelSpecValidator(),
    ManufacturingFeasibilityValidator(),
]
