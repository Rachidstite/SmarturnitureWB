import importlib
import sys
import types
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import Mock, patch


class _FakeSignal:
    def connect(self, _callback):
        return None


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
        self.currentIndexChanged = _FakeSignal()

    def addItem(self, text):
        self.items.append(text)


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


class TestConfiguratorV2ReadModelsContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            read_models = importlib.import_module("ui.configurator_v2.read_models")
            workspace = importlib.import_module("ui.configurator_v2.workspace")
        return read_models, workspace

    def test_read_model_classes_exist_and_are_passive(self):
        read_models, _ = self._import_modules()

        tree_node = read_models.ProjectTreeNodeReadModel(
            node_id="project-1",
            parent_id="root",
            node_type="PROJECT",
            label="Project 1",
            state="Draft",
            is_supported=True,
            is_stale=False,
        )
        tree = read_models.ProjectTreeReadModel(root_nodes=(tree_node,))
        inspector_field = read_models.InspectorFieldReadModel(
            name="width",
            label="Width",
            value="1800",
            unit="mm",
            editable=False,
            source_reference="ProjectTreeRegion",
        )
        inspector = read_models.InspectorReadModel(fields=(inspector_field,))
        preview_item = read_models.PreviewItemReadModel(
            item_id="door-01",
            item_type="DOOR",
            label="Left Door",
            visible=True,
            selected=False,
            display_metadata=(("role", "front"),),
            source_reference="PreviewRegion",
        )
        preview = read_models.PreviewReadModel(items=(preview_item,))
        message = read_models.MessageReadModel(
            message_id="msg-1",
            severity="WARNING",
            category="Commercial warnings",
            text="Example",
            source_reference="MessageCenter",
        )
        message_center = read_models.MessageCenterReadModel(messages=(message,))
        section = read_models.ReviewSectionReadModel(
            section_name="Summary",
            rows=(("status", "ready"),),
            warnings=("check fit",),
            source_reference="ReviewRegion",
        )
        review = read_models.ReviewPanelReadModel(
            panel_name="Manufacturing",
            sections=(section,),
        )

        with self.assertRaises(FrozenInstanceError):
            tree_node.label = "Changed"

        self.assertEqual(tree.root_nodes[0].label, "Project 1")
        self.assertEqual(inspector.fields[0].value, "1800")
        self.assertEqual(preview.items[0].display_metadata, (("role", "front"),))
        self.assertEqual(message_center.highest_severity, "INFO")
        self.assertEqual(review.sections[0].section_name, "Summary")

    def test_preview_read_model_rejects_backend_objects(self):
        read_models, _ = self._import_modules()

        with self.assertRaises(TypeError):
            read_models.PreviewItemReadModel(
                item_id="door-01",
                item_type="DOOR",
                label="Left Door",
                visible=True,
                selected=False,
                display_metadata=((Mock(), "front"),),
                source_reference="PreviewRegion",
            )

        with self.assertRaises(TypeError):
            read_models.PreviewReadModel(items=(Mock(),))

    def test_workspace_holds_read_model_placeholders_without_backend_calls(self):
        read_models, workspace_module = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings,
        )

        self.assertIsInstance(
            workspace.project_tree_read_model,
            read_models.ProjectTreeReadModel,
        )
        self.assertIsInstance(
            workspace.inspector_read_model,
            read_models.InspectorReadModel,
        )
        self.assertIsInstance(
            workspace.preview_read_model,
            read_models.PreviewReadModel,
        )
        self.assertIsInstance(
            workspace.message_center_read_model,
            read_models.MessageCenterReadModel,
        )
        self.assertEqual(
            len(workspace.review_panel_read_models),
            len(workspace.review_panel_names),
        )
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
