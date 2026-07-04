# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Manufacturing Projection Adapter Contract Tests
#
# Verifies:
# - adapter converts manufacturing-like source to ReviewPanelReadModel
# - supports duck-typed operation objects
# - supports dict-like manufacturing summaries
# - supports list/tuple operation sources
# - output contains only CV2 read models
# - no raw manufacturing objects leak
# - severity/status/message fields preserved
# - missing fields fall back safely
# - deterministic
# - no input mutation
# - no manufacturing/domain/cost/FreeCAD/Qt imports
# - no engine/workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class _FakeMfgOp:
    """Simulates a manufacturing operation object from a backend domain."""

    def __init__(self, label, status="PASS", message="", component_id=""):
        self.operation_label = label
        self.operation_status = status
        self.operation_message = message
        self.component_id = component_id


class _FakeMfgSource:
    """Simulates a manufacturing source with an operations list."""

    def __init__(self, ops):
        self.operations = list(ops)


class TestManufacturingProjectionAdapterContract(unittest.TestCase):
    """Verify manufacturing projection adapter contract."""

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

        # load dependency order: read_models first, then projection_adapters
        rm = _load("ui.configurator_v2.read_models", "ui/configurator_v2/read_models.py")
        pa = _load("ui.configurator_v2.projection_adapters", "ui/configurator_v2/projection_adapters.py")
        return rm, pa

    # ── Rule 1: converts source to ReviewPanelReadModel ──────────

    def test_converts_manufacturing_source_to_review_panel(self):
        """Manufacturing-like source produces ReviewPanelReadModel."""
        rm, pa = self._import_adapter()

        source = _FakeMfgSource([
            _FakeMfgOp("CNC Cut", "PASS", "All panels cut"),
            _FakeMfgOp("Edge Banding", "PASS", "Edges applied"),
        ])
        result = pa.build_manufacturing_review_projection(source)

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertEqual(result.panel_name, "Manufacturing")
        self.assertTrue(result.available)

    # ── Rule 2: duck-typed operation objects ─────────────────────

    def test_supports_duck_typed_operation_objects(self):
        """Adapter accepts objects with operation_label, operation_status, etc."""
        rm, pa = self._import_adapter()

        source = _FakeMfgSource([
            _FakeMfgOp("Drilling", "PASS", "All holes correct"),
            _FakeMfgOp("Assembly", "FAIL", "Alignment off", "cabinet-1"),
        ])
        result = pa.build_manufacturing_review_projection(source)

        self.assertEqual(len(result.sections), 2)  # Failed + Passed
        passed_section = [s for s in result.sections if s.section_name == "Passed"][0]
        failed_section = [s for s in result.sections if s.section_name == "Failed"][0]

        self.assertEqual(len(passed_section.rows), 1)
        self.assertEqual(passed_section.rows[0][0], "Drilling")
        self.assertIn("PASS", passed_section.rows[0][1])

        self.assertEqual(len(failed_section.rows), 1)
        self.assertEqual(failed_section.rows[0][0], "Assembly")
        self.assertIn("FAIL", failed_section.rows[0][1])
        self.assertIn("[cabinet-1]", failed_section.rows[0][1])

    # ── Rule 3: dict-like manufacturing summaries ────────────────

    def test_supports_dict_source(self):
        """Adapter accepts dict with 'operations' key."""
        rm, pa = self._import_adapter()

        source = {
            "operations": [
                {"operation_label": "CNC Cut", "operation_status": "PASS"},
                {"operation_label": "Edge Band", "operation_status": "WARNING",
                 "operation_message": "Edge thickness mismatch"},
            ]
        }
        result = pa.build_manufacturing_review_projection(source)

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertGreater(len(result.sections), 0)

    # ── Rule 4: list/tuple operation sources ─────────────────────

    def test_supports_list_source(self):
        """Adapter accepts a plain list of operation objects."""
        rm, pa = self._import_adapter()

        source = [
            _FakeMfgOp("Operation A", "PASS"),
            _FakeMfgOp("Operation B", "FAIL", "Error in path"),
        ]
        result = pa.build_manufacturing_review_projection(source)

        self.assertGreater(len(result.sections), 0)
        self.assertTrue(result.available)

    def test_supports_tuple_source(self):
        """Adapter accepts a plain tuple of operation objects."""
        rm, pa = self._import_adapter()

        source = (
            _FakeMfgOp("Op1", "PASS"),
            _FakeMfgOp("Op2", "SKIPPED"),
        )
        result = pa.build_manufacturing_review_projection(source)

        self.assertTrue(result.available)

    # ── Rule 5: output contains only CV2 read models ─────────────

    def test_output_contains_only_cv2_read_models(self):
        """All output elements are CV2-native types."""
        _, pa = self._import_adapter()

        source = _FakeMfgSource([
            _FakeMfgOp("Test Op", "PASS"),
        ])
        result = pa.build_manufacturing_review_projection(source)

        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))

        for section in result.sections:
            self.assertFalse(hasattr(section, "Shape"))
            for row in section.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)

    # ── Rule 6: no raw manufacturing objects leak ────────────────

    def test_no_raw_manufacturing_objects_leak(self):
        """Output ReviewPanelReadModel contains no manufacturing source refs."""
        _, pa = self._import_adapter()

        source = _FakeMfgSource([
            _FakeMfgOp("Op1", "PASS"),
        ])
        result = pa.build_manufacturing_review_projection(source)

        # Check each row value for "operation_status" key name — would leak
        # if raw objects were passed through
        for section in result.sections:
            for row in section.rows:
                self.assertNotIn("operation_status", row[1].lower())

    # ── Rule 7: status fields preserved ──────────────────────────

    def test_status_and_message_preserved(self):
        """Severity/status/message fields appear in output rows."""
        _, pa = self._import_adapter()

        source = [
            _FakeMfgOp("Test", "WARNING", "Check tolerance"),
        ]
        result = pa.build_manufacturing_review_projection(source)

        warning_section = [s for s in result.sections if s.section_name == "Warnings"][0]
        self.assertEqual(len(warning_section.rows), 1)
        self.assertIn("WARNING", warning_section.rows[0][1])
        self.assertIn("Check tolerance", warning_section.rows[0][1])

    # ── Rule 8: missing fields fall back safely ──────────────────

    def test_missing_label_falls_back_safely(self):
        """Operation without any label gets empty string."""
        _, pa = self._import_adapter()

        source = [{"operation_status": "PASS"}]
        result = pa.build_manufacturing_review_projection(source)

        passed_section = [s for s in result.sections if s.section_name == "Passed"]
        self.assertEqual(len(passed_section), 1)

    def test_none_source_returns_unavailable(self):
        """None source returns unavailable panel."""
        rm, pa = self._import_adapter()
        result = pa.build_manufacturing_review_projection(None)

        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    def test_empty_operations_returns_unavailable(self):
        """Empty operations list returns unavailable with placeholder section."""
        _, pa = self._import_adapter()

        result = pa.build_manufacturing_review_projection([])
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0].rows[0][0], "Status")

    # ── Rule 9: deterministic ────────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        _, pa = self._import_adapter()

        source = _FakeMfgSource([
            _FakeMfgOp("A", "PASS"),
            _FakeMfgOp("B", "FAIL", "Error"),
        ])
        r1 = pa.build_manufacturing_review_projection(source)
        r2 = pa.build_manufacturing_review_projection(source)

        self.assertEqual(r1, r2)

    # ── Rule 10: no input mutation ───────────────────────────────

    def test_no_input_mutation(self):
        """Original source object is not modified by projection."""
        _, pa = self._import_adapter()

        ops = [_FakeMfgOp("A", "PASS")]
        source = _FakeMfgSource(ops)
        original_label = ops[0].operation_label

        pa.build_manufacturing_review_projection(source)

        self.assertEqual(ops[0].operation_label, original_label)

    # ── Rule 11: no domain/manufacturing imports ─────────────────

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

    # ── Rule 12: no engine/workflow naming ───────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the adapter function."""
        _, pa = self._import_adapter()

        func = pa.build_manufacturing_review_projection
        func_name = func.__name__

        engine_tokens = ["engine", "workflow", "service", "event", "bus",
                         "store", "controller", "registry", "renderer"]
        for token in engine_tokens:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"Function name '{func_name}' should not contain '{token}'",
            )

    # ── Rule 13: operations grouped by status ────────────────────

    def test_operations_grouped_by_status(self):
        """Operations are grouped into PASS, FAIL, WARNING, SKIPPED sections."""
        _, pa = self._import_adapter()

        source = [
            _FakeMfgOp("A", "PASS"),
            _FakeMfgOp("B", "FAIL", "B failed"),
            _FakeMfgOp("C", "WARNING", "C warning"),
            _FakeMfgOp("D", "SKIPPED"),
            _FakeMfgOp("E", "UNKNOWN"),
        ]
        result = pa.build_manufacturing_review_projection(source)

        section_names = {s.section_name for s in result.sections}
        self.assertIn("Passed", section_names)
        self.assertIn("Failed", section_names)
        self.assertIn("Warnings", section_names)
        self.assertIn("Skipped", section_names)
        self.assertIn("Other", section_names)

    # ── Rule 14: status ordering preserved ───────────────────────

    def test_status_fallback_to_unknown(self):
        """Operation without status gets UNKNOWN and goes to Other section."""
        _, pa = self._import_adapter()

        source = [
            {"operation_label": "No Status Op"},
        ]
        result = pa.build_manufacturing_review_projection(source)

        other = [s for s in result.sections if s.section_name == "Other"]
        self.assertEqual(len(other), 1)
        self.assertIn("UNKNOWN", other[0].rows[0][1])


if __name__ == "__main__":
    unittest.main()
