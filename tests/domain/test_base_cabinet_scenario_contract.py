import unittest
from dataclasses import asdict, is_dataclass

from domain.base_cabinet_scenario import BaseCabinetScenario


class TestBaseCabinetScenarioContract(unittest.TestCase):
    def test_default_values(self):
        scenario = BaseCabinetScenario()
        self.assertEqual(scenario.scenario_id, "base-cabinet-scenario-v1")
        self.assertEqual(scenario.scenario_name, "Base Cabinet Scenario")
        self.assertEqual(scenario.cabinet_type, "Base Cabinet")
        self.assertEqual(scenario.door_count, 2)
        self.assertEqual(scenario.shelf_count, 1)
        self.assertTrue(scenario.has_back_panel)
        self.assertTrue(scenario.edge_banding_required)
        self.assertTrue(scenario.manufacturing_validation_required)
        self.assertTrue(scenario.engineering_validation_required)
        self.assertTrue(scenario.quotation_required)

    def test_dataclass_behavior(self):
        scenario = BaseCabinetScenario()
        self.assertTrue(is_dataclass(scenario))
        self.assertEqual(
            scenario,
            BaseCabinetScenario(),
        )

    def test_immutability(self):
        scenario = BaseCabinetScenario()
        with self.assertRaises((AttributeError, TypeError)):
            scenario.door_count = 3

    def test_serialization_friendliness(self):
        scenario = BaseCabinetScenario()
        data = asdict(scenario)
        self.assertEqual(data["scenario_id"], "base-cabinet-scenario-v1")
        self.assertEqual(data["door_count"], 2)
        self.assertIn("quotation_required", data)

    def test_no_runtime_behavior(self):
        scenario = BaseCabinetScenario()
        self.assertFalse(hasattr(scenario, "run"))
        self.assertFalse(hasattr(scenario, "execute"))
        self.assertFalse(hasattr(scenario, "build"))


if __name__ == "__main__":
    unittest.main()
