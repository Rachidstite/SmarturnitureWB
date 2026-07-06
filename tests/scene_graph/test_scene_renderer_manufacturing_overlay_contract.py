# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Scene Graph
# SceneRenderer → Minifix & Confirmat Manufacturing Overlay Contract Tests
#
# HFG-3A: SceneRenderer consumes minifix_holes and confirmat_holes
# from VisualMetadata and produces overlay commands.
#
# Verifies:
#  1. minifix_holes produce overlay commands
#  2. confirmat_holes produce overlay commands
#  3. empty fields produce no overlays
#  4. existing overlays still work
#  5. renderer does not mutate VisualMetadata
#  6. renderer does not import manufacturing modules
#  7. renderer does not inspect hardware_intent
#  8. GeometryRenderer remains untouched
#  9. no arithmetic / no machining calculation
# 10. overlay command labels/types are stable
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
    start = target_node.lineno - 1
    end = target_node.end_lineno
    return "".join(lines[start:end])


def _function_imported_modules(func_name: str) -> set[str]:
    """Return imported module names inside a specific function/method."""
    source, _ = _renderer_ast()
    body = _function_body_source(source, func_name)
    if not body:
        return set()
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


# ── Overlay methods relevant to manufacturing hole types ──────────

MANUFACTURING_OVERLAY_METHODS = (
    "_minifix_overlays",
    "_confirmat_overlays",
    "_shelf_pin_hole_overlays",
    "_drawer_slide_hole_overlays",
    "_hinge_cup_hole_overlays",
    "_hinge_plate_position_overlays",
    "_screw_hole_overlays",
    "_minifix_viewport_command",
    "_confirmat_viewport_command",
    "_shelf_pin_viewport_command",
    "_drawer_slide_viewport_command",
    "_hinge_cup_viewport_command",
    "_hinge_plate_viewport_command",
    "_screw_viewport_command",
)


class TestSceneRendererMinifixConfirmatOverlayContract(unittest.TestCase):
    """Verify SceneRenderer correctly visualizes minifix_holes and confirmat_holes."""

    # ── 1. minifix_holes produce overlay commands ─────────────────

    def test_minifix_holes_produce_overlay_commands(self):
        """minifix_holes in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            minifix_holes=(
                DrillHoleVisual(
                    panel_identity="panel-A",
                    face="LEFT",
                    x=37.0, y=100.0, z=0.0,
                    diameter=15.0, depth=12.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-minifix-001",
                    hardware_intent="INTENT_MINIFIX_15",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        # Overlay produced with correct type
        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "minifix_hole")
        self.assertEqual(overlays[0]["visual_type"], "MINIFIX_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-A")
        self.assertEqual(overlays[0]["face"], "LEFT")
        self.assertEqual(overlays[0]["x"], 37.0)
        self.assertEqual(overlays[0]["y"], 100.0)
        self.assertEqual(overlays[0]["diameter"], 15.0)
        self.assertEqual(overlays[0]["depth"], 12.0)

        # Viewport command produced
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "minifix_hole")
        self.assertEqual(commands[0]["panel_identity"], "panel-A")
        self.assertEqual(commands[0]["diameter"], 15.0)

    # ── 2. confirmat_holes produce overlay commands ────────────────

    def test_confirmat_holes_produce_overlay_commands(self):
        """confirmat_holes in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            confirmat_holes=(
                DrillHoleVisual(
                    panel_identity="panel-B",
                    face="RIGHT",
                    x=37.0, y=50.0, z=0.0,
                    diameter=8.0, depth=50.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-confirmat-001",
                    hardware_intent="INTENT_CONFIRMAT_50",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        # Overlay produced with correct type
        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "confirmat_hole")
        self.assertEqual(overlays[0]["visual_type"], "CONFIRMAT_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-B")
        self.assertEqual(overlays[0]["face"], "RIGHT")
        self.assertEqual(overlays[0]["x"], 37.0)
        self.assertEqual(overlays[0]["y"], 50.0)
        self.assertEqual(overlays[0]["diameter"], 8.0)
        self.assertEqual(overlays[0]["depth"], 50.0)

        # Viewport command produced
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "confirmat_hole")
        self.assertEqual(commands[0]["panel_identity"], "panel-B")
        self.assertEqual(commands[0]["diameter"], 8.0)

    # ── 3. empty fields produce no overlays ────────────────────────

    def test_empty_minifix_produces_no_overlays(self):
        """Empty minifix_holes produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(minifix_holes=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_empty_confirmat_produces_no_overlays(self):
        """Empty confirmat_holes produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(confirmat_holes=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_default_visual_metadata_produces_no_minifix_confirmat(self):
        """Default VisualMetadata produces no minifix or confirmat overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata()
        overlays = SceneRenderer.build_visual_overlays(vm)

        minifix_count = sum(
            1 for o in overlays if o.get("overlay_type") == "minifix_hole"
        )
        confirmat_count = sum(
            1 for o in overlays if o.get("overlay_type") == "confirmat_hole"
        )

        self.assertEqual(minifix_count, 0)
        self.assertEqual(confirmat_count, 0)

    # ── 4. existing overlays still work ────────────────────────────

    def test_existing_edge_overlays_still_work_with_minifix_confirmat(self):
        """Edge banding overlays unchanged when minifix/confirmat are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            EdgeBandVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        edge = EdgeBandVisual(side="TOP", banding="ABS", label="TOP: ABS")

        vm = VisualMetadata(
            edge_banding=(edge,),
            minifix_holes=(
                DrillHoleVisual(hardware_intent="INTENT_MINIFIX_15"),
            ),
            confirmat_holes=(
                DrillHoleVisual(hardware_intent="INTENT_CONFIRMAT_50"),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        # edge_banding overlay is first (unchanged)
        edge_overlays = [o for o in overlays if o["overlay_type"] == "edge_banding"]
        self.assertEqual(len(edge_overlays), 1)
        self.assertEqual(edge_overlays[0]["side"], "TOP")
        self.assertEqual(edge_overlays[0]["banding"], "ABS")

    def test_existing_drill_hole_overlays_still_work_with_minifix_confirmat(self):
        """Drill hole overlays unchanged when minifix/confirmat are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        drill = DrillHoleVisual(
            panel_identity="P1",
            x=10.0, y=20.0, diameter=5.0, depth=12.0,
        )

        vm = VisualMetadata(
            drill_holes=(drill,),
            minifix_holes=(
                DrillHoleVisual(hardware_intent="INTENT_MINIFIX_15"),
            ),
            confirmat_holes=(
                DrillHoleVisual(hardware_intent="INTENT_CONFIRMAT_50"),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        drill_overlays = [o for o in overlays if o["overlay_type"] == "drill_hole"]
        self.assertEqual(len(drill_overlays), 1)
        self.assertEqual(drill_overlays[0]["x"], 10.0)
        self.assertEqual(drill_overlays[0]["y"], 20.0)
        self.assertEqual(drill_overlays[0]["diameter"], 5.0)

    def test_existing_groove_overlays_still_work_with_minifix_confirmat(self):
        """Groove overlays unchanged when minifix/confirmat are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            GrooveVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        groove = GrooveVisual(
            panel_identity="BACK-1", face="BACK",
            depth=8.0, label="Back panel groove",
        )

        vm = VisualMetadata(
            grooves=(groove,),
            minifix_holes=(
                DrillHoleVisual(hardware_intent="INTENT_MINIFIX_15"),
            ),
            confirmat_holes=(
                DrillHoleVisual(hardware_intent="INTENT_CONFIRMAT_50"),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        groove_overlays = [o for o in overlays if o["overlay_type"] == "groove"]
        self.assertEqual(len(groove_overlays), 1)
        self.assertEqual(groove_overlays[0]["face"], "BACK")

    def test_existing_hardware_marker_overlays_still_work_with_minifix_confirmat(self):
        """Hardware marker overlays unchanged when minifix/confirmat are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            HardwareMarkerVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        marker = HardwareMarkerVisual(
            panel_identity="door-01", sku="HINGE_BLUM_110_V1",
            quantity=2, hardware_category="HINGE",
        )

        vm = VisualMetadata(
            hardware_markers=(marker,),
            minifix_holes=(
                DrillHoleVisual(hardware_intent="INTENT_MINIFIX_15"),
            ),
            confirmat_holes=(
                DrillHoleVisual(hardware_intent="INTENT_CONFIRMAT_50"),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        hw_overlays = [o for o in overlays if o["overlay_type"] == "hardware_marker"]
        self.assertEqual(len(hw_overlays), 1)
        self.assertEqual(hw_overlays[0]["sku"], "HINGE_BLUM_110_V1")

    # ── 5. renderer does not mutate VisualMetadata ─────────────────

    def test_minifix_overlay_pipeline_does_not_mutate_metadata(self):
        """_minifix_overlays does not modify the input metadata."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=37.0, y=100.0, diameter=15.0,
            hardware_intent="INTENT_MINIFIX_15",
        )
        vm = VisualMetadata(minifix_holes=(hole,))
        original_repr = repr(vm)

        SceneRenderer.build_visual_overlays(vm)

        self.assertEqual(repr(vm), original_repr,
                         msg="build_visual_overlays must not mutate VisualMetadata")

    def test_confirmat_overlay_pipeline_does_not_mutate_metadata(self):
        """_confirmat_overlays does not modify the input metadata."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=37.0, y=100.0, diameter=8.0,
            hardware_intent="INTENT_CONFIRMAT_50",
        )
        vm = VisualMetadata(confirmat_holes=(hole,))
        original_repr = repr(vm)

        SceneRenderer.build_visual_overlays(vm)

        self.assertEqual(repr(vm), original_repr,
                         msg="build_visual_overlays must not mutate VisualMetadata")

    def test_drill_hole_visual_remains_unchanged_after_overlay(self):
        """Individual DrillHoleVisual must stay unchanged after overlay build."""
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

    # ── 6. renderer does not import manufacturing modules ──────────

    def test_minifix_confirmat_methods_do_not_import_manufacturing(self):
        """Minifix/confirmat overlay methods must not import manufacturing modules."""
        forbidden_prefixes = ["manufacturing", "factory_operational_intelligence"]

        for method_name in MANUFACTURING_OVERLAY_METHODS:
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

    # ── 7. renderer does not inspect hardware_intent ────────────────

    def test_minifix_confirmat_methods_do_not_inspect_hardware_intent(self):
        """Minifix/confirmat overlay methods must not reference hardware_intent."""
        for method_name in MANUFACTURING_OVERLAY_METHODS:
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

    # ── 8. GeometryRenderer remains untouched ─────────────────────
    # Note: shelf_pin_hole is a pre-existing manufacturing feature kind
    # string in gui/renderer.py (3D geometry pipeline), unrelated to
    # the overlay type. Only new overlay-only strings are checked.

    def test_scene_renderer_does_not_import_geometry_renderer(self):
        """SceneRenderer must not import GeometryRenderer."""
        source = RENDERER_PATH.read_text(encoding="utf-8")
        self.assertNotIn(
            "GeometryRenderer",
            source,
            msg="scene_graph/renderer.py must not import GeometryRenderer",
        )

    def test_geometry_renderer_not_dependent_on_minifix_confirmat(self):
        """GeometryRenderer must not reference minifix/confirmat overlay types."""
        src_path = REPO_ROOT / "gui" / "renderer.py"
        if not src_path.exists():
            self.skipTest("gui/renderer.py not found — GeometryRenderer not in this environment")

        source = src_path.read_text(encoding="utf-8")
        forbidden = [
            "minifix_hole",
            "confirmat_hole",
            "minifix_overlay",
            "confirmat_overlay",
        ]
        for token in forbidden:
            self.assertNotIn(
                token, source,
                msg=f"gui/renderer.py (GeometryRenderer) must not reference {token}",
            )

    # ── 9. no arithmetic / no machining calculation ───────────────

    def test_minifix_confirmat_methods_have_no_arithmetic(self):
        """Minifix/confirmat overlay methods must not perform arithmetic."""
        for method_name in MANUFACTURING_OVERLAY_METHODS:
            arithmetic_found = _function_has_arithmetic(method_name)
            self.assertEqual(
                arithmetic_found, [],
                msg=(
                    f"SceneRenderer.{method_name} contains arithmetic "
                    f"operations: {arithmetic_found}. "
                    f"Renderer must not calculate machining positions."
                ),
            )

    # ── 10. overlay command labels/types are stable ────────────────

    def test_minifix_overlay_label_type_stable(self):
        """Minifix overlay labels and types are deterministic and stable."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            minifix_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    x=37.0, y=100.0,
                    diameter=15.0, depth=12.0,
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        # Overlay contract
        self.assertEqual(overlays[0]["overlay_type"], "minifix_hole")
        self.assertEqual(overlays[0]["visual_type"], "MINIFIX_SYMBOL")

        # Viewport command contract
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "minifix_hole")
        self.assertEqual(commands[0]["label"], "Minifix hole")

        # Same metadata produces identical output (idempotent)
        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_confirmat_overlay_label_type_stable(self):
        """Confirmat overlay labels and types are deterministic and stable."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            confirmat_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    x=37.0, y=50.0,
                    diameter=8.0, depth=50.0,
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        # Overlay contract
        self.assertEqual(overlays[0]["overlay_type"], "confirmat_hole")
        self.assertEqual(overlays[0]["visual_type"], "CONFIRMAT_SYMBOL")

        # Viewport command contract
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "confirmat_hole")
        self.assertEqual(commands[0]["label"], "Confirmat hole")

        # Same metadata produces identical output (idempotent)
        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_minifix_overlay_fields_match_drill_hole_schema(self):
        """Minifix overlays carry all positional fields from DrillHoleVisual."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            minifix_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT",
                    x=37.0, y=100.0, z=5.0,
                    diameter=15.0, depth=12.0,
                    axis="Z",
                    is_through=True,
                    source_operation_reference="op-ref",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        o = overlays[0]

        self.assertEqual(o["panel_identity"], "P1")
        self.assertEqual(o["face"], "LEFT")
        self.assertEqual(o["x"], 37.0)
        self.assertEqual(o["y"], 100.0)
        self.assertEqual(o["z"], 5.0)
        self.assertEqual(o["diameter"], 15.0)
        self.assertEqual(o["depth"], 12.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], True)
        self.assertEqual(o["source_operation_reference"], "op-ref")

    def test_confirmat_overlay_fields_match_drill_hole_schema(self):
        """Confirmat overlays carry all positional fields from DrillHoleVisual."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            confirmat_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="RIGHT",
                    x=37.0, y=50.0, z=0.0,
                    diameter=8.0, depth=50.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-ref-conf",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        o = overlays[0]

        self.assertEqual(o["panel_identity"], "P1")
        self.assertEqual(o["face"], "RIGHT")
        self.assertEqual(o["x"], 37.0)
        self.assertEqual(o["y"], 50.0)
        self.assertEqual(o["z"], 0.0)
        self.assertEqual(o["diameter"], 8.0)
        self.assertEqual(o["depth"], 50.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], False)
        self.assertEqual(o["source_operation_reference"], "op-ref-conf")

    # ═══════════════════════════════════════════════════════════════
    # HFG-3B — Shelf Pin and Drawer Slide Overlays
    # ═══════════════════════════════════════════════════════════════

    # ── 1. shelf_pin_holes produce overlay commands ────────────────

    def test_shelf_pin_holes_produce_overlay_commands(self):
        """shelf_pin_holes in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            shelf_pin_holes=(
                DrillHoleVisual(
                    panel_identity="panel-C",
                    face="LEFT",
                    x=2.0, y=64.0, z=0.0,
                    diameter=5.0, depth=10.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-shelf-pin-001",
                    hardware_intent="INTENT_SHELF_PIN",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        # Overlay produced with correct type
        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "shelf_pin_hole")
        self.assertEqual(overlays[0]["visual_type"], "SHELF_PIN_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-C")
        self.assertEqual(overlays[0]["face"], "LEFT")
        self.assertEqual(overlays[0]["x"], 2.0)
        self.assertEqual(overlays[0]["y"], 64.0)
        self.assertEqual(overlays[0]["diameter"], 5.0)
        self.assertEqual(overlays[0]["depth"], 10.0)

        # Viewport command produced
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "shelf_pin_hole")
        self.assertEqual(commands[0]["panel_identity"], "panel-C")
        self.assertEqual(commands[0]["diameter"], 5.0)

    # ── 2. drawer_slide_holes produce overlay commands ─────────────

    def test_drawer_slide_holes_produce_overlay_commands(self):
        """drawer_slide_holes in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            drawer_slide_holes=(
                DrillHoleVisual(
                    panel_identity="panel-D",
                    face="LEFT",
                    x=10.0, y=50.0, z=0.0,
                    diameter=4.0, depth=12.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-drawer-slide-001",
                    hardware_intent="INTENT_DRAWER_SLIDE",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        # Overlay produced with correct type
        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "drawer_slide_hole")
        self.assertEqual(overlays[0]["visual_type"], "DRAWER_SLIDE_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-D")
        self.assertEqual(overlays[0]["face"], "LEFT")
        self.assertEqual(overlays[0]["x"], 10.0)
        self.assertEqual(overlays[0]["y"], 50.0)
        self.assertEqual(overlays[0]["diameter"], 4.0)
        self.assertEqual(overlays[0]["depth"], 12.0)

        # Viewport command produced
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "drawer_slide_hole")
        self.assertEqual(commands[0]["panel_identity"], "panel-D")
        self.assertEqual(commands[0]["diameter"], 4.0)

    # ── 3. empty fields produce no overlays ────────────────────────

    def test_empty_shelf_pin_produces_no_overlays(self):
        """Empty shelf_pin_holes produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(shelf_pin_holes=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_empty_drawer_slide_produces_no_overlays(self):
        """Empty drawer_slide_holes produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(drawer_slide_holes=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_default_metadata_produces_no_shelf_pin_drawer_slide(self):
        """Default VisualMetadata produces no shelf_pin or drawer_slide overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata()
        overlays = SceneRenderer.build_visual_overlays(vm)

        sp_count = sum(
            1 for o in overlays if o.get("overlay_type") == "shelf_pin_hole"
        )
        ds_count = sum(
            1 for o in overlays if o.get("overlay_type") == "drawer_slide_hole"
        )

        self.assertEqual(sp_count, 0)
        self.assertEqual(ds_count, 0)

    # ── 4. existing overlays still work (with shelf_pin/drawer_slide) ──

    def test_existing_overlays_still_work_with_shelf_pin_and_drawer_slide(self):
        """Existing overlays unchanged when shelf_pin/drawer_slide are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            EdgeBandVisual,
            GrooveVisual,
            HardwareMarkerVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            edge_banding=(EdgeBandVisual(side="TOP", banding="ABS"),),
            drill_holes=(DrillHoleVisual(panel_identity="P1", x=10.0, y=20.0),),
            grooves=(GrooveVisual(panel_identity="BACK-1", face="BACK", depth=8.0),),
            hardware_markers=(HardwareMarkerVisual(
                panel_identity="door-01", sku="HINGE_BLUM", quantity=2,
            ),),
            shelf_pin_holes=(
                DrillHoleVisual(hardware_intent="INTENT_SHELF_PIN"),
            ),
            drawer_slide_holes=(
                DrillHoleVisual(hardware_intent="INTENT_DRAWER_SLIDE"),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        self.assertEqual(
            len([o for o in overlays if o["overlay_type"] == "edge_banding"]), 1)
        self.assertEqual(
            len([o for o in overlays if o["overlay_type"] == "drill_hole"]), 1)
        self.assertEqual(
            len([o for o in overlays if o["overlay_type"] == "groove"]), 1)
        self.assertEqual(
            len([o for o in overlays if o["overlay_type"] == "hardware_marker"]), 1)
        self.assertEqual(
            len([o for o in overlays if o["overlay_type"] == "shelf_pin_hole"]), 1)
        self.assertEqual(
            len([o for o in overlays if o["overlay_type"] == "drawer_slide_hole"]), 1)

    # ── 5. renderer does not mutate VisualMetadata ─────────────────

    def test_shelf_pin_overlay_does_not_mutate_metadata(self):
        """shelf_pin_hole overlay pipeline does not modify input metadata."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=2.0, y=64.0, diameter=5.0,
            hardware_intent="INTENT_SHELF_PIN",
        )
        vm = VisualMetadata(shelf_pin_holes=(hole,))
        original_repr = repr(vm)

        SceneRenderer.build_visual_overlays(vm)

        self.assertEqual(repr(vm), original_repr,
                         msg="build_visual_overlays must not mutate VisualMetadata")

    def test_drawer_slide_overlay_does_not_mutate_metadata(self):
        """drawer_slide_hole overlay pipeline does not modify input metadata."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=10.0, y=50.0, diameter=4.0,
            hardware_intent="INTENT_DRAWER_SLIDE",
        )
        vm = VisualMetadata(drawer_slide_holes=(hole,))
        original_repr = repr(vm)

        SceneRenderer.build_visual_overlays(vm)

        self.assertEqual(repr(vm), original_repr,
                         msg="build_visual_overlays must not mutate VisualMetadata")

    # ── 6. (covered by test_minifix_confirmat_methods_do_not_import_manufacturing) ──
    # Uses MANUFACTURING_OVERLAY_METHODS which now includes the 4 new methods

    # ── 7. (covered by test_minifix_confirmat_methods_do_not_inspect_hardware_intent) ──
    # Uses MANUFACTURING_OVERLAY_METHODS which now includes the 4 new methods

    # ── 8. GeometryRenderer remains untouched ─────────────────────

    # ── 9. (covered by test_minifix_confirmat_methods_have_no_arithmetic) ──
    # Uses MANUFACTURING_OVERLAY_METHODS which now includes the 4 new methods

    # ── 10. overlay command labels/types are stable ────────────────

    def test_shelf_pin_overlay_label_type_stable(self):
        """Shelf pin overlay labels and types are deterministic and stable."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            shelf_pin_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    x=2.0, y=64.0,
                    diameter=5.0, depth=10.0,
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays[0]["overlay_type"], "shelf_pin_hole")
        self.assertEqual(overlays[0]["visual_type"], "SHELF_PIN_SYMBOL")

        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "shelf_pin_hole")
        self.assertEqual(commands[0]["label"], "Shelf pin hole")

        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_drawer_slide_overlay_label_type_stable(self):
        """Drawer slide overlay labels and types are deterministic and stable."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            drawer_slide_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    x=10.0, y=50.0,
                    diameter=4.0, depth=12.0,
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays[0]["overlay_type"], "drawer_slide_hole")
        self.assertEqual(overlays[0]["visual_type"], "DRAWER_SLIDE_SYMBOL")

        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "drawer_slide_hole")
        self.assertEqual(commands[0]["label"], "Drawer slide hole")

        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_shelf_pin_overlay_fields_match_drill_hole_schema(self):
        """Shelf pin overlays carry all positional fields from DrillHoleVisual."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            shelf_pin_holes=(
                DrillHoleVisual(
                    panel_identity="P1",
                    face="LEFT",
                    x=2.0, y=64.0, z=0.0,
                    diameter=5.0, depth=10.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-sp",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        o = overlays[0]

        self.assertEqual(o["panel_identity"], "P1")
        self.assertEqual(o["face"], "LEFT")
        self.assertEqual(o["x"], 2.0)
        self.assertEqual(o["y"], 64.0)
        self.assertEqual(o["z"], 0.0)
        self.assertEqual(o["diameter"], 5.0)
        self.assertEqual(o["depth"], 10.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], False)
        self.assertEqual(o["source_operation_reference"], "op-sp")

    def test_drawer_slide_overlay_fields_match_drill_hole_schema(self):
        """Drawer slide overlays carry all positional fields from DrillHoleVisual."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            drawer_slide_holes=(
                DrillHoleVisual(
                    panel_identity="P2",
                    face="RIGHT",
                    x=10.0, y=50.0, z=5.0,
                    diameter=4.0, depth=12.0,
                    axis="Z",
                    is_through=True,
                    source_operation_reference="op-ds",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        o = overlays[0]

        self.assertEqual(o["panel_identity"], "P2")
        self.assertEqual(o["face"], "RIGHT")
        self.assertEqual(o["x"], 10.0)
        self.assertEqual(o["y"], 50.0)
        self.assertEqual(o["z"], 5.0)
        self.assertEqual(o["diameter"], 4.0)
        self.assertEqual(o["depth"], 12.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], True)
        self.assertEqual(o["source_operation_reference"], "op-ds")

    # ── 11. minifix/confirmat behavior remains unchanged ───────────

    def test_minifix_confirmat_unchanged_when_shelf_pin_drawer_slide_present(self):
        """Minifix/confirmat overlays identical with or without shelf_pin/drawer_slide."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        mf_hole = DrillHoleVisual(
            panel_identity="P1", x=37.0, y=100.0, diameter=15.0,
            hardware_intent="INTENT_MINIFIX_15",
        )
        cf_hole = DrillHoleVisual(
            panel_identity="P1", x=37.0, y=50.0, diameter=8.0,
            hardware_intent="INTENT_CONFIRMAT_50",
        )

        vm_base = VisualMetadata(minifix_holes=(mf_hole,), confirmat_holes=(cf_hole,))
        vm_ext = VisualMetadata(
            minifix_holes=(mf_hole,),
            confirmat_holes=(cf_hole,),
            shelf_pin_holes=(
                DrillHoleVisual(hardware_intent="INTENT_SHELF_PIN"),
            ),
            drawer_slide_holes=(
                DrillHoleVisual(hardware_intent="INTENT_DRAWER_SLIDE"),
            ),
        )

        overlays_base = SceneRenderer.build_visual_overlays(vm_base)
        overlays_ext = SceneRenderer.build_visual_overlays(vm_ext)

        # Minifix overlays identical
        mf_base = [o for o in overlays_base if o["overlay_type"] == "minifix_hole"]
        mf_ext = [o for o in overlays_ext if o["overlay_type"] == "minifix_hole"]
        self.assertEqual(mf_base, mf_ext)

        # Confirmat overlays identical
        cf_base = [o for o in overlays_base if o["overlay_type"] == "confirmat_hole"]
        cf_ext = [o for o in overlays_ext if o["overlay_type"] == "confirmat_hole"]
        self.assertEqual(cf_base, cf_ext)

        # Shelf pin and drawer slide added
        sp_ext = [o for o in overlays_ext if o["overlay_type"] == "shelf_pin_hole"]
        ds_ext = [o for o in overlays_ext if o["overlay_type"] == "drawer_slide_hole"]
        self.assertEqual(len(sp_ext), 1)
        self.assertEqual(len(ds_ext), 1)

    # ═══════════════════════════════════════════════════════════════
    # HFG-3C — Hinge Cup and Hinge Plate Position Overlays
    # ═══════════════════════════════════════════════════════════════

    # ── 1. hinge_cup_holes produce overlay commands ────────────────

    def test_hinge_cup_holes_produce_overlay_commands(self):
        """hinge_cup_holes in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            hinge_cup_holes=(
                DrillHoleVisual(
                    panel_identity="panel-E",
                    face="LEFT",
                    x=20.0, y=100.0, z=0.0,
                    diameter=35.0, depth=12.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-hinge-cup-001",
                    hardware_intent="INTENT_HINGE",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "hinge_cup_hole")
        self.assertEqual(overlays[0]["visual_type"], "HINGE_CUP_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-E")
        self.assertEqual(overlays[0]["face"], "LEFT")
        self.assertEqual(overlays[0]["x"], 20.0)
        self.assertEqual(overlays[0]["y"], 100.0)
        self.assertEqual(overlays[0]["diameter"], 35.0)
        self.assertEqual(overlays[0]["depth"], 12.0)

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "hinge_cup_hole")
        self.assertEqual(commands[0]["panel_identity"], "panel-E")
        self.assertEqual(commands[0]["diameter"], 35.0)

    # ── 2. hinge_plate_positions produce overlay commands ──────────

    def test_hinge_plate_positions_produce_overlay_commands(self):
        """hinge_plate_positions in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            hinge_plate_positions=(
                DrillHoleVisual(
                    panel_identity="panel-F",
                    face="LEFT",
                    x=30.0, y=50.0, z=0.0,
                    diameter=5.0, depth=12.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-hinge-plate-001",
                    hardware_intent="INTENT_HINGE",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "hinge_plate_position")
        self.assertEqual(overlays[0]["visual_type"], "HINGE_PLATE_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-F")
        self.assertEqual(overlays[0]["face"], "LEFT")
        self.assertEqual(overlays[0]["x"], 30.0)
        self.assertEqual(overlays[0]["y"], 50.0)
        self.assertEqual(overlays[0]["diameter"], 5.0)
        self.assertEqual(overlays[0]["depth"], 12.0)

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "hinge_plate_position")
        self.assertEqual(commands[0]["panel_identity"], "panel-F")
        self.assertEqual(commands[0]["diameter"], 5.0)

    # ── 3. empty fields produce no overlays ────────────────────────

    def test_empty_hinge_cup_produces_no_overlays(self):
        """Empty hinge_cup_holes produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(hinge_cup_holes=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)
        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_empty_hinge_plate_produces_no_overlays(self):
        """Empty hinge_plate_positions produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(hinge_plate_positions=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)
        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_default_metadata_produces_no_hinge_overlays(self):
        """Default VisualMetadata produces no hinge_cup or hinge_plate overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata()
        overlays = SceneRenderer.build_visual_overlays(vm)

        hc = sum(1 for o in overlays if o.get("overlay_type") == "hinge_cup_hole")
        hp = sum(1 for o in overlays if o.get("overlay_type") == "hinge_plate_position")
        self.assertEqual(hc, 0)
        self.assertEqual(hp, 0)

    # ── 4. existing overlays still work (with hinge fields) ────────

    def test_existing_overlays_still_work_with_hinge_fields(self):
        """Existing overlays unchanged when hinge_cup/plate are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            EdgeBandVisual,
            GrooveVisual,
            HardwareMarkerVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            edge_banding=(EdgeBandVisual(side="TOP", banding="ABS"),),
            drill_holes=(DrillHoleVisual(panel_identity="P1", x=10.0, y=20.0),),
            grooves=(GrooveVisual(panel_identity="BACK-1", face="BACK", depth=8.0),),
            hardware_markers=(HardwareMarkerVisual(
                panel_identity="door-01", sku="HINGE_BLUM", quantity=2,
            ),),
            hinge_cup_holes=(DrillHoleVisual(hardware_intent="INTENT_HINGE"),),
            hinge_plate_positions=(DrillHoleVisual(hardware_intent="INTENT_HINGE"),),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        for ot in ("edge_banding", "drill_hole", "groove", "hardware_marker",
                   "hinge_cup_hole", "hinge_plate_position"):
            self.assertEqual(
                len([o for o in overlays if o["overlay_type"] == ot]), 1,
                msg=f"Expected exactly 1 overlay of type '{ot}'")

    # ── 5. renderer does not mutate VisualMetadata ─────────────────

    def test_hinge_cup_overlay_does_not_mutate_metadata(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=20.0, y=100.0, diameter=35.0,
            hardware_intent="INTENT_HINGE",
        )
        vm = VisualMetadata(hinge_cup_holes=(hole,))
        orig = repr(vm)
        SceneRenderer.build_visual_overlays(vm)
        self.assertEqual(repr(vm), orig)

    def test_hinge_plate_overlay_does_not_mutate_metadata(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=30.0, y=50.0, diameter=5.0,
            hardware_intent="INTENT_HINGE",
        )
        vm = VisualMetadata(hinge_plate_positions=(hole,))
        orig = repr(vm)
        SceneRenderer.build_visual_overlays(vm)
        self.assertEqual(repr(vm), orig)

    # ── 6, 7, 9 covered by MANUFACTURING_OVERLAY_METHODS ───────────

    # ── 10. overlay command labels/types are stable ────────────────

    def test_hinge_cup_overlay_label_type_stable(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            hinge_cup_holes=(DrillHoleVisual(
                panel_identity="P1", x=20.0, y=100.0,
                diameter=35.0, depth=12.0,
            ),),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays[0]["overlay_type"], "hinge_cup_hole")
        self.assertEqual(overlays[0]["visual_type"], "HINGE_CUP_SYMBOL")
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "hinge_cup_hole")
        self.assertEqual(commands[0]["label"], "Hinge cup hole")

        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_hinge_plate_overlay_label_type_stable(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            hinge_plate_positions=(DrillHoleVisual(
                panel_identity="P1", x=30.0, y=50.0,
                diameter=5.0, depth=12.0,
            ),),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays[0]["overlay_type"], "hinge_plate_position")
        self.assertEqual(overlays[0]["visual_type"], "HINGE_PLATE_SYMBOL")
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "hinge_plate_position")
        self.assertEqual(commands[0]["label"], "Hinge plate position")

        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_hinge_cup_overlay_fields_match_drill_hole_schema(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            hinge_cup_holes=(DrillHoleVisual(
                panel_identity="P1", face="LEFT",
                x=20.0, y=100.0, z=5.0,
                diameter=35.0, depth=12.0,
                axis="Z", is_through=True,
                source_operation_reference="op-hc",
            ),),
        )
        o = SceneRenderer.build_visual_overlays(vm)[0]
        self.assertEqual(o["panel_identity"], "P1")
        self.assertEqual(o["face"], "LEFT")
        self.assertEqual(o["x"], 20.0)
        self.assertEqual(o["y"], 100.0)
        self.assertEqual(o["z"], 5.0)
        self.assertEqual(o["diameter"], 35.0)
        self.assertEqual(o["depth"], 12.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], True)
        self.assertEqual(o["source_operation_reference"], "op-hc")

    def test_hinge_plate_overlay_fields_match_drill_hole_schema(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            hinge_plate_positions=(DrillHoleVisual(
                panel_identity="P2", face="RIGHT",
                x=30.0, y=50.0, z=0.0,
                diameter=5.0, depth=12.0,
                axis="Z", is_through=False,
                source_operation_reference="op-hp",
            ),),
        )
        o = SceneRenderer.build_visual_overlays(vm)[0]
        self.assertEqual(o["panel_identity"], "P2")
        self.assertEqual(o["face"], "RIGHT")
        self.assertEqual(o["x"], 30.0)
        self.assertEqual(o["y"], 50.0)
        self.assertEqual(o["z"], 0.0)
        self.assertEqual(o["diameter"], 5.0)
        self.assertEqual(o["depth"], 12.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], False)
        self.assertEqual(o["source_operation_reference"], "op-hp")

    # ── 11. all prior overlay types remain unchanged ───────────────

    def test_all_prior_overlays_unchanged_when_hinge_fields_present(self):
        """All prior manufacturing overlays identical with or without hinge fields."""
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        mf = DrillHoleVisual(panel_identity="P1", x=37.0, y=100.0,
                              hardware_intent="INTENT_MINIFIX_15")
        cf = DrillHoleVisual(panel_identity="P1", x=37.0, y=50.0,
                              hardware_intent="INTENT_CONFIRMAT_50")
        sp = DrillHoleVisual(panel_identity="P1", x=2.0, y=64.0,
                              hardware_intent="INTENT_SHELF_PIN")
        ds = DrillHoleVisual(panel_identity="P1", x=10.0, y=50.0,
                              hardware_intent="INTENT_DRAWER_SLIDE")

        vm_base = VisualMetadata(
            minifix_holes=(mf,), confirmat_holes=(cf,),
            shelf_pin_holes=(sp,), drawer_slide_holes=(ds,),
        )
        vm_ext = VisualMetadata(
            minifix_holes=(mf,), confirmat_holes=(cf,),
            shelf_pin_holes=(sp,), drawer_slide_holes=(ds,),
            hinge_cup_holes = (DrillHoleVisual(hardware_intent="INTENT_HINGE"),),
            hinge_plate_positions = (DrillHoleVisual(hardware_intent="INTENT_HINGE"),),
        )

        b = SceneRenderer.build_visual_overlays(vm_base)
        e = SceneRenderer.build_visual_overlays(vm_ext)

        for ot in ("minifix_hole", "confirmat_hole", "shelf_pin_hole", "drawer_slide_hole"):
            self.assertEqual(
                [o for o in b if o["overlay_type"] == ot],
                [o for o in e if o["overlay_type"] == ot],
                msg=f"Overlay type '{ot}' changed when hinge fields added",
            )

        # Hinge overlays present
        self.assertEqual(len([o for o in e if o["overlay_type"] == "hinge_cup_hole"]), 1)
        self.assertEqual(len([o for o in e if o["overlay_type"] == "hinge_plate_position"]), 1)

    # ═══════════════════════════════════════════════════════════════
    # HFG-3D — Screw Holes and Manufacturing Overlay Completion
    # ═══════════════════════════════════════════════════════════════

    # ── 1. screw_holes produce overlay commands ────────────────────

    def test_screw_holes_produce_overlay_commands(self):
        """screw_holes in VisualMetadata produce overlay dicts and viewport commands."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            screw_holes=(
                DrillHoleVisual(
                    panel_identity="panel-G",
                    face="LEFT",
                    x=15.0, y=80.0, z=0.0,
                    diameter=3.5, depth=10.0,
                    axis="Z",
                    is_through=False,
                    source_operation_reference="op-screw-001",
                    hardware_intent="INTENT_SCREW",
                ),
            ),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "screw_hole")
        self.assertEqual(overlays[0]["visual_type"], "SCREW_SYMBOL")
        self.assertEqual(overlays[0]["panel_identity"], "panel-G")
        self.assertEqual(overlays[0]["face"], "LEFT")
        self.assertEqual(overlays[0]["x"], 15.0)
        self.assertEqual(overlays[0]["y"], 80.0)
        self.assertEqual(overlays[0]["diameter"], 3.5)
        self.assertEqual(overlays[0]["depth"], 10.0)

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "screw_hole")
        self.assertEqual(commands[0]["panel_identity"], "panel-G")
        self.assertEqual(commands[0]["diameter"], 3.5)

    # ── 2. empty fields produce no overlays ────────────────────────

    def test_empty_screw_holes_produce_no_overlays(self):
        """Empty screw_holes produce no overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(screw_holes=())
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)
        self.assertEqual(overlays, [])
        self.assertEqual(commands, [])

    def test_default_metadata_produces_no_screw_overlays(self):
        """Default VisualMetadata produces no screw_hole overlays."""
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata()
        overlays = SceneRenderer.build_visual_overlays(vm)
        sc = sum(1 for o in overlays if o.get("overlay_type") == "screw_hole")
        self.assertEqual(sc, 0)

    # ── 3. existing overlays still work ────────────────────────────

    def test_existing_overlays_still_work_with_screw_holes(self):
        """Existing overlays unchanged when screw_holes are present."""
        from scene_graph.metadata import (
            DrillHoleVisual,
            EdgeBandVisual,
            GrooveVisual,
            HardwareMarkerVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            edge_banding=(EdgeBandVisual(side="TOP", banding="ABS"),),
            drill_holes=(DrillHoleVisual(panel_identity="P1", x=10.0, y=20.0),),
            grooves=(GrooveVisual(panel_identity="BACK-1", face="BACK", depth=8.0),),
            hardware_markers=(HardwareMarkerVisual(
                panel_identity="door-01", sku="HINGE_BLUM", quantity=2,
            ),),
            screw_holes=(DrillHoleVisual(hardware_intent="INTENT_SCREW"),),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)

        for ot in ("edge_banding", "drill_hole", "groove", "hardware_marker", "screw_hole"):
            self.assertEqual(len([o for o in overlays if o["overlay_type"] == ot]), 1)

    # ── 4. renderer does not mutate VisualMetadata ─────────────────

    def test_screw_overlay_does_not_mutate_metadata(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=15.0, y=80.0, diameter=3.5,
            hardware_intent="INTENT_SCREW",
        )
        vm = VisualMetadata(screw_holes=(hole,))
        orig = repr(vm)
        SceneRenderer.build_visual_overlays(vm)
        self.assertEqual(repr(vm), orig)

    # ── 5, 6, 7, 8 covered by MANUFACTURING_OVERLAY_METHODS ────────

    # ── 9. overlay command label/type is stable ────────────────────

    def test_screw_overlay_label_type_stable(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            screw_holes=(DrillHoleVisual(
                panel_identity="P1", x=15.0, y=80.0,
                diameter=3.5, depth=10.0,
            ),),
        )
        overlays = SceneRenderer.build_visual_overlays(vm)
        commands = SceneRenderer.build_viewport_overlay_commands(overlays)

        self.assertEqual(overlays[0]["overlay_type"], "screw_hole")
        self.assertEqual(overlays[0]["visual_type"], "SCREW_SYMBOL")
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["overlay_type"], "screw_hole")
        self.assertEqual(commands[0]["label"], "Screw hole")

        overlays_2 = SceneRenderer.build_visual_overlays(vm)
        commands_2 = SceneRenderer.build_viewport_overlay_commands(overlays_2)
        self.assertEqual(overlays, overlays_2)
        self.assertEqual(commands, commands_2)

    def test_screw_overlay_fields_match_drill_hole_schema(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        vm = VisualMetadata(
            screw_holes=(DrillHoleVisual(
                panel_identity="P3", face="RIGHT",
                x=15.0, y=80.0, z=2.0,
                diameter=3.5, depth=10.0,
                axis="Z", is_through=True,
                source_operation_reference="op-sc",
            ),),
        )
        o = SceneRenderer.build_visual_overlays(vm)[0]
        self.assertEqual(o["panel_identity"], "P3")
        self.assertEqual(o["face"], "RIGHT")
        self.assertEqual(o["x"], 15.0)
        self.assertEqual(o["y"], 80.0)
        self.assertEqual(o["z"], 2.0)
        self.assertEqual(o["diameter"], 3.5)
        self.assertEqual(o["depth"], 10.0)
        self.assertEqual(o["axis"], "Z")
        self.assertEqual(o["is_through"], True)
        self.assertEqual(o["source_operation_reference"], "op-sc")

    # ── 10. all prior overlays unchanged when screw_holes present ──

    def test_all_prior_overlays_unchanged_when_screw_holes_present(self):
        """All prior manufacturing overlays identical with or without screw_holes."""
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        mf = DrillHoleVisual(panel_identity="P1", x=37.0, y=100.0,
                              hardware_intent="INTENT_MINIFIX_15")
        cf = DrillHoleVisual(panel_identity="P1", x=37.0, y=50.0,
                              hardware_intent="INTENT_CONFIRMAT_50")
        sp = DrillHoleVisual(panel_identity="P1", x=2.0, y=64.0,
                              hardware_intent="INTENT_SHELF_PIN")
        ds = DrillHoleVisual(panel_identity="P1", x=10.0, y=50.0,
                              hardware_intent="INTENT_DRAWER_SLIDE")
        hc = DrillHoleVisual(panel_identity="P1", x=20.0, y=100.0,
                              hardware_intent="INTENT_HINGE")
        hp = DrillHoleVisual(panel_identity="P1", x=30.0, y=50.0,
                              hardware_intent="INTENT_HINGE")

        vm_base = VisualMetadata(
            minifix_holes=(mf,), confirmat_holes=(cf,),
            shelf_pin_holes=(sp,), drawer_slide_holes=(ds,),
            hinge_cup_holes=(hc,), hinge_plate_positions=(hp,),
        )
        vm_ext = VisualMetadata(
            minifix_holes=(mf,), confirmat_holes=(cf,),
            shelf_pin_holes=(sp,), drawer_slide_holes=(ds,),
            hinge_cup_holes=(hc,), hinge_plate_positions=(hp,),
            screw_holes=(DrillHoleVisual(hardware_intent="INTENT_SCREW"),),
        )

        b = SceneRenderer.build_visual_overlays(vm_base)
        e = SceneRenderer.build_visual_overlays(vm_ext)

        for ot in ("minifix_hole", "confirmat_hole", "shelf_pin_hole",
                   "drawer_slide_hole", "hinge_cup_hole", "hinge_plate_position"):
            self.assertEqual(
                [o for o in b if o["overlay_type"] == ot],
                [o for o in e if o["overlay_type"] == ot],
                msg=f"Overlay type '{ot}' changed when screw_holes added",
            )

        self.assertEqual(len([o for o in e if o["overlay_type"] == "screw_hole"]), 1)

    # ── 11. All manufacturing drilling fields are covered ──────────

    def test_all_manufacturing_drill_fields_covered_by_overlays(self):
        """Every VisualMetadata manufacturing drilling field has an overlay type.

        This is the HFG-3 completion gate: all 7 manufacturing drill
        fields in VisualMetadata must produce distinct overlays.
        """
        from scene_graph.metadata import (
            DrillHoleVisual,
            VisualMetadata,
        )
        from scene_graph.renderer import SceneRenderer

        hole = DrillHoleVisual(
            panel_identity="P1", x=10.0, y=10.0,
            hardware_intent="INTENT_MINIFIX_15",
        )

        vm = VisualMetadata(
            minifix_holes=(hole,),
            confirmat_holes=(hole,),
            shelf_pin_holes=(hole,),
            drawer_slide_holes=(hole,),
            hinge_cup_holes=(hole,),
            hinge_plate_positions=(hole,),
            screw_holes=(hole,),
        )

        overlays = SceneRenderer.build_visual_overlays(vm)

        expected_overlay_types = {
            "minifix_hole",
            "confirmat_hole",
            "shelf_pin_hole",
            "drawer_slide_hole",
            "hinge_cup_hole",
            "hinge_plate_position",
            "screw_hole",
        }

        produced = {o["overlay_type"] for o in overlays}

        missing = expected_overlay_types - produced
        extra = produced - expected_overlay_types
        self.assertSetEqual(
            expected_overlay_types, produced,
            msg=(
                f"Missing overlay types: {missing}. "
                f"Extra overlay types: {extra}. "
                f"All 7 manufacturing drill fields should produce overlays."
            ),
        )


class TestHfg4A1UnifiedHoleStyleDecoration(unittest.TestCase):
    """HFG-4A.1 — Unified Hole Style Decoration.

    Every hole viewport command produced by SceneRenderer must carry
    a hole_style key. Non-hole commands must NOT carry hole_style.
    Specific overlay types resolve to specific style strings.
    overlay_type values remain unchanged.
    """

    # ── Helper: build a single viewport command for a given overlay_type

    @staticmethod
    def _command_for(overlay_type, is_through=False, **kw):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        field_map = {
            "drill_hole": "drill_holes",
            "minifix_hole": "minifix_holes",
            "confirmat_hole": "confirmat_holes",
            "shelf_pin_hole": "shelf_pin_holes",
            "drawer_slide_hole": "drawer_slide_holes",
            "hinge_cup_hole": "hinge_cup_holes",
            "screw_hole": "screw_holes",
            "hinge_plate_position": "hinge_plate_positions",
        }
        hole = DrillHoleVisual(
            panel_identity="P1", x=10.0, y=10.0,
            is_through=is_through, **kw,
        )
        vm = VisualMetadata(**{field_map[overlay_type]: (hole,)})
        overlays = SceneRenderer.build_visual_overlays(vm)
        cmds = SceneRenderer.build_viewport_overlay_commands(overlays)
        return cmds[0] if cmds else None

    # ── 1. All hole commands have hole_style ───────────────────────

    def test_drill_hole_has_hole_style(self):
        cmd = self._command_for("drill_hole")
        self.assertIn("hole_style", cmd)

    def test_minifix_hole_has_hole_style(self):
        cmd = self._command_for("minifix_hole")
        self.assertIn("hole_style", cmd)

    def test_confirmat_hole_has_hole_style(self):
        cmd = self._command_for("confirmat_hole")
        self.assertIn("hole_style", cmd)

    def test_shelf_pin_hole_has_hole_style(self):
        cmd = self._command_for("shelf_pin_hole")
        self.assertIn("hole_style", cmd)

    def test_drawer_slide_hole_has_hole_style(self):
        cmd = self._command_for("drawer_slide_hole")
        self.assertIn("hole_style", cmd)

    def test_hinge_cup_hole_has_hole_style(self):
        cmd = self._command_for("hinge_cup_hole")
        self.assertIn("hole_style", cmd)

    def test_screw_hole_has_hole_style(self):
        cmd = self._command_for("screw_hole")
        self.assertIn("hole_style", cmd)

    # ── 2. Non-hole commands do NOT have hole_style ────────────────

    def test_edge_banding_no_hole_style(self):
        from scene_graph.metadata import EdgeBandVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(edge_banding=(EdgeBandVisual(side="TOP", banding="ABS"),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("hole_style", cmds[0])

    def test_groove_no_hole_style(self):
        from scene_graph.metadata import GrooveVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(grooves=(GrooveVisual(face="BACK", depth=8.0),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("hole_style", cmds[0])

    def test_hardware_marker_no_hole_style(self):
        from scene_graph.metadata import HardwareMarkerVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(hardware_markers=(
            HardwareMarkerVisual(panel_identity="P1", sku="HINGE", quantity=1),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("hole_style", cmds[0])

    def test_hinge_plate_position_no_hole_style(self):
        cmd = self._command_for("hinge_plate_position")
        self.assertNotIn("hole_style", cmd)

    # ── 3. Correct style values ───────────────────────────────────

    def test_hinge_cup_hole_style_is_cup(self):
        cmd = self._command_for("hinge_cup_hole")
        self.assertEqual(cmd["hole_style"], "cup")

    def test_screw_hole_style_is_pilot(self):
        cmd = self._command_for("screw_hole")
        self.assertEqual(cmd["hole_style"], "pilot")

    def test_blind_hole_style_is_blind(self):
        for ot in ("drill_hole", "minifix_hole", "confirmat_hole",
                   "shelf_pin_hole", "drawer_slide_hole"):
            cmd = self._command_for(ot, is_through=False)
            self.assertEqual(cmd["hole_style"], "blind",
                             msg=f"{ot} with is_through=False")

    def test_through_hole_style_is_through(self):
        for ot in ("drill_hole", "minifix_hole", "confirmat_hole",
                   "shelf_pin_hole", "drawer_slide_hole"):
            cmd = self._command_for(ot, is_through=True)
            self.assertEqual(cmd["hole_style"], "through",
                             msg=f"{ot} with is_through=True")

    # ── 4. overlay_type remains unchanged ─────────────────────────

    def test_overlay_types_preserved_with_hole_style(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        hole = DrillHoleVisual(panel_identity="P1", x=10.0, y=10.0)
        vm = VisualMetadata(
            drill_holes=(hole,),
            minifix_holes=(hole,),
            confirmat_holes=(hole,),
            shelf_pin_holes=(hole,),
            drawer_slide_holes=(hole,),
            hinge_cup_holes=(hole,),
            screw_holes=(hole,),
        )
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        for cmd in cmds:
            ot = cmd["overlay_type"]
            if ot in ("edge_banding", "groove", "hardware_marker", "hinge_plate_position"):
                continue
            self.assertIn("hole_style", cmd,
                          msg=f"Missing hole_style for {ot}")
            self.assertEqual(cmd["overlay_type"], ot,
                             msg=f"overlay_type should remain {ot}")

    # ── 5. All hole commands have drill_direction ──────────────────

    def test_drill_hole_has_drill_direction(self):
        cmd = self._command_for("drill_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    def test_minifix_hole_has_drill_direction(self):
        cmd = self._command_for("minifix_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    def test_confirmat_hole_has_drill_direction(self):
        cmd = self._command_for("confirmat_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    def test_shelf_pin_hole_has_drill_direction(self):
        cmd = self._command_for("shelf_pin_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    def test_drawer_slide_hole_has_drill_direction(self):
        cmd = self._command_for("drawer_slide_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    def test_hinge_cup_hole_has_drill_direction(self):
        cmd = self._command_for("hinge_cup_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    def test_screw_hole_has_drill_direction(self):
        cmd = self._command_for("screw_hole", face="LEFT")
        self.assertIn("drill_direction", cmd)

    # ── 6. Non-hole commands do NOT have drill_direction ───────────

    def test_edge_banding_no_drill_direction(self):
        from scene_graph.metadata import EdgeBandVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(edge_banding=(EdgeBandVisual(side="TOP", banding="ABS"),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("drill_direction", cmds[0])

    def test_groove_no_drill_direction(self):
        from scene_graph.metadata import GrooveVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(grooves=(GrooveVisual(face="BACK", depth=8.0),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("drill_direction", cmds[0])

    def test_hardware_marker_no_drill_direction(self):
        from scene_graph.metadata import HardwareMarkerVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(hardware_markers=(
            HardwareMarkerVisual(panel_identity="P1", sku="HINGE", quantity=1),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("drill_direction", cmds[0])

    def test_hinge_plate_position_no_drill_direction(self):
        cmd = self._command_for("hinge_plate_position")
        self.assertNotIn("drill_direction", cmd)

    # ── 7. Face normalization ─────────────────────────────────────

    def test_drill_direction_front_upper(self):
        cmd = self._command_for("drill_hole", face="FRONT")
        self.assertEqual(cmd["drill_direction"], "front")

    def test_drill_direction_front_lower(self):
        cmd = self._command_for("drill_hole", face="front")
        self.assertEqual(cmd["drill_direction"], "front")

    def test_drill_direction_back_title(self):
        cmd = self._command_for("drill_hole", face="Back")
        self.assertEqual(cmd["drill_direction"], "back")

    def test_drill_direction_left(self):
        cmd = self._command_for("drill_hole", face="LEFT")
        self.assertEqual(cmd["drill_direction"], "left")

    def test_drill_direction_right(self):
        cmd = self._command_for("drill_hole", face="RIGHT")
        self.assertEqual(cmd["drill_direction"], "right")

    def test_drill_direction_top(self):
        cmd = self._command_for("drill_hole", face="TOP")
        self.assertEqual(cmd["drill_direction"], "top")

    def test_drill_direction_bottom(self):
        cmd = self._command_for("drill_hole", face="BOTTOM")
        self.assertEqual(cmd["drill_direction"], "bottom")

    def test_drill_direction_empty(self):
        cmd = self._command_for("drill_hole", face="")
        self.assertEqual(cmd["drill_direction"], "unknown")

    def test_drill_direction_invalid(self):
        cmd = self._command_for("drill_hole", face="INVALID_FACE")
        self.assertEqual(cmd["drill_direction"], "unknown")

    # ── 8. Existing face value preserved ──────────────────────────

    def test_drill_direction_face_field_preserved(self):
        cmd = self._command_for("drill_hole", face="LEFT")
        self.assertEqual(cmd["face"], "LEFT",
                         msg="command['face'] must retain original casing")

    # ── 9. hole_style from HFG-4A unchanged -----------------------

    def test_hole_style_still_present_with_drill_direction(self):
        cmd = self._command_for("minifix_hole", is_through=True)
        self.assertIn("hole_style", cmd)
        self.assertEqual(cmd["hole_style"], "through")

    # ── 10. overlay_type preserved ---------------------------------

    def test_overlay_type_preserved_with_drill_direction(self):
        cmd = self._command_for("screw_hole")
        self.assertEqual(cmd["overlay_type"], "screw_hole")

    # ── 11. All hole commands have hole_depth + hole_depth_mode ────

    def test_drill_hole_has_hole_depth(self):
        cmd = self._command_for("drill_hole", depth=10.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    def test_minifix_hole_has_hole_depth(self):
        cmd = self._command_for("minifix_hole", depth=12.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    def test_confirmat_hole_has_hole_depth(self):
        cmd = self._command_for("confirmat_hole", depth=50.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    def test_shelf_pin_hole_has_hole_depth(self):
        cmd = self._command_for("shelf_pin_hole", depth=10.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    def test_drawer_slide_hole_has_hole_depth(self):
        cmd = self._command_for("drawer_slide_hole", depth=12.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    def test_hinge_cup_hole_has_hole_depth(self):
        cmd = self._command_for("hinge_cup_hole", depth=12.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    def test_screw_hole_has_hole_depth(self):
        cmd = self._command_for("screw_hole", depth=10.0)
        self.assertIn("hole_depth", cmd)
        self.assertIn("hole_depth_mode", cmd)

    # ── 12. Non-hole commands do NOT have hole_depth/hole_depth_mode

    def test_edge_banding_no_hole_depth(self):
        from scene_graph.metadata import EdgeBandVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(edge_banding=(EdgeBandVisual(side="TOP", banding="ABS"),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("hole_depth", cmds[0])
        self.assertNotIn("hole_depth_mode", cmds[0])

    def test_groove_no_hole_depth(self):
        from scene_graph.metadata import GrooveVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(grooves=(GrooveVisual(face="BACK", depth=8.0),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("hole_depth", cmds[0])
        self.assertNotIn("hole_depth_mode", cmds[0])

    def test_hardware_marker_no_hole_depth(self):
        from scene_graph.metadata import HardwareMarkerVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer
        vm = VisualMetadata(hardware_markers=(
            HardwareMarkerVisual(panel_identity="P1", sku="HINGE", quantity=1),))
        cmds = SceneRenderer.build_viewport_overlay_commands(
            SceneRenderer.build_visual_overlays(vm))
        self.assertNotIn("hole_depth", cmds[0])
        self.assertNotIn("hole_depth_mode", cmds[0])

    def test_hinge_plate_position_no_hole_depth(self):
        cmd = self._command_for("hinge_plate_position")
        self.assertNotIn("hole_depth", cmd)
        self.assertNotIn("hole_depth_mode", cmd)

    # ── 13. Through hole depth resolution ─────────────────────────

    def test_through_hole_depth_zero(self):
        cmd = self._command_for("drill_hole", is_through=True, depth=99.0)
        self.assertEqual(cmd["hole_depth"], 0.0)

    def test_through_hole_depth_mode(self):
        cmd = self._command_for("drill_hole", is_through=True, depth=99.0)
        self.assertEqual(cmd["hole_depth_mode"], "through")

    # ── 14. Blind hole depth resolution ───────────────────────────

    def test_blind_hole_depth_positive(self):
        cmd = self._command_for("drill_hole", is_through=False, depth=12.5)
        self.assertEqual(cmd["hole_depth"], 12.5)

    def test_blind_hole_depth_mode(self):
        cmd = self._command_for("drill_hole", is_through=False, depth=12.5)
        self.assertEqual(cmd["hole_depth_mode"], "blind")

    # ── 15. Missing depth returns unspecified ──────────────────────

    def test_missing_depth_returns_unspecified(self):
        cmd = self._command_for("drill_hole")  # no depth kwarg
        self.assertEqual(cmd["hole_depth"], 0.0)
        self.assertEqual(cmd["hole_depth_mode"], "unspecified")

    # ── 16. Negative depth ────────────────────────────────────────

    def test_negative_depth_returns_unspecified(self):
        cmd = self._command_for("drill_hole", depth=-3)
        self.assertEqual(cmd["hole_depth"], 0.0)
        self.assertEqual(cmd["hole_depth_mode"], "unspecified")

    # ── 17. Existing fields unchanged ──────────────────────────────

    def test_overlay_type_unchanged_with_hole_depth(self):
        cmd = self._command_for("minifix_hole", depth=12.0)
        self.assertEqual(cmd["overlay_type"], "minifix_hole")

    def test_face_unchanged_with_hole_depth(self):
        cmd = self._command_for("drill_hole", face="LEFT", depth=10.0)
        self.assertEqual(cmd["face"], "LEFT")

    def test_hole_style_unchanged_with_hole_depth(self):
        cmd = self._command_for("hinge_cup_hole", depth=12.0)
        self.assertEqual(cmd["hole_style"], "cup")

    def test_drill_direction_unchanged_with_hole_depth(self):
        cmd = self._command_for("drill_hole", face="TOP", depth=10.0)
        self.assertEqual(cmd["drill_direction"], "top")


if __name__ == "__main__":
    unittest.main()
