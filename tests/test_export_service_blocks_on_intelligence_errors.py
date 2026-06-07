import unittest
from unittest.mock import patch

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
)

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportServiceBlocking(
    unittest.TestCase
):

    @patch(
        "services.canonical_manufacturing_export_service.HybridManufacturingExtractor"
    )
    @patch(
        "services.canonical_manufacturing_export_service.ManufacturingRuleEngine"
    )
    def test_export_blocked_when_errors_exist(
        self,
        engine_cls,
        extractor_cls
    ):

        extractor_cls.extract.return_value = []

        engine = engine_cls.return_value

        engine.validate.return_value = [
            RuleResult(
                passed=False,
                level=ResultLevel.ERROR,
                code="FAIL",
                message="fatal"
            )
        ]

        engine.can_export.return_value = False

        with self.assertRaises(
            RuntimeError
        ):
            CanonicalManufacturingExportService.export(
                object(),
                "dummy.csv"
            )


if __name__ == "__main__":
    unittest.main()
