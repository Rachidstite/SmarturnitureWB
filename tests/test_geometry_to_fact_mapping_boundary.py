import importlib
import inspect
import re
import unittest


class TestGeometryToFactMappingBoundary(unittest.TestCase):
    def test_available_clearance_extractor_has_no_banned_dependencies(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact_extractor"
        )
        source = inspect.getsource(module)

        self.assertIn(
            "from project_engineering.available_operational_clearance_fact import",
            source,
        )

        for token in (
            "project_geometry",
            "ProjectGeometry",
            "scene_graph",
            "SceneGraph",
            "FreeCAD",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "operational_clearance_distance_rule",
            "operational_clearance_facts_rule",
            "operational_rule_result",
            "operational_decision_report",
            "operational_decision_from_rule_results",
            "cabinet_operational_readiness_report",
            "project_operational_readiness_report",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_available_clearance_extractor_signature_stays_generic(self):
        module = importlib.import_module(
            "project_engineering.available_operational_clearance_fact_extractor"
        )
        signature = inspect.signature(module.extract_available_operational_clearance_fact)

        self.assertEqual(
            list(signature.parameters),
            ["component_id", "available_clearance_mm", "direction", "source"],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
