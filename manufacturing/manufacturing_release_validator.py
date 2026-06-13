from manufacturing.manufacturing_validator import ManufacturingValidator
from manufacturing.manufacturing_warnings_analyzer import (
    ManufacturingWarningsAnalyzer,
)


class ManufacturingReleaseValidator:

    def validate(self, package):
        warnings = ManufacturingWarningsAnalyzer().analyze(package)
        warnings += ManufacturingValidator().validate(package)

        return {
            "ready": len(warnings) == 0,
            "warnings": warnings,
        }
