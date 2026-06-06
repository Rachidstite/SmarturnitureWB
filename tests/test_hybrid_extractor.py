import unittest
from types import SimpleNamespace

from domain.core_types import MachiningOperation
from manufacturing.hybrid_extractor import HybridManufacturingExtractor


class TestHybridManufacturingExtractor(unittest.TestCase):

    def test_modern_operations_do_not_fan_out_to_unrelated_panels(self):
        panel_a = SimpleNamespace(
            identity=SimpleNamespace(key="PANEL_A"),
            role="SIDE_PANEL",
            width=100,
            height=200,
            thickness=18,
            material="MDF",
            machining_ops=[
                MachiningOperation(
                    op_type="DRILL",
                    diameter=5,
                    depth=12,
                    face="TOP",
                    local_x=10,
                    local_y=20,
                )
            ],
        )

        panel_b = SimpleNamespace(
            identity=SimpleNamespace(key="PANEL_B"),
            role="SHELF",
            width=100,
            height=200,
            thickness=18,
            material="MDF",
            machining_ops=[],
        )

        scene_graph = SimpleNamespace(
            physical_nodes=[panel_a, panel_b],
            all_nodes=lambda: [panel_a, panel_b],
            get_node=lambda key: {
                "PANEL_A": panel_a,
                "PANEL_B": panel_b,
            }.get(key),
        )

        specs = HybridManufacturingExtractor.extract(scene_graph)
        specs_by_identity = {
            spec.identity: spec
            for spec in specs
        }

        self.assertEqual(
            len(specs_by_identity["PANEL_A"].unified_operations),
            1
        )
        self.assertEqual(
            len(specs_by_identity["PANEL_B"].unified_operations),
            0
        )


if __name__ == "__main__":
    unittest.main()
