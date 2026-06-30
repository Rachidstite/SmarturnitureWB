import inspect
import unittest
from unittest.mock import patch

import application.manufacturing_application_service as service_module
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
)
from domain.base_cabinet_specification import BaseCabinetSpecification


class TestManufacturingApplicationPipeline(unittest.TestCase):
    def test_application_pipeline_builds_package_then_decision(self):
        from manufacturing.manufacturing_decision import ManufacturingDecision
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        manufacturing_package = object()
        production_package = ManufacturingProductionPackage()
        decision = ManufacturingDecision(status="PASS", ready_for_production=True)
        entry_result = BaseCabinetManufacturingOutputsEntryResult(
            cut_list=object(),
            manufacturing_package=manufacturing_package,
            metadata={},
        )

        with patch.object(
            service_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=entry_result,
        ), patch.object(
            service_module,
            "ManufacturingProductionPackageBuilder",
        ) as package_builder_class, patch.object(
            service_module,
            "ManufacturingDecisionBuilder",
        ) as decision_builder_class:
            package_builder_class.return_value.build.return_value = production_package
            decision_builder_class.return_value.build.return_value = decision

            result = ManufacturingApplicationService().execute(
                specification=BaseCabinetSpecification()
            )

        package_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        decision_builder_class.return_value.build.assert_called_once_with(
            production_evidence=production_package.production_evidence
        )
        self.assertIs(
            result.data["manufacturing_production_package"],
            production_package,
        )
        self.assertIs(result.data["manufacturing_decision"], decision)

    def test_door_hinge_warning_becomes_review_decision(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )
        from tests.manufacturing.test_door_hardware_evidence_in_production_package import (
            TestDoorHardwareEvidenceInProductionPackage,
        )

        entry_result = BaseCabinetManufacturingOutputsEntryResult(
            cut_list=object(),
            manufacturing_package=(
                TestDoorHardwareEvidenceInProductionPackage
                ._package_with_door_without_hinge_metadata()
            ),
            metadata={},
        )

        with patch.object(
            service_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=entry_result,
        ):
            result = ManufacturingApplicationService().execute(
                specification=BaseCabinetSpecification()
            )

        production_package = result.data["manufacturing_production_package"]
        decision = result.data["manufacturing_decision"]

        self.assertIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            production_package.release_warnings,
        )
        self.assertEqual(decision.status, "WARNING")
        self.assertEqual(decision.legacy_readiness_status, "REVIEW")
        self.assertFalse(decision.ready_for_production)

    def test_builders_remain_independent(self):
        import manufacturing.manufacturing_decision_builder as decision_builder
        import manufacturing.manufacturing_production_package_builder as package_builder

        package_builder_source = inspect.getsource(package_builder)
        decision_builder_source = inspect.getsource(decision_builder)

        self.assertNotIn("ManufacturingDecisionBuilder", package_builder_source)
        self.assertNotIn(
            "manufacturing_decision_builder",
            package_builder_source,
        )
        self.assertNotIn(
            "ManufacturingProductionPackageBuilder",
            decision_builder_source,
        )
        self.assertNotIn(
            "manufacturing_production_package_builder",
            decision_builder_source,
        )


if __name__ == "__main__":
    unittest.main()
