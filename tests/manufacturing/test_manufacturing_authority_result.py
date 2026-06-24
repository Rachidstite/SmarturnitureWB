import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingAuthorityResult(unittest.TestCase):

    def test_dataclass_exists(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        self.assertTrue(is_dataclass(ManufacturingAuthorityResult))

    def test_exact_field_order(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingAuthorityResult)],
            [
                "engineering_component_inventory",
                "manufacturing_model_inventory_counts",
                "manufacturing_model_report",
                "manufacturing_runtime_result",
                "manufacturing_factory_intelligence_result",
                "manufacturing_executive_report",
                "factory_governance_authority_report",
            ],
        )

    def test_defaults_are_none(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        result = ManufacturingAuthorityResult()

        self.assertIsNone(result.engineering_component_inventory)
        self.assertIsNone(result.manufacturing_model_inventory_counts)
        self.assertIsNone(result.manufacturing_model_report)
        self.assertIsNone(result.manufacturing_runtime_result)
        self.assertIsNone(result.manufacturing_factory_intelligence_result)
        self.assertIsNone(result.manufacturing_executive_report)
        self.assertIsNone(result.factory_governance_authority_report)

    def test_accepts_all_approved_references(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        engineering_component_inventory = object()
        manufacturing_model_inventory_counts = object()
        manufacturing_model_report = object()
        manufacturing_runtime_result = object()
        manufacturing_factory_intelligence_result = object()
        manufacturing_executive_report = object()
        factory_governance_authority_report = object()

        result = ManufacturingAuthorityResult(
            engineering_component_inventory=engineering_component_inventory,
            manufacturing_model_inventory_counts=manufacturing_model_inventory_counts,
            manufacturing_model_report=manufacturing_model_report,
            manufacturing_runtime_result=manufacturing_runtime_result,
            manufacturing_factory_intelligence_result=manufacturing_factory_intelligence_result,
            manufacturing_executive_report=manufacturing_executive_report,
            factory_governance_authority_report=factory_governance_authority_report,
        )

        self.assertIs(result.engineering_component_inventory, engineering_component_inventory)
        self.assertIs(result.manufacturing_model_inventory_counts, manufacturing_model_inventory_counts)
        self.assertIs(result.manufacturing_model_report, manufacturing_model_report)
        self.assertIs(result.manufacturing_runtime_result, manufacturing_runtime_result)
        self.assertIs(result.manufacturing_factory_intelligence_result, manufacturing_factory_intelligence_result)
        self.assertIs(result.manufacturing_executive_report, manufacturing_executive_report)
        self.assertIs(result.factory_governance_authority_report, factory_governance_authority_report)

    def test_preserves_object_identity(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        engineering_component_inventory = {"inventory": ["A"]}
        manufacturing_model_inventory_counts = {"counts": [1, 2]}
        manufacturing_model_report = {"status": "READY"}
        manufacturing_runtime_result = {"runtime": True}
        manufacturing_factory_intelligence_result = {"factory": True}
        manufacturing_executive_report = {"executive": True}
        factory_governance_authority_report = {"authority": True}

        result = ManufacturingAuthorityResult(
            engineering_component_inventory=engineering_component_inventory,
            manufacturing_model_inventory_counts=manufacturing_model_inventory_counts,
            manufacturing_model_report=manufacturing_model_report,
            manufacturing_runtime_result=manufacturing_runtime_result,
            manufacturing_factory_intelligence_result=manufacturing_factory_intelligence_result,
            manufacturing_executive_report=manufacturing_executive_report,
            factory_governance_authority_report=factory_governance_authority_report,
        )

        self.assertIs(result.engineering_component_inventory, engineering_component_inventory)
        self.assertIs(result.manufacturing_model_inventory_counts, manufacturing_model_inventory_counts)
        self.assertIs(result.manufacturing_model_report, manufacturing_model_report)
        self.assertIs(result.manufacturing_runtime_result, manufacturing_runtime_result)
        self.assertIs(result.manufacturing_factory_intelligence_result, manufacturing_factory_intelligence_result)
        self.assertIs(result.manufacturing_executive_report, manufacturing_executive_report)
        self.assertIs(result.factory_governance_authority_report, factory_governance_authority_report)
        self.assertEqual(engineering_component_inventory, {"inventory": ["A"]})
        self.assertEqual(manufacturing_model_inventory_counts, {"counts": [1, 2]})
        self.assertEqual(manufacturing_model_report, {"status": "READY"})
        self.assertEqual(manufacturing_runtime_result, {"runtime": True})
        self.assertEqual(manufacturing_factory_intelligence_result, {"factory": True})
        self.assertEqual(manufacturing_executive_report, {"executive": True})
        self.assertEqual(factory_governance_authority_report, {"authority": True})

    def test_does_not_mutate_embedded_objects(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        engineering_component_inventory = {"inventory": ["A"]}
        manufacturing_model_inventory_counts = {"counts": [1, 2]}
        manufacturing_model_report = {"status": "READY"}
        manufacturing_runtime_result = {"runtime": True}
        manufacturing_factory_intelligence_result = {"factory": True}
        manufacturing_executive_report = {"executive": True}
        factory_governance_authority_report = {"authority": True}

        snapshot = {
            "engineering_component_inventory": dict(engineering_component_inventory),
            "manufacturing_model_inventory_counts": dict(manufacturing_model_inventory_counts),
            "manufacturing_model_report": dict(manufacturing_model_report),
            "manufacturing_runtime_result": dict(manufacturing_runtime_result),
            "manufacturing_factory_intelligence_result": dict(manufacturing_factory_intelligence_result),
            "manufacturing_executive_report": dict(manufacturing_executive_report),
            "factory_governance_authority_report": dict(factory_governance_authority_report),
        }

        ManufacturingAuthorityResult(
            engineering_component_inventory=engineering_component_inventory,
            manufacturing_model_inventory_counts=manufacturing_model_inventory_counts,
            manufacturing_model_report=manufacturing_model_report,
            manufacturing_runtime_result=manufacturing_runtime_result,
            manufacturing_factory_intelligence_result=manufacturing_factory_intelligence_result,
            manufacturing_executive_report=manufacturing_executive_report,
            factory_governance_authority_report=factory_governance_authority_report,
        )

        self.assertEqual(engineering_component_inventory, snapshot["engineering_component_inventory"])
        self.assertEqual(manufacturing_model_inventory_counts, snapshot["manufacturing_model_inventory_counts"])
        self.assertEqual(manufacturing_model_report, snapshot["manufacturing_model_report"])
        self.assertEqual(manufacturing_runtime_result, snapshot["manufacturing_runtime_result"])
        self.assertEqual(manufacturing_factory_intelligence_result, snapshot["manufacturing_factory_intelligence_result"])
        self.assertEqual(manufacturing_executive_report, snapshot["manufacturing_executive_report"])
        self.assertEqual(factory_governance_authority_report, snapshot["factory_governance_authority_report"])

    def test_has_no_behavior_beyond_being_a_container(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        result = ManufacturingAuthorityResult()

        self.assertTrue(is_dataclass(result))
        self.assertEqual(result.__dict__, {
            "engineering_component_inventory": None,
            "manufacturing_model_inventory_counts": None,
            "manufacturing_model_report": None,
            "manufacturing_runtime_result": None,
            "manufacturing_factory_intelligence_result": None,
            "manufacturing_executive_report": None,
            "factory_governance_authority_report": None,
        })
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "build"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "calculate"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "compute"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "manufacture"))

    def test_does_not_include_excluded_fields(self):
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        field_names = {field.name for field in fields(ManufacturingAuthorityResult)}

        self.assertNotIn("manufacturing_model_executive_result", field_names)
        self.assertNotIn("manufacturing_project_intelligence_result", field_names)
        self.assertNotIn("manufacturing_production_package", field_names)
        self.assertNotIn("drawer_assembly", field_names)
        self.assertNotIn("manufacturing_executive_report_mirror", field_names)
        self.assertNotIn("manufacturing_model_report_mirror", field_names)


if __name__ == "__main__":
    unittest.main()
