# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Dashboard
# Manufacturing Review Summary Contract Tests
#
# Verifies:
# - empty input returns zero summary
# - high/medium/low priority counts read from review_priority
# - category counts read from review_category (not overlay_type)
# - overlay_type alone does not increment category counts
# - top_priority_items prefer high priority
# - values are read from command fields only
# - no forbidden imports
# - no engine/workflow naming
# - deterministic
# - no input mutation
# - no duplicate overlay_type category mapping in source
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import sys
import types
import unittest


class TestManufacturingReviewSummaryContract(unittest.TestCase):
    """Verify manufacturing review summary contract."""

    _rs = None

    @classmethod
    def _import_once(cls):
        if cls._rs is not None:
            return cls._rs

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

        rs = _load("factory_dashboard.review_summary",
                    "factory_dashboard/review_summary.py")
        cls._rs = rs
        return rs

    @classmethod
    def tearDownClass(cls):
        for key in list(sys.modules):
            if key.startswith("factory_dashboard"):
                del sys.modules[key]

    # ── Rule 1: empty input returns zero summary ───────────────────

    def test_none_commands_returns_zero_summary(self):
        """None commands return all-zero summary."""
        rs = self._import_once()
        s = rs.build_manufacturing_review_summary(None)
        self.assertEqual(s.total_review_items, 0)
        self.assertEqual(s.high_priority_count, 0)
        self.assertEqual(s.medium_priority_count, 0)
        self.assertEqual(s.low_priority_count, 0)
        self.assertEqual(s.drilling_count, 0)
        self.assertEqual(s.hardware_count, 0)
        self.assertEqual(s.edge_banding_count, 0)
        self.assertEqual(s.groove_count, 0)
        self.assertEqual(len(s.top_priority_items), 0)

    def test_empty_list_returns_zero_summary(self):
        """Empty list returns all-zero summary."""
        rs = self._import_once()
        s = rs.build_manufacturing_review_summary([])
        self.assertEqual(s.total_review_items, 0)

    # ── Rule 2: priority counts read from review_priority ──────────

    def test_priority_counts(self):
        """High/medium/low counts from review_priority field."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "medium", "review_category": "hardware"},
            {"review_priority": "low", "review_category": "edge_banding"},
            {"review_priority": "low", "review_category": "groove"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.total_review_items, 5)
        self.assertEqual(s.high_priority_count, 2)
        self.assertEqual(s.medium_priority_count, 1)
        self.assertEqual(s.low_priority_count, 2)

    # ── Rule 3: category counts read from review_category ──────────

    def test_drilling_count_from_review_category(self):
        """Drilling count from review_category field."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "medium", "review_category": "drilling"},
            {"review_priority": "low", "review_category": "drilling"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.drilling_count, 3)

    def test_hardware_count_from_review_category(self):
        """Hardware count from review_category field."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "hardware"},
            {"review_priority": "medium", "review_category": "hardware"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.hardware_count, 2)

    def test_edge_banding_count_from_review_category(self):
        """Edge banding count from review_category field."""
        rs = self._import_once()
        commands = [
            {"review_priority": "low", "review_category": "edge_banding"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.edge_banding_count, 1)

    def test_groove_count_from_review_category(self):
        """Groove count from review_category field."""
        rs = self._import_once()
        commands = [
            {"review_priority": "low", "review_category": "groove"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.groove_count, 1)

    def test_all_categories_together(self):
        """All four category counts computed from review_category values."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "medium", "review_category": "hardware"},
            {"review_priority": "low", "review_category": "edge_banding"},
            {"review_priority": "low", "review_category": "groove"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.drilling_count, 3)
        self.assertEqual(s.hardware_count, 1)
        self.assertEqual(s.edge_banding_count, 1)
        self.assertEqual(s.groove_count, 1)
        self.assertEqual(s.total_review_items, 6)

    # ── Rule 4: overlay_type alone does not cause category counts ──

    def test_overlay_type_alone_does_not_increment_category(self):
        """Commands with only overlay_type (no review_category) do not
        contribute to category counts — the mapping from overlay_type
        to category is SceneRenderer's responsibility."""
        rs = self._import_once()
        commands = [
            {"overlay_type": "drill_hole"},
            {"overlay_type": "hinge_plate_position"},
            {"overlay_type": "edge_banding"},
            {"overlay_type": "groove"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        # No review_priority or review_category → total remains 0
        self.assertEqual(s.total_review_items, 0)
        self.assertEqual(s.drilling_count, 0)
        self.assertEqual(s.hardware_count, 0)
        self.assertEqual(s.edge_banding_count, 0)
        self.assertEqual(s.groove_count, 0)

    def test_review_category_without_priority_still_counts_category(self):
        """review_category alone increments category counts even without priority."""
        rs = self._import_once()
        commands = [
            {"review_category": "drilling"},
            {"review_category": "hardware"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.total_review_items, 2)
        self.assertEqual(s.drilling_count, 1)
        self.assertEqual(s.hardware_count, 1)
        # No review_priority → priority counts stay 0
        self.assertEqual(s.high_priority_count, 0)
        self.assertEqual(s.medium_priority_count, 0)
        self.assertEqual(s.low_priority_count, 0)

    # ── Rule 5: top_priority_items prefer high priority ────────────

    def test_top_priority_items_high_first(self):
        """top_priority_items lists high priority before medium before low."""
        rs = self._import_once()
        commands = [
            {"review_priority": "low", "review_category": "groove",
             "label": "groove-1"},
            {"review_priority": "high", "review_category": "drilling",
             "label": "drill-1"},
            {"review_priority": "medium", "review_category": "drilling",
             "label": "minifix-1"},
            {"review_priority": "high", "review_category": "drilling",
             "label": "hinge-1"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        priorities = [p for _, p in s.top_priority_items]
        high_indices = [i for i, p in enumerate(priorities) if p == "high"]
        medium_indices = [i for i, p in enumerate(priorities) if p == "medium"]
        low_indices = [i for i, p in enumerate(priorities) if p == "low"]
        if high_indices and medium_indices:
            self.assertLess(max(high_indices), min(medium_indices))
        if medium_indices and low_indices:
            self.assertLess(max(medium_indices), min(low_indices))

    def test_top_priority_items_include_label(self):
        """top_priority_items uses label, panel_identity, or source_reference."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling",
             "label": "Panel-42", "panel_identity": "PID-42"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(len(s.top_priority_items), 1)
        item_label, priority = s.top_priority_items[0]
        self.assertEqual(item_label, "Panel-42")
        self.assertEqual(priority, "high")

    def test_top_priority_items_fallback_to_panel_identity(self):
        """Falls back to panel_identity when label is missing."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling",
             "panel_identity": "PID-99"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.top_priority_items[0][0], "PID-99")

    def test_top_priority_items_fallback_to_source_reference(self):
        """Falls back to source_reference when label and panel_identity missing."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling",
             "source_reference": "SRC-77"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.top_priority_items[0][0], "SRC-77")

    # ── Rule 6: values read from command fields only ───────────────

    def test_no_review_priority_means_not_counted_as_priority(self):
        """Command without review_priority does not affect priority counts."""
        rs = self._import_once()
        commands = [
            {"review_category": "drilling"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.total_review_items, 1)
        self.assertEqual(s.high_priority_count, 0)
        self.assertEqual(s.drilling_count, 1)

    def test_no_review_fields_skips_command(self):
        """Command without review_priority or review_category is skipped."""
        rs = self._import_once()
        commands = [
            {"overlay_type": "drill_hole"},
            {"some_field": "value"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(s.total_review_items, 0)

    # ── Rule 7: deterministic ──────────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "medium", "review_category": "drilling"},
            {"review_priority": "low", "review_category": "edge_banding"},
        ]
        r1 = rs.build_manufacturing_review_summary(commands)
        r2 = rs.build_manufacturing_review_summary(commands)
        self.assertEqual(r1, r2)

    # ── Rule 8: no input mutation ──────────────────────────────────

    def test_no_input_mutation(self):
        """Original command list is not modified."""
        rs = self._import_once()
        commands = [{"review_priority": "high", "review_category": "drilling"}]
        original = repr(commands)
        rs.build_manufacturing_review_summary(commands)
        self.assertEqual(repr(commands), original)

    # ── Rule 9: no forbidden imports ───────────────────────────────

    def test_no_forbidden_imports(self):
        """review_summary.py must not import domain/manufacturing/FreeCAD/Qt."""
        with open("factory_dashboard/review_summary.py") as f:
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
                msg=f"review_summary.py must not import '{token}'",
            )

    # ── Rule 10: no engine/workflow naming ─────────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the function."""
        rs = self._import_once()
        func = rs.build_manufacturing_review_summary
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

    # ── Rule 11: summary dataclass is frozen ───────────────────────

    def test_summary_is_frozen(self):
        """ManufacturingReviewSummary is a frozen dataclass."""
        rs = self._import_once()
        self.assertTrue(hasattr(rs.ManufacturingReviewSummary, "__dataclass_fields__"))
        with self.assertRaises(Exception):
            s = rs.ManufacturingReviewSummary()
            s.total_review_items = 99

    # ── Rule 12: no duplicate overlay_type category mapping ────────

    def test_no_duplicate_category_mapping_in_source(self):
        """review_summary.py must not contain overlay_type category classification
        sets or functions — SceneRenderer's review_category is the single source."""
        with open("factory_dashboard/review_summary.py") as f:
            src = f.read()
        forbidden_patterns = [
            "_DRILLING_TYPES",
            "_HARDWARE_TYPES",
            "_EDGE_BANDING_TYPES",
            "_GROOVE_TYPES",
            "_category_from_overlay_type",
            "overlay_type.*drill_hole",
            "overlay_type.*hinge",
        ]
        for pattern in forbidden_patterns:
            self.assertNotIn(
                pattern, src,
                msg=f"review_summary.py must not contain '{pattern}' — "
                    f"use SceneRenderer's review_category instead",
            )

    # ── Rule 13: total is sum of categories ────────────────────────

    def test_total_summary_integrity(self):
        """Total items equals sum of category counts when all categorised."""
        rs = self._import_once()
        commands = [
            {"review_priority": "high", "review_category": "drilling"},
            {"review_priority": "medium", "review_category": "drilling"},
            {"review_priority": "high", "review_category": "hardware"},
            {"review_priority": "low", "review_category": "edge_banding"},
            {"review_priority": "low", "review_category": "groove"},
        ]
        s = rs.build_manufacturing_review_summary(commands)
        cat_sum = (s.drilling_count + s.hardware_count
                   + s.edge_banding_count + s.groove_count)
        self.assertEqual(s.total_review_items, cat_sum)
