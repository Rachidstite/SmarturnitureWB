# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Factory Readiness Read Model Contract Tests
#
# Verifies:
# - empty input returns UNKNOWN
# - blocked fact returns BLOCKED
# - error/failure fact returns NOT_READY
# - warning fact returns NEEDS_REVIEW
# - positive ready facts return READY only when no blockers/errors/warnings
# - multiple panels aggregate deterministically
# - reasons preserve source panel name
# - input ReviewPanelReadModel objects are not mutated
# - no backend/domain/manufacturing/cost/commercial/FreeCAD/Qt imports
# - no engine/workflow/service naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
import types
import unittest


class TestFactoryReadinessReadModelContract(unittest.TestCase):
    """Verify factory readiness read model contract."""

    _rm = None
    _fr = None

    @classmethod
    def _import_once(cls):
        """Import modules once per test class (not per call)."""
        if cls._rm is not None:
            return cls._rm, cls._fr

        import importlib.machinery
        import importlib.util

        for key in list(sys.modules):
            if key.startswith(("factory_operational_intelligence", "ui.configurator_v2")):
                del sys.modules[key]

        parent1 = types.ModuleType("ui.configurator_v2")
        parent1.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent1

        parent2 = types.ModuleType("factory_operational_intelligence")
        parent2.__path__ = ["factory_operational_intelligence"]
        sys.modules["factory_operational_intelligence"] = parent2

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        rm = _load("ui.configurator_v2.read_models", "ui/configurator_v2/read_models.py")
        fr = _load(
            "factory_operational_intelligence.factory_readiness",
            "factory_operational_intelligence/factory_readiness.py",
        )
        cls._rm = rm
        cls._fr = fr
        return rm, fr

    def _make_panel(self, panel_name, sections=()):
        rm, _ = self._import_once()
        return rm.ReviewPanelReadModel(
            panel_name=panel_name,
            sections=tuple(sections),
            available=True,
        )

    def _make_section(self, section_name, rows=(), warnings=()):
        rm, _ = self._import_once()
        return rm.ReviewSectionReadModel(
            section_name=section_name,
            rows=tuple(rows),
            warnings=tuple(warnings),
        )

    # ── Rule 1: empty input returns UNKNOWN ──────────────────────

    def test_none_input_returns_unknown(self):
        rm, fr = self._import_once()
        result = fr.build_factory_readiness_read_model(None)
        self.assertEqual(result.status, fr.UNKNOWN)
        self.assertEqual(len(result.reasons), 0)

    def test_empty_list_returns_unknown(self):
        rm, fr = self._import_once()
        result = fr.build_factory_readiness_read_model([])
        self.assertEqual(result.status, fr.UNKNOWN)
        self.assertEqual(len(result.reasons), 0)

    def test_panels_without_relevant_data_returns_unknown(self):
        rm, fr = self._import_once()
        panels = (
            rm.ReviewPanelReadModel(
                panel_name="Cost",
                sections=(
                    rm.ReviewSectionReadModel(
                        section_name="Totals",
                        rows=(("Total", "500.00 USD"),),
                    ),
                ),
                available=True,
            ),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.UNKNOWN)

    # ── Rule 2: blocked fact returns BLOCKED ─────────────────────

    def test_blocked_section_returns_blocked(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Release", (
                self._make_section("Blocked", (("Critical", "BLOCKED — Cannot ship"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.BLOCKED)
        self.assertGreater(result.blocking_count, 0)

    def test_blocked_row_value_returns_blocked(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Errors", (("Rule A", "BLOCKED — Out of tolerance"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.BLOCKED)

    def test_blocked_warning_returns_blocked(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Errors", (), warnings=("BLOCKED: Cannot proceed",)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.BLOCKED)

    # ── Rule 3: error/failure fact returns NOT_READY ─────────────

    def test_failed_section_returns_not_ready(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Manufacturing", (
                self._make_section("Failed", (("CNC Cut", "FAIL — Edge mismatch"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NOT_READY)

    def test_errors_section_returns_not_ready(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Errors", (("Width Check", "ERROR — Out of tolerance"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NOT_READY)

    def test_fail_row_value_returns_not_ready(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Manufacturing", (
                self._make_section("Operations", (("Assembly", "FAIL — Alignment off"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NOT_READY)

    # ── Rule 4: warning fact returns NEEDS_REVIEW ────────────────

    def test_warning_section_returns_needs_review(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Warnings", (("Depth Check", "WARNING — Near limit"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NEEDS_REVIEW)

    def test_pending_row_value_returns_needs_review(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Commercial", (
                self._make_section("Discounts", (("Quote", "PENDING — Awaiting approval"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NEEDS_REVIEW)

    # ── Rule 5: positive ready facts return READY only when clean ─

    def test_passed_only_returns_ready(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Manufacturing", (
                self._make_section("Passed", (("CNC Cut", "PASS"), ("Edge Banding", "PASS"))),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.READY)
        self.assertEqual(result.ready_count, 2)

    def test_ready_not_returned_when_blocker_exists(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Manufacturing", (
                self._make_section("Passed", (("CNC Cut", "PASS"),)),
                self._make_section("Failed", (("Assembly", "FAIL"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NOT_READY)  # not READY

    def test_ready_not_returned_when_warning_exists(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Passed", (("Width", "PASS"),)),
                self._make_section("Warnings", (("Depth", "WARNING — near limit"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.NEEDS_REVIEW)  # not READY

    def test_released_section_returns_ready(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Release", (
                self._make_section("Ready", (("Production", "RELEASED"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.READY)

    # ── Rule 6: multiple panels aggregate deterministically ──────

    def test_multiple_panels_aggregate_correctly(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Errors", (("Rule", "FAIL"),)),
            )),
            self._make_panel("Manufacturing", (
                self._make_section("Passed", (("CNC", "PASS"),)),
            )),
            self._make_panel("Release", (
                self._make_section("Blocked", (("Critical", "BLOCKED"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(result.status, fr.BLOCKED)

    def test_deterministic(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Validation", (
                self._make_section("Errors", (("Rule", "FAIL"),)),
                self._make_section("Warnings", (("Other", "WARNING"),)),
            )),
            self._make_panel("Manufacturing", (
                self._make_section("Passed", (("CNC", "PASS"),)),
            )),
        )
        r1 = fr.build_factory_readiness_read_model(panels)
        r2 = fr.build_factory_readiness_read_model(panels)
        self.assertEqual(r1, r2)

    # ── Rule 7: reasons preserve source panel name ───────────────

    def test_reasons_preserve_source_panel(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Manufacturing", (
                self._make_section("Failed", (("CNC", "FAIL — Error"),)),
            )),
            self._make_panel("Release", (
                self._make_section("Blocked", (("Ship", "BLOCKED"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        source_panels = {r.source_panel for r in result.reasons}
        self.assertIn("Manufacturing", source_panels)
        self.assertIn("Release", source_panels)

    # ── Rule 8: input not mutated ────────────────────────────────

    def test_no_input_mutation(self):
        rm, fr = self._import_once()
        panel = self._make_panel("Validation", (
            self._make_section("Errors", (("Rule", "FAIL"),)),
        ))
        original_name = panel.panel_name
        fr.build_factory_readiness_read_model((panel,))
        self.assertEqual(panel.panel_name, original_name)

    # ── Rule 9: no forbidden imports ─────────────────────────────

    def test_no_forbidden_imports(self):
        rm, fr = self._import_once()
        with open("factory_operational_intelligence/factory_readiness.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines()
                 if l.strip().startswith(("import ", "from "))]
        text = "\n".join(lines)
        forbidden = [
            "domain.", "manufacturing.", "cost_intelligence.",
            "commercial_outputs.", "optimization.", "FreeCAD",
            "QtWidgets", "QtCore", "QtGui",
        ]
        for token in forbidden:
            self.assertNotIn(
                token, text,
                msg=f"factory_readiness.py must not import '{token}'",
            )

    # ── Rule 10: no engine/workflow naming ──────────────────────

    def test_no_engine_workflow_naming(self):
        rm, fr = self._import_once()
        func_name = fr.build_factory_readiness_read_model.__name__
        forbidden = ["engine", "workflow", "service", "event", "bus",
                     "store", "controller", "registry", "renderer"]
        for token in forbidden:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"'{func_name}' should not contain '{token}'",
            )

    # ── Rule extra: source_panels populated correctly ────────────

    def test_source_panels_populated(self):
        rm, fr = self._import_once()
        panels = (
            self._make_panel("Manufacturing", (
                self._make_section("Passed", (("Op", "PASS"),)),
            )),
            self._make_panel("Validation", (
                self._make_section("Errors", (("Rule", "FAIL"),)),
            )),
        )
        result = fr.build_factory_readiness_read_model(panels)
        self.assertIn("Manufacturing", result.source_panels)
        self.assertIn("Validation", result.source_panels)
        self.assertEqual(len(result.source_panels), 2)

    def test_summary_message_present(self):
        rm, fr = self._import_once()
        result = fr.build_factory_readiness_read_model(None)
        self.assertTrue(len(result.summary_message) > 0)
        result2 = fr.build_factory_readiness_read_model(
            (self._make_panel("Validation", (self._make_section("Errors", (("R", "FAIL"),)),)),)
        )
        self.assertIn("NOT_READY", result2.summary_message)


if __name__ == "__main__":
    unittest.main()
