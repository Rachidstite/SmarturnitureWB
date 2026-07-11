import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
import domain.base_cabinet_manufacturing_outputs_entry as outputs_entry_module
from core.material_manager import MaterialManager
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
    build_base_cabinet_manufacturing_outputs_entry,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from engine.geometry_engine import GeometryEngine
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from scene_graph.builder import SceneGraphBuilder
from shared.identity import PanelIdentity


class FakeEngineeringCabinet:
    def __init__(self, scene_graph):
        self.graph = scene_graph


class IntegrationCabinetBuilder:
    def __init__(self):
        self.scene_graph = None

    def build(self, cabinet):
        material_manager = MaterialManager()
        geometry_engine = GeometryEngine(cabinet, material_manager)
        geometry_engine.resolve_all()
        self.scene_graph = SceneGraphBuilder(
            cabinet,
            material_manager,
        ).build(geometry_engine)
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class TestBaseCabinetManufacturingOutputsEntryContract(unittest.TestCase):
    def test_accepts_base_cabinet_specification(self):
        scene_graph = object()
        manufacturing_package = object()
        cut_list = object()

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ) as engineering_entry, patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type(
                "AdapterResult",
                (),
                {"metadata": {"door_count": 2}},
            )(),
        ) as adapt_spy:
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = cut_list

            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        engineering_entry.assert_called_once()
        runtime_builder_class.return_value.build.assert_called_once_with(scene_graph)
        cutlist_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        adapt_spy.assert_called_once()
        self.assertIsInstance(result, BaseCabinetManufacturingOutputsEntryResult)

    def test_uses_engineering_entry(self):
        scene_graph = object()
        manufacturing_package = object()

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ) as engineering_entry, patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type("AdapterResult", (), {"metadata": {}})(),
        ):
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = object()

            build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        engineering_entry.assert_called_once()
        runtime_builder_class.return_value.build.assert_called_once_with(scene_graph)

    def test_uses_manufacturing_runtime_pipeline_builder(self):
        scene_graph = object()
        manufacturing_package = object()

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type("AdapterResult", (), {"metadata": {}})(),
        ):
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = object()

            build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        runtime_builder_class.return_value.build.assert_called_once_with(scene_graph)

    def test_uses_manufacturing_cutlist_builder(self):
        scene_graph = object()
        manufacturing_package = object()
        cut_list = object()

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type("AdapterResult", (), {"metadata": {}})(),
        ):
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = cut_list

            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        cutlist_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        self.assertIs(result.cut_list, cut_list)

    def test_reference_cabinet_hinge_placements_host_on_resolved_side_panels_and_target_doors(self):
        captured = {}

        def _capture_compile(_compiler_self, project, context):
            captured["project"] = project
            captured["context"] = context

        specification = BaseCabinetSpecification()

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ), patch.object(
            outputs_entry_module.ManufacturingCompiler,
            "compile",
            new=_capture_compile,
        ):
            cabinet = engineering_entry_module.build_base_cabinet_engineering_cabinet(
                specification
            )
            outputs_entry_module._inject_base_cabinet_hinge_hardware(
                cabinet,
                cabinet.graph,
            )

        placements = [
            placement
            for placement in getattr(captured.get("project"), "placements", []) or []
            if getattr(placement, "hardware_intent", "") == "INTENT_HINGE"
        ]
        self.assertTrue(placements, "Expected resolved hinge placements for reference cabinet")

        cabinet_id = outputs_entry_module._resolve_cabinet_id(cabinet)
        for placement in placements:
            expected_host_node_id = PanelIdentity.make_side(
                cabinet_id,
                getattr(placement, "hinge_side", ""),
            ).key
            self.assertIsNotNone(
                cabinet.graph.get_node(expected_host_node_id),
                f"Expected authoritative side panel node to exist: {expected_host_node_id}",
            )
            self.assertNotEqual(
                placement.host_node_id,
                placement.target_node_id,
                "Hinge host and target topology must not collapse onto the door",
            )
            self.assertEqual(
                placement.host_node_id,
                expected_host_node_id,
                "Hinge host_node_id must resolve to the receiving cabinet side panel",
            )
            self.assertIn(
                "_DOOR-",
                str(getattr(placement, "target_node_id", "") or ""),
                "Hinge target_node_id must remain the door identity",
            )

    def test_reference_cabinet_hinge_placement_counts_follow_resolved_construction_doors_without_duplicates(self):
        captured = {}

        def _capture_compile(_compiler_self, project, context):
            captured["project"] = project
            captured["context"] = context

        specification = BaseCabinetSpecification()

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ), patch.object(
            outputs_entry_module.ManufacturingCompiler,
            "compile",
            new=_capture_compile,
        ):
            cabinet = engineering_entry_module.build_base_cabinet_engineering_cabinet(
                specification
            )
            outputs_entry_module._inject_base_cabinet_hinge_hardware(
                cabinet,
                cabinet.graph,
            )

        placements = [
            placement
            for placement in getattr(captured.get("project"), "placements", []) or []
            if getattr(placement, "hardware_intent", "") == "INTENT_HINGE"
        ]
        actual_by_target = {}
        for placement in placements:
            target_id = str(getattr(placement, "target_node_id", "") or "")
            actual_by_target[target_id] = actual_by_target.get(target_id, 0) + 1

        cabinet_id = outputs_entry_module._resolve_cabinet_id(cabinet)
        expected_by_target = {}
        for engineering_door, construction_door in zip(
            getattr(cabinet.engineering_model, "doors", ()) or (),
            getattr(cabinet.construction_model, "doors", ()) or (),
        ):
            door_id = PanelIdentity.make_door(
                cabinet_id,
                engineering_door.section_index,
                engineering_door.door_index,
            ).key
            expected_by_target[door_id] = int(
                getattr(construction_door, "hinge_count", 0) or 0
            )

        self.assertEqual(
            actual_by_target,
            expected_by_target,
            "Each resolved door must keep its hinge count without duplicate placements",
        )
        self.assertEqual(
            len(
                {
                    str(getattr(placement, "source_operation_reference", "") or "")
                    for placement in placements
                }
            ),
            len(placements),
            "Each hinge placement must keep a unique source_operation_reference",
        )

    def test_returns_cut_list(self):
        scene_graph = object()
        manufacturing_package = object()
        cut_list = object()

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type("AdapterResult", (), {"metadata": {}})(),
        ):
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = cut_list

            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        self.assertIs(result.cut_list, cut_list)

    def test_returns_manufacturing_package(self):
        scene_graph = object()
        manufacturing_package = object()

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type("AdapterResult", (), {"metadata": {}})(),
        ):
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = object()

            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        self.assertIs(result.manufacturing_package, manufacturing_package)

    def test_preserves_metadata(self):
        scene_graph = object()
        manufacturing_package = object()
        metadata = {
            "door_count": 3,
            "shelf_count": 2,
            "has_back_panel": False,
            "edge_banding_required": True,
            "toe_kick_required": True,
            "hinge_family": "STANDARD_110",
            "drawer_family": "DRAWER_CUSTOM",
        }

        with patch.object(
            outputs_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            outputs_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            outputs_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class, patch.object(
            outputs_entry_module.BaseCabinetSpecificationAdapter,
            "adapt",
            return_value=type("AdapterResult", (), {"metadata": metadata})(),
        ):
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = object()

            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )

        self.assertEqual(result.metadata, metadata)
        self.assertIsNot(result.metadata, metadata)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(outputs_entry_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_new_engine_builder_runtime_added(self):
        source = inspect.getsource(outputs_entry_module)
        self.assertIn("build_base_cabinet_engineering_cabinet", source)
        self.assertIn("ManufacturingRuntimePipelineBuilder", source)
        self.assertIn("ManufacturingCutlistBuilder", source)
        self.assertNotIn("ManufacturingPackageBuilder", source)
        self.assertNotIn("ManufacturingRuntimeBuilder", source)
        self.assertNotIn("ManufacturingCutlistEngine", source)

    def test_default_two_door_cabinet_preserves_hinges_into_hardware_bom(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ):
            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification()
            )
            production_package = ManufacturingProductionPackageBuilder().build(
                result.manufacturing_package
            )

        hinge_rows = [
            row
            for row in production_package.hardware_report.bom_rows
            if row.hardware_sku == "HINGE_BLUM_110_V1"
        ]
        assembly_rows = [
            row
            for row in production_package.assembly_report.rows
            if row.hardware_required == "HINGE_BLUM_110_V1"
        ]
        self.assertEqual(len(hinge_rows), 1)
        self.assertEqual(len(assembly_rows), 1)
        self.assertEqual(hinge_rows[0].quantity, 4)
        self.assertEqual(len(hinge_rows[0].component_reference), 2)
        self.assertEqual(len(hinge_rows[0].source_operation_references), 4)
        self.assertEqual(assembly_rows[0].hardware_quantity, 4)
        self.assertTrue(assembly_rows[0].required_machining)
        self.assertNotIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            production_package.warnings,
        )

    def test_zero_door_cabinet_emits_no_hinge_hardware(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ):
            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification(door_count=0)
            )
            production_package = ManufacturingProductionPackageBuilder().build(
                result.manufacturing_package
            )

        self.assertEqual(
            [
                row
                for row in production_package.hardware_report.bom_rows
                if "HINGE" in row.hardware_sku
            ],
            [],
        )
        self.assertNotIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            production_package.warnings,
        )

    def test_single_door_quantity_matches_resolved_hinge_count(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ):
            result = build_base_cabinet_manufacturing_outputs_entry(
                BaseCabinetSpecification(door_count=1)
            )
            production_package = ManufacturingProductionPackageBuilder().build(
                result.manufacturing_package
            )

        hinge_rows = [
            row
            for row in production_package.hardware_report.bom_rows
            if row.hardware_sku == "HINGE_BLUM_110_V1"
        ]
        self.assertEqual(len(hinge_rows), 1)
        self.assertEqual(hinge_rows[0].quantity, 2)
        self.assertEqual(len(hinge_rows[0].component_reference), 1)

    def test_taller_supported_cabinet_increases_hinge_bom_quantity_from_resolved_count(self):
        tall_specification = BaseCabinetSpecification(
            height_mm=1100.0,
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            toe_kick_required=True,
        )

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ):
            result = build_base_cabinet_manufacturing_outputs_entry(
                tall_specification
            )
            production_package = ManufacturingProductionPackageBuilder().build(
                result.manufacturing_package
            )
            construction_model = engineering_entry_module.build_base_cabinet_engineering_cabinet(
                tall_specification
            ).construction_model

        resolved_hinge_count = sum(
            door.hinge_count for door in construction_model.doors
        )
        hinge_rows = [
            row
            for row in production_package.hardware_report.bom_rows
            if row.hardware_sku == "HINGE_BLUM_110_V1"
        ]
        self.assertGreater(resolved_hinge_count, 4)
        self.assertEqual(len(hinge_rows), 1)
        self.assertEqual(hinge_rows[0].quantity, resolved_hinge_count)


if __name__ == "__main__":
    unittest.main()
