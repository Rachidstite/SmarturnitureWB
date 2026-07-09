import inspect
import unittest
import types
from dataclasses import FrozenInstanceError
from importlib import import_module
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModel
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from core.material_manager import MaterialManager
from engine.cabinet import Cabinet
from scene_graph.builder import SceneGraphBuilder
from shared.roles import NodeRole


class FakeCabinetBuilder:
    instances_created = 0
    build_calls = 0
    last_cabinet = None

    def __init__(self):
        type(self).instances_created += 1
        self.scene_graph = object()

    def build(self, cabinet):
        type(self).build_calls += 1
        type(self).last_cabinet = cabinet
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class TestBaseCabinetEngineeringEntryContract(unittest.TestCase):
    def _build_engineered_base_cabinet(self):
        from engine.geometry_engine import GeometryEngine

        fake_freecad = types.ModuleType("FreeCAD")
        fake_part = types.ModuleType("Part")
        fake_part.makeBox = lambda *args, **kwargs: object()
        fake_freecad_gui = types.ModuleType("FreeCADGui")

        cabinet = Cabinet()
        spec = BaseCabinetSpecification()
        attach_base_cabinet_engineering_models(cabinet, spec)

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

        return cabinet, builder

    def _build_scene_graph_from_specification(self, specification):
        from engine.geometry_engine import GeometryEngine

        fake_freecad = types.ModuleType("FreeCAD")
        fake_part = types.ModuleType("Part")
        fake_part.makeBox = lambda *args, **kwargs: object()
        fake_freecad_gui = types.ModuleType("FreeCADGui")

        adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
        cabinet = Cabinet(params=adapter_result.cabinet_params)
        attach_base_cabinet_engineering_models(cabinet, specification)

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

    def test_accepts_base_cabinet_specification(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsInstance(cabinet, Cabinet)
        self.assertIsNotNone(cabinet.construction_model)
        self.assertIsInstance(cabinet.engineering_model, BaseCabinetEngineeringModel)
        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)

    def test_uses_adapter(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            BaseCabinetSpecificationAdapter,
            "adapt",
            wraps=BaseCabinetSpecificationAdapter.adapt,
        ) as adapt_spy, patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            build_base_cabinet_engineering_cabinet(BaseCabinetSpecification())

        adapt_spy.assert_called_once()
        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)

    def test_attach_helper_populates_construction_and_engineering_models(self):
        from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModelBuilder

        cabinet = Cabinet()
        spec = BaseCabinetSpecification()

        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            BaseCabinetEngineeringModelBuilder,
            "build",
            wraps=BaseCabinetEngineeringModelBuilder.build,
        ) as engineering_model_build:
            result = attach_base_cabinet_engineering_models(cabinet, spec)

        self.assertIs(result, cabinet)
        self.assertIsNotNone(cabinet.construction_model)
        self.assertIsNotNone(cabinet.engineering_model)
        resolver_cls.resolve.assert_called_once()
        engineering_model_build.assert_called_once()

    def test_base_engineering_model_starts_with_no_dividers(self):
        from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModelBuilder

        cabinet = Cabinet()
        spec = BaseCabinetSpecification()
        attach_base_cabinet_engineering_models(cabinet, spec)

        self.assertEqual(len(getattr(cabinet.engineering_model, "dividers", ())), 0)
        self.assertEqual(len(getattr(cabinet.engineering_model, "shelves", ())), 1)

    def test_base_engineering_model_remains_frozen_when_enriched(self):
        cabinet = Cabinet()
        spec = BaseCabinetSpecification()
        attach_base_cabinet_engineering_models(cabinet, spec)
        engineering_model = cabinet.engineering_model

        with self.assertRaises(FrozenInstanceError):
            engineering_model.shelves = ()

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
            builder.mat.mdf_thickness = 18.0
            builder.geo = type(
                "Geo",
                (),
                {
                    "resolved_sections": [
                        type(
                            "Section",
                            (),
                            {
                                "shelves": [
                                    type(
                                        "Shelf",
                                        (),
                                        {
                                            "width": 100.0,
                                            "depth": 300.0,
                                            "x": 10.0,
                                            "y": 20.0,
                                            "z": 30.0,
                                        },
                                    )()
                                ],
                                "divider": type(
                                    "Divider",
                                    (),
                                    {
                                        "width": 12.0,
                                        "depth": 18.0,
                                        "height": 200.0,
                                        "x": 50.0,
                                        "y": 60.0,
                                        "z": 70.0,
                                    },
                                )(),
                            },
                        )(),
                        type(
                            "Section",
                            (),
                            {
                                "shelves": [
                                    type(
                                        "Shelf",
                                        (),
                                        {
                                            "width": 101.0,
                                            "depth": 301.0,
                                            "x": 11.0,
                                            "y": 21.0,
                                            "z": 31.0,
                                        },
                                    )()
                                ],
                                "divider": type(
                                    "Divider",
                                    (),
                                    {
                                        "width": 13.0,
                                        "depth": 19.0,
                                        "height": 201.0,
                                        "x": 51.0,
                                        "y": 61.0,
                                        "z": 71.0,
                                    },
                                )(),
                            },
                        )(),
                        type(
                            "Section",
                            (),
                            {
                                "shelves": [
                                    type(
                                        "Shelf",
                                        (),
                                        {
                                            "width": 102.0,
                                            "depth": 302.0,
                                            "x": 12.0,
                                            "y": 22.0,
                                            "z": 32.0,
                                        },
                                    )()
                                ],
                                "divider": None,
                            },
                        )(),
                    ]
                },
            )()

            builder._attach_section_engineering_components()

        self.assertIsNot(cabinet.engineering_model, engineering_model)
        self.assertEqual(len(cabinet.engineering_model.shelves), 3)
        self.assertEqual(len(cabinet.engineering_model.dividers), 2)
        self.assertEqual(len(getattr(engineering_model, "shelves", ())), 1)
        self.assertEqual(len(getattr(engineering_model, "dividers", ())), 0)

    def test_engineering_scene_graph_emits_shelves_and_dividers(self):
        from domain.base_cabinet_engineering_model import (
            BackPanelInstallationMode,
            BackPanelStrategy,
            EngineeringBackPanel,
            EngineeringDividerPlacement,
            EngineeringPanelPlacement,
            EngineeringShelfPlacement,
            BaseCabinetEngineeringModel,
        )

        cabinet = Cabinet()
        cabinet.params.width = 1800.0
        cabinet.params.height = 2200.0
        cabinet.params.depth = 600.0
        cabinet.params.sec_count = 3
        cabinet.engineering_model = BaseCabinetEngineeringModel(
            construction_model=types.SimpleNamespace(),
            left_side_panel=EngineeringPanelPlacement(
                "SIDE_PANEL", "Left", 18.0, 600.0, 2200.0, (0.0, 0.0, 0.0), 18.0, "MDF_18"
            ),
            right_side_panel=EngineeringPanelPlacement(
                "SIDE_PANEL", "Right", 18.0, 600.0, 2200.0, (1782.0, 0.0, 0.0), 18.0, "MDF_18"
            ),
            top_panel=EngineeringPanelPlacement(
                "TOP_PANEL", "Top", 1764.0, 600.0, 18.0, (18.0, 0.0, 2182.0), 18.0, "MDF_18"
            ),
            bottom_panel=EngineeringPanelPlacement(
                "BOTTOM_PANEL", "Bottom", 1764.0, 600.0, 18.0, (18.0, 0.0, 0.0), 18.0, "MDF_18"
            ),
            back_panel=EngineeringBackPanel(
                "BACK_PANEL",
                "Back",
                1764.0,
                8.0,
                2164.0,
                (18.0, 592.0, 18.0),
                8.0,
                "HDF_3",
                BackPanelInstallationMode.GROOVED,
                "Inside rear groove behind side/top/bottom panels",
                BackPanelStrategy.FULL_CABINET,
                3.0,
                4.0,
                "ConstructionResolver",
            ),
            shelves=(
                EngineeringShelfPlacement("SEC-1_Shelf_1", 0, "SEC-1", "bridge", 432.0, 300.0, 18.0, (18.0, 18.0, 100.0)),
                EngineeringShelfPlacement("SEC-2_Shelf_1", 1, "SEC-2", "bridge", 864.0, 300.0, 18.0, (468.0, 18.0, 100.0)),
                EngineeringShelfPlacement("SEC-3_Shelf_1", 2, "SEC-3", "bridge", 432.0, 300.0, 18.0, (1350.0, 18.0, 100.0)),
            ),
            dividers=(
                EngineeringDividerPlacement("SEC-1_Divider", 0, "SEC-1", "bridge", 18.0, 520.0, 2100.0, (450.0, 18.0, 98.0)),
                EngineeringDividerPlacement("SEC-2_Divider", 1, "SEC-2", "bridge", 18.0, 520.0, 2100.0, (1350.0, 18.0, 98.0)),
            ),
        )

        graph = SceneGraphBuilder(cabinet, MaterialManager()).build(
            type("Geo", (), {"resolved_top": type("Top", (), {"width": 1.0, "depth": 1.0, "thickness": 1.0, "x": 0.0, "y": 0.0, "z": 0.0})()})()
        )

        roles = [node.role for node in graph.all_nodes()]
        self.assertEqual(roles.count(NodeRole.SHELF), 3)
        self.assertEqual(roles.count(NodeRole.DIVIDER), 2)

    def test_base_cabinet_divider_starts_on_bottom_panel_top_face(self):
        cabinet, builder = self._build_engineered_base_cabinet()
        divider = cabinet.engineering_model.dividers[0]

        expected_z = cabinet.params.base_height + builder.mat.mdf_thickness
        self.assertAlmostEqual(divider.position_mm[2], expected_z)

    def test_base_cabinet_divider_height_matches_full_structural_rule(self):
        cabinet, builder = self._build_engineered_base_cabinet()
        divider = cabinet.engineering_model.dividers[0]

        expected_height = (
            cabinet.params.height
            - cabinet.params.base_height
            - (2 * builder.mat.mdf_thickness)
        )
        self.assertAlmostEqual(divider.height_mm, expected_height)

    def test_base_cabinet_divider_depth_remains_unchanged(self):
        cabinet, builder = self._build_engineered_base_cabinet()
        divider = cabinet.engineering_model.dividers[0]
        resolved_divider = builder.geo.resolved_sections[0].divider

        self.assertAlmostEqual(divider.depth_mm, resolved_divider.depth)

    def test_base_cabinet_divider_x_position_remains_unchanged(self):
        cabinet, builder = self._build_engineered_base_cabinet()
        divider = cabinet.engineering_model.dividers[0]
        resolved_divider = builder.geo.resolved_sections[0].divider

        self.assertAlmostEqual(divider.position_mm[0], resolved_divider.x)

    def test_base_cabinet_divider_y_position_remains_unchanged(self):
        cabinet, builder = self._build_engineered_base_cabinet()
        divider = cabinet.engineering_model.dividers[0]
        resolved_divider = builder.geo.resolved_sections[0].divider

        self.assertAlmostEqual(divider.position_mm[1], resolved_divider.y)

    def test_scene_graph_copies_base_cabinet_divider_geometry_unchanged(self):
        cabinet, builder = self._build_engineered_base_cabinet()
        graph = SceneGraphBuilder(cabinet, builder.mat).build(builder.geo)

        scene_dividers = [node for node in graph.all_nodes() if node.role == NodeRole.DIVIDER]
        self.assertEqual(len(scene_dividers), len(cabinet.engineering_model.dividers))

        for scene_divider, engineering_divider in zip(
            scene_dividers,
            cabinet.engineering_model.dividers,
        ):
            self.assertAlmostEqual(scene_divider.x, engineering_divider.position_mm[0])
            self.assertAlmostEqual(scene_divider.y, engineering_divider.position_mm[1])
            self.assertAlmostEqual(scene_divider.z, engineering_divider.position_mm[2])
            self.assertAlmostEqual(scene_divider.width, engineering_divider.width_mm)
            self.assertAlmostEqual(scene_divider.depth, engineering_divider.depth_mm)
            self.assertAlmostEqual(scene_divider.height, engineering_divider.height_mm)


    def test_open_sections_populate_engineering_shelves_from_geometry(self):
        from core.material_manager import MaterialManager
        from engine.geometry_engine import GeometryEngine
        from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter

        cabinet = Cabinet()
        cabinet.params.width = 1800.0
        cabinet.params.height = 2200.0
        cabinet.params.depth = 600.0
        cabinet.params.base_height = 80.0
        cabinet.params.sec_count = 3
        cabinet.params.section_widths = [450.0, 900.0, 450.0]
        cabinet.params.sec_data = {
            0: types.SimpleNamespace(drawers=0, drawer_type='Inset', shelves=1, doors='None', door_count=2),
            1: types.SimpleNamespace(drawers=0, drawer_type='Inset', shelves=1, doors='None', door_count=2),
            2: types.SimpleNamespace(drawers=0, drawer_type='Inset', shelves=1, doors='None', door_count=2),
        }

        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)

        fake_freecad = types.ModuleType('FreeCAD')
        fake_part = types.ModuleType('Part')
        fake_part.makeBox = lambda *args, **kwargs: object()
        fake_freecad_gui = types.ModuleType('FreeCADGui')

        with patch.dict(
            'sys.modules',
            {
                'FreeCAD': fake_freecad,
                'Part': fake_part,
                'FreeCADGui': fake_freecad_gui,
            },
        ):
            cabinet_builder_module = import_module('engine.cabinet_builder')
            builder = cabinet_builder_module.CabinetBuilder()
            builder._cabinet = cabinet
            builder.mat = MaterialManager()
            builder.geo = GeometryEngine(cabinet, builder.mat)
            builder.geo.resolve_all()
            builder._attach_section_engineering_components()

        self.assertEqual(len(cabinet.engineering_model.shelves), 3)
        self.assertEqual(len(cabinet.engineering_model.dividers), 2)

    def test_changing_shelf_count_changes_resulting_scene_graph(self):
        low_spec = BaseCabinetSpecification(shelf_count=0, door_count=0)
        high_spec = BaseCabinetSpecification(shelf_count=1, door_count=0)

        _, low_graph = self._build_scene_graph_from_specification(low_spec)
        _, high_graph = self._build_scene_graph_from_specification(high_spec)

        low_shelves = [
            node for node in low_graph.all_nodes() if node.role == NodeRole.SHELF
        ]
        high_shelves = [
            node for node in high_graph.all_nodes() if node.role == NodeRole.SHELF
        ]

        self.assertEqual(len(low_shelves), 0)
        self.assertEqual(len(high_shelves), 1)

    def test_changing_door_count_changes_resulting_scene_graph(self):
        low_spec = BaseCabinetSpecification(shelf_count=0, door_count=1)
        high_spec = BaseCabinetSpecification(shelf_count=0, door_count=4)

        _, low_graph = self._build_scene_graph_from_specification(low_spec)
        _, high_graph = self._build_scene_graph_from_specification(high_spec)

        low_doors = [
            node for node in low_graph.all_nodes() if node.role == NodeRole.DOOR_PANEL
        ]
        high_doors = [
            node for node in high_graph.all_nodes() if node.role == NodeRole.DOOR_PANEL
        ]

        self.assertEqual(len(low_doors), 1)
        self.assertEqual(len(high_doors), 4)

    def test_delegates_to_existing_cabinet_builder(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            build_base_cabinet_engineering_cabinet(BaseCabinetSpecification())

        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)
        self.assertIsInstance(FakeCabinetBuilder.last_cabinet, Cabinet)
        self.assertIsNotNone(FakeCabinetBuilder.last_cabinet.construction_model)
        self.assertIsInstance(
            FakeCabinetBuilder.last_cabinet.engineering_model,
            BaseCabinetEngineeringModel,
        )

    def test_returns_existing_cabinet_type(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertIsInstance(cabinet, Cabinet)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(engineering_entry_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_runtime_execution_methods(self):
        source = inspect.getsource(engineering_entry_module)
        self.assertNotIn("def run", source)
        self.assertNotIn("def execute", source)

    def test_no_runtime_imports_in_source(self):
        source = inspect.getsource(engineering_entry_module)
        self.assertNotIn("manufacturing", source.lower())
        self.assertNotIn("validation", source.lower())


if __name__ == "__main__":
    unittest.main()
