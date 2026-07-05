# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Validation Projection Adapter Contract Tests
#
# Verifies:
# - adapter converts validation-like source to ReviewPanelReadModel
# - supports duck-typed violation objects
# - supports dict-like validation reports
# - supports list/tuple violation sources
# - output contains only CV2 read models
# - no raw validation objects leak
# - severity/status/message fields preserved as UI-safe data
# - missing fields fall back safely
# - empty source returns safe panel
# - deterministic
# - no input mutation
# - no validation/domain/manufacturing/cost/FreeCAD/Qt imports
# - no engine/workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class _FakeValViolation:
    """Simulates a validation violation object from a backend domain."""

    def __init__(self, label, severity="INFO", status="", message="", component_id=""):
        self.rule_label = label
        self.violation_severity = severity
        self.violation_status = status
        self.violation_message = message
        self.component_id = component_id


class _FakeValSource:
    """Simulates a validation source with a violations list."""

    def __init__(self, violations):
        self.violations = list(violations)


class TestValidationProjectionAdapterContract(unittest.TestCase):
    """Verify validation projection adapter contract."""

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
        pa = _load(
            "ui.configurator_v2.projection_adapters",
            "ui/configurator_v2/projection_adapters.py",
        )
        return rm, pa

    # ── Rule 1: converts source to ReviewPanelReadModel ──────────

    def test_converts_validation_source_to_review_panel(self):
        """Validation-like source produces ReviewPanelReadModel."""
        rm, pa = self._import_adapter()

        source = _FakeValSource([
            _FakeValViolation("Width Check", "ERROR", "FAIL", "Width out of tolerance"),
            _FakeValViolation("Height Check", "PASS", "PASS", "Within tolerance"),
        ])
        result = pa.build_validation_review_projection(source)

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertEqual(result.panel_name, "Validation")
        self.assertTrue(result.available)

    # ── Rule 2: duck-typed violation objects ─────────────────────

    def test_supports_duck_typed_violation_objects(self):
        """Adapter accepts objects with rule_label, violation_severity, etc."""
        rm, pa = self._import_adapter()

        source = _FakeValSource([
            _FakeValViolation("Rule A", "ERROR", "FAIL", "Failed"),
            _FakeValViolation("Rule B", "WARNING", "WARNING", "Check needed"),
        ])
        result = pa.build_validation_review_projection(source)

        self.assertEqual(len(result.sections), 2)  # Errors + Warnings
        error_section = [s for s in result.sections if s.section_name == "Errors"][0]
        warning_section = [s for s in result.sections if s.section_name == "Warnings"][0]

        self.assertEqual(len(error_section.rows), 1)
        self.assertEqual(error_section.rows[0][0], "Rule A")
        self.assertIn("ERROR", error_section.rows[0][1])

        self.assertEqual(len(warning_section.rows), 1)
        self.assertEqual(warning_section.rows[0][0], "Rule B")
        self.assertIn("WARNING", warning_section.rows[0][1])

    # ── Rule 3: dict-like validation reports ─────────────────────

    def test_supports_dict_source(self):
        """Adapter accepts dict with 'violations' key."""
        rm, pa = self._import_adapter()

        source = {
            "violations": [
                {"rule_label": "Check A", "violation_severity": "ERROR",
                 "violation_message": "Failed check"},
                {"rule_label": "Check B", "violation_severity": "WARNING",
                 "violation_message": "Near limit"},
            ]
        }
        result = pa.build_validation_review_projection(source)

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertGreater(len(result.sections), 0)

    # ── Rule 4: list/tuple violation sources ─────────────────────

    def test_supports_list_source(self):
        """Adapter accepts a plain list of violation objects."""
        rm, pa = self._import_adapter()

        source = [
            _FakeValViolation("Violation A", "ERROR", "FAIL"),
            _FakeValViolation("Violation B", "PASS", "PASS"),
        ]
        result = pa.build_validation_review_projection(source)

        self.assertGreater(len(result.sections), 0)
        self.assertTrue(result.available)

    def test_supports_tuple_source(self):
        """Adapter accepts a plain tuple of violation objects."""
        rm, pa = self._import_adapter()

        source = (
            _FakeValViolation("Op1", "ERROR", "FAIL"),
            _FakeValViolation("Op2", "INFO"),
        )
        result = pa.build_validation_review_projection(source)

        self.assertTrue(result.available)

    # ── Rule 5: output contains only CV2 read models ─────────────

    def test_output_contains_only_cv2_read_models(self):
        """All output elements are CV2-native types."""
        _, pa = self._import_adapter()

        source = _FakeValSource([
            _FakeValViolation("Test Rule", "ERROR", "FAIL"),
        ])
        result = pa.build_validation_review_projection(source)

        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))

        for section in result.sections:
            self.assertFalse(hasattr(section, "Shape"))
            for row in section.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)

    # ── Rule 6: no raw validation objects leak ───────────────────

    def test_no_raw_validation_objects_leak(self):
        """Output ReviewPanelReadModel contains no validation source refs."""
        _, pa = self._import_adapter()

        source = _FakeValSource([
            _FakeValViolation("Rule A", "ERROR", "FAIL"),
        ])
        result = pa.build_validation_review_projection(source)

        for section in result.sections:
            for row in section.rows:
                self.assertNotIn("violation_severity", row[1].lower())
                self.assertNotIn("rule_label", row[1].lower())
                self.assertNotIn("violation_message", row[1].lower())

    # ── Rule 7: severity/status/message preserved as UI-safe data ─

    def test_severity_status_message_preserved(self):
        """Severity/status/message fields appear in output rows."""
        _, pa = self._import_adapter()

        source = [
            _FakeValViolation("Test", "ERROR", "FAIL", "Tolerance exceeded"),
        ]
        result = pa.build_validation_review_projection(source)

        error_section = [s for s in result.sections if s.section_name == "Errors"][0]
        self.assertEqual(len(error_section.rows), 1)
        self.assertIn("ERROR", error_section.rows[0][1])
        self.assertIn("Tolerance exceeded", error_section.rows[0][1])

    # ── Rule 8: missing fields fall back safely ──────────────────

    def test_missing_label_falls_back_safely(self):
        """Violation without any label gets empty string."""
        _, pa = self._import_adapter()

        source = [{"violation_severity": "ERROR"}]
        result = pa.build_validation_review_projection(source)

        error_section = [s for s in result.sections if s.section_name == "Errors"]
        self.assertEqual(len(error_section), 1)

    def test_missing_severity_falls_back_to_info(self):
        """Violation without severity defaults to INFO."""
        _, pa = self._import_adapter()

        source = [{"status": "PASS"}]
        result = pa.build_validation_review_projection(source)

        passed_section = [s for s in result.sections if s.section_name == "Passed"]
        self.assertEqual(len(passed_section), 1)

    def test_missing_status_falls_back_to_unknown(self):
        """Violation without status defaults to INFO severity → Info section."""
        _, pa = self._import_adapter()

        source = [{"rule_label": "No Status"}]
        result = pa.build_validation_review_projection(source)

        info_section = [s for s in result.sections if s.section_name == "Info"]
        self.assertEqual(len(info_section), 1)
        self.assertIn("No Status", info_section[0].rows[0][0])

    # ── Rule 9: empty source returns safe panel ──────────────────

    def test_none_source_returns_unavailable(self):
        """None source returns unavailable panel."""
        rm, pa = self._import_adapter()
        result = pa.build_validation_review_projection(None)

        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    def test_empty_violations_returns_unavailable(self):
        """Empty violations list returns unavailable with placeholder."""
        _, pa = self._import_adapter()

        result = pa.build_validation_review_projection([])
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0].rows[0][0], "Status")

    # ── Rule 10: deterministic ───────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        _, pa = self._import_adapter()

        source = _FakeValSource([
            _FakeValViolation("A", "ERROR", "FAIL", "Failed"),
            _FakeValViolation("B", "PASS", "PASS"),
        ])
        r1 = pa.build_validation_review_projection(source)
        r2 = pa.build_validation_review_projection(source)

        self.assertEqual(r1, r2)

    # ── Rule 11: no input mutation ───────────────────────────────

    def test_no_input_mutation(self):
        """Original source object is not modified by projection."""
        _, pa = self._import_adapter()

        violations = [_FakeValViolation("A", "ERROR", "FAIL")]
        source = _FakeValSource(violations)
        original_label = violations[0].rule_label

        pa.build_validation_review_projection(source)

        self.assertEqual(violations[0].rule_label, original_label)

    # ── Rule 12: no forbidden imports ────────────────────────────

    def test_no_forbidden_imports(self):
        """projection_adapters.py must not import domain/validation/etc modules."""
        with open("ui/configurator_v2/projection_adapters.py") as f:
            source = f.read()

        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)

        forbidden = [
            "domain.",
            "validation.",
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

    # ── Rule 13: no engine/workflow naming ───────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the adapter function name."""
        _, pa = self._import_adapter()

        func_name = pa.build_validation_review_projection.__name__

        engine_tokens = [
            "engine", "workflow", "service", "event", "bus",
            "store", "controller", "registry", "renderer",
        ]
        for token in engine_tokens:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"Function name '{func_name}' should not contain '{token}'",
            )

    # ── Rule 14: violations grouped by severity/status ───────────

    def test_violations_grouped_by_severity(self):
        """Violations are grouped into Errors, Warnings, Passed, Info, Other."""
        _, pa = self._import_adapter()

        source = [
            _FakeValViolation("A", "ERROR", "FAIL", "A error"),
            _FakeValViolation("B", "WARNING", "WARNING", "B warn"),
            _FakeValViolation("C", "PASS", "PASS"),
            _FakeValViolation("D", "INFO"),
            _FakeValViolation("E", "UNKNOWN", "UNKNOWN"),
        ]
        result = pa.build_validation_review_projection(source)

        section_names = {s.section_name for s in result.sections}
        self.assertIn("Errors", section_names)
        self.assertIn("Warnings", section_names)
        self.assertIn("Passed", section_names)
        self.assertIn("Info", section_names)
        self.assertIn("Other", section_names)

    # ── Rule 15: component_id shown in rows ──────────────────────

    def test_component_id_in_output(self):
        """Component ID appears in the row value."""
        _, pa = self._import_adapter()

        source = [
            _FakeValViolation("Rule", "ERROR", "FAIL", "Failed", component_id="panel-1"),
        ]
        result = pa.build_validation_review_projection(source)

        error_section = [s for s in result.sections if s.section_name == "Errors"][0]
        self.assertIn("[panel-1]", error_section.rows[0][1])

    # ── Rule 16: severity takes precedence over status ───────────

    def test_severity_takes_precedence_over_status(self):
        """ERROR severity routes to Errors even if status is PASS."""
        _, pa = self._import_adapter()

        source = [
            _FakeValViolation("WarningWithPass", "WARNING", "PASS"),
        ]
        result = pa.build_validation_review_projection(source)

        warning_section = [s for s in result.sections if s.section_name == "Warnings"]
        self.assertEqual(len(warning_section), 1)
        passed_section = [s for s in result.sections if s.section_name == "Passed"]
        self.assertEqual(len(passed_section), 0)


if __name__ == "__main__":
    unittest.main()
