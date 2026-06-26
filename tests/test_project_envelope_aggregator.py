import importlib
import inspect
import re
import unittest
from unittest.mock import patch

from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_envelope_aggregator import (
    aggregate_project_envelope_from_bounds,
)
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


class TestProjectEnvelopeAggregator(unittest.TestCase):
    def test_aggregates_one_bounds_measurement(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-1",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )

        envelope = aggregate_project_envelope_from_bounds([bounds])

        self.assertIsInstance(envelope, ProjectEnvelope)
        self.assertEqual((envelope.x_min, envelope.y_min, envelope.z_min), (1.0, 2.0, 3.0))
        self.assertEqual((envelope.x_max, envelope.y_max, envelope.z_max), (4.0, 5.0, 6.0))

    def test_aggregates_multiple_bounds_measurements(self):
        bounds_measurements = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-2",
                x_min=10.0,
                y_min=20.0,
                z_min=30.0,
                x_max=40.0,
                y_max=50.0,
                z_max=60.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-3",
                x_min=5.0,
                y_min=15.0,
                z_min=25.0,
                x_max=45.0,
                y_max=55.0,
                z_max=65.0,
            ),
        ]

        envelope = aggregate_project_envelope_from_bounds(bounds_measurements)

        self.assertEqual((envelope.x_min, envelope.y_min, envelope.z_min), (5.0, 15.0, 25.0))
        self.assertEqual((envelope.x_max, envelope.y_max, envelope.z_max), (45.0, 55.0, 65.0))

    def test_negative_coordinates_work(self):
        bounds_measurements = [
            SceneNodeBoundsMeasurement(
                node_id="NODE-4",
                x_min=-10.0,
                y_min=-20.0,
                z_min=-30.0,
                x_max=-5.0,
                y_max=-15.0,
                z_max=-25.0,
            ),
            SceneNodeBoundsMeasurement(
                node_id="NODE-5",
                x_min=-12.0,
                y_min=-18.0,
                z_min=-35.0,
                x_max=-3.0,
                y_max=-10.0,
                z_max=-20.0,
            ),
        ]

        envelope = aggregate_project_envelope_from_bounds(bounds_measurements)

        self.assertEqual((envelope.x_min, envelope.y_min, envelope.z_min), (-12.0, -20.0, -35.0))
        self.assertEqual((envelope.x_max, envelope.y_max, envelope.z_max), (-3.0, -10.0, -20.0))

    def test_empty_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            aggregate_project_envelope_from_bounds([])

    def test_final_source_is_project_envelope_builder(self):
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-6",
            x_min=0.0,
            y_min=0.0,
            z_min=0.0,
            x_max=1.0,
            y_max=1.0,
            z_max=1.0,
        )

        envelope = aggregate_project_envelope_from_bounds([bounds])

        self.assertEqual(envelope.source, "project-envelope-builder")

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_envelope_aggregator")
        source = inspect.getsource(module)

        self.assertIn("aggregate_project_envelope_from_bounds", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_envelope_aggregator")
        source = inspect.getsource(module)

        for token in (
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
            "collision",
            "footprint",
            "adjacency",
            "alignment",
            "installation",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_function_signature_remains_generic(self):
        signature = inspect.signature(aggregate_project_envelope_from_bounds)
        self.assertEqual(list(signature.parameters), ["bounds_measurements"])
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)

    def test_reuses_build_project_envelope_instead_of_manual_aggregation(self):
        module = importlib.import_module("project_engineering.project_envelope_aggregator")
        bounds = SceneNodeBoundsMeasurement(
            node_id="NODE-7",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
        )
        expected_envelope = ProjectEnvelope(
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
            source="project-envelope-builder",
        )

        with patch.object(
            module,
            "build_project_envelope_from_bounds",
            side_effect=lambda item: ProjectEnvelope(
                x_min=item.x_min,
                y_min=item.y_min,
                z_min=item.z_min,
                x_max=item.x_max,
                y_max=item.y_max,
                z_max=item.z_max,
                source="project-envelope-from-bounds",
            ),
        ) as from_bounds_mock, patch.object(
            module,
            "build_project_envelope",
            return_value=expected_envelope,
        ) as build_mock:
            result = module.aggregate_project_envelope_from_bounds([bounds])

        self.assertIs(result, expected_envelope)
        from_bounds_mock.assert_called_once_with(bounds)
        build_mock.assert_called_once()
        self.assertEqual(len(build_mock.call_args.args[0]), 1)

    def test_does_not_contain_manual_min_max_aggregation_logic(self):
        module = importlib.import_module("project_engineering.project_envelope_aggregator")
        source = inspect.getsource(module)

        for token in (
            "min(",
            "max(",
            "x_min=",
            "y_min=",
            "z_min=",
            "x_max=",
            "y_max=",
            "z_max=",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertNotRegex(source, re.compile(r"\bclass\s+"))


if __name__ == "__main__":
    unittest.main()
