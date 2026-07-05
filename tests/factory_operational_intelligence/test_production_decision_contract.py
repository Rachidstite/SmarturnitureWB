# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Production Decision Contract Tests
#
# Verifies:
# - deterministic output
# - frozen dataclasses
# - immutable
# - empty input
# - START_READY
# - START_AFTER_REVIEW
# - HOLD
# - BLOCKED
# - UNKNOWN
# - traceability to blocking and recommendation IDs
# - no backend imports
# - no AI
# - no scheduling
# - no execution
# - no calculations
# - no mutation
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class TestProductionDecisionContract(unittest.TestCase):
    """Verify production decision read model contract."""

    _rm = None
    _fr = None
    _ba = None
    _ar = None
    _pd = None

    @classmethod
    def _import_once(cls):
        if cls._pd is not None:
            return cls._rm, cls._fr, cls._ba, cls._ar, cls._pd

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
        fr = _load("factory_operational_intelligence.factory_readiness",
                    "factory_operational_intelligence/factory_readiness.py")
        ba = _load("factory_operational_intelligence.blocking_analysis",
                    "factory_operational_intelligence/blocking_analysis.py")
        ar = _load("factory_operational_intelligence.factory_action_recommendation",
                    "factory_operational_intelligence/factory_action_recommendation.py")
        pd = _load("factory_operational_intelligence.production_decision",
                    "factory_operational_intelligence/production_decision.py")
        cls._rm = rm
        cls._fr = fr
        cls._ba = ba
        cls._ar = ar
        cls._pd = pd
        return rm, fr, ba, ar, pd

    def _make_blocking_item(self, category, panel, severity, message="", item_id=""):
        ba = self._ba
        return ba.FactoryBlockingItem(
            blocking_item_id=item_id or f"{panel.upper().replace(' ', '_')}:{category.upper().replace(' ', '_')}:0",
            operational_category=category,
            source_panel=panel,
            severity=severity,
            human_message=message or f"{severity} in {category}",
            operational_impact=f"Impact from {panel}",
        )

    def _make_blocking_analysis(self, status, items):
        ba = self._ba
        return ba.FactoryBlockingAnalysisReadModel(
            status=status,
            blocking_items=tuple(items),
            critical_count=sum(1 for i in items if i.severity == "BLOCKED"),
            high_count=sum(1 for i in items if i.severity == "ERROR"),
            medium_count=sum(1 for i in items if i.severity == "WARNING"),
            low_count=sum(1 for i in items if i.severity == "INFO"),
            source_panels=tuple(sorted(set(i.source_panel for i in items))),
        )

    def _make_recommendation(self, rid, confidence, blocking_ref="", responsible=""):
        ar = self._ar
        return ar.FactoryRecommendation(
            recommendation_id=rid,
            blocking_reference=blocking_ref,
            knowledge_source="Test",
            knowledge_reference="Test rules",
            responsible_domain=responsible or "Engineering",
            recommended_action="Review and correct",
            recommendation_reason="Test reason",
            confidence=confidence,
            human_message=f"[{confidence}] Test action (Test — Test rules)",
        )

    def _make_recommendations_model(self, status, recs):
        ar = self._ar
        return ar.FactoryRecommendationReadModel(
            status=status,
            recommendations=tuple(recs),
            high_confidence_count=sum(1 for r in recs if r.confidence == "HIGH"),
            medium_confidence_count=sum(1 for r in recs if r.confidence == "MEDIUM"),
            low_confidence_count=sum(1 for r in recs if r.confidence == "LOW"),
            none_confidence_count=sum(1 for r in recs if r.confidence not in ("HIGH", "MEDIUM", "LOW")),
        )

    def _make_readiness(self, status):
        fr = self._fr
        return fr.FactoryReadinessReadModel(status=status)

    # ── Deterministic output ─────────────────────────────────────

    def test_deterministic(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        r1 = pd.build_production_decision_read_model(readiness, analysis, recs)
        r2 = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(r1, r2)

    # ── Frozen dataclasses ───────────────────────────────────────

    def test_decision_reason_is_frozen(self):
        rm, fr, ba, ar, pd = self._import_once()
        self.assertTrue(hasattr(pd.ProductionDecisionReason, "__dataclass_fields__"))

    def test_read_model_is_frozen(self):
        rm, fr, ba, ar, pd = self._import_once()
        self.assertTrue(hasattr(pd.ProductionDecisionReadModel, "__dataclass_fields__"))

    # ── Immutable / no mutation ──────────────────────────────────

    def test_no_input_mutation(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        orig = readiness.status
        pd.build_production_decision_read_model(readiness, None, None)
        self.assertEqual(readiness.status, orig)

    # ── Empty/NONE inputs ────────────────────────────────────────

    def test_none_all_returns_unknown(self):
        rm, fr, ba, ar, pd = self._import_once()
        result = pd.build_production_decision_read_model(None, None, None)
        self.assertEqual(result.decision_status, pd.UNKNOWN)

    def test_none_readiness_returns_unknown(self):
        rm, fr, ba, ar, pd = self._import_once()
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(None, analysis, recs)
        self.assertEqual(result.decision_status, pd.UNKNOWN)

    def test_none_analysis_returns_unknown(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, None, recs)
        self.assertEqual(result.decision_status, pd.UNKNOWN)

    def test_none_recommendations_returns_unknown(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        analysis = self._make_blocking_analysis("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, None)
        self.assertEqual(result.decision_status, pd.UNKNOWN)

    # ── BLOCKED ──────────────────────────────────────────────────

    def test_blocked_when_readiness_blocked(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.BLOCKED)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.BLOCKED)

    def test_blocked_when_critical_blocker_exists(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NOT_READY)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED",
                                       item_id="MFG:BLOCKED:0"),),
        )
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.BLOCKED)

    # ── HOLD ─────────────────────────────────────────────────────

    def test_hold_when_readiness_not_ready(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NOT_READY)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR",
                                       item_id="MFG:ERR:0"),),
        )
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.HOLD)

    def test_hold_when_high_count_exists(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NEEDS_REVIEW)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR",
                                       item_id="MFG:ERR:0"),),
        )
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.HOLD)

    # ── START_AFTER_REVIEW ───────────────────────────────────────

    def test_start_after_review_when_warnings_exist(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NEEDS_REVIEW)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "WARNING",
                                       item_id="MFG:WARN:0"),),
        )
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.START_AFTER_REVIEW)

    # ── START_READY ──────────────────────────────────────────────

    def test_start_ready_when_all_clear(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.START_READY)

    # ── UNKNOWN ──────────────────────────────────────────────────

    def test_unknown_when_readiness_unknown(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.UNKNOWN)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.decision_status, pd.UNKNOWN)

    # ── Traceability ─────────────────────────────────────────────

    def test_blocking_item_ids_present(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NOT_READY)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR",
                                       item_id="MFG:ERR:0"),),
        )
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertIn("MFG:ERR:0", result.blocking_item_ids)

    def test_recommendation_ids_present(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NOT_READY)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR",
                                       item_id="MFG:ERR:0"),),
        )
        recs = self._make_recommendations_model(
            "",
            (self._make_recommendation("REC-0001", "HIGH", "MFG:ERR:0", "Manufacturing"),),
        )
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertIn("REC-0001", result.recommendation_ids)

    def test_decision_reason_has_traceability(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NOT_READY)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR",
                                       item_id="MFG:ERR:0"),),
        )
        recs = self._make_recommendations_model(
            "",
            (self._make_recommendation("REC-0001", "HIGH", "MFG:ERR:0", "Manufacturing"),),
        )
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        blocking_refs = [r.blocking_item_id for r in result.decision_reasons]
        rec_refs = [r.recommendation_id for r in result.decision_reasons]
        self.assertTrue(
            any("MFG:ERR:0" in bid for bid in blocking_refs) or
            any("REC-0001" in rid for rid in rec_refs),
        )

    # ── Confidence ───────────────────────────────────────────────

    def test_confidence_none_when_no_recommendations(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.confidence, "NONE")

    def test_confidence_lowest_across_recommendations(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.NOT_READY)
        analysis = self._make_blocking_analysis(
            "",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR",
                                       item_id="MFG:ERR:0"),),
        )
        recs = self._make_recommendations_model(
            "",
            (self._make_recommendation("R1", "HIGH"),
             self._make_recommendation("R2", "MEDIUM")),
        )
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertEqual(result.confidence, "MEDIUM")

    # ── Summary message ──────────────────────────────────────────

    def test_summary_contains_status(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertIn(pd.START_READY, result.summary_message)

    # ── No backend leakage ───────────────────────────────────────

    def test_no_backend_leakage(self):
        rm, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        analysis = self._make_blocking_analysis("", ())
        recs = self._make_recommendations_model("", ())
        result = pd.build_production_decision_read_model(readiness, analysis, recs)
        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))

    # ── No forbidden imports ─────────────────────────────────────

    def test_no_forbidden_imports(self):
        with open("factory_operational_intelligence/production_decision.py") as f:
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
                msg=f"production_decision.py must not import '{token}'",
            )

    # ── No engine/workflow naming ────────────────────────────────

    def test_no_engine_workflow_naming(self):
        rm, fr, ba, ar, pd = self._import_once()
        name = pd.build_production_decision_read_model.__name__
        for token in ("engine", "workflow", "service", "event", "bus",
                       "store", "controller", "registry", "renderer", "ai", "schedule"):
            self.assertNotIn(
                token, name.lower(),
                msg=f"'{name}' should not contain '{token}'",
            )


if __name__ == "__main__":
    unittest.main()
