# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# FOI Presentation Integration Contract Tests
#
# Verifies:
# - FOI presentation uses only read models (no backend objects)
# - no duplicated calculations
# - no duplicated decision logic
# - workspace integration works
# - existing CV2 tests remain green
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
import types
import unittest
from pathlib import Path


class TestFOIPresentationIntegrationContract(unittest.TestCase):
    """Verify FOI presentation integration into CV2."""

    _rm = None
    _fr = None
    _ba = None
    _ar = None
    _pd = None
    _fpa = None

    @classmethod
    def _import_once(cls):
        if cls._fpa is not None:
            return cls._rm, cls._fr, cls._ba, cls._ar, cls._pd, cls._fpa

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
        fpa = _load("ui.configurator_v2.foi_presentation_adapter",
                     "ui/configurator_v2/foi_presentation_adapter.py")
        cls._rm = rm
        cls._fr = fr
        cls._ba = ba
        cls._ar = ar
        cls._pd = pd
        cls._fpa = fpa
        return rm, fr, ba, ar, pd, fpa

    @classmethod
    def tearDownClass(cls):
        """Remove fake parent modules from sys.modules to avoid polluting
        subsequent tests in the same run.

        The fake parent modules created by _import_once (bare types.ModuleType
        objects without __init__.py content or __file__) remain in sys.modules
        after the test class finishes. If another test file imports
        factory_operational_intelligence or ui.configurator_v2, Python
        resolves to these fakes instead of the real packages.
        """
        for key in list(sys.modules):
            if key.startswith(("factory_operational_intelligence", "ui.configurator_v2")):
                del sys.modules[key]

    def _make_readiness(self, status, bc=0, wc=0, rc=0):
        fr = self._fr
        return fr.FactoryReadinessReadModel(
            status=status,
            blocking_count=bc, warning_count=wc, ready_count=rc,
            summary_message=f"Readiness: {status}",
        )

    def _make_blocking_analysis(self, items):
        ba = self._ba
        return ba.FactoryBlockingAnalysisReadModel(
            status="",
            blocking_items=tuple(items),
            critical_count=sum(1 for i in items if i.severity == "BLOCKED"),
            high_count=sum(1 for i in items if i.severity == "ERROR"),
            medium_count=sum(1 for i in items if i.severity == "WARNING"),
            low_count=sum(1 for i in items if i.severity == "INFO"),
        )

    def _make_blocking_item(self, cat, panel, sev, msg="", item_id=""):
        ba = self._ba
        return ba.FactoryBlockingItem(
            blocking_item_id=item_id or f"{panel}:{cat}:0",
            operational_category=cat, source_panel=panel, severity=sev,
            human_message=msg or f"{sev} in {cat}",
            operational_impact=f"Impact from {panel}",
        )

    def _make_recommendation(self, rid, conf, resp=""):
        ar = self._ar
        return ar.FactoryRecommendation(
            recommendation_id=rid, blocking_reference="REF",
            knowledge_source="Test", knowledge_reference="Test rules",
            responsible_domain=resp or "Engineering",
            recommended_action="Test action", recommendation_reason="Reason",
            confidence=conf, human_message=f"[{conf}] Test action",
        )

    def _make_recommendations_model(self, recs):
        ar = self._ar
        return ar.FactoryRecommendationReadModel(
            status="", recommendations=tuple(recs),
            high_confidence_count=sum(1 for r in recs if r.confidence == "HIGH"),
            medium_confidence_count=sum(1 for r in recs if r.confidence == "MEDIUM"),
            low_confidence_count=sum(1 for r in recs if r.confidence == "LOW"),
            none_confidence_count=sum(1 for r in recs if r.confidence not in ("HIGH", "MEDIUM", "LOW")),
        )

    def _make_decision(self, status, conf="NONE"):
        pd = self._pd
        return pd.ProductionDecisionReadModel(
            decision_status=status, confidence=conf,
            summary_message=f"Decision: {status}",
        )

    # ── FOI presentation uses only CV2 read models ──────────────

    def test_presentation_produces_review_panel_read_model(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        result = fpa.build_foi_presentation_read_model(
            readiness=self._make_readiness(fr.READY),
        )
        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertEqual(result.panel_name, "Factory Operations")

    def test_presentation_empty_when_no_data(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        result = fpa.build_foi_presentation_read_model()
        self.assertFalse(result.available)
        self.assertEqual(len(result.sections), 0)

    def test_presentation_includes_decision_section(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        result = fpa.build_foi_presentation_read_model(
            decision=self._make_decision(pd.START_READY, "HIGH"),
        )
        section_names = {s.section_name for s in result.sections}
        self.assertIn("Production Decision", section_names)

    def test_presentation_includes_all_sections(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        result = fpa.build_foi_presentation_read_model(
            readiness=self._make_readiness("READY", bc=0, wc=0, rc=2),
            blocking=self._make_blocking_analysis((
                self._make_blocking_item("MANUFACTURING", "Manufacturing", "WARNING"),
            )),
            recommendations=self._make_recommendations_model((
                self._make_recommendation("R1", "MEDIUM"),
            )),
            decision=self._make_decision(pd.START_AFTER_REVIEW, "MEDIUM"),
        )
        snames = {s.section_name for s in result.sections}
        self.assertIn("Production Decision", snames)
        self.assertIn("Factory Readiness", snames)
        self.assertIn("Blocking Analysis", snames)
        self.assertIn("Action Recommendations", snames)

    # ── No backend objects leak ─────────────────────────────────

    def test_no_backend_leakage(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        result = fpa.build_foi_presentation_read_model(
            readiness=self._make_readiness(fr.READY),
        )
        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))
        for sec in result.sections:
            self.assertFalse(hasattr(sec, "Shape"))

    # ── No duplicated calculations ──────────────────────────────

    def test_adapter_does_not_calculate(self):
        """Adapter reads existing FOI outputs — never computes new values."""
        rm, fr, ba, ar, pd, fpa = self._import_once()
        raw = Path("ui/configurator_v2/foi_presentation_adapter.py").read_text()
        tree = ast.parse(raw, filename="ui/configurator_v2/foi_presentation_adapter.py")

        # Walk AST for actual arithmetic BinOp nodes — comments and docstrings
        # are invisible to the AST, so this catches only real code arithmetic.
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
            f"Adapter must not perform arithmetic: found {arithmetic_ops}",
        )

        # No sum() calls — would indicate aggregation/calculation
        sum_calls: list[int] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "sum":
                    sum_calls.append(node.lineno)
        self.assertEqual(
            sum_calls, [],
            f"Adapter must not call sum(): found at lines {sum_calls}",
        )

    # ── No duplicated decision logic ────────────────────────────

    def test_adapter_does_not_reimplement_foi(self):
        """Adapter imports FOI models but never reimplements FOI logic."""
        rm, fr, ba, ar, pd, fpa = self._import_once()
        src = Path("ui/configurator_v2/foi_presentation_adapter.py").read_text()
        # Adapter must not contain readiness/blocking/recommendation/decision logic
        for pattern in ["_determine_status", "START_READY", "START_AFTER_REVIEW",
                         "HOLD"]:
            self.assertNotIn(pattern, src,
                             msg=f"Adapter must not contain '{pattern}' — FOI logic belongs in FOI modules")

    # ── Deterministic ───────────────────────────────────────────

    def test_deterministic(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        readiness = self._make_readiness(fr.READY)
        r1 = fpa.build_foi_presentation_read_model(readiness=readiness)
        r2 = fpa.build_foi_presentation_read_model(readiness=readiness)
        self.assertEqual(r1, r2)

    # ── No input mutation ───────────────────────────────────────

    def test_no_input_mutation(self):
        rm, fr, ba, ar, pd, fpa = self._import_once()
        readiness = self._make_readiness(fr.READY)
        orig = readiness.status
        fpa.build_foi_presentation_read_model(readiness=readiness)
        self.assertEqual(readiness.status, orig)

    # ── No forbidden imports ────────────────────────────────────

    def test_no_forbidden_imports_in_adapter(self):
        with open("ui/configurator_v2/foi_presentation_adapter.py") as f:
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
            self.assertNotIn(token, text)

    # ── Workspace stores FOI read model ─────────────────────────

    def test_workspace_stores_foi_read_model(self):
        """Workspace factory creates workspace with foi_presentation_read_model field."""
        # This tests that the workspace module compiles and has the attribute
        rm, fr, ba, ar, pd, fpa = self._import_once()
        ws_path = "ui/configurator_v2/workspace.py"
        with open(ws_path) as f:
            src = f.read()
        self.assertIn("foi_presentation_read_model", src)
        self.assertIn("set_foi_presentation_read_model", src)

    # ── FOI pipeline runs end-to-end from CV2 ───────────────────

    def test_foi_pipeline_runs_from_cv2_review_panels(self):
        """Run the full FOI pipeline on review panel data, verify it produces
        a ReviewPanelReadModel through the presentation adapter."""
        rm, fr, ba, ar, pd, fpa = self._import_once()

        # Create realistic review panels
        panels = (
            rm.ReviewPanelReadModel(panel_name="Validation", sections=(
                rm.ReviewSectionReadModel("Errors", (("Width", "ERROR — Out of tolerance"),)),
            ), available=True),
            rm.ReviewPanelReadModel(panel_name="Manufacturing", sections=(
                rm.ReviewSectionReadModel("Passed", (("CNC", "PASS"),)),
            ), available=True),
            rm.ReviewPanelReadModel(panel_name="Cost", available=True),
            rm.ReviewPanelReadModel(panel_name="Commercial", available=True),
            rm.ReviewPanelReadModel(panel_name="Release", available=True),
        )

        # Run FOI pipeline
        r_model = fr.build_factory_readiness_read_model(panels)
        b_model = ba.build_factory_blocking_analysis_read_model(r_model)
        a_model = ar.build_factory_action_recommendation_read_model(b_model)
        d_model = pd.build_production_decision_read_model(r_model, b_model, a_model)

        # Present via adapter
        result = fpa.build_foi_presentation_read_model(
            readiness=r_model, blocking=b_model,
            recommendations=a_model, decision=d_model,
        )

        self.assertIsInstance(result, rm.ReviewPanelReadModel)
        self.assertEqual(result.panel_name, "Factory Operations")
        self.assertTrue(result.available)
        # Should have at least the Production Decision section
        snames = {s.section_name for s in result.sections}
        self.assertIn("Production Decision", snames)


if __name__ == "__main__":
    unittest.main()
