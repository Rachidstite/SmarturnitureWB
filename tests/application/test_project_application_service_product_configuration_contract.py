import inspect
import unittest
from unittest.mock import patch

import application.project_application_service as project_svc_module
from application.application_service_result import ApplicationServiceResult
from application.project_application_service import ProjectApplicationService
from domain.base_cabinet_product_result import BaseCabinetProductResult
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration


def _fake_project_result(specification=None, quotation_document=None):
    return BaseCabinetProductResult(
        specification=specification,
        scenario=object(),
        engineering=object(),
        validation=object(),
        manufacturing_outputs=object(),
        cost=object(),
        commercial=object(),
        quotation_document=quotation_document,
        diagnostics=(),
    )


class TestProjectApplicationServiceProductConfigurationContract(unittest.TestCase):
    def test_execute_from_product_configuration_returns_application_service_result(
        self,
    ):
        service = ProjectApplicationService()
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            return_value=_fake_project_result(),
        ):
            result = service.execute_from_product_configuration(
                configuration=configuration,
                create_document=False,
            )

        self.assertIsInstance(result, ApplicationServiceResult)

    def test_result_contains_project_result_and_specification(self):
        service = ProjectApplicationService()
        configuration = ProductConfiguration(
            family_id="base_cabinet",
            width=750.0,
            height=900.0,
            depth=620.0,
        )

        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            side_effect=lambda specification, quotation_metadata=None: (
                _fake_project_result(specification=specification)
            ),
        ):
            result = service.execute_from_product_configuration(
                configuration=configuration,
                create_document=False,
            )

        self.assertTrue(result.success)
        self.assertIn("project_result", result.data)
        self.assertIn("specification", result.data)

        specification = result.data["specification"]
        project_result = result.data["project_result"]

        self.assertEqual(specification.width_mm, configuration.width)
        self.assertEqual(specification.height_mm, configuration.height)
        self.assertEqual(specification.depth_mm, configuration.depth)
        self.assertIsNotNone(project_result.engineering)
        self.assertIsNotNone(project_result.manufacturing_outputs)
        self.assertIsNotNone(project_result.cost)
        self.assertIsNotNone(project_result.commercial)

    def test_existing_execute_specification_api_still_works(self):
        service = ProjectApplicationService()
        specification = BaseCabinetSpecification(
            width_mm=700.0,
            height_mm=800.0,
            depth_mm=600.0,
        )

        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            return_value=_fake_project_result(specification=specification),
        ):
            result = service.execute(
                specification=specification,
                create_document=False,
            )

        self.assertTrue(result.success)
        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertIn("project_result", result.data)

    def test_unsupported_family_id_raises_value_error_through_adapter_path(self):
        service = ProjectApplicationService()
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with self.assertRaises(ValueError):
            service.execute_from_product_configuration(
                configuration=configuration,
                create_document=False,
            )

    def test_create_document_false_passes_through_without_forcing_document_creation(
        self,
    ):
        service = ProjectApplicationService()
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            side_effect=lambda specification, quotation_metadata=None: (
                _fake_project_result(
                    specification=specification,
                    quotation_document=None,
                )
            ),
        ) as workflow_spy:
            result = service.execute_from_product_configuration(
                configuration=configuration,
                quotation_metadata={"quotation_number": "Q-001"},
                create_document=False,
            )

        self.assertIsNone(result.data["document_name"])
        self.assertIsNone(result.data["project_result"].quotation_document)
        workflow_spy.assert_called_once()
        self.assertEqual(
            workflow_spy.call_args.kwargs["quotation_metadata"],
            {"quotation_number": "Q-001"},
        )

    def test_no_engineering_manufacturing_cost_or_commercial_application_service_or_new_pipeline_is_used(
        self,
    ):
        method_source = inspect.getsource(
            ProjectApplicationService.execute_from_product_configuration
        )
        module_source = inspect.getsource(project_svc_module)

        for token in (
            "EngineeringApplicationService",
            "ManufacturingApplicationService",
            "CostApplicationService",
            "CommercialApplicationService",
        ):
            self.assertNotIn(token, method_source)

        import_lines = [
            line.strip()
            for line in module_source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        forbidden = (
            "application.engineering_application_service",
            "application.manufacturing_application_service",
            "CostApplicationService",
            "CommercialApplicationService",
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)


if __name__ == "__main__":
    unittest.main()
