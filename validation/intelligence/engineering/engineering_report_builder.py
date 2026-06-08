from validation.intelligence.engineering.engineering_report import (
    EngineeringReport,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class EngineeringReportBuilder:

    def build(
        self,
        results,
    ):

        errors = [
            r
            for r in results
            if r.level == EngineeringLevel.ERROR
        ]

        warnings = [
            r
            for r in results
            if r.level == EngineeringLevel.WARNING
        ]

        recommendations = [
            r
            for r in results
            if getattr(
                r.level,
                "name",
                ""
            ) == "RECOMMENDATION"
        ]

        return EngineeringReport(
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )
