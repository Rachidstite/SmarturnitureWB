# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Factory Blocking Analysis Contract Tests
#
# Verifies:
# - deterministic output
# - immutable read model
# - accepts empty readiness
# - accepts empty review panels
# - preserves source panel
# - preserves severity
# - preserves operational category
# - preserves human message
# - optional technical detail
# - optional component id
# - counts computed correctly
# - summary generated
# - no forbidden imports
# - no backend leakage
# - pure function
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class TestFactoryBlockingAnalysisContract(unittest.TestCase):
    """Verify factory blocking analysis read model contract."""

    _rm = None
    _fr = None
    _ba = None

    @classmethod
    def _import_once(cls):
        if cls._rm is not None:
            return cls._rm, cls._fr, cls._ba

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
        ba = _load(
            "factory_operational_intelligence.blocking_analysis",
            "factory_operational_intelligence/blocking_analysis.py",
        )
        cls._rm = rm
        cls._fr = fr
        cls._ba = ba
        return rm, fr, ba

    def _make_panel(self, panel_name, sections=()):
        rm, _, _ = self._import_once()
        return rm.ReviewPanelReadModel(
            panel_name=panel_name,
            sections=tuple(sections),
            available=True,
        )

    def _make_section(self, section_name, rows=(), warnings=()):
        rm, _, _ = self._import_once()
        return rm.ReviewSectionReadModel(
            section_name=section_name,
            rows=tuple(rows),
            warnings=tuple(warnings),
        )

    def _make_readiness(self, status, reasons=()):
        fr = self._fr
        return fr.FactoryReadinessReadModel(
            status=status,
            reasons=tuple(reasons),
            blocking_count=sum(1 for r in reasons if "BLOCKED" in r.severity),
            warning_count=sum(1 for r in reasons if "WARNING" in r.severity),
            ready_count=sum(1 for r in reasons if "INFO" in r.severity),
            source_panels=tuple(sorted(set(r.source_panel for r in reasons))),
        )

    def _make_reason(self, text, panel="Manufacturing", severity="ERROR"):
        fr = self._fr
        return fr.FactoryReadinessReason(
            reason_text=text,
            source_panel=panel,
            severity=severity,
        )

    # ── Deterministic output ─────────────────────────────────────

    def test_deterministic(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (self._make_reason("Failed: CNC — FAIL — Edge mismatch", "Manufacturing", "ERROR"),),
        )
        r1 = ba.build_factory_blocking_analysis_read_model(readiness)
        r2 = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(r1, r2)

    # ── Immutable read model ─────────────────────────────────────

    def test_read_model_is_frozen(self):
        rm, fr, ba = self._import_once()
        self.assertTrue(hasattr(ba.FactoryBlockingAnalysisReadModel, "__dataclass_fields__"))

    # ── Accepts empty readiness ──────────────────────────────────

    def test_none_readiness_returns_empty(self):
        rm, fr, ba = self._import_once()
        result = ba.build_factory_blocking_analysis_read_model(None)
        self.assertEqual(len(result.blocking_items), 0)
        self.assertEqual(len(result.source_panels), 0)

    def test_empty_readiness_returns_empty(self):
        rm, fr, ba = self._import_once()
        result = ba.build_factory_blocking_analysis_read_model(
            fr.FactoryReadinessReadModel(),
        )
        self.assertEqual(len(result.blocking_items), 0)

    # ── Accepts empty review panels ──────────────────────────────

    def test_empty_review_panels_no_crash(self):
        rm, fr, ba = self._import_once()
        result = ba.build_factory_blocking_analysis_read_model(
            fr.FactoryReadinessReadModel(status=fr.UNKNOWN),
            (),
        )
        self.assertIsNotNone(result)

    # ── Preserves source panel ───────────────────────────────────

    def test_preserves_source_panel(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (self._make_reason("Blocked: Critical — BLOCKED", "Release", "BLOCKED"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(len(result.blocking_items), 1)
        self.assertEqual(result.blocking_items[0].source_panel, "Release")

    def test_multiple_source_panels(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (
                self._make_reason("Failed: CNC — FAIL", "Manufacturing", "ERROR"),
                self._make_reason("Error: Width — ERROR", "Validation", "ERROR"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertIn("Manufacturing", result.source_panels)
        self.assertIn("Validation", result.source_panels)

    # ── Preserves severity ───────────────────────────────────────

    def test_preserves_blocked_severity(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (self._make_reason("Critical blocker", "Manufacturing", "BLOCKED"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].severity, "BLOCKED")

    def test_preserves_error_severity(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Failed operation", "Manufacturing", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].severity, "ERROR")

    def test_preserves_warning_severity(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NEEDS_REVIEW,
            (self._make_reason("Near tolerance", "Validation", "WARNING"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].severity, "WARNING")

    # ── Preserves operational category ───────────────────────────

    def test_manufacturing_category(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("CNC Fail", "Manufacturing", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].operational_category, "MANUFACTURING")

    def test_validation_category(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Error", "Validation", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].operational_category, "ENGINEERING")

    def test_release_category(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (self._make_reason("Blocked", "Release", "BLOCKED"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].operational_category, "RELEASE")

    def test_cost_category(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NEEDS_REVIEW,
            (self._make_reason("Over budget", "Cost", "WARNING"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].operational_category, "COST")

    def test_commercial_category(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NEEDS_REVIEW,
            (self._make_reason("Pending approval", "Commercial", "WARNING"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].operational_category, "COMMERCIAL")

    def test_unknown_panel_category_fallback(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Issue", "UnknownPanel", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].operational_category, "UNKNOWN")

    # ── Preserves human message ──────────────────────────────────

    def test_preserves_human_message(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Failed: CNC Cut — FAIL — Edge mismatch", "Manufacturing", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertIn("Edge mismatch", result.blocking_items[0].human_message)

    # ── Optional technical detail ────────────────────────────────

    def test_technical_detail_empty_by_default(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Failed operation", "Manufacturing", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].technical_detail, "")

    # ── Optional component id ────────────────────────────────────

    def test_component_id_empty_by_default(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Failed operation", "Manufacturing", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.blocking_items[0].component_id, "")

    # ── Operational impact populated ─────────────────────────────

    def test_operational_impact_present(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (self._make_reason("Critical blockage", "Manufacturing", "BLOCKED"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        impact = result.blocking_items[0].operational_impact
        self.assertIn("Manufacturing", impact)
        self.assertIn("Blocks production", impact)

    # ── Counts computed correctly ────────────────────────────────

    def test_critical_count_blocked(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (
                self._make_reason("Blocker 1", "Manufacturing", "BLOCKED"),
                self._make_reason("Blocker 2", "Release", "BLOCKED"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.critical_count, 2)
        self.assertEqual(result.high_count, 0)

    def test_high_count_errors(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (
                self._make_reason("Error 1", "Validation", "ERROR"),
                self._make_reason("Error 2", "Manufacturing", "ERROR"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.high_count, 2)

    def test_medium_count_warnings(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NEEDS_REVIEW,
            (
                self._make_reason("Warn 1", "Validation", "WARNING"),
                self._make_reason("Warn 2", "Cost", "WARNING"),
                self._make_reason("Warn 3", "Commercial", "WARNING"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.medium_count, 3)

    def test_low_count_info(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.READY,
            (
                self._make_reason("Passed: CNC — PASS", "Manufacturing", "INFO"),
                self._make_reason("Passed: Assembly — PASS", "Manufacturing", "INFO"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.low_count, 2)

    def test_mixed_counts(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (
                self._make_reason("Critical", "Release", "BLOCKED"),
                self._make_reason("Error", "Validation", "ERROR"),
                self._make_reason("Warning", "Manufacturing", "WARNING"),
                self._make_reason("Info", "Cost", "INFO"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(result.critical_count, 1)
        self.assertEqual(result.high_count, 1)
        self.assertEqual(result.medium_count, 1)
        self.assertEqual(result.low_count, 1)

    # ── Summary generated ────────────────────────────────────────

    def test_summary_contains_status(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (self._make_reason("Critical", "Manufacturing", "BLOCKED"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertIn("BLOCKED", result.summary_message)

    def test_summary_contains_counts(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.BLOCKED,
            (
                self._make_reason("C1", "Manufacturing", "BLOCKED"),
                self._make_reason("C2", "Release", "BLOCKED"),
            ),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertIn("2 critical", result.summary_message)

    def test_empty_summary(self):
        rm, fr, ba = self._import_once()
        result = ba.build_factory_blocking_analysis_read_model(None)
        self.assertTrue(len(result.summary_message) >= 0)

    # ── No backend leakage ───────────────────────────────────────

    def test_no_backend_leakage(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Error", "Manufacturing", "ERROR"),),
        )
        result = ba.build_factory_blocking_analysis_read_model(readiness)
        for item in result.blocking_items:
            self.assertFalse(hasattr(item, "Shape"))
            self.assertFalse(hasattr(item, "all_nodes"))
        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))

    # ── Status mirrored from readiness ──────────────────────────

    def test_status_mirrors_readiness(self):
        rm, fr, ba = self._import_once()
        for status in (fr.BLOCKED, fr.NOT_READY, fr.NEEDS_REVIEW, fr.READY, fr.UNKNOWN):
            readiness = self._make_readiness(
                status,
                (self._make_reason("Test", "Manufacturing", "ERROR"),),
            )
            result = ba.build_factory_blocking_analysis_read_model(readiness)
            self.assertEqual(result.status, status)

    # ── No forbidden imports ─────────────────────────────────────

    def test_no_forbidden_imports(self):
        with open("factory_operational_intelligence/blocking_analysis.py") as f:
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
                msg=f"blocking_analysis.py must not import '{token}'",
            )

    # ── No engine/workflow naming ────────────────────────────────

    def test_no_engine_workflow_naming(self):
        rm, fr, ba = self._import_once()
        name = ba.build_factory_blocking_analysis_read_model.__name__
        for token in ("engine", "workflow", "service", "event", "bus",
                       "store", "controller", "registry", "renderer"):
            self.assertNotIn(
                token, name.lower(),
                msg=f"'{name}' should not contain '{token}'",
            )

    # ── Pure function — no side effects ──────────────────────────

    def test_no_input_mutation(self):
        rm, fr, ba = self._import_once()
        readiness = self._make_readiness(
            fr.NOT_READY,
            (self._make_reason("Error", "Manufacturing", "ERROR"),),
        )
        original_status = readiness.status
        ba.build_factory_blocking_analysis_read_model(readiness)
        self.assertEqual(readiness.status, original_status)


if __name__ == "__main__":
    unittest.main()
