from validation.intelligence.unified.unified_report import (
    UnifiedReport,
)


class UnifiedReportBuilder:

    def build(
        self,
        manufacturing_report,
        engineering_report,
    ):

        errors = (
            list(
                getattr(
                    manufacturing_report,
                    "errors",
                    [],
                )
            )
            +
            list(
                getattr(
                    engineering_report,
                    "errors",
                    [],
                )
            )
        )

        warnings = (
            list(
                getattr(
                    manufacturing_report,
                    "warnings",
                    [],
                )
            )
            +
            list(
                getattr(
                    engineering_report,
                    "warnings",
                    [],
                )
            )
        )

        recommendations = (
            list(
                getattr(
                    manufacturing_report,
                    "recommendations",
                    [],
                )
            )
            +
            list(
                getattr(
                    engineering_report,
                    "recommendations",
                    [],
                )
            )
        )

        return UnifiedReport(
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )
