import importlib
import sys
import types
import unittest
from unittest.mock import patch


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
    def __init__(
        self,
        node_id,
        label,
        role_name,
        x,
        y,
        z,
        width,
        depth,
        height,
        *,
        visible=True,
        selectable=True,
        metadata=None,
    ):
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
        self.metadata = metadata or {}
        self.role = types.SimpleNamespace(name=role_name)


class _FakeSceneGraph:
    def __init__(self, nodes):
        self._nodes = list(nodes)

    def all_nodes(self):
        return list(self._nodes)


class TestVisualComponentLibraryContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            scene_projection = importlib.import_module("ui.configurator_v2.scene_projection")
            visual_components = importlib.import_module("ui.configurator_v2.visual_components")
            projection_adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
            workspace = importlib.import_module("ui.configurator_v2.workspace")
        return scene_projection, visual_components, projection_adapters, workspace

    def _build_projection(self, scene_projection_module):
        graph = _FakeSceneGraph(
            [
                _FakeNode(
                    "cabinet-1",
                    "Base Cabinet",
                    "CABINET",
                    0.0,
                    0.0,
                    0.0,
                    600.0,
                    580.0,
                    720.0,
                    metadata={"material": "Oak", "finish": "Matte"},
                ),
                _FakeNode(
                    "door-1",
                    "Left Door",
                    "DOOR_PANEL",
                    18.0,
                    0.0,
                    0.0,
                    297.0,
                    18.0,
                    700.0,
                    metadata={"material": "Oak", "hinge": "Soft Close"},
                ),
            ]
        )
        return scene_projection_module.build_scene_projection(
            graph,
            selected_node_id="door-1",
            highlight_target="door-1",
            representation_status="Ready",
            source_reference="SceneGraph",
        )

    def test_visual_components_are_presentation_only(self):
        _, visual_components, _, _ = self._import_modules()

        component = visual_components.DoorVisualComponent(
            id="door-1",
            display_name="Left Door",
            material_name="Oak",
            visibility=True,
            selection_state="SELECTED",
            highlight_state="HIGHLIGHTED",
            display_state="HIGHLIGHTED",
            display_metadata=(("hinge", "Soft Close"),),
            warnings=("Check reveal",),
            representation_status="Ready",
            base_color="#B9825A",
            accent_color="#5B3A29",
            label="Left Door",
            tooltip="Left Door | Door",
            source_reference="SceneProjection:door-1",
        )

        self.assertEqual(component.component_type, "DOOR")
        self.assertFalse(hasattr(component, "Shape"))
        self.assertFalse(hasattr(component, "ViewObject"))
        self.assertFalse(hasattr(component, "Document"))
        self.assertFalse(hasattr(component, "node_id"))

    def test_factory_converts_scene_projection_to_visual_components(self):
        scene_projection, visual_components, _, _ = self._import_modules()
        projection = self._build_projection(scene_projection)

        components = visual_components.build_visual_components(projection)

        self.assertEqual(len(components), 2)
        self.assertIsInstance(components[0], visual_components.CabinetVisualComponent)
        self.assertIsInstance(components[1], visual_components.DoorVisualComponent)
        self.assertEqual(components[1].selection_state, "SELECTED")
        self.assertEqual(components[1].highlight_state, "HIGHLIGHTED")
        self.assertEqual(components[1].display_state, "HIGHLIGHTED")
        self.assertTrue(all(component.__class__.__name__.endswith("Component") for component in components))
        self.assertTrue(all(not hasattr(component, "Shape") for component in components))

    def test_preview_adapter_accepts_visual_components(self):
        scene_projection, visual_components, projection_adapters, _ = self._import_modules()
        components = visual_components.build_visual_components(self._build_projection(scene_projection))

        read_model = projection_adapters.build_preview_read_model(
            {
                "visual_components": components,
                "preview_mode": "Design View",
                "preview_title": "Visual Component Preview",
            }
        )

        self.assertTrue(read_model.scene_available)
        self.assertEqual(read_model.node_count, 2)
        self.assertEqual(read_model.highlighted_item_id, "door-1")
        self.assertEqual(read_model.highlighted_item_type, "DOOR")
        self.assertIn("material", dict(read_model.items[0].display_metadata))

    def test_preview_region_consumes_visual_components(self):
        scene_projection, visual_components, projection_adapters, workspace_module = self._import_modules()
        components = visual_components.build_visual_components(self._build_projection(scene_projection))
        workspace = workspace_module.create_configurator_v2_workspace()
        read_model = projection_adapters.build_preview_read_model(
            {
                "visual_components": components,
                "preview_title": "Component Preview",
                "preview_mode": "Design View",
            }
        )

        workspace.set_preview_visual_components(components, read_model)

        self.assertEqual(workspace.preview_visual_components, components)
        self.assertEqual(workspace.preview_region.visual_components, components)
        self.assertIs(workspace.preview_region.read_model, read_model)
        self.assertIn("Preview Title: Component Preview", workspace.preview_region.render_rows)
        self.assertIn("Node Count: 2", workspace.preview_region.render_rows)
        self.assertIn("Selected Node: door-1", workspace.preview_region.render_rows)


if __name__ == "__main__":
    unittest.main()
