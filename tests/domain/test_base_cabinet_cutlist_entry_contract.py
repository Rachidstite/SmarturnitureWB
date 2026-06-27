import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_cutlist_entry as cutlist_entry_module
from domain.base_cabinet_cutlist_entry import build_base_cabinet_cutlist
from domain.base_cabinet_specification import BaseCabinetSpecification
from manufacturing.manufacturing_cutlist_report import ManufacturingCutlistReport


class FakeEngineeringCabinet:
    def __init__(self, scene_graph):
        self.graph = scene_graph


class TestBaseCabinetCutlistEntryContract(unittest.TestCase):
    def test_accepts_base_cabinet_specification(self):
        scene_graph = object()
        manufacturing_package = object()
        report = ManufacturingCutlistReport(items=[{"identity": "P1"}], total_items=1)

        with patch.object(
            cutlist_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ) as engineering_entry, patch.object(
            cutlist_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            cutlist_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class:
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = report

            result = build_base_cabinet_cutlist(BaseCabinetSpecification())

        engineering_entry.assert_called_once()
        runtime_builder_class.return_value.build.assert_called_once_with(scene_graph)
        cutlist_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        self.assertIs(result, report)

    def test_uses_engineering_entry_and_scene_graph(self):
        scene_graph = object()
        manufacturing_package = object()

        with patch.object(
            cutlist_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ) as engineering_entry, patch.object(
            cutlist_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            cutlist_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class:
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = object()

            build_base_cabinet_cutlist(BaseCabinetSpecification())

        engineering_entry.assert_called_once()
        runtime_builder_class.return_value.build.assert_called_once_with(scene_graph)

    def test_delegates_to_manufacturing_runtime_pipeline_builder(self):
        scene_graph = object()
        manufacturing_package = object()

        with patch.object(
            cutlist_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            cutlist_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            cutlist_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class:
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = object()

            build_base_cabinet_cutlist(BaseCabinetSpecification())

        runtime_builder_class.return_value.build.assert_called_once_with(scene_graph)

    def test_delegates_to_manufacturing_cutlist_builder(self):
        scene_graph = object()
        manufacturing_package = object()
        report = ManufacturingCutlistReport(items=[], total_items=0)

        with patch.object(
            cutlist_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            cutlist_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            cutlist_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class:
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = report

            result = build_base_cabinet_cutlist(BaseCabinetSpecification())

        cutlist_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        self.assertIs(result, report)

    def test_returns_existing_cut_list_type(self):
        scene_graph = object()
        manufacturing_package = object()
        report = ManufacturingCutlistReport(items=[], total_items=0)

        with patch.object(
            cutlist_entry_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=FakeEngineeringCabinet(scene_graph),
        ), patch.object(
            cutlist_entry_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_class, patch.object(
            cutlist_entry_module,
            "ManufacturingCutlistBuilder",
        ) as cutlist_builder_class:
            runtime_builder_class.return_value.build.return_value = (
                type("RuntimeResult", (), {"manufacturing_package": manufacturing_package})()
            )
            cutlist_builder_class.return_value.build.return_value = report

            result = build_base_cabinet_cutlist(BaseCabinetSpecification())

        self.assertIsInstance(result, ManufacturingCutlistReport)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(cutlist_entry_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_runtime_duplication(self):
        source = inspect.getsource(cutlist_entry_module)
        self.assertIn("build_base_cabinet_engineering_cabinet", source)
        self.assertIn("ManufacturingRuntimePipelineBuilder", source)
        self.assertIn("ManufacturingCutlistBuilder", source)
        self.assertNotIn("ManufacturingPackageBuilder", source)


if __name__ == "__main__":
    unittest.main()
