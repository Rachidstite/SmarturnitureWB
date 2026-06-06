from validation.hybrid_manufacturing_validator import (
    HybridManufacturingValidator
)


class UnifiedOperationValidationAdapter:

    def __init__(self):

        self.validator = (
            HybridManufacturingValidator()
        )

    def validate(self, specs):

        if not specs:
            return []

        operations = getattr(
            specs[0],
            "unified_operations",
            []
        )

        return self.validator.validate(
            operations
        )
