import inspect
import unittest
from unittest.mock import patch

import application.engineering_application_service as eng_svc_module
import application.manufacturing_application_service as mfg_svc_module
import application.project_application_service as project_svc_module
from application.engineering_application_service import EngineeringApplicationService
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from application.project_application_service import ProjectApplicationService
from application.application_service_result import ApplicationServiceResult
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_base_cabinet_adapter import (
    adapt_product_configuration_to_base_cabinet_specification,
)
from domain.wall_cabinet_engineering_entry import WallCabinetEngineeringEntryResult


class TestApplicationServiceFamilyRoutingContract(unittest.TestCase):
    def _assert_module_does_not_import_product_family_catalog(self, module):
        module_source = inspect.getsource(module)
        import_lines = [
            line.strip()
            for line in module_source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        for line in import_lines:
            self.assertNotIn("product_family_catalog", line)

    def test_engineering_service_routes_wall_cabinet_to_wall_entry(self):
        service = EngineeringApplicationService()
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with patch.object(
            eng_svc_module,
            "adapt_product_configuration_to_base_cabinet_specification",
        ) as adapter_spy, patch.object(
            eng_svc_module,
            "build_base_cabinet_engineering_cabinet",
        ) as base_entry_spy:
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        self.assertTrue(result.success)
        self.assertIsInstance(result.data, WallCabinetEngineeringEntryResult)
        self.assertIsNone(result.data.cabinet)
        self.assertFalse(result.data.executable_geometry)
        self.assertIsNotNone(result.data.engineering_model)
        self.assertEqual(result.data.engineering_model.mounting_type, "wall")
        self.assertEqual(result.data.engineering_model.support_strategy, "wall_mounted")
        self.assertIn("does not yet produce geometry", result.data.reason.lower())
        adapter_spy.assert_not_called()
        base_entry_spy.assert_not_called()

    def test_manufacturing_service_routes_wall_cabinet_to_wall_entry(self):
        service = ManufacturingApplicationService()
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with patch.object(
            mfg_svc_module,
            "adapt_product_configuration_to_base_cabinet_specification",
        ) as adapter_spy, patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
        ) as entry_spy:
            result = service.execute_from_product_configuration(
                configuration=configuration
            )

        self.assertTrue(result.success)
        self.assertIsInstance(result.data, WallCabinetEngineeringEntryResult)
        self.assertIsNone(result.data.cabinet)
        self.assertFalse(result.data.executable_geometry)
        self.assertIsNotNone(result.data.engineering_model)
        self.assertEqual(result.data.engineering_model.mounting_type, "wall")
        self.assertEqual(result.data.engineering_model.support_strategy, "wall_mounted")
        self.assertIn("does not yet produce geometry", result.data.reason.lower())
        adapter_spy.assert_not_called()
        entry_spy.assert_not_called()

    def test_project_service_routes_wall_cabinet_to_wall_entry(self):
        service = ProjectApplicationService()
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with patch.object(
            project_svc_module,
            "adapt_product_configuration_to_base_cabinet_specification",
        ) as adapter_spy, patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
        ) as workflow_spy:
            result = service.execute_from_product_configuration(
                configuration=configuration,
                create_document=False,
            )

        self.assertTrue(result.success)
        self.assertIsInstance(result.data, WallCabinetEngineeringEntryResult)
        self.assertIsNone(result.data.cabinet)
        self.assertFalse(result.data.executable_geometry)
        self.assertIsNotNone(result.data.engineering_model)
        self.assertEqual(result.data.engineering_model.mounting_type, "wall")
        self.assertEqual(result.data.engineering_model.support_strategy, "wall_mounted")
        self.assertIn("does not yet produce geometry", result.data.reason.lower())
        adapter_spy.assert_not_called()
        workflow_spy.assert_not_called()

    def test_unknown_family_is_rejected_with_clear_message(self):
        service = EngineeringApplicationService()
        configuration = ProductConfiguration(
            family_id="WARDROBE",
            width=900.0,
            height=2100.0,
            depth=600.0,
        )

        with self.assertRaisesRegex(ValueError, r"WARDROBE.*unknown family"):
            service.execute_from_product_configuration(configuration=configuration)

    def test_base_cabinet_still_reaches_adapter_through_all_application_services(
        self,
    ):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
        )
        expected_specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
        )

        with patch.object(
            eng_svc_module,
            "adapt_product_configuration_to_base_cabinet_specification",
            return_value=expected_specification,
        ) as eng_adapter_spy, patch.object(
            EngineeringApplicationService,
            "execute",
            return_value=ApplicationServiceResult(
                success=True,
                data={"specification": expected_specification},
                errors=(),
                diagnostics=(),
            ),
        ) as eng_execute_spy:
            eng_result = EngineeringApplicationService().execute_from_product_configuration(
                configuration=configuration
            )

        with patch.object(
            mfg_svc_module,
            "adapt_product_configuration_to_base_cabinet_specification",
            return_value=expected_specification,
        ) as mfg_adapter_spy, patch.object(
            ManufacturingApplicationService,
            "execute",
            return_value=ApplicationServiceResult(
                success=True,
                data={"specification": expected_specification},
                errors=(),
                diagnostics=(),
            ),
        ) as mfg_execute_spy:
            mfg_result = ManufacturingApplicationService().execute_from_product_configuration(
                configuration=configuration
            )

        with patch.object(
            project_svc_module,
            "adapt_product_configuration_to_base_cabinet_specification",
            return_value=expected_specification,
        ) as project_adapter_spy, patch.object(
            ProjectApplicationService,
            "execute",
            return_value=ApplicationServiceResult(
                success=True,
                data={"specification": expected_specification},
                errors=(),
                diagnostics=(),
            ),
        ) as project_execute_spy:
            project_result = ProjectApplicationService().execute_from_product_configuration(
                configuration=configuration,
                create_document=False,
            )

        self.assertTrue(eng_result.success)
        self.assertTrue(mfg_result.success)
        self.assertTrue(project_result.success)
        eng_adapter_spy.assert_called_once()
        eng_execute_spy.assert_called_once()
        mfg_adapter_spy.assert_called_once()
        mfg_execute_spy.assert_called_once()
        project_adapter_spy.assert_called_once()
        project_execute_spy.assert_called_once()

    def test_existing_execute_specification_api_still_works(self):
        service = EngineeringApplicationService()
        specification = BaseCabinetSpecification(
            width_mm=700.0,
            height_mm=800.0,
            depth_mm=600.0,
        )

        with patch.object(
            EngineeringApplicationService,
            "execute",
            return_value=ApplicationServiceResult(
                success=True,
                data={"specification": specification},
                errors=(),
                diagnostics=(),
            ),
        ):
            result = service.execute(specification=specification)

        self.assertTrue(result.success)
        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertEqual(result.data["specification"], specification)

    def test_no_application_service_imports_product_family_catalog(self):
        self._assert_module_does_not_import_product_family_catalog(eng_svc_module)
        self._assert_module_does_not_import_product_family_catalog(mfg_svc_module)
        self._assert_module_does_not_import_product_family_catalog(
            project_svc_module
        )

    def test_existing_base_cabinet_adapter_behavior_remains_unchanged(self):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
            options={
                "door_count": 2,
                "shelf_count": 1,
                "has_back_panel": True,
                "edge_banding_required": True,
                "toe_kick_required": True,
                "hinge_family": "STANDARD_110",
                "drawer_family": "NONE",
            },
        )

        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )

        self.assertIsInstance(specification, BaseCabinetSpecification)
        self.assertEqual(specification.width_mm, 600.0)
        self.assertEqual(specification.height_mm, 720.0)
        self.assertEqual(specification.depth_mm, 580.0)


if __name__ == "__main__":
    unittest.main()
