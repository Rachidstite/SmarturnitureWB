import unittest
from unittest.mock import patch

import application.manufacturing_application_service as service_module
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
)
from domain.product_configuration import ProductConfiguration
from domain.product_family_catalog import BASE_CABINET


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


class TestProductFamilyFactoryIntegrationContract(unittest.TestCase):
    def test_base_cabinet_family_reaches_factory_release_through_public_entry_point(
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
            service_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_fake_entry_result(),
        ), patch.object(
            service_module,
            "ManufacturingProductionPackageBuilder",
        ) as package_builder_class, patch.object(
            service_module,
            "ManufacturingDecisionBuilder",
        ) as decision_builder_class:
            package_builder_class.return_value.build.return_value = (
                _fake_production_package()
            )
            decision_builder_class.return_value.build.return_value = object()

            result = ManufacturingApplicationService().execute_from_product_configuration(
                configuration=configuration
            )

        self.assertTrue(result.success)
        self.assertIn("manufacturing_outputs", result.data)
        self.assertIn("factory_release_package", result.data)
        self.assertIn("specification", result.data)

        specification = result.data["specification"]
        factory_release_package = result.data["factory_release_package"]

        self.assertEqual(specification.width_mm, configuration.width)
        self.assertEqual(specification.height_mm, configuration.height)
        self.assertEqual(specification.depth_mm, configuration.depth)
        self.assertIsNotNone(factory_release_package)


if __name__ == "__main__":
    unittest.main()
