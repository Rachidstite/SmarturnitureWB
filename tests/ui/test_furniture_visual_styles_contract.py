# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Furniture Visual Styles Contract Tests
#
# Verifies:
# - style objects are presentation-only
# - style builder maps DoorVisualComponent → DoorVisualStyle
# - drawer/panel/back/hardware/feature styles work
# - no backend object accepted
# - preview adapter preserves style metadata
# - UI tests pass
# - architecture tests pass
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

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


class TestFurnitureVisualStylesContract(unittest.TestCase):
    """Verify that furniture visual style dataclasses are presentation-only,
    map correctly to VisualComponent subtypes, and integrate with the
    preview pipeline without backend objects."""

    @classmethod
    def _import_modules(cls):
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            scene_projection = importlib.import_module("ui.configurator_v2.scene_projection")
            visual_components = importlib.import_module("ui.configurator_v2.visual_components")
            styles = importlib.import_module("ui.configurator_v2.furniture_visual_styles")
            projection_adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
            workspace = importlib.import_module("ui.configurator_v2.workspace")
        return scene_projection, visual_components, styles, projection_adapters, workspace

    # ── Rule 1: presentation-only ────────────────────────────────────

    def test_style_objects_are_presentation_only(self):
        """Style dataclasses must not carry backend geometry attributes."""
        _, _, styles, _, _ = self._import_modules()

        door_style = styles.DoorVisualStyle(
            style_name="shaker",
            door_type="shaker",
            overlay_inset="overlay",
            handle_position="right",
        )
        self.assertFalse(hasattr(door_style, "Shape"))
        self.assertFalse(hasattr(door_style, "ViewObject"))
        self.assertFalse(hasattr(door_style, "Document"))
        self.assertFalse(hasattr(door_style, "node_id"))

        drawer_style = styles.DrawerVisualStyle(
            front_type="slab",
            internal_box=True,
            slide_type="under-mount",
        )
        self.assertFalse(hasattr(drawer_style, "Shape"))

        panel_style = styles.PanelVisualStyle(
            material_finish="matte",
            color_name="White",
            texture_descriptor="smooth",
            edge_banding_appearance="match",
        )
        self.assertFalse(hasattr(panel_style, "Shape"))

        back_style = styles.BackPanelVisualStyle(thin_panel=True, recessed_panel=False)
        self.assertFalse(hasattr(back_style, "Shape"))

        hw_style = styles.HardwareVisualStyle(
            hinge="Soft Close",
            handle="Bar Pull",
            drawer_slide="Under-mount",
        )
        self.assertFalse(hasattr(hw_style, "Shape"))

        fm_style = styles.FeatureMarkerVisualStyle(
            drilling="5mm x 12mm",
            groove="4mm x 4mm",
        )
        self.assertFalse(hasattr(fm_style, "Shape"))

    # ── Rule 2: no backend objects ───────────────────────────────────

    def test_builder_rejects_backend_objects(self):
        """build_furniture_visual_style must reject non-VisualComponent args."""
        _, _, styles, _, _ = self._import_modules()

        with self.assertRaises(TypeError):
            styles.build_furniture_visual_style(None)  # type: ignore

    def test_builder_rejects_non_component(self):
        """Non-VisualComponent types must be rejected."""
        _, _, styles, _, _ = self._import_modules()

        with self.assertRaises(TypeError):
            styles.build_furniture_visual_style("not-a-component")  # type: ignore

        with self.assertRaises(TypeError):
            styles.build_furniture_visual_style(42)  # type: ignore

    # ── Rule 3: Door style mapping ───────────────────────────────────

    def test_door_style_builder(self):
        """DoorVisualComponent → DoorVisualStyle with correct descriptor fields."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.DoorVisualComponent(
            id="door-1",
            display_name="Left Door",
            material_name="Oak",
            display_metadata=(
                ("door_style", "shaker"),
                ("mount", "overlay"),
                ("handle_position", "right"),
                ("finish", "Matte"),
                ("edge_material", "PVC"),
                ("edge_color", "Matching"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.DoorVisualStyle)
        self.assertEqual(style.door_type, "shaker")
        self.assertEqual(style.overlay_inset, "overlay")
        self.assertEqual(style.handle_position, "right")
        self.assertEqual(style.material.material_name, "Oak")
        self.assertEqual(style.material.finish, "Matte")
        self.assertEqual(style.edge_band.material, "PVC")
        self.assertEqual(style.edge_band.color, "Matching")
        self.assertFalse(hasattr(style, "Shape"))

    def test_door_style_variants(self):
        """All door type variants produce valid DoorVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        for door_type in ("slab", "shaker", "glass", "framed", "flush"):
            component = visual_components.DoorVisualComponent(
                id=f"door-{door_type}",
                display_name=f"{door_type.title()} Door",
                display_metadata=(
                    ("door_style", door_type),
                    ("mount", "overlay" if door_type != "flush" else "inset"),
                ),
            )
            style = styles.build_furniture_visual_style(component)
            self.assertIsInstance(style, styles.DoorVisualStyle)
            self.assertEqual(style.door_type, door_type)

    # ── Rule 4: Drawer style ─────────────────────────────────────────

    def test_drawer_style_builder(self):
        """DrawerVisualComponent → DrawerVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.DrawerVisualComponent(
            id="drawer-1",
            display_name="Upper Drawer",
            material_name="Oak",
            display_metadata=(
                ("front_type", "slab"),
                ("internal_box", "true"),
                ("slide_type", "under-mount"),
                ("handle_position", "center"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.DrawerVisualStyle)
        self.assertEqual(style.front_type, "slab")
        self.assertTrue(style.internal_box)
        self.assertEqual(style.slide_type, "under-mount")
        self.assertEqual(style.handle_position, "center")

    def test_drawer_framed_front(self):
        """Drawer framed front variant."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.DrawerVisualComponent(
            id="drawer-framed",
            display_metadata=(
                ("front_type", "framed"),
                ("internal_box", "false"),
                ("slide_type", "side-mount"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertEqual(style.front_type, "framed")
        self.assertFalse(style.internal_box)
        self.assertEqual(style.slide_type, "side-mount")

    # ── Rule 5: Panel style ──────────────────────────────────────────

    def test_panel_style_builder(self):
        """PanelVisualComponent → PanelVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.PanelVisualComponent(
            id="panel-1",
            display_name="Side Panel",
            material_name="MDF",
            display_metadata=(
                ("finish", "matte"),
                ("color_name", "White"),
                ("texture", "smooth"),
                ("edge_appearance", "match"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.PanelVisualStyle)
        self.assertEqual(style.material_finish, "matte")
        self.assertEqual(style.color_name, "White")
        self.assertEqual(style.texture_descriptor, "smooth")
        self.assertEqual(style.edge_banding_appearance, "match")

    # ── Rule 6: Back panel style ─────────────────────────────────────

    def test_back_panel_style_builder(self):
        """BackPanelVisualComponent → BackPanelVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.BackPanelVisualComponent(
            id="back-1",
            display_name="Back Panel",
            display_metadata=(
                ("thin_panel", "true"),
                ("recessed_panel", "true"),
                ("groove", "single"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.BackPanelVisualStyle)
        self.assertTrue(style.thin_panel)
        self.assertTrue(style.recessed_panel)
        self.assertEqual(style.groove_indicator, "single")

    # ── Rule 7: Hardware style ───────────────────────────────────────

    def test_hardware_style_builder(self):
        """HardwareVisualComponent → HardwareVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.HardwareVisualComponent(
            id="hw-1",
            display_name="Door Hardware",
            display_metadata=(
                ("hinge", "Soft Close 110°"),
                ("handle", "Bar Pull 128mm"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.HardwareVisualStyle)
        self.assertEqual(style.hinge, "Soft Close 110°")
        self.assertEqual(style.handle, "Bar Pull 128mm")
        self.assertEqual(style.drawer_slide, "")
        self.assertEqual(style.shelf_pin, "")
        self.assertEqual(style.minifix, "")
        self.assertEqual(style.confirmat, "")

    def test_hardware_style_all_fields(self):
        """HardwareVisualStyle with all hardware fields populated."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.HardwareVisualComponent(
            id="hw-full",
            display_metadata=(
                ("hinge", "Hinge A"),
                ("handle", "Handle B"),
                ("drawer_slide", "Slide C"),
                ("shelf_pin", "Pin D"),
                ("minifix", "Minifix E"),
                ("confirmat", "Confirmat F"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertEqual(style.hinge, "Hinge A")
        self.assertEqual(style.handle, "Handle B")
        self.assertEqual(style.drawer_slide, "Slide C")
        self.assertEqual(style.shelf_pin, "Pin D")
        self.assertEqual(style.minifix, "Minifix E")
        self.assertEqual(style.confirmat, "Confirmat F")

    # ── Rule 8: Feature marker style ─────────────────────────────────

    def test_feature_marker_style_builder(self):
        """FeatureMarkerComponent → FeatureMarkerVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        component = visual_components.FeatureMarkerComponent(
            id="fm-1",
            display_name="Drill Pattern",
            display_metadata=(
                ("drilling", "5mm x 12mm"),
                ("groove", "4mm x 4mm"),
                ("cutout", "50mm x 30mm"),
                ("edge_band_feature", "2mm"),
            ),
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.FeatureMarkerVisualStyle)
        self.assertEqual(style.drilling, "5mm x 12mm")
        self.assertEqual(style.groove, "4mm x 4mm")
        self.assertEqual(style.cutout, "50mm x 30mm")
        self.assertEqual(style.edge_band_feature, "2mm")

    # ── Rule 9: apply_furniture_visual_styles batch ──────────────────

    def test_apply_furniture_visual_styles_batch(self):
        """apply_furniture_visual_styles returns one style per component."""
        _, visual_components, styles, _, _ = self._import_modules()

        components = (
            visual_components.DoorVisualComponent(
                id="d1", display_metadata=(("door_style", "shaker"),)
            ),
            visual_components.DrawerVisualComponent(
                id="dr1", display_metadata=(("front_type", "slab"),)
            ),
            visual_components.PanelVisualComponent(id="p1"),
        )
        result = styles.apply_furniture_visual_styles(components)

        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], styles.DoorVisualStyle)
        self.assertIsInstance(result[1], styles.DrawerVisualStyle)
        self.assertIsInstance(result[2], styles.PanelVisualStyle)

    def test_apply_furniture_visual_styles_empty(self):
        """apply_furniture_visual_styles handles empty input."""
        _, _, styles, _, _ = self._import_modules()
        result = styles.apply_furniture_visual_styles(())
        self.assertEqual(result, ())

    # ── Rule 10: Style descriptor pairs ──────────────────────────────

    def test_style_descriptor_pairs_roundtrip(self):
        """style_descriptor_pairs flattens a style into metadata pairs."""
        _, _, styles, _, _ = self._import_modules()

        door_style = styles.DoorVisualStyle(
            style_name="shaker",
            door_type="shaker",
            overlay_inset="overlay",
            handle_position="right",
            material=styles.MaterialVisualDescriptor(material_name="Oak", finish="Matte"),
            edge_band=styles.EdgeBandVisualStyle(material="PVC", color="Matching"),
        )
        pairs = dict(styles.style_descriptor_pairs(door_style))

        self.assertEqual(pairs.get("style_name"), "shaker")
        self.assertEqual(pairs.get("door_type"), "shaker")
        self.assertEqual(pairs.get("mount"), "overlay")
        self.assertEqual(pairs.get("handle_position"), "right")
        self.assertEqual(pairs.get("style_material"), "Oak")
        self.assertEqual(pairs.get("style_finish"), "Matte")
        self.assertEqual(pairs.get("edge_band_material"), "PVC")
        self.assertEqual(pairs.get("edge_band_color"), "Matching")

    def test_style_descriptor_pairs_empty(self):
        """style_descriptor_pairs returns () for None."""
        _, _, styles, _, _ = self._import_modules()
        self.assertEqual(styles.style_descriptor_pairs(None), ())

    # ── Rule 11: MaterialVisualDescriptor ────────────────────────────

    def test_material_is_empty_check(self):
        """MaterialVisualDescriptor.is_empty reports missing material."""
        _, _, styles, _, _ = self._import_modules()

        empty = styles.MaterialVisualDescriptor()
        self.assertTrue(empty.is_empty)

        populated = styles.MaterialVisualDescriptor(material_name="Oak")
        self.assertFalse(populated.is_empty)

    def test_edge_band_is_empty_check(self):
        """EdgeBandVisualStyle.is_empty reports missing band data."""
        _, _, styles, _, _ = self._import_modules()

        empty = styles.EdgeBandVisualStyle()
        self.assertTrue(empty.is_empty)

        populated = styles.EdgeBandVisualStyle(material="PVC")
        self.assertFalse(populated.is_empty)

    # ── Rule 12: Summary labels ──────────────────────────────────────

    def test_style_summary_label(self):
        """style_summary_label produces human-readable summaries."""
        _, _, styles, _, _ = self._import_modules()

        door = styles.DoorVisualStyle(
            door_type="shaker",
            overlay_inset="overlay",
            material=styles.MaterialVisualDescriptor(material_name="Oak"),
        )
        label = styles.style_summary_label(door)
        self.assertIn("shaker", label)
        self.assertIn("overlay", label)
        self.assertIn("Oak", label)

        drawer = styles.DrawerVisualStyle(
            front_type="slab",
            slide_type="under-mount",
        )
        label = styles.style_summary_label(drawer)
        self.assertIn("slab", label)
        self.assertIn("under-mount", label)

        panel = styles.PanelVisualStyle(
            material_finish="matte",
            color_name="White",
            edge_banding_appearance="match",
        )
        label = styles.style_summary_label(panel)
        self.assertIn("White", label)

        back = styles.BackPanelVisualStyle(
            thin_panel=True,
            recessed_panel=True,
            groove_indicator="single",
        )
        label = styles.style_summary_label(back)
        self.assertIn("thin", label)
        self.assertIn("recessed", label)

        hw = styles.HardwareVisualStyle(hinge="Soft Close")
        label = styles.style_summary_label(hw)
        self.assertIn("Soft Close", label)

        fm = styles.FeatureMarkerVisualStyle(drilling="5mm", groove="4mm", edge_band_feature="2mm")
        label = styles.style_summary_label(fm)
        self.assertIn("5mm", label)
        self.assertIn("eb:2mm", label)

    def test_style_summary_label_none(self):
        """style_summary_label handles None."""
        _, _, styles, _, _ = self._import_modules()
        self.assertEqual(styles.style_summary_label(None), "No style")

    # ── Rule 13: Preview adapter preserves style metadata ────────────

    def test_preview_adapter_includes_style_pairs(self):
        """Preview items built from visual components include style metadata."""
        _, visual_components, styles, projection_adapters, _ = self._import_modules()

        components = (
            visual_components.DoorVisualComponent(
                id="door-1",
                display_name="Shaker Door",
                material_name="Oak",
                display_metadata=(
                    ("door_style", "shaker"),
                    ("mount", "overlay"),
                    ("handle_position", "right"),
                    ("finish", "Matte"),
                ),
            ),
        )
        read_model = projection_adapters.build_preview_read_model(
            {"visual_components": components}
        )

        self.assertEqual(read_model.node_count, 1)
        item = read_model.items[0]
        meta = dict(item.display_metadata)

        # Standard fields
        self.assertEqual(meta.get("material"), "Oak")

        # Style-derived fields
        self.assertEqual(meta.get("style_name"), "shaker")
        self.assertEqual(meta.get("door_type"), "shaker")
        self.assertEqual(meta.get("mount"), "overlay")
        self.assertEqual(meta.get("handle_position"), "right")
        self.assertEqual(meta.get("style_material"), "Oak")
        self.assertEqual(meta.get("style_finish"), "Matte")

    # ── Rule 14: Preview region displays styles ──────────────────────

    def test_preview_region_computes_styles(self):
        """PreviewRegion.set_visual_components computes and stores styles."""
        _, visual_components, styles, projection_adapters, workspace_module = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()

        components = (
            visual_components.DoorVisualComponent(
                id="door-1", display_metadata=(("door_style", "shaker"),)
            ),
        )
        read_model = projection_adapters.build_preview_read_model(
            {"visual_components": components}
        )
        workspace.set_preview_visual_components(components, read_model)

        self.assertEqual(len(workspace.preview_region.visual_styles), 1)
        self.assertIsInstance(
            workspace.preview_region.visual_styles[0],
            styles.DoorVisualStyle,
        )
        # Style summary should appear in render rows
        style_rows = [r for r in workspace.preview_region.render_rows if "Style" in r]
        self.assertTrue(len(style_rows) >= 1)

    # ── Rule 15: Unregistered component gets generic style ───────────

    def test_unregistered_component_gets_generic_style(self):
        """Components without a specific builder get a base FurnitureVisualStyle."""
        _, visual_components, styles, _, _ = self._import_modules()

        # ShelfVisualComponent has no dedicated style builder
        component = visual_components.ShelfVisualComponent(
            id="shelf-1",
            material_name="Oak",
        )
        style = styles.build_furniture_visual_style(component)

        self.assertIsInstance(style, styles.FurnitureVisualStyle)
        self.assertNotIsInstance(style, styles.DoorVisualStyle)

    # ── Rule 16: Edge band descriptor ────────────────────────────────

    def test_edge_band_descriptor(self):
        """EdgeBandVisualStyle handles thickness conversion."""
        _, _, styles, _, _ = self._import_modules()

        eb = styles.EdgeBandVisualStyle(
            material="ABS",
            color="White",
            thickness_mm=1.0,
            application="glued",
        )
        self.assertEqual(eb.material, "ABS")
        self.assertEqual(eb.color, "White")
        self.assertEqual(eb.thickness_mm, 1.0)
        self.assertEqual(eb.application, "glued")

    # ── Rule 17: Material descriptor ─────────────────────────────────

    def test_material_descriptor(self):
        """MaterialVisualDescriptor fields are strings."""
        _, _, styles, _, _ = self._import_modules()

        md = styles.MaterialVisualDescriptor(
            material_name="Oak",
            finish="Matte",
            color_name="Natural",
            texture_descriptor="Wood grain",
            supplier="Supplier X",
        )
        self.assertEqual(md.material_name, "Oak")
        self.assertEqual(md.finish, "Matte")
        self.assertEqual(md.color_name, "Natural")
        self.assertEqual(md.texture_descriptor, "Wood grain")
        self.assertEqual(md.supplier, "Supplier X")


if __name__ == "__main__":
    unittest.main()
