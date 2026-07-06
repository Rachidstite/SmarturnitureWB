# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Dashboard
# Manufacturing Render Dashboard Consumption Contract Tests
#
# Verifies:
# - Dashboard consumes renderer review metadata when commands present
# - Existing dashboard behavior unchanged when commands None/empty
# - Dashboard does not recompute metadata fields
# - No duplicate extraction logic exists in dashboard layer
# - High-priority review items surfaced distinctly
# - No forbidden imports in dashboard_read_model.py
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import sys
import types
import unittest


class TestManufacturingRenderDashboardContract(unittest.TestCase):
    """Verify factory dashboard manufacturing render review consumption."""

    _dd = None

    @classmethod
    def _import_once(cls):
        if cls._dd is not None:
            return cls._dd

        for key in list(sys.modules):
            if key.startswith("factory_dashboard"):
                del sys.modules[key]

        parent = types.ModuleType("factory_dashboard")
        parent.__path__ = ["factory_dashboard"]
        sys.modules["factory_dashboard"] = parent

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        dd = _load("factory_dashboard.dashboard_read_model",
                     "factory_dashboard/dashboard_read_model.py")
        cls._dd = dd
        return dd

    @classmethod
    def tearDownClass(cls):
        for key in list(sys.modules):
            if key.startswith("factory_dashboard"):
                del sys.modules[key]

    # ── Rule 1: dashboard consumes renderer review metadata ────────

    def test_consumes_priority_from_commands(self):
        """review_priority extracted from viewport commands."""
        dd = self._import_once()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsNotNone(section)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")

    def test_consumes_all_render_fields(self):
        """All six rendering metadata fields extracted."""
        dd = self._import_once()
        commands = [{
            "review_priority": "high",
            "review_category": "drilling",
            "hole_style": "blind",
            "drill_direction": "front",
            "hole_depth": 15.0,
            "hole_depth_mode": "blind",
            "overlay_type": "drill_hole",
        }]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsNotNone(section)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")
        self.assertEqual(rows.get("Review Category"), "drilling")
        self.assertEqual(rows.get("Hole Style"), "blind")
        self.assertEqual(rows.get("Drill Direction"), "front")
        self.assertEqual(rows.get("Hole Depth"), "15.0")
        self.assertEqual(rows.get("Hole Depth Mode"), "blind")

    def test_section_name_is_manufacturing_review_details(self):
        """Section is named 'Manufacturing Review Details'."""
        dd = self._import_once()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertEqual(section.section_name, "Manufacturing Review Details")

    def test_accepts_single_dict(self):
        """Single command dict (not wrapped in list) is accepted."""
        dd = self._import_once()
        command = {"review_priority": "high", "overlay_type": "drill_hole"}
        section = dd.build_manufacturing_render_dashboard_section(command)
        self.assertIsNotNone(section)
        rows = dict(section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")

    def test_aggregates_multiple_commands(self):
        """Multiple priority values aggregated across commands."""
        dd = self._import_once()
        commands = [
            {"review_priority": "high", "overlay_type": "minifix_hole"},
            {"review_priority": "medium", "overlay_type": "drill_hole"},
        ]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        rows = dict(section.rows)
        self.assertIn("high", rows.get("Review Priority", ""))
        self.assertIn("medium", rows.get("Review Priority", ""))

    # ── Rule 2: existing behavior unchanged when commands absent ───

    def test_none_commands_returns_none(self):
        """None commands return None (no section added)."""
        dd = self._import_once()
        section = dd.build_manufacturing_render_dashboard_section(None)
        self.assertIsNone(section)

    def test_empty_list_returns_none(self):
        """Empty list of commands returns None."""
        dd = self._import_once()
        section = dd.build_manufacturing_render_dashboard_section([])
        self.assertIsNone(section)

    def test_no_render_fields_returns_none(self):
        """Commands without known render fields return None."""
        dd = self._import_once()
        commands = [{"overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsNone(section)

    # ── Rule 3: dashboard does not recompute metadata fields ───────

    def test_does_not_recompute_hole_style(self):
        """Hole style is read from command, not recomputed from overlay_type."""
        dd = self._import_once()
        # overlay_type alone would imply 'through' if recomputed, but
        # the function should only read the pre-computed hole_style field
        commands = [{"overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsNone(section)  # no hole_style field → no section

    def test_does_not_recompute_drill_direction(self):
        """Drill direction is read from command, not recomputed from face."""
        dd = self._import_once()
        commands = [{"face": "FRONT", "overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsNone(section)  # no drill_direction field → no section

    def test_does_not_recompute_hole_depth(self):
        """Hole depth is read from command, not recomputed."""
        dd = self._import_once()
        commands = [{"depth": 15.0, "is_through": False, "overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsNone(section)  # no hole_depth/hole_depth_mode field → no section

    # ── Rule 4: no duplicate extraction logic ──────────────────────

    def test_source_field_name_straight_through(self):
        """Field name maps directly: the renderer field IS the row label."""
        dd = self._import_once()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIn("Review Priority", dict(section.rows))

        # No inference — the value is exactly what SceneRenderer wrote
        self.assertEqual(dict(section.rows)["Review Priority"], "high")

    # ── Rule 5: high-priority items surfaced distinctly ────────────

    def test_high_priority_surfaced(self):
        """High priority renders as a distinct row value."""
        dd = self._import_once()
        commands = [
            {"review_priority": "high", "overlay_type": "hinge_cup_hole"},
            {"review_priority": "medium", "overlay_type": "drill_hole"},
        ]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        rows = dict(section.rows)
        priority_value = rows.get("Review Priority", "")
        self.assertIn("high", priority_value)

    # ── Rule 6: deterministic ─────────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        dd = self._import_once()
        commands = [
            {"review_priority": "high", "overlay_type": "drill_hole"},
            {"review_priority": "medium", "overlay_type": "drill_hole"},
        ]
        r1 = dd.build_manufacturing_render_dashboard_section(commands)
        r2 = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertEqual(r1, r2)

    # ── Rule 7: no input mutation ─────────────────────────────────

    def test_no_input_mutation(self):
        """Original command list is not modified."""
        dd = self._import_once()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        original = repr(commands)
        dd.build_manufacturing_render_dashboard_section(commands)
        self.assertEqual(repr(commands), original)

    # ── Rule 8: no forbidden imports ───────────────────────────────

    def test_no_forbidden_imports(self):
        """dashboard_read_model.py must not import domain/manufacturing/FreeCAD/Qt."""
        with open("factory_dashboard/dashboard_read_model.py") as f:
            src = f.read()

        import_lines = [
            line for line in src.splitlines()
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
            "factory_operational_intelligence",
            "ui.configurator_v2",
        ]
        for token in forbidden:
            self.assertNotIn(
                token,
                import_text,
                msg=f"dashboard_read_model.py must not import '{token}'",
            )

    # ── Rule 9: no engine/workflow naming ─────────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the function."""
        dd = self._import_once()
        func = dd.build_manufacturing_render_dashboard_section
        func_name = func.__name__

        forbidden_tokens = [
            "engine", "workflow", "service", "event", "bus",
            "store", "controller", "registry", "renderer",
            "ai", "schedule", "chart",
        ]
        for token in forbidden_tokens:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"Function name '{func_name}' should not contain '{token}'",
            )

    # ── Rule 10: output type is FactoryDashboardSection ────────────

    def test_output_is_factory_dashboard_section(self):
        """Returns a FactoryDashboardSection or None."""
        dd = self._import_once()
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        section = dd.build_manufacturing_render_dashboard_section(commands)
        self.assertIsInstance(section, dd.FactoryDashboardSection)
        self.assertIsInstance(section.rows, tuple)
        for row in section.rows:
            self.assertIsInstance(row, tuple)
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[0], str)
            self.assertIsInstance(row[1], str)
