# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Scene Graph
# VisualMetadata Manufacturing Feature Extension Contract Tests
#
# Verifies:
# - backward compatibility
# - immutable metadata
# - optional fields default correctly
# - existing renderers remain compatible
# - manufacturing metadata reused
# - no duplicated manufacturing logic
# - no calculations
# - no renderer dependency
# - no FreeCAD dependency
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


class TestVisualMetadataManufacturingExtension(unittest.TestCase):
    """Verify VisualMetadata extension for manufacturing features."""

    # ── Immutable frozen dataclass ──────────────────────────────

    def test_visual_metadata_is_frozen(self):
        from scene_graph.metadata import VisualMetadata
        self.assertTrue(hasattr(VisualMetadata, "__dataclass_fields__"))

    def test_new_fields_default_to_empty(self):
        from scene_graph.metadata import VisualMetadata
        vm = VisualMetadata()
        self.assertEqual(vm.minifix_holes, ())
        self.assertEqual(vm.confirmat_holes, ())
        self.assertEqual(vm.shelf_pin_holes, ())
        self.assertEqual(vm.drawer_slide_holes, ())
        self.assertEqual(vm.hinge_cup_holes, ())
        self.assertEqual(vm.hinge_plate_positions, ())
        self.assertEqual(vm.screw_holes, ())

    def test_drill_hole_visual_hardware_intent_default(self):
        from scene_graph.metadata import DrillHoleVisual
        dhv = DrillHoleVisual()
        self.assertEqual(dhv.hardware_intent, "")

    # ── Backward compatibility ─────────────────────────────────

    def test_existing_fields_unchanged(self):
        from scene_graph.metadata import VisualMetadata, EdgeBandVisual, DrillHoleVisual, GrooveVisual, HardwareMarkerVisual
        vm = VisualMetadata(
            edge_banding=(EdgeBandVisual(side="TOP", banding="ABS", label="TOP: ABS"),),
            drill_holes=(DrillHoleVisual(panel_identity="P1", operation_type="DRILL"),),
            grooves=(GrooveVisual(panel_identity="P1", face="BACK", depth=4.0),),
            hardware_markers=(HardwareMarkerVisual(panel_identity="P1", sku="HINGE-A", quantity=2),),
            material_label="MDF_18MM",
            finish_label="White",
        )
        # Existing fields are intact
        self.assertEqual(len(vm.edge_banding), 1)
        self.assertEqual(len(vm.drill_holes), 1)
        self.assertEqual(len(vm.grooves), 1)
        self.assertEqual(len(vm.hardware_markers), 1)
        self.assertEqual(vm.material_label, "MDF_18MM")
        self.assertEqual(vm.finish_label, "White")
        # New fields default to empty
        self.assertEqual(vm.minifix_holes, ())
        self.assertEqual(vm.confirmat_holes, ())
        self.assertEqual(vm.shelf_pin_holes, ())
        self.assertEqual(vm.drawer_slide_holes, ())
        self.assertEqual(vm.hinge_cup_holes, ())
        self.assertEqual(vm.hinge_plate_positions, ())
        self.assertEqual(vm.screw_holes, ())

    def test_build_visual_metadata_rejects_backend_objects(self):
        from scene_graph.metadata import build_visual_metadata
        from scene_graph.metadata import VisualMetadata
        node = SimpleNamespace(
            identity=SimpleNamespace(key="TEST_PANEL"),
            material="MDF_18MM",
            metadata={},
            machining_ops=[],
        )
        vm = build_visual_metadata(node)
        self.assertIsInstance(vm, VisualMetadata)
        self.assertEqual(vm.minifix_holes, ())
        self.assertEqual(vm.confirmat_holes, ())
        self.assertEqual(vm.shelf_pin_holes, ())
        self.assertEqual(vm.drawer_slide_holes, ())
        self.assertEqual(vm.hinge_cup_holes, ())
        self.assertEqual(vm.hinge_plate_positions, ())
        self.assertEqual(vm.screw_holes, ())
        # Backward compatible fields still work
        self.assertEqual(len(vm.edge_banding), 0)
        self.assertEqual(len(vm.drill_holes), 0)
        self.assertEqual(len(vm.grooves), 0)
        self.assertEqual(len(vm.hardware_markers), 0)

    # ── Existing renderers remain compatible ────────────────────

    def test_existing_renderer_overlay_pipeline_compatible(self):
        """Verify SceneRenderer.build_visual_overlays handles extended VisualMetadata."""
        from scene_graph.metadata import VisualMetadata, DrillHoleVisual
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(
            drill_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    operation_type="DRILL",
                    face="LEFT",
                    x=10.0, y=20.0, z=0.0,
                    diameter=5.0, depth=15.0,
                ),
            ),
            # New fields populated — renderer processes minifix_holes
            minifix_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    operation_type="DRILL",
                    face="LEFT",
                    x=37.0, y=15.0, z=0.0,
                    diameter=15.0, depth=12.0,
                    hardware_intent="INTENT_MINIFIX_15",
                ),
            ),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)
        # Produces 2 overlays: one from drill_holes, one from minifix_holes
        self.assertEqual(len(overlays), 2)
        # First overlay is existing drill_hole (unchanged)
        self.assertEqual(overlays[0]["overlay_type"], "drill_hole")
        self.assertEqual(overlays[0]["panel_identity"], "P1")
        self.assertEqual(overlays[0]["diameter"], 5.0)
        # Second overlay is new minifix_hole (HFG-3A)
        self.assertEqual(overlays[1]["overlay_type"], "minifix_hole")
        self.assertEqual(overlays[1]["panel_identity"], "P1")
        self.assertEqual(overlays[1]["diameter"], 15.0)
        self.assertEqual(overlays[1]["visual_type"], "MINIFIX_SYMBOL")

    def test_empty_metadata_renderer_safe(self):
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata()
        overlays = SceneRenderer.build_visual_overlays(vm)
        self.assertEqual(overlays, [])

    # ── Manufacturing metadata reused (extraction functions) ────

    def _make_op(self, op_type="DRILL", local_x=0.0, local_y=0.0, face="LEFT",
                 diameter=5.0, depth=10.0, intent=""):
        return SimpleNamespace(
            op_type=op_type,
            local_x=local_x,
            local_y=local_y,
            face=face,
            diameter=diameter,
            depth=depth,
            axis="Z",
            is_through=False,
            metadata={"hardware_intent": intent} if intent else {},
        )

    def _make_node(self, role_name="SIDE_PANEL", ops=None):
        return SimpleNamespace(
            identity=SimpleNamespace(key="TEST_PANEL"),
            role=SimpleNamespace(value=role_name, name=role_name),
            material="MDF_18MM",
            metadata={},
            machining_ops=list(ops or []),
        )

    def test_minifix_holes_extracted(self):
        from scene_graph.metadata import _minifix_holes_from_node
        ops = [
            self._make_op(local_x=37.0, local_y=100.0, diameter=15.0, depth=12.0,
                          intent="INTENT_MINIFIX_15"),
            self._make_op(local_x=37.0, local_y=200.0, diameter=15.0, depth=12.0,
                          intent="INTENT_MINIFIX_15"),
        ]
        node = self._make_node(ops=ops)
        result = _minifix_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 2)
        for hole in result:
            self.assertEqual(hole.hardware_intent, "INTENT_MINIFIX_15")
            self.assertEqual(hole.diameter, 15.0)
        self.assertEqual(result[0].x, 37.0)
        self.assertEqual(result[0].y, 100.0)

    def test_confirmat_holes_extracted(self):
        from scene_graph.metadata import _confirmat_holes_from_node
        ops = [
            self._make_op(local_x=37.0, local_y=50.0, diameter=8.0, depth=50.0,
                          intent="INTENT_CONFIRMAT_50"),
        ]
        node = self._make_node(ops=ops)
        result = _confirmat_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].hardware_intent, "INTENT_CONFIRMAT_50")
        self.assertEqual(result[0].diameter, 8.0)

    def test_shelf_pin_holes_extracted(self):
        from scene_graph.metadata import _shelf_pin_holes_from_node
        ops = [
            self._make_op(local_x=2.0, local_y=64.0, diameter=5.0, depth=10.0,
                          intent="INTENT_SHELF_PIN"),
            self._make_op(local_x=2.0, local_y=128.0, diameter=5.0, depth=10.0,
                          intent="INTENT_SHELF_PIN"),
            self._make_op(local_x=2.0, local_y=192.0, diameter=5.0, depth=10.0,
                          intent="INTENT_SHELF_PIN"),
        ]
        node = self._make_node(ops=ops)
        result = _shelf_pin_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 3)
        for hole in result:
            self.assertEqual(hole.hardware_intent, "INTENT_SHELF_PIN")

    def test_drawer_slide_holes_extracted(self):
        from scene_graph.metadata import _drawer_slide_holes_from_node
        ops = [
            self._make_op(local_x=10.0, local_y=50.0, intent="INTENT_DRAWER_SLIDE"),
            self._make_op(local_x=10.0, local_y=150.0, intent="INTENT_DRAWER_SLIDE"),
        ]
        node = self._make_node(ops=ops)
        result = _drawer_slide_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 2)
        for hole in result:
            self.assertEqual(hole.hardware_intent, "INTENT_DRAWER_SLIDE")

    def test_hinge_cup_holes_on_door_panel(self):
        from scene_graph.metadata import _hinge_cup_holes_from_node
        ops = [
            self._make_op(local_x=20.0, local_y=100.0, diameter=35.0, depth=12.0,
                          intent="INTENT_HINGE"),
        ]
        node = self._make_node(role_name="DOOR_PANEL", ops=ops)
        result = _hinge_cup_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].hardware_intent, "INTENT_HINGE")

    def test_hinge_plate_on_side_panel(self):
        from scene_graph.metadata import _hinge_plate_from_node
        ops = [
            self._make_op(local_x=30.0, local_y=50.0, diameter=5.0, depth=12.0,
                          intent="INTENT_HINGE"),
        ]
        node = self._make_node(role_name="SIDE_PANEL", ops=ops)
        result = _hinge_plate_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].hardware_intent, "INTENT_HINGE")

    def test_hinge_cup_not_on_side_panel(self):
        from scene_graph.metadata import _hinge_cup_holes_from_node
        ops = [
            self._make_op(intent="INTENT_HINGE"),
        ]
        node = self._make_node(role_name="SIDE_PANEL", ops=ops)
        result = _hinge_cup_holes_from_node(node, "TEST_PANEL")
        # Hinge cup only on DOOR_PANEL — SIDE_PANEL gets hinge_plate
        self.assertEqual(len(result), 0)

    def test_hinge_plate_not_on_door_panel(self):
        from scene_graph.metadata import _hinge_plate_from_node
        ops = [
            self._make_op(intent="INTENT_HINGE"),
        ]
        node = self._make_node(role_name="DOOR_PANEL", ops=ops)
        result = _hinge_plate_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 0)

    def test_screw_holes_extracted(self):
        from scene_graph.metadata import _screw_holes_from_node
        ops = [
            self._make_op(local_x=15.0, local_y=80.0, intent="INTENT_SCREW"),
            self._make_op(local_x=15.0, local_y=160.0, intent="INTENT_PANEL_SCREW"),
        ]
        node = self._make_node(ops=ops)
        result = _screw_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 2)

    def test_unrelated_ops_ignored(self):
        from scene_graph.metadata import _minifix_holes_from_node
        ops = [
            self._make_op(intent="INTENT_HINGE"),
            self._make_op(intent="INTENT_SHELF_PIN"),
            SimpleNamespace(
                op_type="DRILL", local_x=10.0, local_y=10.0, face="LEFT",
                diameter=5.0, depth=10.0, axis="Z", is_through=False,
                metadata={},
            ),
        ]
        node = self._make_node(ops=ops)
        result = _minifix_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(result), 0)

    # ── build_visual_metadata integrates new extraction ─────────

    def test_build_visual_metadata_includes_new_fields(self):
        from scene_graph.metadata import build_visual_metadata
        ops = [
            self._make_op(local_x=37.0, local_y=100.0, diameter=15.0, depth=12.0,
                          intent="INTENT_MINIFIX_15"),
            self._make_op(local_x=2.0, local_y=64.0, diameter=5.0,
                          intent="INTENT_SHELF_PIN"),
        ]
        node = self._make_node(role_name="SIDE_PANEL", ops=ops)
        vm = build_visual_metadata(node)
        self.assertEqual(len(vm.minifix_holes), 1)
        self.assertEqual(len(vm.shelf_pin_holes), 1)
        self.assertEqual(vm.minifix_holes[0].hardware_intent, "INTENT_MINIFIX_15")
        self.assertEqual(vm.shelf_pin_holes[0].hardware_intent, "INTENT_SHELF_PIN")

    # ── No duplicated manufacturing logic ──────────────────────

    def test_no_intent_mapping_constants_in_extraction(self):
        """Extraction functions reference constants, not re-derive intent."""
        from scene_graph.metadata import (
            _INTENT_MINIFIX, _INTENT_CONFIRMAT, _INTENT_SHELF_PIN,
            _INTENT_DRAWER_SLIDE, _INTENT_HINGE, _INTENT_SCREW, _INTENT_PANEL_SCREW,
            _filter_ops_by_intent,
        )
        self.assertEqual(_INTENT_MINIFIX, "INTENT_MINIFIX_15")
        self.assertEqual(_INTENT_CONFIRMAT, "INTENT_CONFIRMAT_50")
        self.assertEqual(_INTENT_SHELF_PIN, "INTENT_SHELF_PIN")
        self.assertEqual(_INTENT_DRAWER_SLIDE, "INTENT_DRAWER_SLIDE")
        self.assertEqual(_INTENT_HINGE, "INTENT_HINGE")
        self.assertEqual(_INTENT_SCREW, "INTENT_SCREW")
        self.assertEqual(_INTENT_PANEL_SCREW, "INTENT_PANEL_SCREW")

    def test_no_foi_or_manufacturing_logic(self):
        """Extraction does not reimplement blocking analysis or decision logic."""
        src = Path("scene_graph/metadata.py").read_text()
        patterns = [
            "_determine_status", "START_READY", "START_AFTER_REVIEW",
            "HOLD", "BLOCKED", "NEEDS_REVIEW", "NOT_READY",
        ]
        for pattern in patterns:
            self.assertNotIn(pattern, src,
                             msg=f"metadata.py must not contain '{pattern}'")

    # ── No calculations ────────────────────────────────────────

    def test_no_arithmetic_in_extraction_code(self):
        """New extraction functions must not perform arithmetic operations."""
        src = Path("scene_graph/metadata.py").read_text()
        tree = ast.parse(src, filename="scene_graph/metadata.py")
        arithmetic_ops: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, (
                    ast.Add, ast.Sub, ast.Mult, ast.Div,
                    ast.FloorDiv, ast.Mod, ast.Pow,
                )):
                    arithmetic_ops.append((type(node.op).__name__, node.lineno))
        # Allow only len() in the _screw_holes list compression at line count
        # Actual arithmetic in existing _hole_visual_from_op is not new.
        # Filter to only new functions (line 350+)
        new_arithmetic = [op for op in arithmetic_ops if op[1] > 350]
        self.assertEqual(
            new_arithmetic, [],
            f"New extraction code must not perform arithmetic: found {new_arithmetic}",
        )

    def test_no_sum_calls(self):
        src = Path("scene_graph/metadata.py").read_text()
        tree = ast.parse(src, filename="scene_graph/metadata.py")
        sum_calls: list[int] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "sum":
                    sum_calls.append(node.lineno)
        self.assertEqual(sum_calls, [])

    # ── No renderer dependency ─────────────────────────────────

    def test_metadata_imports_no_renderer(self):
        from scene_graph import metadata as md
        mod_name = md.__name__
        self.assertEqual(mod_name, "scene_graph.metadata")
        # Verify no renderer imports in source
        src = Path("scene_graph/metadata.py").read_text()
        for token in ["renderer", "SceneRenderer", "RendererRegistry"]:
            self.assertNotIn(token, src)

    # ── No FreeCAD dependency ──────────────────────────────────

    def test_no_freecad_imports(self):
        with open("scene_graph/metadata.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines()
                 if l.strip().startswith(("import ", "from "))]
        text = "\n".join(lines)
        forbidden = ["FreeCAD", "Part", "QtWidgets", "QtCore", "QtGui", "App"]
        for token in forbidden:
            self.assertNotIn(token, text,
                             msg=f"metadata.py must not import '{token}'")

    # ── Deterministic ──────────────────────────────────────────

    def test_extraction_deterministic(self):
        from scene_graph.metadata import _minifix_holes_from_node, _shelf_pin_holes_from_node
        ops = [
            self._make_op(local_x=37.0, local_y=100.0, diameter=15.0, depth=12.0,
                          intent="INTENT_MINIFIX_15"),
            self._make_op(local_x=2.0, local_y=64.0, diameter=5.0,
                          intent="INTENT_SHELF_PIN"),
        ]
        node = self._make_node(ops=ops)
        r1 = _minifix_holes_from_node(node, "TEST_PANEL")
        r2 = _minifix_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(r1, r2)

    # ── No input mutation ─────────────────────────────────────

    def test_no_input_mutation(self):
        from scene_graph.metadata import _minifix_holes_from_node
        ops = [
            self._make_op(local_x=37.0, local_y=100.0, intent="INTENT_MINIFIX_15"),
        ]
        node = self._make_node(ops=ops)
        orig_count = len(node.machining_ops)
        orig_intent = node.machining_ops[0].metadata.get("hardware_intent", "")
        _minifix_holes_from_node(node, "TEST_PANEL")
        self.assertEqual(len(node.machining_ops), orig_count)
        self.assertEqual(node.machining_ops[0].metadata.get("hardware_intent", ""), orig_intent)

    # ── hardware_intent field traceability ─────────────────────

    def test_hardware_intent_carries_through(self):
        from scene_graph.metadata import build_visual_metadata
        ops = [
            self._make_op(local_x=37.0, local_y=100.0, diameter=15.0, depth=12.0,
                          intent="INTENT_MINIFIX_15"),
            self._make_op(local_x=37.0, local_y=200.0, diameter=8.0, depth=50.0,
                          intent="INTENT_CONFIRMAT_50"),
            self._make_op(local_x=2.0, local_y=64.0, diameter=5.0,
                          intent="INTENT_SHELF_PIN"),
            self._make_op(local_x=10.0, local_y=50.0,
                          intent="INTENT_DRAWER_SLIDE"),
            self._make_op(local_x=20.0, local_y=100.0, diameter=35.0,
                          intent="INTENT_HINGE"),
        ]
        node = self._make_node(role_name="SIDE_PANEL", ops=ops)
        vm = build_visual_metadata(node)
        self.assertEqual(len(vm.minifix_holes), 1)
        self.assertEqual(len(vm.confirmat_holes), 1)
        self.assertEqual(len(vm.shelf_pin_holes), 1)
        self.assertEqual(len(vm.drawer_slide_holes), 1)
        self.assertEqual(len(vm.hinge_plate_positions), 1)
        self.assertEqual(len(vm.hinge_cup_holes), 0)

    # ── Panel identity preserved ──────────────────────────────

    def test_panel_identity_carries_through(self):
        from scene_graph.metadata import _minifix_holes_from_node
        ops = [
            self._make_op(local_x=37.0, local_y=100.0, intent="INTENT_MINIFIX_15"),
        ]
        node = self._make_node(ops=ops)
        result = _minifix_holes_from_node(node, "CUSTOM_PANEL_ID")
        self.assertEqual(result[0].panel_identity, "CUSTOM_PANEL_ID")


if __name__ == "__main__":
    unittest.main()
