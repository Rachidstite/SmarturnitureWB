# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Release Review Wiring Contract Tests
#
# Verifies release review wiring for the final review domain.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest.mock import patch


class _FakeRelItem:
    def __init__(self, label="", category="", status="", severity="",
                 message="", timestamp="", reviewer="", note="", component_id=""):
        self.item_label = label
        self.item_category = category
        self.item_status = status
        self.item_severity = severity
        self.item_message = message
        self.item_timestamp = timestamp
        self.reviewer = reviewer
        self.customer_note = note
        self.component_id = component_id


class _FakeRelSource:
    def __init__(self, items):
        self.release_items = list(items)


class _FakeWidget:
    def __init__(self, *a, **kw):
        self._layout = None; self._object_name = ""; self._enabled = True; self._text = ""
    def setLayout(self, l): self._layout = l
    def setObjectName(self, n): self._object_name = n
    def objectName(self): return self._object_name
    def setEnabled(self, e): self._enabled = bool(e)
    def setMinimumHeight(self, _): return None
    def setWordWrap(self, _): return None
    def setText(self, t): self._text = t
    def text(self): return self._text


class _FakeLayout:
    def __init__(self, *a, **kw): self.items = []
    def addWidget(self, w): self.items.append(w)
    def addLayout(self, l): self.items.append(l)
    def addRow(self, *a): self.items.append(a)


class _FakeComboBox(_FakeWidget):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw); self.items = []
        self.currentIndexChanged = types.SimpleNamespace(connect=lambda cb: None)
    def addItem(self, t): self.items.append(t)


class _FakeSignal:
    def connect(self, _cb): return None


class _FakeButton(_FakeWidget):
    def __init__(self, t="", *a, **kw):
        super().__init__(*a, **kw); self._text = t; self.clicked = _FakeSignal()


class _FakeTabWidget(_FakeWidget):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw); self.tabs = []
    def addTab(self, w, t): self.tabs.append((w, t))


def _fake_qt():
    return types.SimpleNamespace(
        QtWidgets=types.SimpleNamespace(
            QWidget=_FakeWidget, QFrame=_FakeWidget,
            QVBoxLayout=_FakeLayout, QHBoxLayout=_FakeLayout,
            QFormLayout=_FakeLayout, QComboBox=_FakeComboBox,
            QPushButton=_FakeButton, QLabel=_FakeWidget, QTabWidget=_FakeTabWidget,
        ),
        QtCore=types.SimpleNamespace(),
    )


class _WorkspaceStub:
    def __init__(self, panel_names):
        self.review_panel_names = panel_names
        self.review_panel_read_models = ()
        self.message_center_read_model = types.SimpleNamespace(messages=())
    def set_review_panel_read_models(self, m):
        self.review_panel_read_models = tuple(m or ())
    def set_message_center_read_model(self, m): pass


class TestReleaseReviewWiringContract(unittest.TestCase):

    @classmethod
    def _import_modules(cls):
        for k in list(sys.modules):
            if k.startswith("ui.configurator_v2"): del sys.modules[k]
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt()}):
            ws = importlib.import_module("ui.configurator_v2.workspace")
            si = importlib.import_module("ui.configurator_v2.service_integration")
            rm = importlib.import_module("ui.configurator_v2.read_models")
            pa = importlib.import_module("ui.configurator_v2.projection_adapters")
        return rm, pa, ws, si

    def test_wires_release_source_through_adapter(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        s = _FakeRelSource([
            _FakeRelItem("Design Approved", "Checklist", status="DONE"),
            _FakeRelItem("QA Needed", "Approvals", status="PENDING"),
        ])
        r = i.refresh_release_review(s)
        self.assertIsInstance(r, tuple)
        panel = [p for p in r if p.panel_name == "Release"][0]
        self.assertTrue(panel.available)
        sn = {sec.section_name for sec in panel.sections}
        self.assertIn("Checklist", sn)
        self.assertIn("Approvals", sn)

    def test_preserves_other_panels(self):
        """Release panel is replaced while non-Release panels are preserved."""
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        # First set cost panel via its wired method
        i.refresh_cost_review(_FakeCostSource([_FakeCostItem("Wood", "Material", amount="300")]))
        # Then set release panel
        s = _FakeRelSource([_FakeRelItem("Done", "Ready", status="RELEASED")])
        r = i.refresh_release_review(s)
        cost_panel = [p for p in r if p.panel_name == "Cost"][0]
        self.assertTrue(cost_panel.available)  # Cost preserved
        rel_panel = [p for p in r if p.panel_name == "Release"][0]
        self.assertTrue(rel_panel.available)    # Release wired

    def test_returns_tuple_of_review_panel_read_models(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        s = _FakeRelSource([_FakeRelItem("A", "Checklist")])
        for p in i.refresh_release_review(s):
            self.assertIsInstance(p, rm.ReviewPanelReadModel)

    def test_ui_safe_rows(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        s = _FakeRelSource([_FakeRelItem("A", "Checklist", status="DONE")])
        r = i.refresh_release_review(s)
        panel = [p for p in r if p.panel_name == "Release"][0]
        for sec in panel.sections:
            for row in sec.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)
                self.assertIsInstance(row[0], str)
                self.assertIsInstance(row[1], str)

    def test_no_raw_leak(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        s = _FakeRelSource([_FakeRelItem("A", "Checklist", status="DONE")])
        i.refresh_release_review(s)
        for p in w.review_panel_read_models:
            self.assertFalse(hasattr(p, "all_nodes"))
            self.assertFalse(hasattr(p, "Shape"))
            for sec in p.sections:
                for row in sec.rows:
                    self.assertNotIn("item_status", row[1].lower())

    def test_none_source_fallback(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        r = i.refresh_release_review(None)
        self.assertIsInstance(r, tuple)
        self.assertGreaterEqual(len(r), 5)

    def test_empty_source_fallback(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        r = i.refresh_release_review([])
        self.assertIsInstance(r, tuple)
        panel = [p for p in r if p.panel_name == "Release"][0]
        self.assertFalse(panel.available)

    def test_deterministic(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        s = _FakeRelSource([_FakeRelItem("A", "Checklist", status="DONE")])
        self.assertEqual(
            i.refresh_release_review(s),
            i.refresh_release_review(s),
        )

    def test_no_mutation(self):
        rm, pa, ws, si = self._import_modules()
        w = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        b = ws.ConfiguratorV2ServiceBindings()
        i = si.ConfiguratorV2ServiceIntegration(workspace=w, service_bindings=b)
        items = [_FakeRelItem("A", "Checklist")]
        s = _FakeRelSource(items)
        orig = items[0].item_label
        i.refresh_release_review(s)
        self.assertEqual(items[0].item_label, orig)

    def test_no_forbidden_imports(self):
        with open("ui/configurator_v2/service_integration.py") as f:
            c = f.read()
        lines = [l for l in c.splitlines() if l.strip().startswith(("import ", "from "))]
        t = "\n".join(lines)
        for tok in ("domain.", "commercial_outputs.", "cost_intelligence.",
                     "manufacturing.", "optimization.", "FreeCAD",
                     "QtWidgets", "QtCore", "QtGui"):
            self.assertNotIn(tok, t, msg=f"must not import '{tok}'")

    def test_no_engine_workflow_naming(self):
        rm, pa, ws, si = self._import_modules()
        n = si.ConfiguratorV2ServiceIntegration.refresh_release_review.__name__
        for tok in ("engine", "workflow", "event", "bus",
                     "store", "controller", "registry", "renderer"):
            self.assertNotIn(tok, n.lower(), msg=f"'{n}' should not contain '{tok}'")

    def test_no_release_calculation(self):
        with open("ui/configurator_v2/service_integration.py") as f:
            c = f.read()
        self.assertNotIn("sum(", c, "no sum() — no release calculation")


class _FakeCostItem:
    def __init__(self, label="", category="", amount=""):
        self.item_label = label; self.item_category = category; self.item_amount = amount


class _FakeCostSource:
    def __init__(self, items): self.cost_items = list(items)


if __name__ == "__main__":
    unittest.main()
