# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Cost Projection Adapter Contract Tests
#
# Verifies:
# - adapter converts cost-like source to ReviewPanelReadModel
# - supports duck-typed cost item objects
# - supports dict-like cost reports
# - supports list/tuple cost item sources
# - output contains only CV2 read models
# - no raw cost objects leak
# - category/status/severity/amount/currency/message preserved
# - missing fields fall back safely
# - empty source returns safe panel
# - deterministic
# - no input mutation
# - does NOT calculate totals/margin/profit/waste
# - no cost/domain/manufacturing/FreeCAD/Qt imports
# - no engine/workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class _FakeCostItem:
    """Simulates a cost item object from a backend domain."""

    def __init__(self, label="", category="", status="", severity="",
                 amount="", currency="", message="", component_id=""):
        self.item_label = label
        self.item_category = category
        self.item_status = status
        self.item_severity = severity
        self.item_amount = amount
        self.item_currency = currency
        self.item_message = message
        self.component_id = component_id


class _FakeCostSource:
    """Simulates a cost source with a cost_items list."""

    def __init__(self, items):
        self.cost_items = list(items)


class TestCostProjectionAdapterContract(unittest.TestCase):
    """Verify cost projection adapter contract."""

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
        pa = _load(
            "ui.configurator_v2.projection_adapters",
            "ui/configurator_v2/projection_adapters.py",
        )
        return rm, pa

    # ── Rule 1: converts source to ReviewPanelReadModel ──────────

    def test_converts_cost_source_to_review_panel(self):
        """Cost-like source produces ReviewPanelReadModel."""
        rm, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Material Cost", "Material", amount="450.00", currency="USD"),
            _FakeCostItem("Labor Cost", "Labor", amount="200.00", currency="USD"),
        ])
        result = pa.build_cost_review_projection(source)

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertEqual(result.panel_name, "Cost")
        self.assertTrue(result.available)

    # ── Rule 2: duck-typed cost item objects ─────────────────────

    def test_supports_duck_typed_cost_items(self):
        """Adapter accepts objects with item_label, item_category, etc."""
        rm, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Plywood", "Material", amount="300.00", currency="USD"),
            _FakeCostItem("Assembly", "Labor", amount="150.00", currency="USD"),
        ])
        result = pa.build_cost_review_projection(source)

        self.assertEqual(len(result.sections), 2)
        material_section = [s for s in result.sections if s.section_name == "Material"][0]
        labor_section = [s for s in result.sections if s.section_name == "Labor"][0]

        self.assertEqual(len(material_section.rows), 1)
        self.assertEqual(material_section.rows[0][0], "Plywood")
        self.assertIn("300.00", material_section.rows[0][1])

        self.assertEqual(len(labor_section.rows), 1)
        self.assertEqual(labor_section.rows[0][0], "Assembly")
        self.assertIn("150.00", labor_section.rows[0][1])

    # ── Rule 3: dict-like cost reports ───────────────────────────

    def test_supports_dict_source(self):
        """Adapter accepts dict with 'cost_items' key."""
        rm, pa = self._import_adapter()

        source = {
            "cost_items": [
                {"item_label": "Wood", "item_category": "Material",
                 "item_amount": "500.00", "item_currency": "USD"},
                {"item_label": "Hinges", "item_category": "Hardware",
                 "item_amount": "25.00", "item_currency": "USD"},
            ]
        }
        result = pa.build_cost_review_projection(source)

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertGreater(len(result.sections), 0)

    # ── Rule 4: list/tuple cost item sources ─────────────────────

    def test_supports_list_source(self):
        """Adapter accepts a plain list of cost item objects."""
        rm, pa = self._import_adapter()

        source = [
            _FakeCostItem("Material", "Material", amount="400.00"),
            _FakeCostItem("Labor", "Labor", amount="300.00"),
        ]
        result = pa.build_cost_review_projection(source)

        self.assertGreater(len(result.sections), 0)
        self.assertTrue(result.available)

    def test_supports_tuple_source(self):
        """Adapter accepts a plain tuple of cost item objects."""
        rm, pa = self._import_adapter()

        source = (
            _FakeCostItem("Total Cost", "Total", amount="800.00"),
        )
        result = pa.build_cost_review_projection(source)

        self.assertTrue(result.available)
        totals_section = [s for s in result.sections if s.section_name == "Totals"]
        self.assertEqual(len(totals_section), 1)

    # ── Rule 5: output contains only CV2 read models ─────────────

    def test_output_contains_only_cv2_read_models(self):
        """All output elements are CV2-native types."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Test", "Material", amount="100.00"),
        ])
        result = pa.build_cost_review_projection(source)

        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))

        for section in result.sections:
            self.assertFalse(hasattr(section, "Shape"))
            for row in section.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)

    # ── Rule 6: no raw cost objects leak ─────────────────────────

    def test_no_raw_cost_objects_leak(self):
        """Output ReviewPanelReadModel contains no cost source refs."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Item A", "Material", amount="100.00"),
        ])
        result = pa.build_cost_review_projection(source)

        for section in result.sections:
            for row in section.rows:
                self.assertNotIn("item_amount", row[1].lower())
                self.assertNotIn("item_label", row[1].lower())

    # ── Rule 7: fields preserved as UI-safe data ─────────────────

    def test_fields_preserved(self):
        """Category/status/severity/amount/currency/message appear in rows."""
        _, pa = self._import_adapter()

        source = [
            _FakeCostItem(
                label="Material", category="Material", status="ESTIMATED",
                severity="INFO", amount="450.00", currency="USD",
                message="Preliminary quote", component_id="cab-1",
            ),
        ]
        result = pa.build_cost_review_projection(source)

        material_section = [s for s in result.sections if s.section_name == "Material"][0]
        value = material_section.rows[0][1]
        self.assertIn("450.00", value)
        self.assertIn("USD", value)
        self.assertIn("ESTIMATED", value)
        self.assertIn("INFO", value)
        self.assertIn("Preliminary quote", value)
        self.assertIn("[cab-1]", value)

    # ── Rule 8: missing fields fall back safely ──────────────────

    def test_missing_label_falls_back_safely(self):
        """Item without any label gets empty string."""
        _, pa = self._import_adapter()

        source = [{"item_category": "Material", "item_amount": "50.00"}]
        result = pa.build_cost_review_projection(source)

        material = [s for s in result.sections if s.section_name == "Material"]
        self.assertEqual(len(material), 1)

    def test_missing_amount_omits_value(self):
        """Item without amount does not show a zero or computed value."""
        _, pa = self._import_adapter()

        source = [{"item_label": "Consulting", "item_category": "Other"}]
        result = pa.build_cost_review_projection(source)

        other = [s for s in result.sections if s.section_name == "Other"]
        self.assertEqual(len(other), 1)
        # Value should not contain "0" as a computed default
        self.assertNotEqual(other[0].rows[0][1], "0")

    def test_missing_category_goes_to_other(self):
        """Item without category goes to Other section."""
        _, pa = self._import_adapter()

        source = [{"item_label": "Misc", "item_amount": "25.00"}]
        result = pa.build_cost_review_projection(source)

        other = [s for s in result.sections if s.section_name == "Other"]
        self.assertEqual(len(other), 1)

    def test_line_items_key_accepted(self):
        """Adapter accepts source with 'line_items' key."""
        _, pa = self._import_adapter()

        source = {"line_items": [{"item_label": "Wood", "item_category": "Material",
                                  "item_amount": "100.00"}]}
        result = pa.build_cost_review_projection(source)
        self.assertTrue(result.available)

    # ── Rule 9: empty source returns safe panel ──────────────────

    def test_none_source_returns_unavailable(self):
        """None source returns unavailable panel."""
        rm, pa = self._import_adapter()
        result = pa.build_cost_review_projection(None)

        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    def test_empty_items_returns_unavailable(self):
        """Empty cost items list returns unavailable with placeholder."""
        _, pa = self._import_adapter()

        result = pa.build_cost_review_projection([])
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0].rows[0][0], "Status")

    # ── Rule 10: deterministic ───────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Material", "Material", amount="300.00"),
            _FakeCostItem("Labor", "Labor", amount="200.00"),
        ])
        r1 = pa.build_cost_review_projection(source)
        r2 = pa.build_cost_review_projection(source)

        self.assertEqual(r1, r2)

    # ── Rule 11: no input mutation ───────────────────────────────

    def test_no_input_mutation(self):
        """Original source object is not modified by projection."""
        _, pa = self._import_adapter()

        items = [_FakeCostItem("Material", "Material", amount="300.00")]
        source = _FakeCostSource(items)
        original_label = items[0].item_label

        pa.build_cost_review_projection(source)

        self.assertEqual(items[0].item_label, original_label)

    # ── Rule 12: does NOT calculate missing totals ────────────────

    def test_does_not_calculate_totals(self):
        """When no Total category item exists, no Totals section is created."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Wood", "Material", amount="300.00"),
            _FakeCostItem("Labor", "Labor", amount="200.00"),
        ])
        result = pa.build_cost_review_projection(source)

        totals = [s for s in result.sections if s.section_name == "Totals"]
        self.assertEqual(len(totals), 0)

    def test_totals_only_when_category_is_total(self):
        """Totals section only appears when an item has category 'Total'."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Total Cost", "Total", amount="500.00"),
            _FakeCostItem("Wood", "Material", amount="300.00"),
        ])
        result = pa.build_cost_review_projection(source)

        totals = [s for s in result.sections if s.section_name == "Totals"]
        self.assertEqual(len(totals), 1)
        self.assertEqual(totals[0].rows[0][0], "Total Cost")

    # ── Rule 13: does NOT calculate margin/profit/waste ──────────

    def test_does_not_calculate_margin(self):
        """No margin section unless item with category 'margin' exists."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Wood", "Material", amount="300.00"),
        ])
        result = pa.build_cost_review_projection(source)

        margin_sections = [s for s in result.sections if s.section_name == "Margin"]
        self.assertEqual(len(margin_sections), 0)

    # ── Rule 14: no forbidden imports ────────────────────────────

    def test_no_forbidden_imports(self):
        """projection_adapters.py must not import cost/domain/etc modules."""
        with open("ui/configurator_v2/projection_adapters.py") as f:
            source = f.read()

        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)

        forbidden = [
            "domain.",
            "cost_intelligence.",
            "manufacturing.",
            "optimization.",
            "commercial_outputs.",
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

    # ── Rule 15: no engine/workflow naming ───────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the adapter function name."""
        _, pa = self._import_adapter()

        func_name = pa.build_cost_review_projection.__name__

        forbidden_tokens = [
            "engine", "workflow", "service", "event", "bus",
            "store", "controller", "registry", "renderer",
        ]
        for token in forbidden_tokens:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"Function name '{func_name}' should not contain '{token}'",
            )

    # ── Rule 16: totals section appears first ────────────────────

    def test_totals_section_first(self):
        """Totals section is first when present."""
        _, pa = self._import_adapter()

        source = _FakeCostSource([
            _FakeCostItem("Wood", "Material", amount="300.00"),
            _FakeCostItem("Total Cost", "Total", amount="500.00"),
        ])
        result = pa.build_cost_review_projection(source)

        self.assertEqual(result.sections[0].section_name, "Totals")


if __name__ == "__main__":
    unittest.main()
