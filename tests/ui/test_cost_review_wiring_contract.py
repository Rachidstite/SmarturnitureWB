# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Cost Review Wiring Contract Tests
#
# Verifies:
# - refresh_cost_review wires source through build_cost_review_projection
# - outputs ReviewPanelReadModel with cost facts as UI-safe rows
# - no raw cost objects leak
# - existing review panel path remains compatible
# - missing/None source falls back safely
# - deterministic
# - input not mutated
# - no cost/domain/manufacturing/FreeCAD/Qt imports
# - no engine/workflow naming introduced
# - no cost calculation occurs in service_integration.py
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class _FakeCostItem:
    """Simulates a cost item object from a backend domain."""

    def __init__(self, label="", category="", status="", severity="",
                 amount="", currency="", message="", component_id=""):
        self.item_label = label
        self.item_category = category
        self.item_status = status
        self.item_severity = severity
        self.item_amount = amount
        self.item_currency = currency
        self.item_message = message
        self.component_id = component_id


class _FakeCostSource:
    """Simulates a cost source with a cost_items list."""

    def __init__(self, items):
        self.cost_items = list(items)


class _FakeWidget:
    def __init__(self, *args, **kwargs):
        self._layout = None
        self._object_name = ""
        self._enabled = True
        self._text = ""

    def setLayout(self, layout):
        self._layout = layout
    def setObjectName(self, name):
        self._object_name = name
    def objectName(self):
        return self._object_name
    def setEnabled(self, enabled):
        self._enabled = bool(enabled)
    def setMinimumHeight(self, _height):
        return None
    def setWordWrap(self, _enabled):
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
    def addRow(self, *_args):
        self.items.append(_args)


class _FakeComboBox(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.currentIndexChanged = types.SimpleNamespace(connect=lambda cb: None)
    def addItem(self, text):
        self.items.append(text)


class _FakeSignal:
    def connect(self, _callback):
        return None


class _FakeButton(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self.clicked = _FakeSignal()


class _FakeTabWidget(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = []
    def addTab(self, widget, title):
        self.tabs.append((widget, title))


def _fake_qt_module():
    return types.SimpleNamespace(
        QtWidgets=types.SimpleNamespace(
            QWidget=_FakeWidget, QFrame=_FakeWidget,
            QVBoxLayout=_FakeLayout, QHBoxLayout=_FakeLayout,
            QFormLayout=_FakeLayout, QComboBox=_FakeComboBox,
            QPushButton=_FakeButton, QLabel=_FakeWidget,
            QTabWidget=_FakeTabWidget,
        ),
        QtCore=types.SimpleNamespace(),
    )


class _WorkspaceStub:
    def __init__(self, panel_names):
        self.review_panel_names = panel_names
        self.review_panel_read_models = ()
        self.message_center_read_model = types.SimpleNamespace(messages=())
    def set_review_panel_read_models(self, read_models):
        self.review_panel_read_models = tuple(read_models or ())
    def set_message_center_read_model(self, read_model):
        pass


class TestCostReviewWiringContract(unittest.TestCase):
    """Verify cost review wiring in service integration."""

    @classmethod
    def _import_modules(cls):
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            ws_mod = importlib.import_module("ui.configurator_v2.workspace")
            si_mod = importlib.import_module("ui.configurator_v2.service_integration")
            rm_mod = importlib.import_module("ui.configurator_v2.read_models")
            pa_mod = importlib.import_module("ui.configurator_v2.projection_adapters")
        return rm_mod, pa_mod, ws_mod, si_mod

    # ── Rule 1: wires cost source through adapter ─────────────────

    def test_wires_cost_source_through_adapter(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        source = _FakeCostSource([
            _FakeCostItem("Wood", "Material", amount="300.00", currency="USD"),
            _FakeCostItem("Labor", "Labor", amount="200.00", currency="USD"),
        ])
        result = integration.refresh_cost_review(source)
        self.assertIsInstance(result, tuple)
        cost_panel = [p for p in result if p.panel_name == "Cost"][0]
        self.assertTrue(cost_panel.available)
        section_names = {s.section_name for s in cost_panel.sections}
        self.assertIn("Material", section_names)
        self.assertIn("Labor", section_names)

    # ── Rule 2: returns ReviewPanelReadModel ──────────────────────

    def test_returns_tuple_of_review_panel_read_models(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        source = _FakeCostSource([_FakeCostItem("Item", "Material", amount="100.00")])
        result = integration.refresh_cost_review(source)
        for panel in result:
            self.assertIsInstance(panel, rm.ReviewPanelReadModel)

    # ── Rule 3: UI-safe rows ───────────────────────────────────────

    def test_output_contains_cost_facts_as_ui_safe_rows(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        source = _FakeCostSource([_FakeCostItem("Wood", "Material", amount="300.00")])
        result = integration.refresh_cost_review(source)
        cost_panel = [p for p in result if p.panel_name == "Cost"][0]
        for section in cost_panel.sections:
            for row in section.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)
                self.assertIsInstance(row[0], str)
                self.assertIsInstance(row[1], str)

    # ── Rule 4: no raw cost objects leak ───────────────────────────

    def test_no_raw_cost_objects_leak(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        source = _FakeCostSource([_FakeCostItem("Item", "Material", amount="100.00")])
        integration.refresh_cost_review(source)
        for panel in workspace.review_panel_read_models:
            self.assertFalse(hasattr(panel, "all_nodes"))
            self.assertFalse(hasattr(panel, "Shape"))
            for section in panel.sections:
                for row in section.rows:
                    self.assertNotIn("item_amount", row[1].lower())

    # ── Rule 5: existing review panel path unchanged ───────────────

    def test_existing_review_path_unchanged(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        result = integration._refresh_review_panels(
            source=None, message_text="Test", source_reference="test",
        )
        self.assertIsInstance(result, tuple)
        for panel in result:
            self.assertIsInstance(panel, rm.ReviewPanelReadModel)

    def test_other_refresh_methods_unchanged(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        for name in ("refresh_commercial_review", "refresh_release_review"):
            result = getattr(integration, name)(None)
            self.assertIsInstance(result, tuple)
            for panel in result:
                self.assertIsInstance(panel, rm.ReviewPanelReadModel)

    # ── Rule 6: missing/empty source falls back ────────────────────

    def test_none_source_falls_back_safely(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        result = integration.refresh_cost_review(None)
        self.assertIsInstance(result, tuple)
        self.assertGreaterEqual(len(result), 5)

    def test_empty_items_falls_back_safely(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        result = integration.refresh_cost_review([])
        self.assertIsInstance(result, tuple)
        cost_panel = [p for p in result if p.panel_name == "Cost"][0]
        self.assertFalse(cost_panel.available)

    # ── Rule 7: deterministic ──────────────────────────────────────

    def test_deterministic(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        source = _FakeCostSource([
            _FakeCostItem("A", "Material", amount="100.00"),
            _FakeCostItem("B", "Labor", amount="200.00"),
        ])
        r1 = integration.refresh_cost_review(source)
        r2 = integration.refresh_cost_review(source)
        self.assertEqual(r1, r2)

    # ── Rule 8: no input mutation ──────────────────────────────────

    def test_no_input_mutation(self):
        rm, pa, ws, si = self._import_modules()
        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace, service_bindings=bindings,
        )
        items = [_FakeCostItem("A", "Material", amount="100.00")]
        source = _FakeCostSource(items)
        original_label = items[0].item_label
        integration.refresh_cost_review(source)
        self.assertEqual(items[0].item_label, original_label)

    # ── Rule 9: no forbidden imports ───────────────────────────────

    def test_no_forbidden_imports(self):
        with open("ui/configurator_v2/service_integration.py") as f:
            content = f.read()
        import_lines = [
            line for line in content.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)
        forbidden = [
            "domain.", "cost_intelligence.", "manufacturing.",
            "optimization.", "commercial_outputs.",
            "FreeCAD", "QtWidgets", "QtCore", "QtGui",
        ]
        for token in forbidden:
            self.assertNotIn(
                token, import_text,
                msg=f"service_integration.py must not import '{token}'",
            )

    # ── Rule 10: no engine/workflow naming ─────────────────────────

    def test_no_engine_workflow_naming(self):
        rm, pa, ws, si = self._import_modules()
        method = si.ConfiguratorV2ServiceIntegration.refresh_cost_review
        func_name = method.__name__
        for token in ("engine", "workflow", "event", "bus",
                       "store", "controller", "registry", "renderer"):
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"'{func_name}' should not contain '{token}'",
            )

    # ── Rule 11: no cost calculation in service_integration.py ─────

    def test_no_cost_calculation_in_service_integration(self):
        """service_integration.py contains no sum() call or cost aggregation."""
        with open("ui/configurator_v2/service_integration.py") as f:
            content = f.read()
        # sum() calls would indicate aggregation/calculation in the wiring layer
        # (tuple/list construction and f-string arithmetic are excluded — they're
        #  structural Python, not business calculation)
        self.assertNotIn("sum(", content)


if __name__ == "__main__":
    unittest.main()
