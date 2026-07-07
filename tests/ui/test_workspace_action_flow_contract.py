"""
Alpha-UI-2: End-to-End Workspace Action Flow — Contract Tests
==============================================================
"""

import importlib.machinery
import importlib.util
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


class _FakeSignal:
    def connect(self, _callback):
        return None


class _FakeWidget:
    def __init__(self, *args, **kwargs):
        self._layout = None
        self._text = ""
        self._enabled = True

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def setEnabled(self, enabled):
        self._enabled = bool(enabled)

    def setMinimumHeight(self, _height):
        return None

    def setWordWrap(self, _enabled):
        return None

    def setCheckable(self, _enabled):
        return None

    def setChecked(self, _enabled):
        return None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeLayout:
    def __init__(self, *args, **kwargs):
        self.items = []

    def addWidget(self, widget):
        self.items.append(widget)

    def addLayout(self, layout):
        self.items.append(layout)

    def setContentsMargins(self, *_args):
        return None


class _FakeComboBox(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.currentIndexChanged = _FakeSignal()

    def addItem(self, text):
        self.items.append(text)

    def setCurrentText(self, _text):
        return None


class _FakeButton(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self.clicked = _FakeSignal()


class _FakeLabel(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text


class _FakeTabWidget(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = []

    def addTab(self, widget, title):
        self.tabs.append((widget, title))

    def setTabText(self, index, title):
        if 0 <= index < len(self.tabs):
            widget, _ = self.tabs[index]
            self.tabs[index] = (widget, title)


def _fake_qt_module():
    fake_qt_widgets = types.SimpleNamespace(
        QWidget=_FakeWidget,
        QFrame=_FakeWidget,
        QVBoxLayout=_FakeLayout,
        QHBoxLayout=_FakeLayout,
        QLabel=_FakeLabel,
        QPushButton=_FakeButton,
        QComboBox=_FakeComboBox,
        QTabWidget=_FakeTabWidget,
    )
    fake_qt_core = types.SimpleNamespace()
    return types.SimpleNamespace(QtWidgets=fake_qt_widgets, QtCore=fake_qt_core)


class TestWorkspaceActionFlowContract(unittest.TestCase):
    """Contract tests for generate_manufacturing, review_cost, review_commercial."""

    _si = None
    _ws = None
    @classmethod
    def _load_modules(cls):
        """Load needed modules via SourceFileLoader, bypassing real Qt."""
        if cls._si is not None:
            return cls._si, cls._ws

        for key in list(sys.modules):
            if key.startswith(("ui.configurator_v2", "core",
                               "factory_dashboard", "factory_operational_intelligence",
                               "manufacturing", "cost_intelligence", "ui")):
                del sys.modules[key]

        # Stub parent packages
        for name in ("ui", "ui.configurator_v2", "core",
                     "factory_dashboard", "factory_operational_intelligence",
                     "manufacturing", "cost_intelligence"):
            parent = types.ModuleType(name)
            parent.__path__ = [name.replace(".", "/")]
            sys.modules[name] = parent

        sys.modules["core.qt_compat"] = _fake_qt_module()

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
            mod = importlib.util.module_from_spec(spec)
            mod.__file__ = path
            mod.__loader__ = loader
            mod.__package__ = name.rsplit(".", 1)[0]
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        def _export(module_name, package_name, names):
            module = sys.modules[module_name]
            package = sys.modules[package_name]
            for name in names:
                setattr(package, name, getattr(module, name))

        _load("factory_dashboard.dashboard_read_model",
              "factory_dashboard/dashboard_read_model.py")
        _load("factory_dashboard.review_summary",
              "factory_dashboard/review_summary.py")
        _export(
            "factory_dashboard.dashboard_read_model",
            "factory_dashboard",
            (
                "FactoryDashboardReadModel",
                "FactoryDashboardSection",
                "build_factory_dashboard_read_model",
                "build_manufacturing_render_dashboard_section",
                "build_nesting_savings_dashboard_section",
            ),
        )
        _export(
            "factory_dashboard.review_summary",
            "factory_dashboard",
            ("ManufacturingReviewSummary", "build_manufacturing_review_summary"),
        )

        _load("factory_operational_intelligence.factory_readiness",
              "factory_operational_intelligence/factory_readiness.py")
        _load("factory_operational_intelligence.blocking_analysis",
              "factory_operational_intelligence/blocking_analysis.py")
        _load("factory_operational_intelligence.factory_action_recommendation",
              "factory_operational_intelligence/factory_action_recommendation.py")
        _load("factory_operational_intelligence.production_decision",
              "factory_operational_intelligence/production_decision.py")
        _export(
            "factory_operational_intelligence.factory_readiness",
            "factory_operational_intelligence",
            ("build_factory_readiness_read_model",),
        )
        _export(
            "factory_operational_intelligence.blocking_analysis",
            "factory_operational_intelligence",
            ("build_factory_blocking_analysis_read_model",),
        )
        _export(
            "factory_operational_intelligence.factory_action_recommendation",
            "factory_operational_intelligence",
            ("build_factory_action_recommendation_read_model",),
        )
        _export(
            "factory_operational_intelligence.production_decision",
            "factory_operational_intelligence",
            ("build_production_decision_read_model",),
        )

        ws = _load("ui.configurator_v2.workspace", "ui/configurator_v2/workspace.py")
        si = _load("ui.configurator_v2.service_integration", "ui/configurator_v2/service_integration.py")
        cls._si = si
        cls._ws = ws
        return si, ws

    def _make_workspace(self):
        self._load_modules()
        ws = SimpleNamespace()
        dashboard_mod = sys.modules["factory_dashboard"]
        ws.review_panel_names = ("Validation", "Manufacturing", "Cost", "Commercial", "Release")
        ws.review_panel_read_models = ()
        ws.message_center_read_model = SimpleNamespace(messages=())
        ws.factory_dashboard_read_model = dashboard_mod.FactoryDashboardReadModel()
        ws._foi_readiness = None
        ws._foi_blocking = None
        ws._foi_recommendations = None
        ws._foi_decision = None
        ws._nesting_savings_report = None
        ws._nesting_savings_dashboard_section = None
        ws._manufacturing_production_package = None
        ws._manufacturing_cost_summary = None
        ws._manufacturing_commercial_result = None
        ws._last_review_panels = None

        def set_review_panel_read_models(models):
            ws._last_review_panels = models
            ws.review_panel_read_models = models

        def set_message_center_read_model(m):
            ws.message_center_read_model = m

        def set_manufacturing_result(pkg):
            ws._manufacturing_production_package = pkg

        def set_cost_result(cs):
            ws._manufacturing_cost_summary = cs

        def set_commercial_result(cr):
            ws._manufacturing_commercial_result = cr

        def set_factory_dashboard_read_model(read_model):
            ws.factory_dashboard_read_model = read_model

        def set_nesting_savings_report(report):
            ws._nesting_savings_report = report

        def set_nesting_savings_dashboard_section(section):
            ws._nesting_savings_dashboard_section = section

        ws.set_review_panel_read_models = set_review_panel_read_models
        ws.set_message_center_read_model = set_message_center_read_model
        ws.set_manufacturing_result = set_manufacturing_result
        ws.set_cost_result = set_cost_result
        ws.set_commercial_result = set_commercial_result
        ws.set_factory_dashboard_read_model = set_factory_dashboard_read_model
        ws.set_nesting_savings_report = set_nesting_savings_report
        ws.set_nesting_savings_dashboard_section = set_nesting_savings_dashboard_section

        set_review_panel_read_models(
            tuple(SimpleNamespace(panel_name=n, sections=(), available=False)
                  for n in ws.review_panel_names)
        )
        return ws

    def _make_bindings(self):
        _, ws_mod = self._load_modules()
        return ws_mod.ConfiguratorV2ServiceBindings()

    def _make_integration(self, workspace=None, service_bindings=None):
        si_mod, _ = self._load_modules()
        return si_mod.ConfiguratorV2ServiceIntegration(
            workspace=workspace or self._make_workspace(),
            service_bindings=service_bindings,
        )

    # ── 1. generate_manufacturing stores production result ────────────

    def test_generate_manufacturing_requires_source(self):
        integration = self._make_integration()
        status = integration.generate_manufacturing(source=None)
        self.assertEqual(status, "no_source")

    def test_generate_manufacturing_stores_result(self):
        self._load_modules()
        ws = self._make_workspace()
        bindings = self._make_bindings()
        runtime_builder = Mock()
        package_builder = Mock()
        bindings.manufacturing_runtime_pipeline_builder = runtime_builder
        bindings.manufacturing_production_package_builder = package_builder
        integration = self._make_integration(ws, service_bindings=bindings)

        pkg = SimpleNamespace(
            cutlist_report=SimpleNamespace(items=[]),
            edge_report=None, machining_report=None,
            cnc_report=None, assembly_report=None, hardware_report=None,
        )

        runtime_builder.return_value.build.return_value = SimpleNamespace(
            manufacturing_package=SimpleNamespace()
        )
        package_builder.return_value.build.return_value = pkg
        status = integration.generate_manufacturing(source=object())

        self.assertEqual(status, "ok")
        self.assertIs(ws._manufacturing_production_package, pkg)

    def test_generate_manufacturing_refreshes_manufacturing_panel(self):
        self._load_modules()
        ws = self._make_workspace()
        bindings = self._make_bindings()
        runtime_builder = Mock()
        package_builder = Mock()
        bindings.manufacturing_runtime_pipeline_builder = runtime_builder
        bindings.manufacturing_production_package_builder = package_builder
        integration = self._make_integration(ws, service_bindings=bindings)

        runtime_builder.return_value.build.return_value = SimpleNamespace(
            manufacturing_package=SimpleNamespace()
        )
        package_builder.return_value.build.return_value = SimpleNamespace(
            cutlist_report=SimpleNamespace(items=[]),
            edge_report=None, machining_report=None,
            cnc_report=None, assembly_report=None, hardware_report=None,
        )
        integration.generate_manufacturing(source=object())

        self.assertIsNotNone(ws._last_review_panels)
        names = tuple(getattr(p, "panel_name", "") for p in ws._last_review_panels)
        self.assertIn("Manufacturing", names)

    # ── 2. review_cost fails safely before manufacturing ─────────────

    def test_review_cost_fails_before_manufacturing(self):
        integration = self._make_integration()
        status = integration.review_cost()
        self.assertEqual(status, "no_manufacturing")

    # ── 3. review_cost consumes stored production package ─────────────

    def test_review_cost_consumes_stored_package(self):
        self._load_modules()
        ws = self._make_workspace()
        bindings = self._make_bindings()
        cost_builder = Mock()
        bindings.manufacturing_cost_pipeline_builder = cost_builder
        integration = self._make_integration(ws, service_bindings=bindings)
        ws._manufacturing_production_package = SimpleNamespace()

        cost_summary = SimpleNamespace(
            cost_report=SimpleNamespace(material_cost=600.0, total_manufacturing_cost=600.0),
            total_manufacturing_cost=600.0, warnings=[], risk_level="LOW",
        )

        cost_builder.return_value.build.return_value = cost_summary
        status = integration.review_cost()

        self.assertEqual(status, "ok")
        cost_builder.return_value.build.assert_called_once_with(ws._manufacturing_production_package)
        self.assertIs(ws._manufacturing_cost_summary, cost_summary)

    # ── 4. review_commercial fails safely before cost ────────────────

    def test_review_commercial_fails_before_cost(self):
        integration = self._make_integration()
        status = integration.review_commercial()
        self.assertEqual(status, "no_cost")

    # ── 5. review_commercial consumes stored cost summary ─────────────

    def test_review_commercial_consumes_stored_cost(self):
        self._load_modules()
        ws = self._make_workspace()
        bindings = self._make_bindings()
        commercial_builder = Mock()
        bindings.manufacturing_commercial_pipeline_builder = commercial_builder
        integration = self._make_integration(ws, service_bindings=bindings)
        ws._manufacturing_production_package = SimpleNamespace()
        ws._manufacturing_cost_summary = SimpleNamespace(
            cost_report=SimpleNamespace(total_manufacturing_cost=600.0),
            total_manufacturing_cost=600.0,
        )

        commercial_result = SimpleNamespace(
            manufacturing_cost_summary=SimpleNamespace(total_manufacturing_cost=600.0),
            quotation_report=SimpleNamespace(
                production_cost=600.0, markup_rate=0.25,
                markup_amount=150.0, selling_price=750.0, currency="MAD",
            ),
            profitability_report=SimpleNamespace(
                gross_profit=150.0, gross_margin_rate=0.20, profitability_status="MEDIUM",
            ),
        )

        commercial_builder.return_value.build.return_value = commercial_result
        status = integration.review_commercial(markup_rate=0.25)

        self.assertEqual(status, "ok")
        self.assertIs(ws._manufacturing_commercial_result, commercial_result)

    # ── 6. dashboard nesting savings support ──────────────────────────

    def test_refresh_dashboard_preserves_behavior_without_nesting_savings(self):
        self._load_modules()
        ws = self._make_workspace()
        dashboard_mod = sys.modules["factory_dashboard"]
        ws._foi_readiness = SimpleNamespace(
            status="READY",
            blocking_count=0,
            warning_count=0,
            ready_count=2,
            summary_message="Readiness: READY",
        )
        ws._foi_blocking = SimpleNamespace(
            status="READY",
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
        )
        ws._foi_recommendations = SimpleNamespace(
            recommendations=(SimpleNamespace(),),
            high_confidence_count=1,
            medium_confidence_count=0,
            low_confidence_count=0,
            none_confidence_count=0,
        )
        ws._foi_decision = SimpleNamespace(
            decision_status="START_READY",
            confidence="HIGH",
            summary_message="Decision: START_READY",
            blocking_item_ids=(),
            recommendation_ids=(),
        )
        integration = self._make_integration(ws)

        dashboard = integration.refresh_dashboard()

        self.assertIsInstance(dashboard, dashboard_mod.FactoryDashboardReadModel)
        self.assertEqual(
            tuple(section.section_name for section in dashboard.sections),
            (
                "Factory Readiness",
                "Blocking Analysis",
                "Action Recommendations",
                "Production Decision",
            ),
        )

    def test_refresh_dashboard_includes_nesting_savings_section_from_report(self):
        self._load_modules()
        ws = self._make_workspace()
        dashboard_mod = sys.modules["factory_dashboard"]
        ws._foi_readiness = SimpleNamespace(
            status="READY",
            blocking_count=0,
            warning_count=0,
            ready_count=1,
            summary_message="Readiness: READY",
        )
        ws._foi_decision = SimpleNamespace(
            decision_status="START_READY",
            confidence="HIGH",
            summary_message="Decision: START_READY",
            blocking_item_ids=(),
            recommendation_ids=(),
        )
        ws._nesting_savings_report = SimpleNamespace(
            material_savings=120.5,
            waste_reduction=33.25,
            recovered_value_delta=10.0,
            total_manufacturing_cost_delta=-87.75,
            profitability_delta=54.0,
        )
        integration = self._make_integration(ws)

        dashboard = integration.refresh_dashboard()

        self.assertIsInstance(dashboard, dashboard_mod.FactoryDashboardReadModel)
        self.assertEqual(
            dashboard.sections[-1].section_name,
            "Nesting Savings Comparison",
        )

    def test_refresh_dashboard_uses_precomputed_nesting_section_when_provided(self):
        self._load_modules()
        ws = self._make_workspace()
        dashboard_mod = sys.modules["factory_dashboard"]
        ws._nesting_savings_dashboard_section = dashboard_mod.FactoryDashboardSection(
            section_name="Nesting Savings Comparison",
            rows=(("Material Savings", "999.99"),),
        )
        integration = self._make_integration(ws)

        dashboard = integration.refresh_dashboard()

        self.assertEqual(len(dashboard.sections), 1)
        self.assertEqual(dashboard.sections[0].rows, (("Material Savings", "999.99"),))

    def test_refresh_dashboard_displays_nesting_savings_values_exactly(self):
        self._load_modules()
        ws = self._make_workspace()
        ws._nesting_savings_report = SimpleNamespace(
            material_savings=123.4,
            waste_reduction=0.0,
            recovered_value_delta=-5.5,
            total_manufacturing_cost_delta=-42.25,
            profitability_delta=9.99,
        )
        integration = self._make_integration(ws)

        dashboard = integration.refresh_dashboard()
        rows = dict(dashboard.sections[0].rows)

        self.assertEqual(rows["Material Savings"], "123.40")
        self.assertEqual(rows["Waste Reduction"], "0.00")
        self.assertEqual(rows["Recovered Value Improvement"], "-5.50")
        self.assertEqual(rows["Total Manufacturing Cost Delta"], "-42.25")
        self.assertEqual(rows["Profitability Impact"], "9.99")

    # ── 7. no duplicate pipeline/builders ─────────────────────────────

    def test_methods_reuse_existing_pipelines(self):
        import inspect
        si_mod, _ = self._load_modules()
        source = inspect.getsource(si_mod)
        self.assertIn("ManufacturingRuntimePipelineBuilder", source)
        self.assertIn("ManufacturingCostPipelineBuilder", source)
        self.assertIn("ManufacturingCommercialPipelineBuilder", source)
        # No new pipeline classes defined inside service_integration
        marker_pos = source.find("class ConfiguratorV2ServiceIntegration")
        end_pos = source.find("class EngineeringProjectionResult")
        body_start = source.find("\n", marker_pos)
        body = source[body_start:end_pos] if end_pos > body_start else source[body_start:]
        self.assertNotIn("class ", body)

    # ── 8. no forbidden imports ──────────────────────────────────────

    def test_no_freecad_imports(self):
        import inspect
        si_mod, _ = self._load_modules()
        source = inspect.getsource(si_mod)
        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)
        self.assertNotIn("FreeCAD", import_text)
        self.assertNotIn("import Part", import_text)

    def test_no_scene_renderer_import(self):
        import inspect
        si_mod, _ = self._load_modules()
        source = inspect.getsource(si_mod)
        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)
        self.assertNotIn("SceneRenderer", import_text)

    def test_no_optimization_internals(self):
        import inspect
        si_mod, _ = self._load_modules()
        source = inspect.getsource(si_mod)
        self.assertNotIn("NestingSavingsBuilder", source)
        self.assertNotIn("NestingSavingsReport", source)
        self.assertNotIn("ManufacturingCostCalculator", source)
        self.assertNotIn("WasteIntelligenceBuilder", source)


if __name__ == "__main__":
    unittest.main()
