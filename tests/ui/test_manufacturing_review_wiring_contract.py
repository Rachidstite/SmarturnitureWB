# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Manufacturing Review Wiring Contract Tests
#
# Verifies:
# - refresh_manufacturing_review wires source through
#   build_manufacturing_review_projection
# - outputs ReviewPanelReadModel with manufacturing facts as UI-safe rows
# - no raw manufacturing objects leak
# - existing review panel path remains compatible
# - missing/None source falls back safely
# - deterministic
# - input not mutated
# - no manufacturing/domain/cost/optimization/commercial/FreeCAD/Qt imports
# - no engine/workflow naming introduced
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class _FakeMfgOp:
    """Simulates a manufacturing operation object from a backend domain."""

    def __init__(self, label, status="PASS", message="", component_id=""):
        self.operation_label = label
        self.operation_status = status
        self.operation_message = message
        self.component_id = component_id


class _FakeMfgSource:
    """Simulates a manufacturing source with an operations list."""

    def __init__(self, ops):
        self.operations = list(ops)


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
            QWidget=_FakeWidget,
            QFrame=_FakeWidget,
            QVBoxLayout=_FakeLayout,
            QHBoxLayout=_FakeLayout,
            QFormLayout=_FakeLayout,
            QComboBox=_FakeComboBox,
            QPushButton=_FakeButton,
            QLabel=_FakeWidget,
            QTabWidget=_FakeTabWidget,
        ),
        QtCore=types.SimpleNamespace(),
    )


class _WorkspaceStub:
    """Minimal workspace stub: records what set_review_panel_read_models receives."""

    def __init__(self, panel_names):
        self.review_panel_names = panel_names
        self.review_panel_read_models = ()
        self.message_center_read_model = types.SimpleNamespace(messages=())

    def set_review_panel_read_models(self, read_models):
        self.review_panel_read_models = tuple(read_models or ())

    def set_message_center_read_model(self, read_model):
        pass


class TestManufacturingReviewWiringContract(unittest.TestCase):
    """Verify manufacturing review wiring in service integration."""

    @classmethod
    def _import_modules(cls):
        """Import modules with core.qt_compat mocked to avoid PySide6 SIGILL."""
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            ws_mod = importlib.import_module("ui.configurator_v2.workspace")
            si_mod = importlib.import_module("ui.configurator_v2.service_integration")
            rm_mod = importlib.import_module("ui.configurator_v2.read_models")
            pa_mod = importlib.import_module("ui.configurator_v2.projection_adapters")
        return rm_mod, pa_mod, ws_mod, si_mod

    # ── Rule 1: wires manufacturing source through adapter ─────────

    def test_wires_manufacturing_source_through_adapter(self):
        """refresh_manufacturing_review routes source to build_manufacturing_review_projection."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        source = _FakeMfgSource([
            _FakeMfgOp("CNC Cut", "PASS", "All panels cut"),
            _FakeMfgOp("Edge Banding", "FAIL", "Edge mismatch"),
        ])
        result = integration.refresh_manufacturing_review(source)

        self.assertIsInstance(result, tuple)
        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        self.assertTrue(mfg_panel.available)
        section_names = {s.section_name for s in mfg_panel.sections}
        self.assertIn("Passed", section_names)
        self.assertIn("Failed", section_names)

    # ── Rule 2: returns/exposes ReviewPanelReadModel ───────────────

    def test_returns_tuple_of_review_panel_read_models(self):
        """Output tuple contains ReviewPanelReadModel instances."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        source = _FakeMfgSource([_FakeMfgOp("Op1", "PASS")])
        result = integration.refresh_manufacturing_review(source)

        for panel in result:
            self.assertIsInstance(panel, rm.ReviewPanelReadModel)

    # ── Rule 3: output contains manufacturing facts as UI-safe rows ─

    def test_output_contains_manufacturing_facts_as_ui_safe_rows(self):
        """Manufacturing fact rows are (str, str) tuples — no raw objects."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        source = _FakeMfgSource([
            _FakeMfgOp("Drilling", "PASS", "All holes correct"),
        ])
        result = integration.refresh_manufacturing_review(source)

        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        for section in mfg_panel.sections:
            for row in section.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)
                self.assertIsInstance(row[0], str)
                self.assertIsInstance(row[1], str)

    # ── Rule 4: no raw manufacturing object leaks ──────────────────

    def test_no_raw_manufacturing_objects_leak(self):
        """Workspace stores no raw manufacturing source references."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        source = _FakeMfgSource([_FakeMfgOp("Op1", "PASS")])
        integration.refresh_manufacturing_review(source)

        for panel in workspace.review_panel_read_models:
            self.assertFalse(hasattr(panel, "all_nodes"))
            self.assertFalse(hasattr(panel, "Shape"))
            for section in panel.sections:
                for row in section.rows:
                    self.assertNotIn("operation_status", row[1].lower())

    # ── Rule 5: existing review panel path remains compatible ──────

    def test_existing_review_path_unchanged(self):
        """Calling _refresh_review_panels directly still works."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        result = integration._refresh_review_panels(
            source=None,
            message_text="Test fallback",
            source_reference="test_refresh",
        )

        self.assertIsInstance(result, tuple)
        for panel in result:
            self.assertIsInstance(panel, rm.ReviewPanelReadModel)

    def test_other_refresh_methods_unchanged(self):
        """refresh_validation, refresh_cost_review, etc. still delegate to _refresh_review_panels."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        for method_name in (
            "refresh_validation",
            "refresh_cost_review",
            "refresh_commercial_review",
            "refresh_release_review",
        ):
            method = getattr(integration, method_name)
            result = method(None)
            self.assertIsInstance(result, tuple)
            for panel in result:
                self.assertIsInstance(panel, rm.ReviewPanelReadModel)

    # ── Rule 6: missing/empty source falls back safely ────────────

    def test_none_source_falls_back_safely(self):
        """None source falls back to empty panels."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        result = integration.refresh_manufacturing_review(None)

        self.assertIsInstance(result, tuple)
        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        self.assertGreaterEqual(len(result), 5)

    def test_empty_operations_falls_back_safely(self):
        """Empty operations source returns available=False manufacturing panel."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        result = integration.refresh_manufacturing_review([])

        self.assertIsInstance(result, tuple)
        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        self.assertFalse(mfg_panel.available)

    # ── Rule 7: deterministic ──────────────────────────────────────

    def test_deterministic(self):
        """Same inputs produce identical outputs."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        source = _FakeMfgSource([
            _FakeMfgOp("A", "PASS"),
            _FakeMfgOp("B", "FAIL", "Error"),
        ])
        r1 = integration.refresh_manufacturing_review(source)
        r2 = integration.refresh_manufacturing_review(source)

        self.assertEqual(r1, r2)

    # ── Rule 8: input source is not mutated ────────────────────────

    def test_no_input_mutation(self):
        """Original source object is not modified by the wiring."""
        rm, pa, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        ops = [_FakeMfgOp("A", "PASS")]
        source = _FakeMfgSource(ops)
        original_label = ops[0].operation_label

        integration.refresh_manufacturing_review(source)

        self.assertEqual(ops[0].operation_label, original_label)

    # ── Rule 9: no forbidden imports in service_integration.py ─────

    def test_no_forbidden_imports(self):
        """service_integration.py must not import domain/manufacturing/cost/FreeCAD/Qt."""
        with open("ui/configurator_v2/service_integration.py") as f:
            source = f.read()

        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)

        forbidden = [
            "domain.",
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
                msg=f"service_integration.py must not import '{token}'",
            )

    # ── Rule 10: no engine/workflow naming introduced ──────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow/service naming in the wiring method."""
        rm, pa, ws, si = self._import_modules()

        method = si.ConfiguratorV2ServiceIntegration.refresh_manufacturing_review
        func_name = method.__name__

        forbidden_tokens = [
            "engine", "workflow", "event", "bus",
            "store", "controller", "registry", "renderer",
        ]
        for token in forbidden_tokens:
            self.assertNotIn(
                token, func_name.lower(),
                msg=f"Method name '{func_name}' should not contain '{token}'",
            )

    # ── Rule 11 & 12: existing tests pass (verified by CI commands) ─
    #    python3 -m pytest tests/ui -q
    #    python3 -m pytest tests/architecture -q


if __name__ == "__main__":
    unittest.main()
