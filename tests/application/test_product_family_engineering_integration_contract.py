import unittest
from typing import Any
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from application.engineering_application_service import EngineeringApplicationService
from domain.product_configuration import ProductConfiguration
from domain.product_family_catalog import BASE_CABINET
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


class TestProductFamilyEngineeringIntegrationContract(unittest.TestCase):
    def setUp(self):
        _reset_fake_cabinet_builder()

    def test_base_cabinet_family_creates_real_engineering_cabinet_through_public_entry_point(
        self,
    ):
        configuration = ProductConfiguration(
            family_id=BASE_CABINET.family_id,
            width=BASE_CABINET.default_parameters["width_mm"],
            height=BASE_CABINET.default_parameters["height_mm"],
            depth=BASE_CABINET.default_parameters["depth_mm"],
            options=dict(BASE_CABINET.engineering_defaults)
            | dict(BASE_CABINET.manufacturing_defaults),
        )

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            result = EngineeringApplicationService().execute_from_product_configuration(
                configuration=configuration
            )

        self.assertTrue(result.success)
        self.assertIn("cabinet", result.data)
        self.assertIn("specification", result.data)

        cabinet = result.data["cabinet"]
        specification = result.data["specification"]

        self.assertIsInstance(cabinet, Cabinet)
        self.assertIsNotNone(cabinet.engineering_model)
        self.assertIsNotNone(cabinet.construction_model)
        self.assertEqual(specification.width_mm, configuration.width)
        self.assertEqual(specification.height_mm, configuration.height)
        self.assertEqual(specification.depth_mm, configuration.depth)


if __name__ == "__main__":
    unittest.main()
