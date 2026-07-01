import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestVisualCapabilityContract(unittest.TestCase):
    def test_dataclass_contract_is_stable(self):
        from scene_graph.visual_capability import VisualCapability

        self.assertTrue(is_dataclass(VisualCapability))
        self.assertEqual(
            [field.name for field in fields(VisualCapability)],
            [
                "supports_edge_visualization",
                "supports_drill_visualization",
                "supports_groove_visualization",
                "supports_hardware_visualization",
                "supports_material_visualization",
                "supports_dimension_visualization",
            ],
        )

    def test_safe_defaults(self):
        from scene_graph.visual_capability import VisualCapability

        capability = VisualCapability()

        self.assertFalse(capability.supports_edge_visualization)
        self.assertFalse(capability.supports_drill_visualization)
        self.assertFalse(capability.supports_groove_visualization)
        self.assertFalse(capability.supports_hardware_visualization)
        self.assertFalse(capability.supports_material_visualization)
        self.assertFalse(capability.supports_dimension_visualization)

    def test_independent_default_instances(self):
        from scene_graph.visual_capability import VisualCapability

        first = VisualCapability()
        second = VisualCapability()

        self.assertIsNot(first, second)
        self.assertEqual(first, second)

    def test_no_renderer_dependency(self):
        import scene_graph.visual_capability as module

        source = inspect.getsource(module)

        self.assertNotIn("SceneRenderer", source)
        self.assertNotIn("renderer", source.lower())

    def test_no_manufacturing_dependency(self):
        import scene_graph.visual_capability as module

        source = inspect.getsource(module)

        self.assertNotIn("manufacturing", source.lower())
        self.assertNotIn("CNCReport", source)
        self.assertNotIn("HardwareBom", source)

    def test_no_geometry_dependency(self):
        import scene_graph.visual_capability as module

        source = inspect.getsource(module)

        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraphBuilder", source)
        self.assertNotIn("FreeCAD", source)


if __name__ == "__main__":
    unittest.main()
