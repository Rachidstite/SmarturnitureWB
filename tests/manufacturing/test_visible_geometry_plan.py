import unittest
from pathlib import Path
from types import SimpleNamespace


class TestVisibleGeometryPlan(unittest.TestCase):

    def _projected_back_groove(self, node_id="CAB_SIDE_L"):
        from manufacturing.visible_geometry_plan import VisibleGeometryFeatureSpec

        return VisibleGeometryFeatureSpec(
            name=f"{node_id}_Back_Groove",
            kind="back_panel_groove",
            node_id=node_id,
            placement=(10.0, 577.0, 18.0),
            size=(8.0, 3.2, 684.0),
            label="Back panel groove",
        )

    def test_builds_manufacturing_geometry_from_existing_project_data(self):
        from domain.manufacturing_compiler import ManufacturingCompiler
        from domain.core_types import NodeRole
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
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
        drawer_face_role = type(
            "DrawerFaceRole",
            (),
            {
                "name": "DRAWER_FACE",
                "value": "DRAWER_FACE",
                "__hash__": object.__hash__,
            },
        )()
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
            joinery=SimpleNamespace(edges=[]),
            topology=SimpleNamespace(d=600.0),
            projected_visible_features=(self._projected_back_groove(),),
            graph=SimpleNamespace(
                _by_role={
                    NodeRole.SIDE_PANEL: [side_left, side_right],
                    drawer_face_role: [drawer_face],
                    NodeRole.DOOR_PANEL: [door],
                },
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
        self.assertNotIn(
            "hinge_cup_hole",
            [feature.kind for feature in build_visible_geometry_plan(project).features],
        )
        self.assertNotIn(
            "hinge_plate_position",
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
        context = RuleContext()
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)
        plan = build_visible_geometry_plan(project)

        kinds = [feature.kind for feature in plan.features]
        self.assertIn("back_panel_groove", kinds)
        self.assertIn("confirmat_hole", kinds)
        self.assertIn("hinge_cup_hole", kinds)
        self.assertIn("shelf_pin_hole", kinds)
        self.assertIn("drawer_slide_line", kinds)
        self.assertIn("wall_mount_prototype", kinds)

        hinge_cups = [feature for feature in plan.features if feature.kind == "hinge_cup_hole"]
        self.assertTrue(hinge_cups)
        self.assertTrue(all(feature.prototype is False for feature in hinge_cups))

        shelf_pins = [feature for feature in plan.features if feature.kind == "shelf_pin_hole"]
        self.assertTrue(any("Shelf pin" in feature.label for feature in shelf_pins))

        self.assertTrue(plan.prototype_lines)

    def test_projected_visible_features_are_included_without_recreating_grooves(self):
        from manufacturing.visible_geometry_plan import build_visible_geometry_plan

        side_left = SimpleNamespace(
            identity=SimpleNamespace(key="CAB_SIDE_L"),
            role=SimpleNamespace(value="SIDE_PANEL"),
            category=SimpleNamespace(value="PHYSICAL"),
            width=18.0,
            height=720.0,
            depth=580.0,
            thickness=18.0,
            transform=SimpleNamespace(x=0.0, y=0.0, z=0.0),
            machining_ops=[],
        )
        project = SimpleNamespace(
            uid="CAB",
            topology=SimpleNamespace(d=580.0),
            projected_visible_features=(self._projected_back_groove(),),
            graph=SimpleNamespace(all_nodes=lambda: [side_left]),
        )

        plan = build_visible_geometry_plan(project)
        groove_features = [
            feature for feature in plan.features if feature.kind == "back_panel_groove"
        ]

        self.assertEqual(len(groove_features), 1)
        self.assertEqual(groove_features[0].node_id, "CAB_SIDE_L")
        self.assertEqual(groove_features[0].size, (8.0, 3.2, 684.0))

    def test_visible_geometry_plan_source_contains_no_hardcoded_back_panel_groove_dimensions(self):
        source = Path("manufacturing/visible_geometry_plan.py").read_text(encoding="utf-8")

        self.assertNotIn("groove_depth = 4.0", source)
        self.assertNotIn("groove_thickness = 2.0", source)
        self.assertNotIn("_back_panel_groove_features", source)

    def test_confirmat_holes_require_compiled_machining_evidence_and_cover_carcass_panels(self):
        from domain.builders import WardrobeBuilder
        from domain.core_types import JoineryType, NodeRole
        from domain.manufacturing_compiler import ManufacturingCompiler
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from manufacturing.visible_geometry_plan import build_visible_geometry_plan

        builder = WardrobeBuilder(
            uid="CONFIRMAT_COVERAGE",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )
        builder.add_divider(x_offset=400.0)
        project = builder.build()
        project.graph.project = project

        bare_plan = build_visible_geometry_plan(project)
        self.assertEqual(
            [feature for feature in bare_plan.features if feature.kind == "confirmat_hole"],
            [],
        )

        context = RuleContext(preferred_connector=JoineryType.CONFIRMAT_50)
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        plan = build_visible_geometry_plan(project)
        confirmat_features = [
            feature for feature in plan.features if feature.kind == "confirmat_hole"
        ]

        self.assertTrue(confirmat_features)
        self.assertTrue(all(feature.prototype is False for feature in confirmat_features))

        confirmat_node_ids = {
            node.identity.key
            for node in project.graph.all_nodes()
            if any(
                str(getattr(op, "metadata", {}).get("hardware_intent", "")).upper()
                == "INTENT_CONFIRMAT_50"
                for op in getattr(node, "machining_ops", []) or []
            )
        }
        self.assertTrue(confirmat_node_ids)
        self.assertTrue(confirmat_node_ids.issubset({feature.node_id for feature in confirmat_features}))
        self.assertTrue(any("Confirmat" in feature.label for feature in confirmat_features))

    def test_edge_banding_features_require_manufacturing_edge_evidence(self):
        from manufacturing.manufacturing_edge_report import ManufacturingEdgeReport
        from manufacturing.visible_geometry_plan import build_visible_geometry_plan

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

        project_without_evidence = SimpleNamespace(
            uid="CAB_EDGE",
            topology=SimpleNamespace(d=600.0),
            graph=SimpleNamespace(
                all_nodes=lambda: [door],
                get_node=lambda key: {"CAB_DOOR_L": door}[key],
            ),
            placements=[],
        )
        bare_plan = build_visible_geometry_plan(project_without_evidence)
        self.assertEqual(
            [feature for feature in bare_plan.features if feature.kind == "edge_banding_strip"],
            [],
        )

        project_with_evidence = SimpleNamespace(
            uid="CAB_EDGE",
            topology=SimpleNamespace(d=600.0),
            graph=SimpleNamespace(
                all_nodes=lambda: [door],
                get_node=lambda key: {"CAB_DOOR_L": door}[key],
            ),
            placements=[],
            manufacturing_production_package=SimpleNamespace(
                edge_report=ManufacturingEdgeReport(
                    items=[
                        {
                            "panel_identity": "CAB_DOOR_L",
                            "edge": "TOP",
                            "banding": "ABS_1MM",
                            "linear_meters": 0.58,
                        }
                    ]
                )
            ),
        )
        plan = build_visible_geometry_plan(project_with_evidence)
        edge_features = [
            feature for feature in plan.features if feature.kind == "edge_banding_strip"
        ]
        self.assertTrue(edge_features)
        self.assertTrue(all(feature.prototype is False for feature in edge_features))
        self.assertTrue(any("ABS_1MM" in feature.label for feature in edge_features))

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

    def test_minifix_holes_require_compiled_machining_evidence_and_cover_carcass_panels(self):
        from domain.builders import WardrobeBuilder
        from domain.core_types import JoineryType
        from domain.manufacturing_compiler import ManufacturingCompiler
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from manufacturing.visible_geometry_plan import build_visible_geometry_plan

        project = WardrobeBuilder(
            uid="MINIFIX_COVERAGE",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        ).build()
        project.graph.project = project

        bare_plan = build_visible_geometry_plan(project)
        self.assertEqual(
            [feature for feature in bare_plan.features if feature.kind == "minifix_hole"],
            [],
        )

        context = RuleContext(preferred_connector=JoineryType.MINIFIX_15)
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        plan = build_visible_geometry_plan(project)
        minifix_features = [
            feature for feature in plan.features if feature.kind == "minifix_hole"
        ]

        self.assertTrue(minifix_features)
        self.assertTrue(all(feature.prototype is False for feature in minifix_features))
        self.assertTrue(
            {
                "MINIFIX_COVERAGE_SIDE_L",
                "MINIFIX_COVERAGE_SIDE_R",
                "MINIFIX_COVERAGE_TOP",
                "MINIFIX_COVERAGE_BOTTOM",
            }.issubset({feature.node_id for feature in minifix_features})
        )
        self.assertTrue(any("Minifix" in feature.label for feature in minifix_features))


if __name__ == "__main__":
    unittest.main()
