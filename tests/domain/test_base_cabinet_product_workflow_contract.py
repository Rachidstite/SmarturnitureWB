import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_product_workflow as workflow_module
from domain.base_cabinet_product_result import BaseCabinetProductResult
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_scenario import BaseCabinetScenario
from domain.base_cabinet_specification import BaseCabinetSpecification


class TestBaseCabinetProductWorkflowContract(unittest.TestCase):
    def test_accepts_base_cabinet_specification(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ) as engineering_entry, patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ) as validation_entry, patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ) as outputs_entry:
            result = build_base_cabinet_product_workflow(specification)

        engineering_entry.assert_called_once_with(specification)
        validation_entry.assert_called_once_with(specification)
        outputs_entry.assert_called_once_with(specification)
        self.assertIsInstance(result, BaseCabinetProductResult)

    def test_returns_base_cabinet_product_result(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            result = build_base_cabinet_product_workflow(specification)

        self.assertIsInstance(result, BaseCabinetProductResult)

    def test_uses_engineering_entry(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ) as engineering_entry, patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            build_base_cabinet_product_workflow(specification)

        engineering_entry.assert_called_once_with(specification)

    def test_uses_validation_entry(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ) as validation_entry, patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            build_base_cabinet_product_workflow(specification)

        validation_entry.assert_called_once_with(specification)

    def test_uses_manufacturing_outputs_entry(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ) as outputs_entry:
            build_base_cabinet_product_workflow(specification)

        outputs_entry.assert_called_once_with(specification)

    def test_includes_scenario(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            result = build_base_cabinet_product_workflow(specification)

        self.assertIsInstance(result.scenario, BaseCabinetScenario)
        self.assertIs(result.scenario.specification, specification)

    def test_preserves_metadata(self):
        specification = BaseCabinetSpecification()
        metadata = {"door_count": 2, "drawer_family": "NONE"}

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": []})(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": metadata})(),
        ):
            result = build_base_cabinet_product_workflow(specification)

        self.assertEqual(result.metadata, metadata)
        self.assertIsNot(result.metadata, metadata)

    def test_fills_diagnostics(self):
        specification = BaseCabinetSpecification()
        violations = [object(), object()]

        with patch.object(
            workflow_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=object(),
        ), patch.object(
            workflow_module,
            "validate_base_cabinet_specification",
            return_value=type("Validation", (), {"violations": violations})(),
        ), patch.object(
            workflow_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=type("Outputs", (), {"metadata": {}})(),
        ):
            result = build_base_cabinet_product_workflow(specification)

        self.assertEqual(result.diagnostics, tuple(violations))

    def test_no_direct_builder_imports(self):
        source = inspect.getsource(workflow_module)
        self.assertNotIn("CabinetBuilder", source)
        self.assertNotIn("ManufacturingRuntimePipelineBuilder", source)
        self.assertNotIn("ManufacturingCutlistBuilder", source)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(workflow_module)
        self.assertNotIn("FreeCAD", source)


if __name__ == "__main__":
    unittest.main()
