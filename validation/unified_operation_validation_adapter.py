from validation.hybrid_manufacturing_validator import (
    HybridManufacturingValidator
)


class UnifiedOperationValidationAdapter:

    def __init__(self):

        self.validator = (
            HybridManufacturingValidator()
        )

    def validate(self, specs):

        issues = []

        for spec in specs:

            issues.extend(
                self.validator.validate(
                    getattr(
                        spec,
                        "unified_operations",
                        []
                    )
                )
            )

        return issues
