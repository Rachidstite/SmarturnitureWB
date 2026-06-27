import unittest
from dataclasses import asdict, fields, is_dataclass

from domain.base_cabinet_scenario import BaseCabinetScenario
from domain.base_cabinet_specification import BaseCabinetSpecification


class TestBaseCabinetScenarioContract(unittest.TestCase):
    def test_default_specification_exists(self):
        scenario = BaseCabinetScenario()
        self.assertEqual(scenario.scenario_id, "base-cabinet-scenario-v1")
        self.assertEqual(scenario.scenario_name, "Base Cabinet Scenario")
        self.assertIsInstance(scenario.specification, BaseCabinetSpecification)
        self.assertEqual(scenario.specification, BaseCabinetSpecification())

    def test_dataclass_behavior(self):
        scenario = BaseCabinetScenario()
        self.assertTrue(is_dataclass(scenario))
        self.assertEqual(
            scenario,
            BaseCabinetScenario(),
        )
        self.assertEqual(
            [field.name for field in fields(BaseCabinetScenario)],
            ["scenario_id", "scenario_name", "specification"],
        )

    def test_immutability(self):
        scenario = BaseCabinetScenario()
        with self.assertRaises((AttributeError, TypeError)):
            scenario.scenario_name = "Changed"
        with self.assertRaises((AttributeError, TypeError)):
            scenario.specification = BaseCabinetSpecification(width_mm=700.0)

    def test_serialization_friendliness(self):
        scenario = BaseCabinetScenario()
        data = asdict(scenario)
        self.assertEqual(data["scenario_id"], "base-cabinet-scenario-v1")
        self.assertIn("specification", data)
        self.assertEqual(data["specification"]["door_count"], 2)
        self.assertEqual(data["specification"]["width_mm"], 600.0)

    def test_no_runtime_behavior(self):
        scenario = BaseCabinetScenario()
        self.assertFalse(hasattr(scenario, "run"))
        self.assertFalse(hasattr(scenario, "execute"))
        self.assertFalse(hasattr(scenario, "build"))


if __name__ == "__main__":
    unittest.main()
