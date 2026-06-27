import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_manufacturing_outputs_entry as outputs_entry_module
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
    build_base_cabinet_manufacturing_outputs_entry,
)
from domain.base_cabinet_specification import BaseCabinetSpecification


class FakeEngineeringCabinet:
    def __init__(self, scene_graph):
        self.graph = scene_graph


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


if __name__ == "__main__":
    unittest.main()
