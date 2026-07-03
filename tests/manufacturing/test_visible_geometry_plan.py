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
        drawer_face = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_DRAWER_F"),
            role=SimpleNamespace(value="DRAWER_FACE"),
            category=SimpleNamespace(value="PHYSICAL"),
            width=580.0,
            height=180.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=18.0, y=200.0, z=0.0),
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
            graph=SimpleNamespace(
                all_nodes=lambda: [side_left, side_right, drawer_face, back, door],
                get_node=lambda key: {
                    "CAB_SIDE_L": side_left,
                    "CAB_SIDE_R": side_right,
                    "CAB_DRAWER_F": drawer_face,
                    "CAB_BACK": back,
                    "CAB_DOOR_L": door,
                }[key],
            ),
            placements=[],
        )

        self.assertNotIn(
            "drawer_slide_line",
            [feature.kind for feature in build_visible_geometry_plan(project).features],
        )

        side_left.machining_ops.append(
            SimpleNamespace(
                op_type="DRILL",
                local_x=2.0,
                local_y=420.0,
                face="LEFT",
                metadata={"hardware_intent": "INTENT_DRAWER_SLIDE"},
            )
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
        self.assertTrue(all(feature.prototype is True for feature in hinge_cups))

        shelf_pins = [feature for feature in plan.features if feature.kind == "shelf_pin_hole"]
        self.assertTrue(any("Shelf pin" in feature.label for feature in shelf_pins))

        self.assertTrue(plan.prototype_lines)

    def test_shelf_pin_holes_require_production_backed_machining_evidence(self):
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
            machining_ops=[],
        )

        project = SimpleNamespace(
            uid="CAB",
            topology=SimpleNamespace(d=600.0),
            graph=SimpleNamespace(all_nodes=lambda: [side_left]),
            placements=[],
        )

        plan = build_visible_geometry_plan(project)

        shelf_pins = [
            feature for feature in plan.features if feature.kind == "shelf_pin_hole"
        ]

        self.assertEqual(shelf_pins, [])

    def test_drawer_slide_lines_require_compiled_machining_evidence(self):
        from types import SimpleNamespace
        from domain.core_types import NodeRole
        from domain.manufacturing_compiler import ManufacturingCompiler
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from manufacturing.visible_geometry_plan import build_visible_geometry_plan

        drawer_face_role = type(
            "DrawerFaceRole",
            (),
            {
                "name": "DRAWER_FACE",
                "value": "DRAWER_FACE",
                "__hash__": object.__hash__,
            },
        )()
        left_side_panel = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_SIDE_L"),
            role=NodeRole.SIDE_PANEL,
            category=SimpleNamespace(value="PHYSICAL"),
            width=600.0,
            height=1982.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=0.0, y=0.0, z=0.0),
            machining_ops=[],
        )
        right_side_panel = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_SIDE_R"),
            role=NodeRole.SIDE_PANEL,
            category=SimpleNamespace(value="PHYSICAL"),
            width=600.0,
            height=1982.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=1182.0, y=0.0, z=0.0),
            machining_ops=[],
        )
        drawer_face = SimpleNamespace(
            identity=SimpleNamespace(key="DRAWER_FACE_1"),
            role=drawer_face_role,
            category=SimpleNamespace(value="PHYSICAL"),
            width=580.0,
            height=180.0,
            depth=18.0,
            thickness=18.0,
            transform=SimpleNamespace(x=0.0, y=0.0, z=0.0),
            machining_ops=[],
        )
        graph = SimpleNamespace(
            _by_role={
                drawer_face_role: [drawer_face],
                NodeRole.SIDE_PANEL: [left_side_panel, right_side_panel],
            },
            all_nodes=lambda: [left_side_panel, right_side_panel, drawer_face],
            get_node=lambda key: {
                "CAB_SIDE_L": left_side_panel,
                "CAB_SIDE_R": right_side_panel,
                "DRAWER_FACE_1": drawer_face,
            }[key],
        )

        project = SimpleNamespace(
            graph=graph,
            joinery=SimpleNamespace(edges=[]),
            topology=SimpleNamespace(d=600.0),
            placements=[],
        )
        context = RuleContext()

        plan = build_visible_geometry_plan(project)
        self.assertFalse(any(feature.kind == "drawer_slide_line" for feature in plan.features))

        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        plan = build_visible_geometry_plan(project)
        slide_features = [
            feature for feature in plan.features if feature.kind == "drawer_slide_line"
        ]

        self.assertTrue(slide_features)
        self.assertTrue(
            all(feature.prototype is False for feature in slide_features)
        )


if __name__ == "__main__":
    unittest.main()
