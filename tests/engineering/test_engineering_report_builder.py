from validation.intelligence.engineering.engineering_report_builder import (
    EngineeringReportBuilder,
)

from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_builder_collects_results():

    results = [

        EngineeringResult(
            passed=False,
            level=EngineeringLevel.WARNING,
            code="WARN",
            message="warning",
        ),

        EngineeringResult(
            passed=False,
            level=EngineeringLevel.ERROR,
            code="ERR",
            message="error",
        ),
    ]

    report = (
        EngineeringReportBuilder()
        .build(results)
    )

    assert len(report.warnings) == 1

    assert len(report.errors) == 1
