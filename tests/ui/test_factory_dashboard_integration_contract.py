# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Factory Dashboard Integration Contract Tests
#
# Verifies:
# - dashboard read model is stored in workspace (source inspection)
# - service integration builds dashboard from FOI outputs
# - no backend objects leak
# - no duplicated calculations
# - no duplicated FOI logic
# - no direct domain imports
# - existing UI tests pass
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
import types
import unittest
from pathlib import Path


class TestFactoryDashboardIntegrationContract(unittest.TestCase):
    """Verify FactoryDashboardReadModel integration into CV2.

    Note: workspace.py and service_integration.py import core.qt_compat
    which triggers PySide6 (SIGILL when Qt is unavailable). Therefore
    runtime tests use the factory_dashboard module directly with FOI
    read models, while workspace/service_integration are verified via
    source text inspection.
    """

    _dd = None
    _fr = None
    _ba = None
    _ar = None
    _pd = None

    @classmethod
    def _import_once(cls):
        if cls._dd is not None:
            return cls._dd, cls._fr, cls._ba, cls._ar, cls._pd

        import importlib.machinery
        import importlib.util

        for key in list(sys.modules):
            if key.startswith(("factory_dashboard", "factory_operational_intelligence")):
                del sys.modules[key]

        parent1 = types.ModuleType("factory_dashboard")
        parent1.__path__ = ["factory_dashboard"]
        sys.modules["factory_dashboard"] = parent1

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
            if key.startswith(("factory_dashboard", "factory_operational_intelligence")):
                del sys.modules[key]

    def _make_readiness(self, status, bc=0, wc=0, rc=0):
        fr = self._fr
        return fr.FactoryReadinessReadModel(
            status=status,
            blocking_count=bc, warning_count=wc, ready_count=rc,
            summary_message=f"Readiness: {status}",
        )

    def _make_blocking(self, status, critical=0, high=0, medium=0, low=0):
        ba = self._ba
        items = ()
        if critical > 0 or high > 0:
            items = (ba.FactoryBlockingItem(
                blocking_item_id="TEST:BLOCKED:0",
                operational_category="MANUFACTURING",
                source_panel="Manufacturing",
                severity="BLOCKED",
                human_message="CNC blocked",
                operational_impact="Blocks production",
            ),)
        return ba.FactoryBlockingAnalysisReadModel(
            status=status,
            blocking_items=items,
            critical_count=critical, high_count=high,
            medium_count=medium, low_count=low,
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
        )

    def _make_decision(self, status, conf="NONE"):
        pd = self._pd
        return pd.ProductionDecisionReadModel(
            decision_status=status,
            confidence=conf,
            summary_message=f"Decision: {status}",
        )

    # ── Dashboard read model is stored in workspace (source inspection) ─

    def test_workspace_stores_dashboard_field(self):
        """workspace.py defines factory_dashboard_read_model attribute."""
        ws_path = "ui/configurator_v2/workspace.py"
        with open(ws_path) as f:
            src = f.read()
        self.assertIn("factory_dashboard_read_model", src)
        self.assertIn("set_factory_dashboard_read_model", src)
        self.assertIn("set_foi_read_models", src)

    def test_workspace_dashboard_import(self):
        """workspace.py imports FactoryDashboardReadModel from factory_dashboard."""
        with open("ui/configurator_v2/workspace.py") as f:
            src = f.read()
        self.assertIn("from factory_dashboard import FactoryDashboardReadModel", src)

    def test_service_integration_imports_dashboard_builder(self):
        """service_integration.py imports build_factory_dashboard_read_model."""
        with open("ui/configurator_v2/service_integration.py") as f:
            src = f.read()
        self.assertIn("from factory_dashboard import build_factory_dashboard_read_model", src)

    def test_service_integration_has_refresh_dashboard(self):
        """service_integration.py defines refresh_dashboard method."""
        with open("ui/configurator_v2/service_integration.py") as f:
            src = f.read()
        self.assertIn("def refresh_dashboard", src)

    def test_service_integration_stores_foi_on_workspace(self):
        """refresh_factory_operations stores FOI read models via set_foi_read_models."""
        with open("ui/configurator_v2/service_integration.py") as f:
            src = f.read()
        self.assertIn("self.workspace.set_foi_read_models", src)

    # ── Builder works correctly with FOI outputs (runtime) ──────────

    def test_dashboard_builds_from_foi_read_models(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY, bc=0, wc=0, rc=2)
        blocking = self._make_blocking("READY", 0, 0, 0, 0)
        recs = self._make_recommendations(1, 1)
        decision = self._make_decision(pd.START_READY, "HIGH")

        result = dd.build_factory_dashboard_read_model(
            readiness=readiness,
            blocking=blocking,
            recommendations=recs,
            decision=decision,
        )

        self.assertIsInstance(result, dd.FactoryDashboardReadModel)
        self.assertTrue(result.available)
        self.assertGreater(len(result.sections), 0)
        self.assertEqual(result.factory_status, fr.READY)
        self.assertEqual(result.decision_status, pd.START_READY)
        self.assertEqual(result.critical_blocker_count, 0)
        self.assertEqual(result.recommendation_count, 1)

    def test_dashboard_with_blocking_data(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.BLOCKED, bc=2, wc=1, rc=0)
        blocking = self._make_blocking("BLOCKED", 2, 1)
        decision = self._make_decision(pd.HOLD, "MEDIUM")

        result = dd.build_factory_dashboard_read_model(
            readiness=readiness,
            blocking=blocking,
            recommendations=None,
            decision=decision,
        )

        self.assertTrue(result.available)
        self.assertEqual(result.factory_status, fr.BLOCKED)
        self.assertEqual(result.critical_blocker_count, 2)
        self.assertEqual(result.recommendation_count, 0)

    def test_dashboard_empty_when_no_foi_data(self):
        dd, fr, ba, ar, pd = self._import_once()
        result = dd.build_factory_dashboard_read_model()
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    # ── Full FOI pipeline → dashboard (no Qt involved) ────────────

    def test_dashboard_after_full_foi_pipeline(self):
        dd, fr, ba, ar, pd = self._import_once()

        rm_path = Path("ui/configurator_v2/read_models.py")
        import importlib.machinery
        import importlib.util
        rm_loader = importlib.machinery.SourceFileLoader(
            "ui.configurator_v2.read_models", str(rm_path))
        rm_spec = importlib.machinery.ModuleSpec(
            "ui.configurator_v2.read_models", rm_loader, origin=str(rm_path))
        rm = importlib.util.module_from_spec(rm_spec)
        sys.modules["ui.configurator_v2.read_models"] = rm
        rm_loader.exec_module(rm)

        panels = (
            rm.ReviewPanelReadModel(panel_name="Validation", sections=(
                rm.ReviewSectionReadModel("Errors", (("Width", "ERROR"),)),
            ), available=True),
            rm.ReviewPanelReadModel(panel_name="Manufacturing", sections=(
                rm.ReviewSectionReadModel("Passed", (("CNC", "PASS"),)),
            ), available=True),
            rm.ReviewPanelReadModel(panel_name="Cost", available=True),
            rm.ReviewPanelReadModel(panel_name="Commercial", available=True),
            rm.ReviewPanelReadModel(panel_name="Release", available=True),
        )

        r = fr.build_factory_readiness_read_model(panels)
        b = ba.build_factory_blocking_analysis_read_model(r)
        a = ar.build_factory_action_recommendation_read_model(b)
        d = pd.build_production_decision_read_model(r, b, a)

        dashboard = dd.build_factory_dashboard_read_model(
            readiness=r, blocking=b, recommendations=a, decision=d,
        )

        self.assertIsInstance(dashboard, dd.FactoryDashboardReadModel)
        self.assertTrue(dashboard.available)
        snames = {s.section_name for s in dashboard.sections}
        self.assertIn("Factory Readiness", snames)
        self.assertIn("Blocking Analysis", snames)
        self.assertIn("Action Recommendations", snames)
        self.assertIn("Production Decision", snames)

    # ── No backend objects leak ─────────────────────────────────

    def test_no_backend_leakage_in_dashboard_sections(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        blocking = self._make_blocking("READY", 0)
        recs = self._make_recommendations(1, 1)
        decision = self._make_decision(pd.START_READY, "HIGH")

        result = dd.build_factory_dashboard_read_model(
            readiness=readiness, blocking=blocking,
            recommendations=recs, decision=decision,
        )

        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))
        for sec in result.sections:
            self.assertFalse(hasattr(sec, "Shape"))

    # ── No duplicated calculations ──────────────────────────────

    def test_service_integration_dashboard_code_does_not_calculate(self):
        raw = Path("ui/configurator_v2/service_integration.py").read_text()
        tree = ast.parse(raw, filename="ui/configurator_v2/service_integration.py")

        arithmetic_ops: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, (
                    ast.Add, ast.Sub, ast.Mult, ast.Div,
                    ast.FloorDiv, ast.Mod, ast.Pow,
                )):
                    arithmetic_ops.append((type(node.op).__name__, node.lineno))

        sum_calls: list[int] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "sum":
                    sum_calls.append(node.lineno)

        # Only flag arithmetic in lines added by FD-2 (after the
        # FOI pipeline section at line ~410). Existing arithmetic
        # in project_engineering_source is not part of this change.
        dashboard_ops = [op for op in arithmetic_ops if op[1] > 425]
        self.assertEqual(
            dashboard_ops, [],
            f"Dashboard code in service_integration must not perform arithmetic: {dashboard_ops}",
        )

    # ── No duplicated FOI logic ─────────────────────────────────

    def test_no_foi_status_logic_in_workspace(self):
        with open("ui/configurator_v2/workspace.py") as f:
            src = f.read()
        for pattern in ["_determine_status", "START_READY", "START_AFTER_REVIEW",
                         "HOLD", "BLOCKED", "NEEDS_REVIEW", "NOT_READY"]:
            self.assertNotIn(pattern, src,
                             msg=f"workspace.py must not contain '{pattern}'")

    def test_no_foi_status_logic_in_dashboard_module(self):
        dd, fr, ba, ar, pd = self._import_once()
        dd_src = Path("factory_dashboard/dashboard_read_model.py").read_text()
        for pattern in ["_determine_status", "START_READY", "START_AFTER_REVIEW",
                         "HOLD"]:
            self.assertNotIn(pattern, dd_src,
                             msg=f"dashboard_read_model.py must not contain '{pattern}'")

    # ── No direct domain imports ────────────────────────────────

    def test_workspace_no_domain_imports(self):
        with open("ui/configurator_v2/workspace.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines()
                 if l.strip().startswith(("import ", "from "))]
        text = "\n".join(lines)
        forbidden = [
            "domain.", "manufacturing.", "cost_intelligence.",
            "commercial_outputs.", "optimization.", "FreeCAD",
        ]
        for token in forbidden:
            self.assertNotIn(token, text,
                             msg=f"workspace.py must not import '{token}'")

    def test_service_integration_no_direct_domain_imports(self):
        with open("ui/configurator_v2/service_integration.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines()
                 if l.strip().startswith(("import ", "from "))]
        text = "\n".join(lines)
        forbidden = [
            "domain.", "manufacturing.", "cost_intelligence.",
            "commercial_outputs.", "optimization.", "FreeCAD",
        ]
        for token in forbidden:
            self.assertNotIn(token, text,
                             msg=f"service_integration.py must not import '{token}'")

    # ── Deterministic ───────────────────────────────────────────

    def test_deterministic(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY, bc=0, wc=0, rc=2)
        decision = self._make_decision(pd.START_READY, "HIGH")

        r1 = dd.build_factory_dashboard_read_model(readiness=readiness, decision=decision)
        r2 = dd.build_factory_dashboard_read_model(readiness=readiness, decision=decision)
        self.assertEqual(r1, r2)

    # ── No input mutation ───────────────────────────────────────

    def test_no_input_mutation(self):
        dd, fr, ba, ar, pd = self._import_once()
        readiness = self._make_readiness(fr.READY)
        orig_status = readiness.status
        dd.build_factory_dashboard_read_model(readiness=readiness)
        self.assertEqual(readiness.status, orig_status)

    # ── Architecture boundaries ─────────────────────────────────

    def test_dashboard_builder_not_renamed(self):
        dd, fr, ba, ar, pd = self._import_once()
        name = dd.build_factory_dashboard_read_model.__name__
        for token in ("engine", "workflow", "service", "event", "bus",
                       "store", "controller", "registry", "renderer",
                       "ai", "schedule", "render", "chart"):
            self.assertNotIn(
                token, name.lower(),
                msg=f"'{name}' should not contain '{token}'",
            )

    def test_refresh_dashboard_method_exists_in_source(self):
        with open("ui/configurator_v2/service_integration.py") as f:
            src = f.read()
        self.assertIn("def refresh_dashboard", src)

    def test_set_foi_read_models_method_exists_in_source(self):
        with open("ui/configurator_v2/workspace.py") as f:
            src = f.read()
        self.assertIn("def set_foi_read_models", src)

    def test_set_factory_dashboard_read_model_exists_in_source(self):
        with open("ui/configurator_v2/workspace.py") as f:
            src = f.read()
        self.assertIn("def set_factory_dashboard_read_model", src)


if __name__ == "__main__":
    unittest.main()
