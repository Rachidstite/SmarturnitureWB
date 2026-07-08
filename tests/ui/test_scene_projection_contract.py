import importlib
from dataclasses import dataclass
import sys
import types
import unittest
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

    def layout(self):
        return self._layout

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

    def setCurrentText(self, text):
        self._text = text


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


class _FakeNode:
    def __init__(self, node_id, label, role_name, x, y, z, width, depth, height, *, visible=True, selectable=True):
        self.identity = types.SimpleNamespace(key=node_id)
        self.node_type = role_name
        self.label = label
        self.name = label
        self.visible = visible
        self.selectable = selectable
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        self.material = "MDF_18MM"
        self.metadata = {
            "display_name": label,
            "source_reference": f"scene:{node_id}",
            "finish": "Oak",
        }
        self.role = types.SimpleNamespace(name=role_name)


class _FakeSceneGraph:
    def __init__(self, nodes):
        self._nodes = list(nodes)

    def all_nodes(self):
        return list(self._nodes)


class TestSceneProjectionContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            scene_projection = importlib.import_module("ui.configurator_v2.scene_projection")
            adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
            workspace_module = importlib.import_module("ui.configurator_v2.workspace")
            integration_module = importlib.import_module("ui.configurator_v2.service_integration")
        return scene_projection, adapters, workspace_module, integration_module

    def _build_fake_scene_graph(self):
        return _FakeSceneGraph(
            [
                _FakeNode("node-1", "Left Side Panel", "SIDE_PANEL", 0.0, 0.0, 0.0, 18.0, 600.0, 720.0),
                _FakeNode("node-2", "Door Panel", "DOOR_PANEL", 18.0, 0.0, 0.0, 450.0, 18.0, 700.0),
            ]
        )

    def test_scene_projection_builder_produces_safe_projection(self):
        scene_projection, _, _, _ = self._import_modules()

        projection = scene_projection.build_scene_projection(
            self._build_fake_scene_graph(),
            selected_node_id="node-2",
            highlight_target="node-2",
            source_reference="SceneGraph",
        )

        self.assertTrue(projection.scene_available)
        self.assertEqual(projection.node_count, 2)
        self.assertEqual(projection.selection.selected_node_id, "node-2")
        self.assertEqual(projection.highlight_target, "node-2")
        self.assertIn("min=", projection.bounds.display_label)
        self.assertEqual(len(projection.nodes), 2)
        self.assertTrue(all(node.__class__.__name__ == "SceneNodeProjection" for node in projection.nodes))
        self.assertTrue(all(not hasattr(node, "Shape") for node in projection.nodes))
        self.assertTrue(all(not hasattr(node, "ViewObject") for node in projection.nodes))

    def test_preview_adapter_accepts_scene_projection(self):
        scene_projection, adapters, _, _ = self._import_modules()
        projection = scene_projection.build_scene_projection(
            self._build_fake_scene_graph(),
            selected_node_id="node-2",
            highlight_target="node-2",
            source_reference="SceneGraph",
        )

        preview_rm = adapters.build_preview_read_model(
            {
                "scene_projection": projection,
                "preview_mode": "Design View",
            }
        )

        self.assertTrue(preview_rm.scene_available)
        self.assertEqual(preview_rm.node_count, 2)
        self.assertEqual(preview_rm.selected_node, "node-2")
        self.assertEqual(preview_rm.highlight_target, "node-2")
        self.assertEqual(preview_rm.representation_status, "Ready")
        self.assertIn("min=", preview_rm.scene_bounds)
        self.assertGreaterEqual(len(preview_rm.items), 2)

    def test_preview_region_consumes_preview_read_model(self):
        scene_projection, adapters, workspace_module, _ = self._import_modules()
        projection = scene_projection.build_scene_projection(
            self._build_fake_scene_graph(),
            selected_node_id="node-2",
            highlight_target="node-2",
            source_reference="SceneGraph",
        )
        preview_rm = adapters.build_preview_read_model({"scene_projection": projection})
        workspace = workspace_module.create_configurator_v2_workspace()

        workspace.set_preview_read_model(preview_rm)

        self.assertIs(workspace.preview_region.read_model, preview_rm)
        self.assertIn("Scene Available: Yes", workspace.preview_region.render_rows)
        self.assertIn("Node Count: 2", workspace.preview_region.render_rows)
        self.assertTrue(any(row.startswith("Bounds: min=") for row in workspace.preview_region.render_rows))
        self.assertIn("Selected Node: node-2", workspace.preview_region.render_rows)
        self.assertIn("Representation Status: Ready", workspace.preview_region.render_rows)

    def test_refresh_preview_uses_scene_projection_without_backend_calls(self):
        scene_projection, adapters, workspace_module, integration_module = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        read_model = integration.refresh_preview(
            {
                "scene_graph": self._build_fake_scene_graph(),
                "selected_node_id": "node-2",
                "highlight_target": "node-2",
                "preview_title": "Scene Projection Preview",
            }
        )

        self.assertTrue(read_model.scene_available)
        self.assertEqual(read_model.node_count, 2)
        self.assertEqual(workspace.preview_read_model, read_model)
        self.assertEqual(workspace.preview_region.read_model, read_model)
        self.assertIn("Preview Title: Scene Projection Preview", workspace.preview_region.render_rows)
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_scene_projection_builder_rejects_backend_objects(self):
        scene_projection, _, _, _ = self._import_modules()

        class _BackendLikeNode:
            Shape = object()

        with self.assertRaises(TypeError):
            scene_projection.build_scene_projection([_BackendLikeNode()])

    def test_safe_metadata_handles_dict_unchanged(self):
        scene_projection, _, _, _ = self._import_modules()

        metadata = {"role": "back_panel", "source_reference": "scene:node-1"}

        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=metadata)),
            (("role", "back_panel"), ("source_reference", "scene:node-1")),
        )

    def test_safe_metadata_handles_list_and_tuple_pairs_unchanged(self):
        scene_projection, _, _, _ = self._import_modules()

        list_metadata = [("role", "back_panel"), ("finish", "Oak")]
        tuple_metadata = (("role", "back_panel"), ("finish", "Oak"))

        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=list_metadata)),
            (("role", "back_panel"), ("finish", "Oak")),
        )
        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=tuple_metadata)),
            (("role", "back_panel"), ("finish", "Oak")),
        )

    def test_safe_metadata_handles_dataclass_metadata(self):
        scene_projection, _, _, _ = self._import_modules()

        @dataclass
        class DataclassMetadata:
            role: str = "back_panel"
            finish: str = "Oak"

        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=DataclassMetadata())),
            (("role", "back_panel"), ("finish", "Oak")),
        )

    def test_safe_metadata_handles_simple_namespace_metadata(self):
        scene_projection, _, _, _ = self._import_modules()

        metadata = types.SimpleNamespace(role="back_panel", finish="Oak")

        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=metadata)),
            (("role", "back_panel"), ("finish", "Oak")),
        )

    def test_safe_metadata_handles_plain_object_metadata(self):
        scene_projection, _, _, _ = self._import_modules()

        class PlainMetadata:
            def __init__(self):
                self.role = "back_panel"
                self.finish = "Oak"

        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=PlainMetadata())),
            (("role", "back_panel"), ("finish", "Oak")),
        )

    def test_safe_metadata_handles_non_iterable_metadata_without_crashing(self):
        scene_projection, _, _, _ = self._import_modules()

        class NonIterableMetadata:
            __slots__ = ()

        self.assertEqual(
            scene_projection._safe_metadata(types.SimpleNamespace(metadata=NonIterableMetadata())),
            (),
        )

    def test_build_scene_projection_handles_object_like_metadata(self):
        scene_projection, _, _, _ = self._import_modules()

        class ObjectLikeNode:
            def __init__(self):
                self.identity = types.SimpleNamespace(key="node-1")
                self.node_type = "BACK_PANEL"
                self.label = "Back Panel"
                self.name = "Back Panel"
                self.visible = True
                self.selectable = True
                self.x = 0.0
                self.y = 0.0
                self.z = 0.0
                self.width = 18.0
                self.depth = 600.0
                self.height = 720.0
                self.metadata = types.SimpleNamespace(role="back_panel", finish="Oak")

        projection = scene_projection.build_scene_projection([ObjectLikeNode()])

        self.assertTrue(projection.scene_available)
        self.assertEqual(projection.node_count, 1)
        self.assertEqual(projection.nodes[0].display_metadata, (("role", "back_panel"), ("finish", "Oak")))


if __name__ == "__main__":
    unittest.main()
