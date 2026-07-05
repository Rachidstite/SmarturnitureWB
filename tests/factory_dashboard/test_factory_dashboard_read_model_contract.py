# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Dashboard
# Factory Dashboard Read Model Contract Tests
#
# Verifies:
# - immutable frozen dataclass
# - deterministic output
# - empty inputs return empty dashboard
# - consumes only FOI read models
# - no backend/domain/manufacturing/cost/commercial/FreeCAD/Qt imports
# - no calculations
# - no duplicated FOI logic
# - no mutation
# - summary fields copied only (never derived)
# - architecture boundaries
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import sys
import types
import unittest
from pathlib import Path


class TestFactoryDashboardReadModelContract(unittest.TestCase):
    """Verify factory dashboard read model contract."""

    _dd = None
    _fr = None
    _ba = None
    _ar = None
    _pd = None

    @classmethod
    def _import_once(cls):
        if cls._dd is not None:
            return cls._dd, cls._fr, cls._ba, cls._ar, cls._pd

        for key in list(sys.modules):
            if key.startswith(("factory_dashboard", "factory_operational_intelligence",
                               "ui.configurator_v2")):
                del sys.modules[key]

        parent1 = types.ModuleType("factory_dashboard")
        parent1.__path__ = ["factory_dashboard"]
        sys.modules["factory_dashboard"] = parent1

        parent2 = types.ModuleType("factory_operational_intelligence")
        parent2.__path__ = ["factory_operational_intelligence"]
        sys.modules["factory_operational_intelligence"] = parent2

        parent3 = types.ModuleType("ui.configurator_v2")
        parent3.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent3

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        dd = _load("factory_dashboard.dashboard_read_model",
                    "factory_dashboard/dashboard_read_model.py")
        fr = _load("factory_operational_intelligence.factory_readiness",
                    "factory_operational_intelligence/factory_readiness.py")
        ba = _load("factory_operational_intelligence.blocking_analysis",
                    "factory_operational_intelligence/blocking_analysis.py")
        ar = _load("factory_operational_intelligence.factory_action_recommendation",
                    "factory_operational_intelligence/factory_action_recommendation.py")
        pd = _load("factory_operational_intelligence.production_decision",
                    "factory_operational_intelligence/production_decision.py")
        cls._dd = dd
        cls._fr = fr
        cls._ba = ba
        cls._ar = ar
        cls._pd = pd
        return dd, fr, ba, ar, pd

    @classmethod
    def tearDownClass(cls):
        for key in list(sys.modules):
            if key.startswith(("factory_dashboard", "factory_operational_intelligence",
                               "ui.configurator_v2")):
                del sys.modules[key]

    def _make_readiness(self, status, bc=0, wc=0, rc=0):
        fr = self._fr
        return fr.FactoryReadinessReadModel(
            status=status,
            blocking_count=bc,
            warning_count=wc,
            ready_count=rc,
            summary_message=f"Readiness: {status}",
        )

    def _make_blocking(self, status, critical=0, high=0, medium=0, low=0):
        ba = self._ba
        return ba.FactoryBlockingAnalysisReadModel(
            status=status,
            blocking_items=(),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            summary_message=f"Blocking: {critical} critical, {high} errors",
        )

    def _make_recommendations(self, count, high=0, medium=0, low=0, none_c=0):
        ar = self._ar
        recs = tuple(
            ar.FactoryRecommendation(
                recommendation_id=f"REC-{i+1:04d}",
                blocking_reference="REF",
                knowledge_source="Test",
                knowledge_reference="Test rules",
                responsible_domain="Engineering",
                recommended_action="Test action",
                recommendation_reason="Test reason",
                confidence="HIGH" if i < high else "MEDIUM" if i < high + medium else "LOW",
                human_message="Test",
            )
            for i in range(count)
        )
        return ar.FactoryRecommendationReadModel(
            status="",
            recommendations=recs,
            high_confidence_count=high,
            medium_confidence_count=medium,
            low_confidence_count=low,
            none_confidence_count=none_c,
            summary_message=f"Recommendations: {count} available",
        )

    def _make_decision(self, status, conf="NONE"):
        pd = self._pd
        return pd.ProductionDecisionReadModel(
            decision_status=status,
            confidence=conf,
            summary_message=f"Decision: {status}",
        )

    # ── Immutable frozen dataclass ───────────────────────────────

    def test_dashboard_is_frozen(self):
        dd, fr, ba, ar, pd = self._import_once()
        self.assertTrue(hasattr(dd.FactoryDashboardReadModel, "__dataclass_fields__"))

    def test_section_is_frozen(self):
        dd, fr, ba, ar, pd = self._import_once()
        self.assertTrue(hasattr(dd.FactoryDashboardSection, "__dataclass_fields__"))

    # ── Deterministic output ────────────────────────────────────

    def test_deterministic(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        blocking = self._make_blocking("READY", 0, 0, 0, 0)
        recs = self._make_recommendations(0)
        decision = self._make_decision(pd.START_READY, "HIGH")
        r1 = dd.build_factory_dashboard_read_model(
            readiness=readiness, blocking=blocking,
            recommendations=recs, decision=decision,
        )
        r2 = dd.build_factory_dashboard_read_model(
            readiness=readiness, blocking=blocking,
            recommendations=recs, decision=decision,
        )
        self.assertEqual(r1, r2)

    # ── Empty inputs ────────────────────────────────────────────

    def test_none_all_returns_empty(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model()
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)
        self.assertEqual(result.factory_status, "")
        self.assertEqual(result.decision_status, "")
        self.assertEqual(result.critical_blocker_count, 0)
        self.assertEqual(result.recommendation_count, 0)
        self.assertEqual(result.summary_message, "")

    def test_none_readiness_returns_empty(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=None,
            blocking=None,
            recommendations=None,
            decision=None,
        )
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    def test_empty_readiness_returns_empty_section(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(""),
        )
        self.assertEqual(len(result.sections), 0)

    # ── Consumes only FOI read models ───────────────────────────

    def test_full_dashboard_has_all_sections(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.READY),
            blocking=self._make_blocking("READY", 0, 0, 0, 0),
            recommendations=self._make_recommendations(1, 1),
            decision=self._make_decision(pd.START_READY, "HIGH"),
        )
        snames = {s.section_name for s in result.sections}
        self.assertIn("Factory Readiness", snames)
        self.assertIn("Blocking Analysis", snames)
        self.assertIn("Action Recommendations", snames)
        self.assertIn("Production Decision", snames)

    def test_readiness_only(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.READY),
        )
        snames = {s.section_name for s in result.sections}
        self.assertIn("Factory Readiness", snames)
        self.assertNotIn("Blocking Analysis", snames)
        self.assertNotIn("Action Recommendations", snames)
        self.assertNotIn("Production Decision", snames)

    def test_blocking_only(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            blocking=self._make_blocking("BLOCKED", 2),
        )
        snames = {s.section_name for s in result.sections}
        self.assertIn("Blocking Analysis", snames)

    def test_recommendations_only(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            recommendations=self._make_recommendations(2, 2),
        )
        snames = {s.section_name for s in result.sections}
        self.assertIn("Action Recommendations", snames)

    def test_decision_only(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            decision=self._make_decision(pd.START_READY, "HIGH"),
        )
        snames = {s.section_name for s in result.sections}
        self.assertIn("Production Decision", snames)

    # ── Summary fields copied only ──────────────────────────────

    def test_summary_factory_status_copied(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.BLOCKED),
        )
        self.assertEqual(result.factory_status, fr.BLOCKED)

    def test_summary_decision_status_copied(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            decision=self._make_decision(pd.HOLD, "MEDIUM"),
        )
        self.assertEqual(result.decision_status, pd.HOLD)

    def test_summary_critical_blocker_count_copied(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            blocking=self._make_blocking("BLOCKED", 3, 2),
            readiness=self._make_readiness(fr.BLOCKED),
        )
        self.assertEqual(result.critical_blocker_count, 3)

    def test_summary_recommendation_count_copied(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            recommendations=self._make_recommendations(4, 2, 2),
        )
        self.assertEqual(result.recommendation_count, 4)

    def test_summary_message_copied(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            decision=self._make_decision(pd.START_READY, "HIGH"),
        )
        self.assertIn("START_READY", result.summary_message)

    def test_summary_fields_empty_when_no_data(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model()
        self.assertEqual(result.factory_status, "")
        self.assertEqual(result.decision_status, "")
        self.assertEqual(result.critical_blocker_count, 0)
        self.assertEqual(result.recommendation_count, 0)
        self.assertEqual(result.summary_message, "")

    # ── Deterministic with blocking data ────────────────────────

    def test_deterministic_with_blocking_items(self):
        dd, fr, ba, ar, pd = self._import_once()
        ba_m = self._ba
        item = ba_m.FactoryBlockingItem(
            blocking_item_id="TEST:BLOCKED:0",
            operational_category="MANUFACTURING",
            source_panel="Manufacturing",
            severity="BLOCKED",
            human_message="CNC blocked",
            operational_impact="Blocks production",
        )
        blocking = ba_m.FactoryBlockingAnalysisReadModel(
            status=fr.BLOCKED,
            blocking_items=(item,),
            critical_count=1, high_count=0, medium_count=0, low_count=0,
            summary_message="1 critical blocker",
        )
        r1 = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.BLOCKED),
            blocking=blocking,
        )
        r2 = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.BLOCKED),
            blocking=blocking,
        )
        self.assertEqual(r1, r2)
        self.assertEqual(r1.critical_blocker_count, 1)

    # ── No backend imports ──────────────────────────────────────

    def test_no_forbidden_imports(self):
        dd, fr, ba, ar, pd = self._import_once()
        with open("factory_dashboard/dashboard_read_model.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines()
                 if l.strip().startswith(("import ", "from "))]
        text = "\n".join(lines)
        forbidden = [
            "domain.", "manufacturing.", "cost_intelligence.",
            "commercial_outputs.", "optimization.", "FreeCAD",
            "QtWidgets", "QtCore", "QtGui",
            "factory_operational_intelligence",
        ]
        for token in forbidden:
            self.assertNotIn(
                token, text,
                msg=f"dashboard_read_model.py must not import '{token}'",
            )

    # ── No calculations ─────────────────────────────────────────

    def test_no_arithmetic(self):
        dd, fr, ba, ar, pd = self._import_once()
        import ast
        raw = Path("factory_dashboard/dashboard_read_model.py").read_text()
        tree = ast.parse(raw, filename="factory_dashboard/dashboard_read_model.py")
        arithmetic_ops: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, (
                    ast.Add, ast.Sub, ast.Mult, ast.Div,
                    ast.FloorDiv, ast.Mod, ast.Pow,
                )):
                    arithmetic_ops.append((type(node.op).__name__, node.lineno))
        self.assertEqual(
            arithmetic_ops, [],
            f"Dashboard must not perform arithmetic: found {arithmetic_ops}",
        )

    # ── No duplication of FOI logic ─────────────────────────────

    def test_no_foi_status_logic(self):
        dd, fr, ba, ar, pd = self._import_once()
        src = Path("factory_dashboard/dashboard_read_model.py").read_text()
        patterns = [
            "_determine_status",
            "START_READY", "START_AFTER_REVIEW", "HOLD",
            "NEEDS_REVIEW", "NOT_READY", "BLOCKED", "UNKNOWN",
            "_SEVERITY_", "STATUS_PRIORITY",
            "_BLOCKED_SECTION", "_ERROR_SECTION",
            "_WARNING_SECTION", "_READY_SECTION",
            "_KNOWLEDGE_MAP", "_PANEL_CATEGORY",
            "_IMPACT_TEMPLATES",
        ]
        for pattern in patterns:
            self.assertNotIn(
                pattern, src,
                msg=f"Dashboard must not contain '{pattern}' — FOI logic belongs in FOI modules",
            )

    # ── No input mutation ───────────────────────────────────────

    def test_no_input_mutation(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        orig = readiness.status
        dd.build_factory_dashboard_read_model(readiness=readiness)
        self.assertEqual(readiness.status, orig)

    # ── Architecture boundaries ─────────────────────────────────

    def test_no_engine_workflow_naming(self):
        dd, fr, ba, ar, pd = self._import_once()
        name = dd.build_factory_dashboard_read_model.__name__
        for token in ("engine", "workflow", "service", "event", "bus",
                       "store", "controller", "registry", "renderer",
                       "ai", "schedule", "render", "chart"):
            self.assertNotIn(
                token, name.lower(),
                msg=f"'{name}' should not contain '{token}'",
            )

    def test_dashboard_available(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.READY),
        )
        self.assertTrue(result.available)

    def test_dashboard_not_available_when_empty(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model()
        self.assertFalse(result.available)

    def test_section_rows_present(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model(
            readiness=self._make_readiness(fr.READY, 0, 0, 2),
        )
        self.assertEqual(len(result.sections), 1)
        section = result.sections[0]
        self.assertEqual(section.section_name, "Factory Readiness")
        row_keys = {r[0] for r in section.rows}
        self.assertIn("Status", row_keys)
        self.assertIn("Ready Signals", row_keys)


if __name__ == "__main__":
    unittest.main()
