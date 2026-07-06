# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Scene Graph
# SceneRenderer → VisualMetadata Manufacturing Metadata Contract Tests
#
# HFG-2.5: Verifies SceneRenderer can safely consume the 7 new
# VisualMetadata manufacturing feature fields without adding
# manufacturing logic.
#
# Verifies:
# 1. SceneRenderer accepts VisualMetadata with all new fields
# 2. Empty fields do not break rendering
# 3. Renderer does not mutate VisualMetadata
# 4. Renderer does not import manufacturing modules (overlay path)
# 5. Renderer does not import factory_operational_intelligence
# 6. Renderer does not reclassify by hardware_intent (overlay path)
# 7. Renderer does not calculate machining positions (overlay path)
# 8. Renderer keeps existing overlay behaviour unchanged
# 9. Renderer has a clear extension point for manufacturing overlays
# 10. GeometryRenderer remains untouched
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERER_PATH = REPO_ROOT / "scene_graph" / "renderer.py"


# ── AST helpers ───────────────────────────────────────────────────


def _renderer_ast():
    """Parse renderer.py and return (source, tree)."""
    source = RENDERER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(RENDERER_PATH))
    return source, tree


def _function_body_source(module_source: str, func_name: str) -> str:
    """Extract the source text of a function/method by name from the module."""
    _, tree = _renderer_ast()

    # Walk top-level / class-level looking for FunctionDef / AsyncFunctionDef
    target_node = None

    def _find(node):
        nonlocal target_node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                target_node = node
                return node
        for child in ast.iter_child_nodes(node):
            result = _find(child)
            if result:
                return result
        return None

    _find(tree)

    if target_node is None:
        return ""

    lines = module_source.splitlines(keepends=True)
    start = target_node.lineno - 1   # 0-indexed
    end = target_node.end_lineno      # exclusive
    return "".join(lines[start:end])


def _function_imported_modules(func_name: str) -> set[str]:
    """Return imported module names inside a specific function/method."""
    source, _ = _renderer_ast()
    body = _function_body_source(source, func_name)
    if not body:
        return set()
    # Dedent so ast.parse is happy with extracted method source
    dedented = textwrap.dedent(body)
    try:
        tree = ast.parse(dedented, filename="<ast>")
    except SyntaxError:
        return set()

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module)
    return imported


def _function_has_arithmetic(func_name: str) -> list[tuple[str, int]]:
    """Check if a given function contains arithmetic operators."""
    source, _ = _renderer_ast()
    body = _function_body_source(source, func_name)
    if not body:
        return []
    dedented = textwrap.dedent(body)
    try:
        tree = ast.parse(dedented, filename="<ast>")
    except SyntaxError:
        return []

    arithmetic_ops = (
        ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.FloorDiv, ast.Mod, ast.Pow,
    )
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, arithmetic_ops):
            found.append((type(node.op).__name__, node.lineno))
    return found


# ── Overlay pipeline methods on SceneRenderer ──────────────────
# These are the methods involved in the overlay building pipeline.
# Non-overlay methods (render, _render_simple_panel, hinge_offsets_for,
# etc.) are excluded — they pre-existed and are not part of the
# metadata-consumption contract.

OVERLAY_METHODS = (
    "build_visual_overlays",
    "build_viewport_overlay_commands",
    "build_manufacturing_overlays",
    "_edge_band_overlays",
    "_drill_hole_overlays",
    "_groove_overlays",
    "_hardware_marker_overlays",
    "_minifix_overlays",
    "_confirmat_overlays",
    "_hardware_visual_type",
    "_edge_viewport_command",
    "_drill_viewport_command",
    "_groove_viewport_command",
    "_hardware_viewport_command",
    "_minifix_viewport_command",
    "_confirmat_viewport_command",
)


class TestSceneRendererManufacturingMetadataContract(unittest.TestCase):
    """Verify SceneRenderer safely consumes VisualMetadata manufacturing fields."""

    # ── 1. SceneRenderer accepts VisualMetadata with all new fields ──

    def test_renderer_accepts_visual_metadata_with_all_new_fields(self):
        """Pass VisualMetadata with all 7 manufacturing fields populated."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            minifix_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    operation_type="DRILL",
                    face="LEFT", x=37.0, y=100.0, z=0.0,
                    diameter=15.0, depth=12.0,
                    hardware_intent="INTENT_MINIFIX_15",
                ),
            ),
            confirmat_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    operation_type="DRILL",
                    face="RIGHT", x=37.0, y=50.0, z=0.0,
                    diameter=8.0, depth=50.0,
                    hardware_intent="INTENT_CONFIRMAT_50",
                ),
            ),
            shelf_pin_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=2.0, y=64.0,
                    hardware_intent="INTENT_SHELF_PIN",
                ),
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=2.0, y=128.0,
                    hardware_intent="INTENT_SHELF_PIN",
                ),
            ),
            drawer_slide_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=10.0, y=50.0,
                    hardware_intent="INTENT_DRAWER_SLIDE",
                ),
            ),
            hinge_cup_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=20.0, y=100.0,
                    diameter=35.0, depth=12.0,
                    hardware_intent="INTENT_HINGE",
                ),
            ),
            hinge_plate_positions=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=30.0, y=50.0,
                    hardware_intent="INTENT_HINGE",
                ),
            ),
            screw_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=15.0, y=80.0,
                    hardware_intent="INTENT_SCREW",
                ),
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT", x=15.0, y=160.0,
                    hardware_intent="INTENT_PANEL_SCREW",
                ),
            ),
        )

        # Must not raise — renderer ignores unknown fields
        overlays = SceneRenderer.build_visual_overlays(vm)
        self.assertIsInstance(overlays, list)

    def test_renderer_accepts_minifix_and_confirmat_individual_fields(self):
        """minifix_holes and confirmat_holes now produce overlays individually."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(hardware_intent="INTENT_MINIFIX_15")

        vm_minifix = VisualMetadata(minifix_holes=(hole,))
        overlays = SceneRenderer.build_visual_overlays(vm_minifix)
        self.assertEqual(len(overlays), 1,
                         msg="minifix_holes should produce 1 overlay")
        self.assertEqual(overlays[0]["overlay_type"], "minifix_hole")

        vm_confirmat = VisualMetadata(confirmat_holes=(hole,))
        overlays = SceneRenderer.build_visual_overlays(vm_confirmat)
        self.assertEqual(len(overlays), 1,
                         msg="confirmat_holes should produce 1 overlay")
        self.assertEqual(overlays[0]["overlay_type"], "confirmat_hole")

    def test_renderer_ignores_remaining_manufacturing_fields(self):
        """The remaining 3 manufacturing fields are still ignored by renderer."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(hardware_intent="INTENT_MINIFIX_15")
        field_names = [
            "hinge_cup_holes",
            "hinge_plate_positions",
            "screw_holes",
        ]
        for name in field_names:
            vm = VisualMetadata(**{name: (hole,)})
            overlays = SceneRenderer.build_visual_overlays(vm)
            self.assertEqual(overlays, [],
                             msg=f"Field {name} should be ignored by renderer")

    # ── 2. Empty fields do not break rendering ───────────────────

    def test_empty_new_fields_do_not_break_renderer(self):
        """VisualMetadata with only new fields set to empty tuples is safe."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            minifix_holes=(),
            confirmat_holes=(),
            shelf_pin_holes=(),
            drawer_slide_holes=(),
            hinge_cup_holes=(),
            hinge_plate_positions=(),
            screw_holes=(),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)
        self.assertEqual(overlays, [])

    def test_empty_metadata_still_safe(self):
        """Default VisualMetadata (all empty) returns no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_visual_overlays(VisualMetadata())
        self.assertEqual(overlays, [])

    def test_viewport_commands_with_minifix_field_produce_commands(self):
        """Full pipeline: minifix_holes produce viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            edge_banding=(),
            drill_holes=(),
            grooves=(),
            hardware_markers=(),
            minifix_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    x=37.0, y=100.0,
                    diameter=15.0, depth=12.0,
                    hardware_intent="INTENT_MINIFIX_15",
                ),
            ),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "minifix_hole")
        self.assertEqual(commands[0]["panel_identity"], "P1")
        self.assertEqual(commands[0]["diameter"], 15.0)

    # ── 3. Renderer does not mutate VisualMetadata ───────────────

    def test_renderer_does_not_mutate_visual_metadata(self):
        """build_visual_overlays does not modify the input metadata."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=37.0, y=100.0,
            hardware_intent="INTENT_MINIFIX_15",
        )
        vm = VisualMetadata(minifix_holes=(hole,))

        original_repr = repr(vm)

        SceneRenderer.build_visual_overlays(vm)

        # Verify frozen dataclass guarantee holds
        self.assertEqual(repr(vm), original_repr)

    def test_build_visual_overlays_does_not_mutate_original_hole(self):
        """Individual DrillHoleVisual inside metadata must stay unchanged."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=37.0, y=100.0, diameter=15.0,
            hardware_intent="INTENT_MINIFIX_15",
        )
        orig_x = hole.x
        orig_y = hole.y
        orig_diameter = hole.diameter

        vm = VisualMetadata(minifix_holes=(hole,))
        SceneRenderer.build_visual_overlays(vm)

        self.assertEqual(hole.x, orig_x)
        self.assertEqual(hole.y, orig_y)
        self.assertEqual(hole.diameter, orig_diameter)

    # ── 4. Renderer does not import manufacturing modules ────────

    def test_overlay_methods_do_not_import_manufacturing(self):
        """Each overlay pipeline method must not import manufacturing modules."""
        forbidden_prefixes = ["manufacturing", "factory_operational_intelligence"]

        for method_name in OVERLAY_METHODS:
            imports = _function_imported_modules(method_name)
            for forbidden in forbidden_prefixes:
                offenders = sorted(
                    m for m in imports
                    if m == forbidden or m.startswith(forbidden + ".")
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"SceneRenderer.{method_name} imports forbidden "
                        f"manufacturing module {forbidden}: {offenders}"
                    ),
                )

    # ── 5. Renderer does not import factory_operational_intelligence ──
    # (Covered by test 4 — same forbidden_prefixes includes it)

    # ── 6. Renderer does not reclassify by hardware_intent ───────

    def test_overlay_methods_do_not_inspect_hardware_intent(self):
        """Overlay pipeline methods must not reference hardware_intent."""
        for method_name in OVERLAY_METHODS:
            source, _ = _renderer_ast()
            body = _function_body_source(source, method_name)
            self.assertNotIn(
                "hardware_intent",
                body,
                msg=(
                    f"SceneRenderer.{method_name} must not inspect "
                    f"hardware_intent — that is manufacturing classification"
                ),
            )

    # ── 7. Renderer does not calculate machining positions ───────

    def test_overlay_methods_have_no_arithmetic(self):
        """Overlay pipeline methods must not perform arithmetic operations."""
        for method_name in OVERLAY_METHODS:
            arithmetic_found = _function_has_arithmetic(method_name)
            self.assertEqual(
                arithmetic_found, [],
                msg=(
                    f"SceneRenderer.{method_name} contains arithmetic "
                    f"operations: {arithmetic_found}. "
                    f"Renderer must not calculate machining positions."
                ),
            )

    # ── 8. Renderer keeps existing overlay behaviour unchanged ───

    def test_existing_edge_overlays_unchanged_with_new_fields(self):
        """Edge banding overlays identical with or without new fields."""
        from scene_graph.metadata import (
            EdgeBandVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        edge = EdgeBandVisual(side="TOP", banding="ABS", label="TOP: ABS")

        vm_without = VisualMetadata(edge_banding=(edge,))
        vm_with = VisualMetadata(
            edge_banding=(edge,),
            minifix_holes=self._one_hole("INTENT_MINIFIX_15"),
        )

        overlays_without = SceneRenderer.build_visual_overlays(vm_without)
        overlays_with = SceneRenderer.build_visual_overlays(vm_with)

        # Edge overlay content must be identical; vm_with also has minifix
        edge_without = [o for o in overlays_without if o["overlay_type"] == "edge_banding"]
        edge_with = [o for o in overlays_with if o["overlay_type"] == "edge_banding"]
        self.assertEqual(edge_without, edge_with)

        # Minifix overlay is present in vm_with
        minifix_overlays = [o for o in overlays_with if o["overlay_type"] == "minifix_hole"]
        self.assertEqual(len(minifix_overlays), 1)
        self.assertEqual(minifix_overlays[0]["visual_type"], "MINIFIX_SYMBOL")

    def test_existing_drill_overlays_unchanged_with_new_fields(self):
        """Drill hole overlays identical with or without new fields."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        drill = DrillHoleVisual(
            panel_identity="P1", operation_type="DRILL",
            face="LEFT", x=10.0, y=20.0, diameter=5.0, depth=12.0,
        )

        vm_without = VisualMetadata(drill_holes=(drill,))
        vm_with = VisualMetadata(
            drill_holes=(drill,),
            confirmat_holes=self._one_hole("INTENT_CONFIRMAT_50"),
        )

        overlays_without = SceneRenderer.build_visual_overlays(vm_without)
        overlays_with = SceneRenderer.build_visual_overlays(vm_with)

        # Drill overlay content must be identical; vm_with also has confirmat
        drill_without = [o for o in overlays_without if o["overlay_type"] == "drill_hole"]
        drill_with = [o for o in overlays_with if o["overlay_type"] == "drill_hole"]
        self.assertEqual(drill_without, drill_with)

        # Confirmat overlay is present in vm_with
        confirmat_overlays = [o for o in overlays_with if o["overlay_type"] == "confirmat_hole"]
        self.assertEqual(len(confirmat_overlays), 1)
        self.assertEqual(confirmat_overlays[0]["visual_type"], "CONFIRMAT_SYMBOL")

    def test_existing_groove_overlays_unchanged_with_new_fields(self):
        """Groove overlays identical with or without new fields."""
        from scene_graph.metadata import (
            GrooveVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        groove = GrooveVisual(
            panel_identity="BACK-1", face="BACK",
            depth=8.0, label="Back panel groove",
        )

        vm_without = VisualMetadata(grooves=(groove,))
        vm_with = VisualMetadata(
            grooves=(groove,),
            shelf_pin_holes=self._one_hole("INTENT_SHELF_PIN"),
            drawer_slide_holes=self._one_hole("INTENT_DRAWER_SLIDE"),
        )

        overlays_without = SceneRenderer.build_visual_overlays(vm_without)
        overlays_with = SceneRenderer.build_visual_overlays(vm_with)

        # Groove overlay content must be identical; vm_with also has shelf_pin + drawer_slide
        groove_without = [o for o in overlays_without if o["overlay_type"] == "groove"]
        groove_with = [o for o in overlays_with if o["overlay_type"] == "groove"]
        self.assertEqual(groove_without, groove_with)

        # Shelf pin and drawer slide overlays are present in vm_with
        sp_overlays = [o for o in overlays_with if o["overlay_type"] == "shelf_pin_hole"]
        ds_overlays = [o for o in overlays_with if o["overlay_type"] == "drawer_slide_hole"]
        self.assertEqual(len(sp_overlays), 1)
        self.assertEqual(len(ds_overlays), 1)

    def test_existing_hardware_marker_overlays_unchanged_with_new_fields(self):
        """Hardware marker overlays identical with or without new fields."""
        from scene_graph.metadata import (
            HardwareMarkerVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        marker = HardwareMarkerVisual(
            panel_identity="door-01", sku="HINGE_BLUM_110_V1",
            quantity=2, hardware_category="HINGE",
        )

        vm_without = VisualMetadata(hardware_markers=(marker,))
        vm_with = VisualMetadata(
            hardware_markers=(marker,),
            hinge_cup_holes=self._one_hole("INTENT_HINGE"),
            hinge_plate_positions=self._one_hole("INTENT_HINGE"),
            screw_holes=self._one_hole("INTENT_SCREW"),
        )

        self.assertEqual(
            SceneRenderer.build_visual_overlays(vm_without),
            SceneRenderer.build_visual_overlays(vm_with),
        )

    def test_viewport_commands_unchanged_with_new_fields(self):
        """Viewport commands pipeline unchanged when metadata has new fields.

        Existing drill_hole overlay must still produce a valid command.
        New minifix/confirmat overlays produce additional commands.
        """
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        drill = DrillHoleVisual(
            panel_identity="P1", operation_type="DRILL",
            face="LEFT", x=10.0, y=20.0, z=0.0,
            diameter=5.0, depth=12.0,
        )

        vm = VisualMetadata(
            drill_holes=(drill,),
            minifix_holes=self._one_hole("INTENT_MINIFIX_15"),
            confirmat_holes=self._one_hole("INTENT_CONFIRMAT_50"),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(len(commands), 3)
        # drill_hole is first (unchanged behaviour)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "drill_hole")
        self.assertEqual(commands[0]["panel_identity"], "P1")
        # minifix_hole is second
        self.assertEqual(commands[1]["overlay_type"], "minifix_hole")
        # confirmat_hole is third
        self.assertEqual(commands[2]["overlay_type"], "confirmat_hole")

    # ── 9. Renderer has a clear extension point for manufacturing overlays ──

    def test_build_manufacturing_overlays_is_public_extension_point(self):
        """SceneRenderer.build_manufacturing_overlays exists and is callable."""
        from scene_graph.renderer import SceneRenderer

        self.assertTrue(
            hasattr(SceneRenderer, "build_manufacturing_overlays"),
            msg="SceneRenderer must expose build_manufacturing_overlays",
        )
        self.assertTrue(
            callable(SceneRenderer.build_manufacturing_overlays),
            msg="build_manufacturing_overlays must be callable",
        )

    def test_build_manufacturing_overlays_accepts_markers(self):
        """Extension point accepts a list of markers and returns them."""
        from scene_graph.renderer import SceneRenderer

        markers = [
            {"marker_type": "minifix", "x": 37.0, "y": 100.0},
            {"marker_type": "confirmat", "x": 37.0, "y": 50.0},
        ]
        result = SceneRenderer.build_manufacturing_overlays(markers)
        self.assertEqual(result, markers)

    def test_build_manufacturing_overlays_accepts_empty_list(self):
        """Extension point handles None or empty markers gracefully."""
        from scene_graph.renderer import SceneRenderer

        self.assertEqual(
            SceneRenderer.build_manufacturing_overlays([]), []
        )
        self.assertEqual(
            SceneRenderer.build_manufacturing_overlays(None), []
        )

    def test_build_manufacturing_overlays_is_static_and_pure(self):
        """Extension point is a staticmethod — no self/document/engine access."""
        from scene_graph.renderer import SceneRenderer

        source, _ = _renderer_ast()
        body = _function_body_source(source, "build_manufacturing_overlays")

        # Must not reference self, doc, or any engine
        for token in ("self", "doc", "Part", "FreeCAD", "App"):
            self.assertNotIn(
                token, body,
                msg=f"build_manufacturing_overlays must not reference {token}",
            )

    # ── 10. GeometryRenderer remains untouched ───────────────────

    def test_geometry_renderer_not_imported_by_scene_renderer(self):
        """SceneRenderer must not import GeometryRenderer."""
        source = RENDERER_PATH.read_text(encoding="utf-8")
        self.assertNotIn(
            "GeometryRenderer",
            source,
            msg="scene_graph/renderer.py must not import GeometryRenderer",
        )

    def test_geometry_renderer_not_dependent_on_visual_metadata(self):
        """GeometryRenderer (gui/renderer.py) must not import VisualMetadata."""
        src_path = REPO_ROOT / "gui" / "renderer.py"
        if not src_path.exists():
            self.skipTest("gui/renderer.py not found — GeometryRenderer not in this environment")

        source = src_path.read_text(encoding="utf-8")
        forbidden = [
            "VisualMetadata",
            "scene_graph.metadata",
            "minifix_holes",
            "confirmat_holes",
            "shelf_pin_holes",
            "drawer_slide_holes",
            "hinge_cup_holes",
            "hinge_plate_positions",
            "screw_holes",
        ]
        for token in forbidden:
            self.assertNotIn(
                token, source,
                msg=f"gui/renderer.py (GeometryRenderer) must not reference {token}",
            )

    def test_geometry_renderer_file_remains_unchanged(self):
        """GeometryRenderer file must not have been modified by this sprint."""
        src_path = REPO_ROOT / "gui" / "renderer.py"
        if not src_path.exists():
            self.skipTest("gui/renderer.py not found")

        source = src_path.read_text(encoding="utf-8")
        self.assertIn("FreeCAD", source, "GeometryRenderer still needs FreeCAD")
        self.assertIn(
            "visible_geometry_plan",
            source,
            "GeometryRenderer still references manufacturing pipeline",
        )

    # ── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _one_hole(intent: str):
        """Create a tuple with one DrillHoleVisual."""
        from scene_graph.metadata import DrillHoleVisual
        return (DrillHoleVisual(
            panel_identity="P1",
            hardware_intent=intent,
        ),)


if __name__ == "__main__":
    unittest.main()
