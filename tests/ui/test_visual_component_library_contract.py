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
        self._updated = False

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

    def update(self):
        self._updated = True

    def width(self):
        return 320

    def height(self):
        return 240

    def rect(self):
        return (0, 0, self.width(), self.height())


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


class _FakeColor:
    def __init__(self, value):
        self.value = value
        self.alpha = 255

    def setAlpha(self, alpha):
        self.alpha = alpha


class _FakePen:
    def __init__(self, color, width):
        self.color = color
        self.width = width


class _FakeBrush:
    def __init__(self, color):
        self.color = color


class _FakePainter:
    Antialiasing = "antialiasing"
    instances = []

    def __init__(self, widget):
        self.widget = widget
        self.operations = []
        self.pen = None
        self.brush = None
        self.ended = False
        type(self).instances.append(self)

    def setRenderHint(self, hint, enabled):
        self.operations.append(("setRenderHint", hint, enabled))

    def fillRect(self, rect, color):
        self.operations.append(("fillRect", rect, color.value, color.alpha))

    def setPen(self, pen):
        self.pen = pen
        self.operations.append(("setPen", pen.color.value, pen.width))

    def setBrush(self, brush):
        self.brush = brush
        self.operations.append(("setBrush", brush.color.value, brush.color.alpha))

    def drawRect(self, x, y, width, height):
        self.operations.append(
            (
                "drawRect",
                x,
                y,
                width,
                height,
                self.pen.color.value if self.pen is not None else "",
                self.brush.color.value if self.brush is not None else "",
                self.brush.color.alpha if self.brush is not None else 255,
            )
        )

    def end(self):
        self.ended = True
        self.operations.append(("end",))


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
        QtGui=types.SimpleNamespace(
            QPainter=_FakePainter,
            QColor=_FakeColor,
            QPen=_FakePen,
            QBrush=_FakeBrush,
        ),
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

    def test_preview_canvas_keeps_only_supported_visible_components(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        components = (
            visual_components.CabinetVisualComponent(
                id="cabinet-1",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
            ),
            visual_components.PanelVisualComponent(
                id="panel-1",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(18.0, 580.0, 720.0)),
            ),
            visual_components.ShelfVisualComponent(
                id="shelf-1",
                bounding_box=scene_bounds(minimum=(18.0, 0.0, 340.0), maximum=(582.0, 580.0, 358.0)),
            ),
            visual_components.DividerVisualComponent(
                id="divider-1",
                bounding_box=scene_bounds(minimum=(290.0, 0.0, 0.0), maximum=(308.0, 580.0, 720.0)),
            ),
            visual_components.BackPanelVisualComponent(
                id="back-1",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 6.0, 720.0)),
            ),
            visual_components.DoorVisualComponent(id="door-1"),
            visual_components.DrawerVisualComponent(id="drawer-1"),
            visual_components.HardwareVisualComponent(id="hw-1"),
            visual_components.ShelfVisualComponent(id="hidden-shelf", visibility=False),
        )

        canvas.set_visual_components(components)

        self.assertEqual(
            tuple(component.component_type for component in canvas.visual_components),
            ("CABINET", "PANEL", "SHELF", "DIVIDER", "BACK_PANEL"),
        )
        self.assertTrue(canvas._updated)

    def test_preview_canvas_paints_rectangles_from_existing_component_bounds(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        _FakePainter.instances.clear()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        components = (
            visual_components.BackPanelVisualComponent(
                id="back-1",
                base_color="#B4A58F",
                accent_color="#64594C",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 6.0, 720.0)),
            ),
            visual_components.CabinetVisualComponent(
                id="cabinet-1",
                base_color="#C8A26E",
                accent_color="#7A5330",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
            ),
            visual_components.ShelfVisualComponent(
                id="shelf-1",
                base_color="#D4B07A",
                accent_color="#6D5332",
                display_state="STALE",
                bounding_box=scene_bounds(minimum=(18.0, 0.0, 340.0), maximum=(582.0, 580.0, 358.0)),
            ),
            visual_components.DoorVisualComponent(
                id="door-1",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(297.0, 18.0, 700.0)),
            ),
        )

        canvas.set_visual_components(components)
        canvas.paintEvent(None)

        self.assertEqual(len(_FakePainter.instances), 1)
        painter = _FakePainter.instances[0]
        draw_ops = [op for op in painter.operations if op[0] == "drawRect"]
        self.assertEqual(len(draw_ops), 4)
        self.assertEqual(draw_ops[0][5], "#64594C")
        self.assertEqual(draw_ops[0][6], "#B4A58F")
        self.assertEqual(draw_ops[3][7], 180)
        self.assertTrue(painter.ended)

    def test_preview_canvas_selected_component_gets_stronger_outline(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        _FakePainter.instances.clear()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            selection_state="SELECTED",
            accent_color="#7A5330",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )

        canvas.set_visual_components((component,))
        canvas.paintEvent(None)

        painter = _FakePainter.instances[0]
        pen_ops = [op for op in painter.operations if op[0] == "setPen"]
        draw_ops = [op for op in painter.operations if op[0] == "drawRect"]
        self.assertEqual(pen_ops[0], ("setPen", "#2F5D50", 4))
        self.assertEqual(len(draw_ops), 1)
        self.assertEqual(draw_ops[0][5], "#2F5D50")

    def test_preview_canvas_highlighted_component_gets_secondary_outline(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        _FakePainter.instances.clear()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            highlight_state="HIGHLIGHTED",
            accent_color="#7A5330",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )

        canvas.set_visual_components((component,))
        canvas.paintEvent(None)

        painter = _FakePainter.instances[0]
        pen_ops = [op for op in painter.operations if op[0] == "setPen"]
        draw_ops = [op for op in painter.operations if op[0] == "drawRect"]
        self.assertEqual(pen_ops[0], ("setPen", "#C56A1A", 2))
        self.assertEqual(len(draw_ops), 2)
        self.assertEqual(draw_ops[0][5], "#C56A1A")
        self.assertEqual(draw_ops[1][1:5], (73, 16, 174, 208))

    def test_preview_canvas_normal_component_outline_remains_unchanged(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        _FakePainter.instances.clear()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            accent_color="#7A5330",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )

        canvas.set_visual_components((component,))
        canvas.paintEvent(None)

        painter = _FakePainter.instances[0]
        pen_ops = [op for op in painter.operations if op[0] == "setPen"]
        draw_ops = [op for op in painter.operations if op[0] == "drawRect"]
        self.assertEqual(pen_ops[0], ("setPen", "#7A5330", 2))
        self.assertEqual(len(draw_ops), 1)
        self.assertEqual(draw_ops[0][5], "#7A5330")

    def test_preview_canvas_selection_state_does_not_change_geometry_fit(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        normal = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )
        selected = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            selection_state="SELECTED",
            highlight_state="HIGHLIGHTED",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )
        bounds = canvas._bounds_for_components((normal,))

        self.assertEqual(canvas._component_rect(normal, bounds), canvas._component_rect(selected, bounds))

    def test_workspace_selection_sync_marks_matching_preview_component(self):
        scene_projection, visual_components, projection_adapters, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        workspace = workspace_module.create_configurator_v2_workspace()
        components = (
            visual_components.CabinetVisualComponent(
                id="cabinet-1",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
            ),
            visual_components.ShelfVisualComponent(
                id="shelf-1",
                bounding_box=scene_bounds(minimum=(18.0, 0.0, 340.0), maximum=(582.0, 580.0, 358.0)),
            ),
        )
        read_model = projection_adapters.build_preview_read_model({"visual_components": components})

        workspace.set_preview_visual_components(components, read_model)
        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="cabinet-1",
                display_name="Cabinet",
                source_region="InspectorRegion",
            )
        )

        selected_component = workspace.preview_visual_components[0]
        other_component = workspace.preview_visual_components[1]
        self.assertEqual(selected_component.selection_state, "SELECTED")
        self.assertEqual(selected_component.highlight_state, "HIGHLIGHTED")
        self.assertEqual(other_component.selection_state, "NORMAL")
        self.assertEqual(other_component.highlight_state, "NORMAL")

    def test_workspace_selection_sync_keeps_components_unchanged_when_no_match(self):
        scene_projection, visual_components, projection_adapters, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        workspace = workspace_module.create_configurator_v2_workspace()
        components = (
            visual_components.CabinetVisualComponent(
                id="cabinet-1",
                bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
            ),
        )
        read_model = projection_adapters.build_preview_read_model({"visual_components": components})

        workspace.set_preview_visual_components(components, read_model)
        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="missing-id",
                display_name="Missing Cabinet",
                source_region="InspectorRegion",
            )
        )

        self.assertEqual(workspace.preview_visual_components, components)
        self.assertEqual(workspace.preview_region.visual_components, components)

    def test_workspace_selection_sync_does_not_change_component_geometry(self):
        scene_projection, visual_components, projection_adapters, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        workspace = workspace_module.create_configurator_v2_workspace()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )
        read_model = projection_adapters.build_preview_read_model({"visual_components": (component,)})

        workspace.set_preview_visual_components((component,), read_model)
        original_bounds = workspace.preview_visual_components[0].bounding_box
        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="cabinet-1",
                display_name="Cabinet",
                source_region="InspectorRegion",
            )
        )

        synchronized_component = workspace.preview_visual_components[0]
        self.assertEqual(synchronized_component.bounding_box, original_bounds)
        self.assertEqual(synchronized_component.id, component.id)
        self.assertEqual(synchronized_component.component_type, component.component_type)

    def test_workspace_selection_without_preview_visuals_keeps_read_model_only_behavior(self):
        _, _, _, workspace_module = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="cabinet-1",
                display_name="Cabinet",
                source_region="InspectorRegion",
            )
        )

        self.assertEqual(workspace.preview_visual_components, ())
        self.assertEqual(workspace.preview_read_model.highlighted_item_id, "cabinet-1")
        self.assertEqual(workspace.preview_region.highlighted_selection_id, "cabinet-1")

    def test_preview_canvas_centers_drawing_in_canvas(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )
        bounds = canvas._bounds_for_components((component,))

        self.assertIsNotNone(bounds)
        fit = canvas._fit_rect_to_canvas(bounds)

        self.assertIsNotNone(fit)
        offset_x, offset_y, drawing_width, drawing_height, _scale = fit
        self.assertAlmostEqual(offset_x, 75.0)
        self.assertAlmostEqual(offset_y, 18.0)
        self.assertAlmostEqual(drawing_width, 170.0)
        self.assertAlmostEqual(drawing_height, 204.0)

    def test_preview_canvas_preserves_aspect_ratio_when_fitting(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(600.0, 580.0, 720.0)),
        )
        bounds = canvas._bounds_for_components((component,))
        rect = canvas._component_rect(component, bounds)

        self.assertAlmostEqual(rect[2] / rect[3], 600.0 / 720.0)

    def test_preview_canvas_applies_consistent_margin_around_fitted_drawing(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="cabinet-1",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(200.0, 580.0, 600.0)),
        )
        bounds = canvas._bounds_for_components((component,))

        self.assertIsNotNone(bounds)
        fit = canvas._fit_rect_to_canvas(bounds)

        self.assertIsNotNone(fit)
        offset_x, offset_y, drawing_width, drawing_height, _scale = fit
        self.assertAlmostEqual(offset_x, 126.0)
        self.assertAlmostEqual(offset_y, 18.0)
        self.assertAlmostEqual((canvas.width() - (offset_x + drawing_width)), 126.0)
        self.assertAlmostEqual((canvas.height() - (offset_y + drawing_height)), 18.0)

    def test_preview_canvas_skips_drawing_when_bounds_are_empty(self):
        scene_projection, visual_components, _, workspace_module = self._import_modules()
        _FakePainter.instances.clear()
        scene_bounds = scene_projection.SceneBoundsProjection
        canvas = workspace_module.PreviewCanvas()
        component = visual_components.CabinetVisualComponent(
            id="flat-cabinet",
            bounding_box=scene_bounds(minimum=(0.0, 0.0, 0.0), maximum=(0.0, 580.0, 720.0)),
        )

        canvas.set_visual_components((component,))

        self.assertIsNone(canvas._bounds_for_components(canvas.visual_components))
        canvas.paintEvent(None)

        self.assertEqual(len(_FakePainter.instances), 1)
        painter = _FakePainter.instances[0]
        draw_ops = [op for op in painter.operations if op[0] == "drawRect"]
        self.assertEqual(draw_ops, [])


if __name__ == "__main__":
    unittest.main()
