# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Manufacturing Render Review Adapter Contract Tests
#
# Verifies:
# - extracts rendering metadata from viewport command dicts
# - handles single command and iterable of commands
# - review_priority, review_category, hole_style, drill_direction,
#   hole_depth, hole_depth_mode surfaced
# - missing metadata preserves section with no rows
# - None/empty commands returns empty section
# - no manufacturing logic duplication
# - no raw renderer objects leak
# - deterministic
# - no input mutation
# - no domain/manufacturing/FreeCAD/Qt imports
# - no engine/workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class TestManufacturingRenderReviewAdapterContract(unittest.TestCase):
    """Verify manufacturing render review projection adapter contract."""

    @classmethod
    def _import_adapter(cls):
        """Import modules directly, bypassing package __init__ chain."""
        import importlib.machinery
        import importlib.util

        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        parent = types.ModuleType("ui.configurator_v2")
        parent.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        rm = _load("ui.configurator_v2.read_models", "ui/configurator_v2/read_models.py")
        pa = _load("ui.configurator_v2.projection_adapters", "ui/configurator_v2/projection_adapters.py")
        return rm, pa

    # ── Rule 1: extracts rendering metadata from viewport commands ─

    def test_extracts_review_priority(self):
        """review_priority extracted from viewport command."""
        rm, pa = self._import_adapter()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")

    def test_extracts_review_category(self):
        """review_category extracted from viewport command."""
        rm, pa = self._import_adapter()
        commands = [{"review_category": "drilling", "overlay_type": "drill_hole"}]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Category"), "drilling")

    def test_extracts_hole_style(self):
        """hole_style extracted from viewport command."""
        rm, pa = self._import_adapter()
        commands = [{"hole_style": "through", "overlay_type": "drill_hole"}]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Hole Style"), "through")

    def test_extracts_drill_direction(self):
        """drill_direction extracted from viewport command."""
        rm, pa = self._import_adapter()
        commands = [{"drill_direction": "front", "overlay_type": "drill_hole"}]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Drill Direction"), "front")

    def test_extracts_hole_depth_and_mode(self):
        """hole_depth and hole_depth_mode extracted from viewport command."""
        rm, pa = self._import_adapter()
        commands = [{
            "hole_depth": 15.0,
            "hole_depth_mode": "blind",
            "overlay_type": "drill_hole",
        }]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Hole Depth"), "15.0")
        self.assertEqual(rows.get("Hole Depth Mode"), "blind")

    def test_extracts_all_fields_from_single_command(self):
        """All rendering metadata fields extracted from one command."""
        rm, pa = self._import_adapter()
        commands = [{
            "review_priority": "high",
            "review_category": "drilling",
            "hole_style": "through",
            "drill_direction": "front",
            "hole_depth": 0.0,
            "hole_depth_mode": "through",
            "overlay_type": "drill_hole",
        }]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")
        self.assertEqual(rows.get("Review Category"), "drilling")
        self.assertEqual(rows.get("Hole Style"), "through")
        self.assertEqual(rows.get("Drill Direction"), "front")
        self.assertEqual(rows.get("Hole Depth"), "0.0")
        self.assertEqual(rows.get("Hole Depth Mode"), "through")

    # ── Rule 2: handles single command dict ───────────────────────

    def test_accepts_single_command_dict(self):
        """Single dict (not wrapped in list) is accepted."""
        rm, pa = self._import_adapter()
        command = {"review_priority": "high", "overlay_type": "drill_hole"}
        section = pa.build_manufacturing_render_review_section(command)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")

    # ── Rule 3: missing metadata returns empty section ────────────

    def test_no_render_fields_returns_empty_section(self):
        """Command dict with no known render fields returns empty section."""
        rm, pa = self._import_adapter()
        commands = [{"overlay_type": "drill_hole"}]
        section = pa.build_manufacturing_render_review_section(commands)
        self.assertEqual(len(section.rows), 0)

    # ── Rule 4: None/empty commands returns empty section ──────────

    def test_none_commands_returns_empty_section(self):
        """None source returns empty section with no rows."""
        rm, pa = self._import_adapter()
        section = pa.build_manufacturing_render_review_section(None)
        self.assertEqual(len(section.rows), 0)

    def test_empty_list_returns_empty_section(self):
        """Empty list returns empty section with no rows."""
        rm, pa = self._import_adapter()
        section = pa.build_manufacturing_render_review_section([])
        self.assertEqual(len(section.rows), 0)

    # ── Rule 5: aggregates values across multiple commands ────────

    def test_aggregates_priority_values_across_commands(self):
        """Multiple priority values collected across commands."""
        rm, pa = self._import_adapter()
        commands = [
            {"review_priority": "high", "overlay_type": "minifix_hole"},
            {"review_priority": "medium", "overlay_type": "drill_hole"},
        ]
        section = pa.build_manufacturing_render_review_section(commands)
        rows = dict(section.rows)
        self.assertIn("high", rows.get("Review Priority", ""))
        self.assertIn("medium", rows.get("Review Priority", ""))

    # ── Rule 6: no raw rendering objects leak ─────────────────────

    def test_no_raw_renderer_objects_leak(self):
        """Output ReviewSectionReadModel contains only string tuples."""
        rm, pa = self._import_adapter()
        commands = [{
            "review_priority": "high",
            "hole_style": "blind",
            "overlay_type": "drill_hole",
        }]
        section = pa.build_manufacturing_render_review_section(commands)
        for row in section.rows:
            self.assertIsInstance(row, tuple)
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[0], str)
            self.assertIsInstance(row[1], str)
        self.assertEqual(section.section_name, "Rendering Details")

    # ── Rule 7: deterministic ─────────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        rm, pa = self._import_adapter()
        commands = [
            {"review_priority": "high", "overlay_type": "drill_hole"},
            {"review_priority": "medium", "overlay_type": "drill_hole"},
        ]
        r1 = pa.build_manufacturing_render_review_section(commands)
        r2 = pa.build_manufacturing_render_review_section(commands)
        self.assertEqual(r1, r2)

    # ── Rule 8: no input mutation ─────────────────────────────────

    def test_no_input_mutation(self):
        """Original command list is not modified by the function."""
        rm, pa = self._import_adapter()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        original = repr(commands)
        pa.build_manufacturing_render_review_section(commands)
        self.assertEqual(repr(commands), original)

    # ── Rule 9: no domain/manufacturing/FreeCAD/Qt imports ────────

    def test_no_domain_imports(self):
        """projection_adapters.py must not import domain modules."""
        with open("ui/configurator_v2/projection_adapters.py") as f:
            source = f.read()

        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)

        forbidden = [
            "domain.",
            "manufacturing.",
            "cost_intelligence.",
            "commercial_outputs.",
            "optimization.",
            "FreeCAD",
            "QtWidgets",
            "QtCore",
            "QtGui",
        ]
        for token in forbidden:
            self.assertNotIn(
                token,
                import_text,
                msg=f"projection_adapters.py must not import '{token}'",
            )

    # ── Rule 10: no engine/workflow naming ────────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the adapter function."""
        rm, pa = self._import_adapter()
        func = pa.build_manufacturing_render_review_section
        func_name = func.__name__

        forbidden_tokens = [
            "engine", "workflow", "service", "event", "bus",
            "store", "controller", "registry", "renderer",
        ]
        for token in forbidden_tokens:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"Function name '{func_name}' should not contain '{token}'",
            )

    # ── Rule 11: no duplication of rendering logic ────────────────

    def test_no_recomputation_of_values(self):
        """Function does not recompute or derive new values — only consumes."""
        rm, pa = self._import_adapter()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        source = pa.build_manufacturing_render_review_section(commands)
        self.assertEqual(source.rows[0][1], "high")
        # Verify no arithmetic or logic transforms the value
        self.assertIsInstance(source.rows[0][1], str)
