# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Commercial Projection Adapter Contract Tests
#
# Verifies:
# - adapter converts commercial-like source to ReviewPanelReadModel
# - supports duck-typed commercial item objects
# - supports dict-like commercial reports
# - supports list/tuple commercial sources
# - output contains only CV2 read models
# - no raw commercial objects leak
# - category/status/severity/value/currency/message/note preserved
# - missing fields fall back safely
# - empty source returns safe panel
# - deterministic
# - no input mutation
# - no commercial calculations
# - no commercial/domain/manufacturing/FreeCAD/Qt imports
# - no engine/workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class _FakeComItem:
    """Simulates a commercial item from a backend domain."""

    def __init__(self, label="", category="", status="", severity="",
                 value="", currency="", message="", note="", component_id=""):
        self.item_label = label
        self.item_category = category
        self.item_status = status
        self.item_severity = severity
        self.item_value = value
        self.item_currency = currency
        self.item_message = message
        self.customer_note = note
        self.component_id = component_id


class _FakeComSource:
    """Simulates a commercial source with a commercial_items list."""

    def __init__(self, items):
        self.commercial_items = list(items)


class TestCommercialProjectionAdapterContract(unittest.TestCase):
    """Verify commercial projection adapter contract."""

    @classmethod
    def _import_adapter(cls):
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
        pa = _load("ui.configurator_v2.projection_adapters",
                    "ui/configurator_v2/projection_adapters.py")
        return rm, pa

    # ── Rule 1: converts source to ReviewPanelReadModel ──────────

    def test_converts_commercial_source_to_review_panel(self):
        rm, pa = self._import_adapter()
        source = _FakeComSource([
            _FakeComItem("Base Price", "Pricing", value="1500.00", currency="USD"),
            _FakeComItem("5% Early Payment", "Discount", value="75.00"),
        ])
        result = pa.build_commercial_review_projection(source)
        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertEqual(result.panel_name, "Commercial")
        self.assertTrue(result.available)

    # ── Rule 2: duck-typed commercial items ──────────────────────

    def test_supports_duck_typed_items(self):
        rm, pa = self._import_adapter()
        source = _FakeComSource([
            _FakeComItem("Unit Price", "Pricing", value="1200.00"),
            _FakeComItem("Volume Discount", "Discount", value="10%"),
        ])
        result = pa.build_commercial_review_projection(source)
        self.assertEqual(len(result.sections), 2)
        pricing = [s for s in result.sections if s.section_name == "Pricing"][0]
        discounts = [s for s in result.sections if s.section_name == "Discounts"][0]
        self.assertEqual(pricing.rows[0][0], "Unit Price")
        self.assertIn("1200.00", pricing.rows[0][1])
        self.assertEqual(discounts.rows[0][0], "Volume Discount")

    # ── Rule 3: dict-like commercial reports ─────────────────────

    def test_supports_dict_source(self):
        rm, pa = self._import_adapter()
        source = {"commercial_items": [
            {"item_label": "Price", "item_category": "Pricing", "item_value": "2000"},
            {"item_label": "Terms", "item_category": "Terms", "item_message": "Net 30"},
        ]}
        result = pa.build_commercial_review_projection(source)
        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertGreater(len(result.sections), 0)

    # ── Rule 4: list/tuple sources ───────────────────────────────

    def test_supports_list_source(self):
        rm, pa = self._import_adapter()
        source = [
            _FakeComItem("Price", "Pricing", value="1000"),
            _FakeComItem("Discount", "Discount", value="100"),
        ]
        result = pa.build_commercial_review_projection(source)
        self.assertTrue(result.available)
        self.assertGreater(len(result.sections), 0)

    def test_supports_tuple_source(self):
        rm, pa = self._import_adapter()
        source = (_FakeComItem("Total", "Summary", value="900"),)
        result = pa.build_commercial_review_projection(source)
        self.assertTrue(result.available)

    # ── Rule 5: CV2-only read models ─────────────────────────────

    def test_output_contains_only_cv2_read_models(self):
        _, pa = self._import_adapter()
        source = _FakeComSource([_FakeComItem("Price", "Pricing", value="500")])
        result = pa.build_commercial_review_projection(source)
        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))
        for section in result.sections:
            self.assertFalse(hasattr(section, "Shape"))
            for row in section.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)

    # ── Rule 6: no backend leakage ───────────────────────────────

    def test_no_raw_commercial_objects_leak(self):
        _, pa = self._import_adapter()
        source = _FakeComSource([_FakeComItem("Price", "Pricing", value="500")])
        result = pa.build_commercial_review_projection(source)
        for section in result.sections:
            for row in section.rows:
                self.assertNotIn("item_value", row[1].lower())
                self.assertNotIn("item_label", row[1].lower())

    # ── Rule 7: fields preserved as UI-safe data ─────────────────

    def test_fields_preserved(self):
        _, pa = self._import_adapter()
        source = [_FakeComItem(
            label="List Price", category="Pricing", status="CONFIRMED",
            severity="INFO", value="2500.00", currency="USD",
            message="Standard pricing", note="Valid until Dec 2026",
            component_id="quote-1",
        )]
        result = pa.build_commercial_review_projection(source)
        pricing = [s for s in result.sections if s.section_name == "Pricing"][0]
        v = pricing.rows[0][1]
        self.assertIn("2500.00", v)
        self.assertIn("USD", v)
        self.assertIn("CONFIRMED", v)
        self.assertIn("INFO", v)
        self.assertIn("Standard pricing", v)
        self.assertIn("[note: Valid until Dec 2026]", v)
        self.assertIn("[quote-1]", v)

    # ── Rule 8: missing fields fall back safely ──────────────────

    def test_missing_label_safe(self):
        _, pa = self._import_adapter()
        source = [{"item_category": "Pricing", "item_value": "100"}]
        result = pa.build_commercial_review_projection(source)
        pricing = [s for s in result.sections if s.section_name == "Pricing"]
        self.assertEqual(len(pricing), 1)

    def test_no_category_goes_to_other(self):
        _, pa = self._import_adapter()
        source = [{"item_label": "Misc Item", "item_value": "50"}]
        result = pa.build_commercial_review_projection(source)
        other = [s for s in result.sections if s.section_name == "Other"]
        self.assertEqual(len(other), 1)

    def test_line_items_key_accepted(self):
        _, pa = self._import_adapter()
        source = {"line_items": [{"item_label": "Price", "item_category": "Pricing",
                                  "item_value": "500"}]}
        result = pa.build_commercial_review_projection(source)
        self.assertTrue(result.available)

    def test_notes_category(self):
        """Items with note/notes/customer_note category go to Notes section."""
        _, pa = self._import_adapter()
        source = [{"item_label": "Payment Note", "item_category": "customer_note",
                   "item_message": "50% upfront"}]
        result = pa.build_commercial_review_projection(source)
        notes = [s for s in result.sections if s.section_name == "Notes"]
        self.assertEqual(len(notes), 1)

    # ── Rule 9: empty source safe ────────────────────────────────

    def test_none_source(self):
        rm, pa = self._import_adapter()
        result = pa.build_commercial_review_projection(None)
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    def test_empty_items(self):
        _, pa = self._import_adapter()
        result = pa.build_commercial_review_projection([])
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0].rows[0][0], "Status")

    # ── Rule 10: deterministic ───────────────────────────────────

    def test_deterministic(self):
        _, pa = self._import_adapter()
        source = _FakeComSource([
            _FakeComItem("Price", "Pricing", value="1000"),
            _FakeComItem("Discount", "Discount", value="100"),
        ])
        r1 = pa.build_commercial_review_projection(source)
        r2 = pa.build_commercial_review_projection(source)
        self.assertEqual(r1, r2)

    # ── Rule 11: no input mutation ───────────────────────────────

    def test_no_input_mutation(self):
        _, pa = self._import_adapter()
        items = [_FakeComItem("Price", "Pricing", value="500")]
        source = _FakeComSource(items)
        original = items[0].item_label
        pa.build_commercial_review_projection(source)
        self.assertEqual(items[0].item_label, original)

    # ── Rule 12: no commercial calculations ──────────────────────

    def test_does_not_calculate_discount(self):
        """No discount section unless item with discount category exists."""
        _, pa = self._import_adapter()
        source = _FakeComSource([_FakeComItem("Price", "Pricing", value="500")])
        result = pa.build_commercial_review_projection(source)
        discounts = [s for s in result.sections if s.section_name == "Discounts"]
        self.assertEqual(len(discounts), 0)

    def test_summary_only_when_category_is_summary(self):
        """Summary section appears only for items with category Summary/Total."""
        _, pa = self._import_adapter()
        source = _FakeComSource([
            _FakeComItem("Grand Total", "Summary", value="500"),
        ])
        result = pa.build_commercial_review_projection(source)
        summary = [s for s in result.sections if s.section_name == "Summary"]
        self.assertEqual(len(summary), 1)

    # ── Rule 13: no forbidden imports ────────────────────────────

    def test_no_forbidden_imports(self):
        with open("ui/configurator_v2/projection_adapters.py") as f:
            source = f.read()
        imports = [l for l in source.splitlines()
                   if l.strip().startswith(("import ", "from "))]
        text = "\n".join(imports)
        forbidden = [
            "domain.", "commercial_outputs.", "cost_intelligence.",
            "manufacturing.", "optimization.", "FreeCAD",
            "QtWidgets", "QtCore", "QtGui",
        ]
        for token in forbidden:
            self.assertNotIn(token, text,
                             msg=f"projection_adapters.py must not import '{token}'")

    # ── Rule 14: no engine/workflow naming ──────────────────────

    def test_no_engine_workflow_naming(self):
        _, pa = self._import_adapter()
        name = pa.build_commercial_review_projection.__name__
        for t in ("engine", "workflow", "service", "event", "bus",
                  "store", "controller", "registry", "renderer"):
            self.assertNotIn(t, name.lower(),
                             msg=f"'{name}' should not contain '{t}'")

    # ── Rule 15: warnings section appears when severity present ──

    def test_warnings_section_for_severity_items(self):
        _, pa = self._import_adapter()
        source = [_FakeComItem("Expired Quote", "Pricing", severity="WARNING",
                               message="Quote expired 30 days ago")]
        result = pa.build_commercial_review_projection(source)
        warnings = [s for s in result.sections if s.section_name == "Warnings"]
        self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
