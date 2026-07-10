import json
import types
import unittest
from importlib import import_module
from unittest.mock import patch

from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from manufacturing.visible_geometry_plan import build_visible_geometry_plan
from scene_graph.builder import SceneGraphBuilder
from shared.roles import NodeRole


class _BoxShape:
    def __init__(self, size, origin=(0.0, 0.0, 0.0), removed_volume=0.0, cuts=None):
        self.size = tuple(float(value) for value in size)
        self.origin = tuple(float(value) for value in origin)
        self.removed_volume = float(removed_volume)
        self.cuts = list(cuts or [])

    @property
    def bounds(self):
        x, y, z = self.origin
        sx, sy, sz = self.size
        return (x, x + sx, y, y + sy, z, z + sz)

    @property
    def volume(self):
        sx, sy, sz = self.size
        return (sx * sy * sz) - self.removed_volume

    def translate(self, vector):
        self.origin = tuple(self.origin[index] + float(vector[index]) for index in range(3))

    def cut(self, other):
        ax0, ax1, ay0, ay1, az0, az1 = self.bounds
        bx0, bx1, by0, by1, bz0, bz1 = other.bounds
        ix = max(0.0, min(ax1, bx1) - max(ax0, bx0))
        iy = max(0.0, min(ay1, by1) - max(ay0, by0))
        iz = max(0.0, min(az1, bz1) - max(az0, bz0))
        removed = ix * iy * iz
        return _BoxShape(
            self.size,
            origin=self.origin,
            removed_volume=self.removed_volume + removed,
            cuts=self.cuts
            + [
                {
                    "tool_origin": other.origin,
                    "tool_size": other.size,
                    "intersection_size": (ix, iy, iz),
                    "intersection_volume": removed,
                }
            ],
        )


class TestBackPanelGrooveRuntimeGeometryContract(unittest.TestCase):
    """Runtime geometry contract using the real base-cabinet path with a deterministic solid emulator.

    FreeCAD/Part is unavailable in the active test environment, so this test proves the
    same runtime coordinate filtering and boolean-cut behavior using a minimal box-solid
    emulator that mirrors the processor's Part.makeBox -> translate -> cut workflow.
    """

    def _build_runtime_graph(self, specification):
        adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
        cabinet = Cabinet(params=adapter_result.cabinet_params)
        attach_base_cabinet_engineering_models(cabinet, specification)

        fake_freecad = types.ModuleType("FreeCAD")
        fake_part = types.ModuleType("Part")
        fake_part.makeBox = lambda *args, **kwargs: object()
        fake_freecad_gui = types.ModuleType("FreeCADGui")

        with patch.dict(
            "sys.modules",
            {
                "FreeCAD": fake_freecad,
                "Part": fake_part,
                "FreeCADGui": fake_freecad_gui,
            },
        ):
            cabinet_builder_module = import_module("engine.cabinet_builder")
            builder = cabinet_builder_module.CabinetBuilder()
            builder._cabinet = cabinet
            builder.mat = MaterialManager()
            builder.geo = GeometryEngine(cabinet, builder.mat)
            builder.geo.resolve_all()
            builder._attach_section_engineering_components()

        graph = SceneGraphBuilder(cabinet, builder.mat).build(builder.geo)
        cabinet.graph = graph
        cabinet.scene_graph = graph
        return cabinet, graph

    @staticmethod
    def _panel_base_dimensions(node):
        if node.role == NodeRole.SIDE_PANEL:
            return (node.thickness, node.depth, node.height)
        if node.role in {NodeRole.TOP_PANEL, NodeRole.BOTTOM_PANEL}:
            return (node.width, node.depth, node.thickness)
        raise AssertionError(f"Unsupported role for this contract: {node.role!r}")

    def test_real_runtime_back_panel_grooves_reduce_panel_geometry(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        cabinet, graph = self._build_runtime_graph(specification)
        project = types.SimpleNamespace(
            cabinet=cabinet,
            graph=graph,
            projected_visible_features=(),
            topology=types.SimpleNamespace(d=specification.depth_mm),
        )
        plan = build_visible_geometry_plan(project)
        groove_features = [
            feature for feature in plan.features if getattr(feature, "kind", "") == "back_panel_groove"
        ]

        self.assertEqual(len(groove_features), 3)

        target_roles = {
            NodeRole.SIDE_PANEL: [],
            NodeRole.BOTTOM_PANEL: [],
        }
        for feature in groove_features:
            node = graph.get_node(feature.node_id)
            target_roles[node.role].append((node, feature))

        self.assertEqual(len(target_roles[NodeRole.SIDE_PANEL]), 2)
        self.assertEqual(len(target_roles[NodeRole.BOTTOM_PANEL]), 1)

        fake_part = types.SimpleNamespace(makeBox=lambda sx, sy, sz: _BoxShape((sx, sy, sz)))
        verification_rows = []

        with patch.object(panel_shape_processor, "Part", fake_part):
            for node, feature in (
                target_roles[NodeRole.SIDE_PANEL] + target_roles[NodeRole.BOTTOM_PANEL]
            ):
                base_dimensions = self._panel_base_dimensions(node)
                base_shape = _BoxShape(base_dimensions)
                base_volume = base_shape.volume
                supported = panel_shape_processor._feature_supported_for_panel(node, feature)
                self.assertTrue(supported, f"Feature must be accepted for {node.identity.key}")

                result_shape = panel_shape_processor.process_panel_shape(
                    base_shape,
                    node,
                    groove_features,
                    panel_origin=(node.x, node.y, node.z),
                )

                self.assertGreaterEqual(len(result_shape.cuts), 1, node.identity.key)
                cut = result_shape.cuts[0]
                self.assertGreater(cut["intersection_volume"], 0.0, node.identity.key)
                self.assertLess(result_shape.volume, base_volume, node.identity.key)
                self.assertGreater(base_volume - result_shape.volume, 0.0, node.identity.key)

                verification_rows.append(
                    {
                        "panel": node.identity.key,
                        "panel_role": node.role.name,
                        "base_dimensions": base_dimensions,
                        "base_volume": base_volume,
                        "groove_dimensions": feature.size,
                        "cutter_count": len(result_shape.cuts),
                        "intersection_volume": cut["intersection_volume"],
                        "final_volume": result_shape.volume,
                        "removed_volume": base_volume - result_shape.volume,
                    }
                )

        self.assertEqual(
            {row["panel_role"] for row in verification_rows},
            {"SIDE_PANEL", "BOTTOM_PANEL"},
        )
        self.assertEqual(len(verification_rows), 3)

        for row in verification_rows:
            self.assertGreater(row["removed_volume"], 0.0, json.dumps(row))


if __name__ == "__main__":
    unittest.main()
