from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from engine.cabinet import Cabinet
from scene_graph.builder import SceneGraphBuilder
from scene_graph.renderer import SceneRenderer
from shared.roles import NodeRole


class _FakeGroup:
    def __init__(self):
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)


class _FakeFeature:
    def __init__(self, name):
        self.Name = name
        self.Shape = None
        self.Placement = None
        self.SmartUUID = ""
        self.ViewObject = SimpleNamespace(ShapeColor=None, Transparency=0)

    def addProperty(self, *_args, **_kwargs):
        return None


class _FakeDoc:
    def __init__(self):
        self.features = []

    def addObject(self, kind, name):
        if kind == "App::DocumentObjectGroup":
            return _FakeGroup()
        feature = _FakeFeature(name)
        self.features.append(feature)
        return feature


class _FakeVector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class _FakePlacement:
    def __init__(self, base, rotation):
        self.Base = base
        self.Rotation = rotation


class _FakeRotation:
    pass


class TestBaseCabinetVerticalPlacementRendering(TestCase):
    def test_renderer_preserves_engineering_z_ranges_for_bottom_and_plinth_nodes(self):
        cabinet = Cabinet()
        specification = BaseCabinetSpecification(toe_kick_required=True)
        attach_base_cabinet_engineering_models(cabinet, specification)

        graph = SceneGraphBuilder(cabinet, MaterialManager()).build(SimpleNamespace())
        target_nodes = [
            node
            for node in graph.all_nodes()
            if node.role in {NodeRole.BOTTOM_PANEL, NodeRole.PLINTH}
        ]

        doc = _FakeDoc()
        renderer = SceneRenderer(doc, MaterialManager(), hw=None, groups={})
        fake_app = SimpleNamespace(
            Placement=_FakePlacement,
            Vector=_FakeVector,
            Rotation=_FakeRotation,
        )
        fake_part = SimpleNamespace(makeBox=lambda width, depth, height: (width, depth, height))

        with patch("scene_graph.renderer.App", fake_app), patch(
            "scene_graph.renderer.Part",
            fake_part,
        ), patch(
            "scene_graph.renderer.process_panel_shape",
            side_effect=lambda base_shape, node, panel_features, panel_origin: {
                "base_shape": base_shape,
                "panel_origin": panel_origin,
            },
        ):
            for node in target_nodes:
                renderer.render(node)

        placements_by_name = {feature.Name: feature.Placement.Base.z for feature in doc.features}
        for node in target_nodes:
            self.assertEqual(placements_by_name[node.identity.key], node.z)
