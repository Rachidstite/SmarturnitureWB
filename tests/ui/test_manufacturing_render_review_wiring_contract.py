# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Manufacturing Render Review Wiring Contract Tests
#
# Verifies:
# - enrich_manufacturing_review_with_rendering appends rendering section
# - existing behaviour unchanged without rendering commands
# - rendering metadata displayed when present
# - no duplication of rendering logic
# - Configurator consumes renderer output without recomputing values
# - backward compatible with existing review panel workflow
# - missing/None commands preserve existing panels
# - no domain/manufacturing/FreeCAD/Qt imports in service_integration
# - no engine/workflow naming introduced
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest.mock import patch


class _FakeWidget:
    def __init__(self, *args, **kwargs):
        self._layout = None
        self._object_name = ""

    def setLayout(self, layout):
        self._layout = layout

    def setObjectName(self, name):
        self._object_name = name

    def objectName(self):
        return self._object_name


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
    """Minimal workspace stub: records review panel state."""

    def __init__(self, panel_names):
        self.review_panel_names = panel_names
        self.review_panel_read_models = ()
        self.message_center_read_model = types.SimpleNamespace(messages=())

    def set_review_panel_read_models(self, read_models):
        self.review_panel_read_models = tuple(read_models or ())

    def set_message_center_read_model(self, read_model):
        pass


class TestManufacturingRenderReviewWiringContract(unittest.TestCase):
    """Verify manufacturing render review wiring in service integration."""

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
        return rm_mod, ws_mod, si_mod

    # ── Rule 1: rendering section appended when commands present ──

    def test_rendering_section_appended_to_manufacturing_panel(self):
        """Rendering Details section added to Manufacturing panel."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        # First populate with a base manufacturing panel
        integration.refresh_manufacturing_review(
            type("Src", (), {"operations": []})()
        )

        # Then enrich with render commands
        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        result = integration.enrich_manufacturing_review_with_rendering(commands)

        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        section_names = {s.section_name for s in mfg_panel.sections}
        self.assertIn("Rendering Details", section_names)

    # ── Rule 2: rendering metadata displayed when present ─────────

    def test_rendering_metadata_displayed_in_section(self):
        """Rendering metadata rows present in the appended section."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        integration.refresh_manufacturing_review(
            type("Src", (), {"operations": []})()
        )

        commands = [{
            "review_priority": "high",
            "review_category": "drilling",
            "hole_style": "blind",
            "drill_direction": "front",
            "overlay_type": "drill_hole",
        }]
        result = integration.enrich_manufacturing_review_with_rendering(commands)

        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        render_section = [s for s in mfg_panel.sections if s.section_name == "Rendering Details"][0]
        rows = dict(render_section.rows)
        self.assertEqual(rows.get("Review Priority"), "high")
        self.assertEqual(rows.get("Review Category"), "drilling")
        self.assertEqual(rows.get("Hole Style"), "blind")
        self.assertEqual(rows.get("Drill Direction"), "front")

    # ── Rule 3: existing behaviour unchanged without commands ──────

    def test_none_commands_unchanged(self):
        """None commands return existing panels unchanged."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        integration.refresh_manufacturing_review(
            type("Src", (), {"operations": []})()
        )
        before = tuple(workspace.review_panel_read_models)

        result = integration.enrich_manufacturing_review_with_rendering(None)

        self.assertEqual(len(result), len(before))
        for panel_before, panel_after in zip(before, result):
            self.assertEqual(panel_before, panel_after)

    def test_empty_commands_unchanged(self):
        """Empty commands list returns existing panels unchanged."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        integration.refresh_manufacturing_review(
            type("Src", (), {"operations": []})()
        )
        before = tuple(workspace.review_panel_read_models)

        result = integration.enrich_manufacturing_review_with_rendering([])

        self.assertEqual(len(result), len(before))
        for panel_before, panel_after in zip(before, result):
            self.assertEqual(panel_before, panel_after)

    # ── Rule 4: backward compatible with existing review panels ───

    def test_no_render_fields_preserves_existing_sections(self):
        """Commands without render metadata preserve existing sections."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        integration.refresh_manufacturing_review(
            type("Src", (), {"operations": []})()
        )
        before = tuple(workspace.review_panel_read_models)

        # Commands exist but have no review metadata fields
        result = integration.enrich_manufacturing_review_with_rendering(
            [{"overlay_type": "drill_hole"}]
        )

        for panel_before, panel_after in zip(before, result):
            self.assertEqual(panel_before, panel_after)

    # ── Rule 5: no duplication of rendering logic ─────────────────

    def test_no_recomputation_of_values(self):
        """Configurator consumes renderer output without recomputing values."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        integration.refresh_manufacturing_review(
            type("Src", (), {"operations": []})()
        )

        commands = [{"review_priority": "high", "overlay_type": "drill_hole"}]
        result = integration.enrich_manufacturing_review_with_rendering(commands)

        mfg_panel = [p for p in result if p.panel_name == "Manufacturing"][0]
        render_section = [s for s in mfg_panel.sections if s.section_name == "Rendering Details"][0]
        rows = dict(render_section.rows)
        # The value comes straight from the command dict — not recomputed
        self.assertEqual(rows.get("Review Priority"), "high")

    # ── Rule 6: no forbidden imports ──────────────────────────────

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

    # ── Rule 7: no engine/workflow naming ─────────────────────────

    def test_no_engine_workflow_naming(self):
        """No engine/workflow naming in the wiring method."""
        rm, ws, si = self._import_modules()

        method = si.ConfiguratorV2ServiceIntegration.enrich_manufacturing_review_with_rendering
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

    # ── Rule 8: existing review path remains compatible ───────────

    def test_existing_refresh_methods_unchanged(self):
        """Existing refresh_manufacturing_review still works without render commands."""
        rm, ws, si = self._import_modules()

        workspace = _WorkspaceStub(ws.ConfiguratorV2ShellModel().review_panels)
        bindings = ws.ConfiguratorV2ServiceBindings()
        integration = si.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        result = integration.refresh_manufacturing_review(None)
        self.assertIsInstance(result, tuple)
        for panel in result:
            self.assertIsInstance(panel, rm.ReviewPanelReadModel)
