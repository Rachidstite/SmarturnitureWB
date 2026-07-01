import inspect
import unittest
from unittest.mock import patch

import application.manufacturing_application_service as mfg_svc_module
from application.application_service_result import ApplicationServiceResult
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration


def _fake_entry_result():
    return BaseCabinetManufacturingOutputsEntryResult(
        cut_list=object(),
        manufacturing_package=object(),
        metadata={"source": "test"},
    )


def _fake_production_package():
    return type(
        "ProductionPackage",
        (),
        {
            "hardware_report": object(),
            "cnc_report": object(),
            "assembly_report": object(),
            "warnings": ["release-warning"],
            "production_evidence": object(),
        },
    )()


class TestManufacturingApplicationServiceProductConfigurationContract(
    unittest.TestCase
):
    def test_execute_from_product_configuration_returns_application_service_result(
        self,
    ):
        service = ManufacturingApplicationService()
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        with patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_fake_entry_result(),
        ), patch.object(
            mfg_svc_module,
            "ManufacturingProductionPackageBuilder",
        ) as package_builder_class, patch.object(
            mfg_svc_module,
            "ManufacturingDecisionBuilder",
        ) as decision_builder_class:
            package_builder_class.return_value.build.return_value = (
                _fake_production_package()
            )
            decision_builder_class.return_value.build.return_value = object()
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        self.assertIsInstance(result, ApplicationServiceResult)

    def test_result_contains_manufacturing_outputs_factory_release_and_specification(
        self,
    ):
        service = ManufacturingApplicationService()
        configuration = ProductConfiguration(
            family_id="base_cabinet",
            width=750.0,
            height=900.0,
            depth=620.0,
        )

        with patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_fake_entry_result(),
        ), patch.object(
            mfg_svc_module,
            "ManufacturingProductionPackageBuilder",
        ) as package_builder_class, patch.object(
            mfg_svc_module,
            "ManufacturingDecisionBuilder",
        ) as decision_builder_class:
            package_builder_class.return_value.build.return_value = (
                _fake_production_package()
            )
            decision_builder_class.return_value.build.return_value = object()
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        self.assertTrue(result.success)
        self.assertIn("manufacturing_outputs", result.data)
        self.assertIn("factory_release_package", result.data)
        self.assertIn("specification", result.data)
        specification = result.data["specification"]
        self.assertEqual(specification.width_mm, configuration.width)
        self.assertEqual(specification.height_mm, configuration.height)
        self.assertEqual(specification.depth_mm, configuration.depth)

    def test_existing_execute_specification_api_still_works(self):
        service = ManufacturingApplicationService()

        with patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_fake_entry_result(),
        ), patch.object(
            mfg_svc_module,
            "ManufacturingProductionPackageBuilder",
        ) as package_builder_class, patch.object(
            mfg_svc_module,
            "ManufacturingDecisionBuilder",
        ) as decision_builder_class:
            package_builder_class.return_value.build.return_value = (
                _fake_production_package()
            )
            decision_builder_class.return_value.build.return_value = object()
            result = service.execute(
                specification=BaseCabinetSpecification(
                    width_mm=700.0,
                    height_mm=800.0,
                    depth_mm=600.0,
                )
            )

        self.assertTrue(result.success)
        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertIn("factory_release_package", result.data)

    def test_unsupported_family_id_raises_value_error_through_adapter_path(self):
        service = ManufacturingApplicationService()
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with self.assertRaises(ValueError):
            service.execute_from_product_configuration(configuration=configuration)

    def test_no_project_engineering_cost_commercial_or_new_pipeline_path_is_used(
        self,
    ):
        method_source = inspect.getsource(
            ManufacturingApplicationService.execute_from_product_configuration
        )
        module_source = inspect.getsource(mfg_svc_module)

        self.assertNotIn("ProjectApplicationService", method_source)
        self.assertNotIn("EngineeringApplicationService", method_source)
        for token in ("cost", "commercial"):
            self.assertNotIn(token, method_source.lower())

        import_lines = [
            line.strip()
            for line in module_source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        forbidden = (
            "application.project_application_service",
            "application.engineering_application_service",
            "cost_intelligence",
            "commercial_outputs",
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)


if __name__ == "__main__":
    unittest.main()
