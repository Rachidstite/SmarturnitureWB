import inspect
import unittest
from typing import Any
from unittest.mock import patch

import application.engineering_application_service as eng_svc_module
import domain.base_cabinet_engineering_entry as engineering_entry_module
from application.application_service_result import ApplicationServiceResult
from application.engineering_application_service import EngineeringApplicationService
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration
from engine.cabinet import Cabinet


class FakeCabinetBuilder:
    instances_created = 0
    build_calls = 0
    last_cabinet = None

    def __init__(self):
        type(self).instances_created += 1
        self.scene_graph = object()

    def build(self, cabinet: Any) -> None:
        type(self).build_calls += 1
        type(self).last_cabinet = cabinet
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


def _reset_fake_cabinet_builder() -> None:
    FakeCabinetBuilder.instances_created = 0
    FakeCabinetBuilder.build_calls = 0
    FakeCabinetBuilder.last_cabinet = None


class TestEngineeringApplicationServiceProductConfigurationContract(unittest.TestCase):
    def setUp(self):
        _reset_fake_cabinet_builder()

    def test_execute_from_product_configuration_returns_application_service_result(self):
        service = EngineeringApplicationService()
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        self.assertIsInstance(result, ApplicationServiceResult)

    def test_result_contains_a_cabinet(self):
        service = EngineeringApplicationService()
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=750.0,
            height=900.0,
            depth=620.0,
        )

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        self.assertTrue(result.success)
        self.assertIn("cabinet", result.data)
        self.assertIsInstance(result.data["cabinet"], Cabinet)

    def test_cabinet_has_engineering_model(self):
        service = EngineeringApplicationService()
        configuration = ProductConfiguration(
            family_id="base_cabinet",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        cabinet = result.data["cabinet"]
        self.assertIsNotNone(cabinet.engineering_model)

    def test_existing_execute_specification_api_still_works(self):
        service = EngineeringApplicationService()

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            result = service.execute(
                specification=BaseCabinetSpecification(
                    width_mm=700.0,
                    height_mm=800.0,
                    depth_mm=600.0,
                )
            )

        self.assertTrue(result.success)
        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertIsInstance(result.data["cabinet"], Cabinet)

    def test_unsupported_family_id_raises_value_error_through_adapter_path(self):
        service = EngineeringApplicationService()
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with self.assertRaises(ValueError):
            service.execute_from_product_configuration(configuration=configuration)

    def test_no_project_application_service_manufacturing_cost_or_commercial_path_is_used(
        self,
    ):
        method_source = inspect.getsource(
            EngineeringApplicationService.execute_from_product_configuration
        )
        module_source = inspect.getsource(eng_svc_module)

        self.assertNotIn("ProjectApplicationService", method_source)
        for token in (
            "manufacturing",
            "cost",
            "commercial",
        ):
            self.assertNotIn(token, method_source.lower())

        import_lines = [
            line.strip()
            for line in module_source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        forbidden = (
            "application.project_application_service",
            "manufacturing",
            "cost_intelligence",
            "commercial_outputs",
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)


if __name__ == "__main__":
    unittest.main()
