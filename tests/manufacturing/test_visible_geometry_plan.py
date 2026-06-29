import unittest
from types import SimpleNamespace


class TestVisibleGeometryPlan(unittest.TestCase):

    def test_builds_manufacturing_geometry_from_existing_project_data(self):
        from manufacturing.visible_geometry_plan import build_visible_geometry_plan

        side_left = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_SIDE_L"),
            role=SimpleNamespace(value="SIDE_PANEL"),
            category=SimpleNamespace(value="PHYSICAL"),
            width=600.0,
            height=2400.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=0.0, y=0.0, z=0.0),
            machining_ops=[
                SimpleNamespace(
                    op_type="DRILL",
                    local_x=2.0,
                    local_y=64.0,
                    face="LEFT",
                    metadata={"hardware_intent": "INTENT_SHELF_PIN"},
                ),
                SimpleNamespace(
                    op_type="DRILL",
                    local_x=2.0,
                    local_y=128.0,
                    face="LEFT",
                    metadata={"hardware_intent": "INTENT_CONFIRMAT_50"},
                ),
            ],
        )
        side_right = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_SIDE_R"),
            role=SimpleNamespace(value="SIDE_PANEL"),
            category=SimpleNamespace(value="PHYSICAL"),
            width=600.0,
            height=2400.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=1182.0, y=0.0, z=0.0),
            machining_ops=[],
        )
        back = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_BACK"),
            role=SimpleNamespace(value="BACK_PANEL"),
            category=SimpleNamespace(value="PHYSICAL"),
            width=1200.0,
            height=2382.0,
            depth=3.0,
            thickness=3.0,
            transform=SimpleNamespace(x=18.0, y=15.0, z=18.0),
            machining_ops=[
                SimpleNamespace(
                    op_type="GROOVE",
                    local_x=4.0,
                    local_y=0.0,
                    face="BACK",
                    metadata={},
                )
            ],
        )
        door = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_DOOR_L"),
            role=SimpleNamespace(value="DOOR_PANEL"),
            category=SimpleNamespace(value="PHYSICAL"),
            width=580.0,
            height=2300.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=18.0, y=600.0, z=0.0),
            machining_ops=[],
        )

        project = SimpleNamespace(
            uid="CAB",
            topology=SimpleNamespace(d=600.0),
            graph=SimpleNamespace(all_nodes=lambda: [side_left, side_right, back, door]),
            placements=[
                SimpleNamespace(
                    host_node_id="CAB_DOOR_L",
                    target_node_id="CAB_DOOR_L",
                    hardware_intent="INTENT_HINGE",
                    anchor=SimpleNamespace(offset_x=22.5, offset_y=100.0, face="BACK"),
                ),
                SimpleNamespace(
                    host_node_id="CAB_SIDE_L",
                    target_node_id="CAB_DOOR_L",
                    hardware_intent="INTENT_DRAWER_SLIDE",
                    anchor=SimpleNamespace(offset_x=0.0, offset_y=420.0, face="LEFT"),
                ),
            ],
        )

        plan = build_visible_geometry_plan(project)

        kinds = [feature.kind for feature in plan.features]
        self.assertIn("back_panel_groove", kinds)
        self.assertIn("hinge_cup_hole", kinds)
        self.assertIn("hinge_plate_position", kinds)
        self.assertIn("shelf_pin_hole", kinds)
        self.assertIn("drilling_indicator", kinds)
        self.assertIn("drawer_slide_line", kinds)
        self.assertIn("wall_mount_prototype", kinds)

        hinge_cups = [feature for feature in plan.features if feature.kind == "hinge_cup_hole"]
        self.assertTrue(any(feature.prototype is False for feature in hinge_cups))

        shelf_pins = [feature for feature in plan.features if feature.kind == "shelf_pin_hole"]
        self.assertTrue(any("Shelf pin" in feature.label for feature in shelf_pins))

        self.assertTrue(plan.prototype_lines)


if __name__ == "__main__":
    unittest.main()
