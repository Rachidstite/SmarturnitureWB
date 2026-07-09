import ast
import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_engineering_model import (
    BackPanelInstallationMode,
    BackPanelStrategy,
    BaseCabinetEngineeringModel,
    map_back_panel_installation_mode,
    map_back_panel_strategy,
)
from domain.construction_resolver import ConstructionResolver
from domain.furniture_construction_model import (
    BackPanelConstruction,
    CabinetConstructionModel,
    CabinetConstructionSpecification,
    ShelfConstruction,
)


class TestConstructionResolverContract(unittest.TestCase):
    def setUp(self):
        self.spec = BaseCabinetSpecification(
            width_mm=800.0,
            height_mm=720.0,
            depth_mm=560.0,
            shelf_count=1,
            has_back_panel=True,
        )
        self.model = ConstructionResolver.resolve(self.spec)

    def test_base_cabinet_specification_is_the_input(self):
        self.assertIsInstance(self.spec, BaseCabinetSpecification)
        self.assertIsInstance(self.model.specification, CabinetConstructionSpecification)
        self.assertEqual(self.model.specification.width_mm, self.spec.width_mm)
        self.assertEqual(self.model.specification.height_mm, self.spec.height_mm)
        self.assertEqual(self.model.specification.depth_mm, self.spec.depth_mm)

    def test_resolver_produces_furniture_construction_model(self):
        self.assertIsInstance(self.model, CabinetConstructionModel)
        self.assertNotIsInstance(self.model.specification, BaseCabinetSpecification)
        self.assertEqual(len(self.model.panels), 4)
        self.assertIsInstance(self.model.back_panel, BackPanelConstruction)
        self.assertEqual(len(self.model.shelves), 1)
        self.assertIsInstance(self.model.shelves[0], ShelfConstruction)

    def test_resolver_disables_back_panel_when_specification_disables_it(self):
        model = ConstructionResolver.resolve(
            BaseCabinetSpecification(
                width_mm=800.0,
                height_mm=720.0,
                depth_mm=560.0,
                shelf_count=1,
                has_back_panel=False,
            )
        )

        self.assertEqual(model.specification.back_panel_type, "NONE")
        self.assertIsNone(model.back_panel)

    def test_model_contains_explicit_construction_decisions(self):
        top = next(panel for panel in self.model.panels if panel.name == "Top")
        bottom = next(panel for panel in self.model.panels if panel.name == "Bottom")
        back = self.model.back_panel
        shelf = self.model.shelves[0]

        self.assertIn("between side panels", top.purpose)
        self.assertIn("between side panels", bottom.purpose)
        self.assertEqual(back.placement, "Inside rear groove behind side/top/bottom panels")
        self.assertEqual(back.installation_mode, "GROOVED")
        self.assertTrue(shelf.is_adjustable)
        self.assertEqual(shelf.fixed_or_adjustable, "ADJUSTABLE")
        self.assertFalse(hasattr(shelf, "position_mm"))

    def test_renderer_scene_graph_does_not_invent_back_panel_decision(self):
        from engine.cabinet import Cabinet
        from scene_graph.builder import SceneGraphBuilder

        cabinet = Cabinet()
        cabinet.params.width = self.spec.width_mm
        cabinet.params.height = self.spec.height_mm
        cabinet.params.depth = self.spec.depth_mm
        cabinet.params.sec_count = 1
        cabinet.construction_model = self.model

        geo = SimpleNamespace(resolved_top=None, resolved_sections=[], is_buildable=True)
        mat = SimpleNamespace(mdf_thickness=18.0, back_thickness=3.0)

        with patch(
            "scene_graph.builder.BackPanelRule",
            side_effect=AssertionError("BackPanelRule should not be used when a construction model exists"),
        ), patch(
            "manufacturing.extractor.ManufacturingExtractor.extract",
            side_effect=AssertionError("Manufacturing must not be touched"),
        ):
            graph = SceneGraphBuilder(cabinet, mat, cabinet_id="REF-CAB").build(geo)

        back_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "BACK_PANEL"
        ]
        shelf_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "SHELF"
        ]

        self.assertEqual(len(back_nodes), 1)
        self.assertEqual(len(shelf_nodes), 1)
        self.assertEqual(back_nodes[0].metadata.source_rule, "ConstructionResolver")
        self.assertEqual(back_nodes[0].x, self.model.specification.material_thickness_mm)
        self.assertEqual(
            back_nodes[0].y,
            self.spec.depth_mm - self.model.specification.back_panel_thickness_mm,
        )
        self.assertEqual(back_nodes[0].z, self.model.specification.material_thickness_mm)
        self.assertEqual(shelf_nodes[0].x, self.model.specification.material_thickness_mm)
        self.assertEqual(shelf_nodes[0].z, self.spec.height_mm / 2.0)

    def test_engineering_model_owns_mvp_panel_coordinates(self):
        from domain.base_cabinet_engineering_model import (
            BaseCabinetEngineeringModelBuilder,
        )

        engineering_model = BaseCabinetEngineeringModelBuilder.build(self.model)

        self.assertIsInstance(engineering_model, BaseCabinetEngineeringModel)
        self.assertEqual(engineering_model.left_side_panel.position_mm, (0.0, 0.0, 0.0))
        self.assertEqual(
            engineering_model.right_side_panel.position_mm,
            (self.spec.width_mm - self.model.specification.material_thickness_mm, 0.0, 0.0),
        )
        self.assertEqual(
            engineering_model.top_panel.position_mm,
            (
                self.model.specification.material_thickness_mm,
                0.0,
                self.spec.height_mm - self.model.specification.material_thickness_mm,
            ),
        )
        self.assertEqual(
            engineering_model.bottom_panel.position_mm,
            (self.model.specification.material_thickness_mm, 0.0, 0.0),
        )
        self.assertEqual(
            engineering_model.back_panel.position_mm,
            (
                self.model.specification.material_thickness_mm,
                self.spec.depth_mm - self.model.specification.back_panel_thickness_mm,
                self.model.specification.material_thickness_mm,
            ),
        )
        self.assertIs(
            engineering_model.back_panel.installation_mode,
            BackPanelInstallationMode.GROOVED,
        )
        self.assertEqual(
            engineering_model.back_panel.placement,
            "Inside rear groove behind side/top/bottom panels",
        )
        self.assertIs(
            engineering_model.back_panel.panel_strategy,
            BackPanelStrategy.FULL_CABINET,
        )
        self.assertEqual(engineering_model.back_panel.groove_depth_mm, 8.0)
        self.assertEqual(engineering_model.back_panel.groove_width_mm, 3.2)
        self.assertEqual(engineering_model.back_panel.source_rule, "ConstructionResolver")
        self.assertEqual(
            engineering_model.shelves[0].position_mm,
            (self.model.specification.material_thickness_mm, 0.0, self.spec.height_mm / 2.0),
        )

    def test_engineering_model_disables_back_panel_when_construction_disables_it(self):
        from domain.base_cabinet_engineering_model import (
            BaseCabinetEngineeringModelBuilder,
        )

        disabled_model = ConstructionResolver.resolve(
            BaseCabinetSpecification(
                width_mm=800.0,
                height_mm=720.0,
                depth_mm=560.0,
                shelf_count=1,
                has_back_panel=False,
            )
        )

        engineering_model = BaseCabinetEngineeringModelBuilder.build(disabled_model)

        self.assertIsNone(engineering_model.back_panel)

    def test_back_panel_mapping_helpers(self):
        self.assertIs(
            map_back_panel_installation_mode("GROOVED"),
            BackPanelInstallationMode.GROOVED,
        )
        self.assertIs(
            map_back_panel_strategy(self.model.specification.back_panel_type),
            BackPanelStrategy.FULL_CABINET,
        )
        with self.assertRaises(ValueError):
            map_back_panel_installation_mode("INVALID")
        with self.assertRaises(ValueError):
            map_back_panel_strategy("UNKNOWN")

    def test_scene_graph_builder_consumes_engineering_coordinates(self):
        from domain.base_cabinet_engineering_model import (
            BaseCabinetEngineeringModelBuilder,
        )
        from engine.cabinet import Cabinet
        from scene_graph.builder import SceneGraphBuilder

        cabinet = Cabinet()
        cabinet.params.width = self.spec.width_mm
        cabinet.params.height = self.spec.height_mm
        cabinet.params.depth = self.spec.depth_mm
        cabinet.params.sec_count = 1
        cabinet.construction_model = self.model
        cabinet.engineering_model = BaseCabinetEngineeringModelBuilder.build(self.model)
        engineering_model = cabinet.engineering_model

        geo = SimpleNamespace(resolved_top=None, resolved_sections=[], is_buildable=True)
        mat = SimpleNamespace(mdf_thickness=18.0, back_thickness=3.0)

        with patch(
            "scene_graph.builder.BackPanelRule",
            side_effect=AssertionError("BackPanelRule should not be used when engineering model exists"),
        ), patch(
            "manufacturing.extractor.ManufacturingExtractor.extract",
            side_effect=AssertionError("Manufacturing must not be touched"),
        ):
            graph = SceneGraphBuilder(cabinet, mat, cabinet_id="REF-CAB").build(geo)

        back_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "BACK_PANEL"
        ]
        shelf_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "SHELF"
        ]

        self.assertEqual(len(back_nodes), 1)
        self.assertEqual(len(shelf_nodes), 1)
        self.assertEqual(back_nodes[0].metadata.source_rule, "ConstructionResolver")
        self.assertEqual(back_nodes[0].metadata.groove_depth, self.model.back_panel.groove_depth_mm)
        self.assertEqual(
            back_nodes[0].metadata.back_offset,
            engineering_model.back_panel.position_mm[1],
        )
        self.assertEqual(back_nodes[0].x, self.model.specification.material_thickness_mm)
        self.assertEqual(
            back_nodes[0].y,
            self.spec.depth_mm - self.model.specification.back_panel_thickness_mm,
        )
        self.assertEqual(back_nodes[0].z, self.model.specification.material_thickness_mm)
        self.assertEqual(shelf_nodes[0].x, self.model.specification.material_thickness_mm)
        self.assertEqual(shelf_nodes[0].z, self.spec.height_mm / 2.0)

    def test_scene_graph_builder_skips_back_panel_when_disabled_in_construction_model(self):
        from domain.base_cabinet_engineering_model import (
            BaseCabinetEngineeringModelBuilder,
        )
        from engine.cabinet import Cabinet
        from scene_graph.builder import SceneGraphBuilder

        spec = BaseCabinetSpecification(
            width_mm=800.0,
            height_mm=720.0,
            depth_mm=560.0,
            shelf_count=1,
            has_back_panel=False,
        )
        model = ConstructionResolver.resolve(spec)
        cabinet = Cabinet()
        cabinet.params.width = spec.width_mm
        cabinet.params.height = spec.height_mm
        cabinet.params.depth = spec.depth_mm
        cabinet.params.sec_count = 1
        cabinet.construction_model = model
        cabinet.engineering_model = BaseCabinetEngineeringModelBuilder.build(model)

        geo = SimpleNamespace(resolved_top=None, resolved_sections=[], is_buildable=True)
        mat = SimpleNamespace(mdf_thickness=18.0, back_thickness=3.0)

        graph = SceneGraphBuilder(cabinet, mat, cabinet_id="REF-CAB").build(geo)

        back_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "BACK_PANEL"
        ]

        self.assertEqual(len(back_nodes), 0)

    def test_construction_slice_does_not_import_freecad_or_manufacturing(self):
        import domain.construction_resolver as resolver_module

        source = inspect.getsource(resolver_module)
        tree = ast.parse(source)
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        lowered = {module.lower() for module in imported_modules}
        self.assertFalse(any("freecad" in module for module in lowered))
        self.assertFalse(any("manufacturing" in module for module in lowered))


if __name__ == "__main__":
    unittest.main()
