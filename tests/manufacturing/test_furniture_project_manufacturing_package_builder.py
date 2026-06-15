import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestFurnitureProjectManufacturingPackageBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.furniture_project_manufacturing_package_builder import (
            FurnitureProjectManufacturingPackageBuilder,
        )

        self.assertTrue(callable(FurnitureProjectManufacturingPackageBuilder().build))

    @patch(
        "manufacturing.furniture_project_manufacturing_package_builder."
        "ManufacturingPackageBuilder"
    )
    @patch(
        "manufacturing.furniture_project_manufacturing_package_builder."
        "ManufacturingRuntimePipelineBuilder"
    )
    def test_empty_project_builds_empty_manufacturing_package(
        self,
        runtime_builder_class,
        package_builder_class,
    ):
        from domain.furniture_project import FurnitureProject
        from manufacturing.furniture_project_manufacturing_package_builder import (
            FurnitureProjectManufacturingPackageBuilder,
        )

        expected_package = object()
        package_builder_class.return_value.build.return_value = expected_package

        result = FurnitureProjectManufacturingPackageBuilder().build(
            FurnitureProject()
        )

        runtime_builder_class.return_value.build.assert_not_called()
        package_builder_class.return_value.build.assert_called_once_with(
            panels=[],
            materials=[],
            machining_operations=[],
            edge_operations=[],
            warnings=[],
        )
        self.assertIs(result, expected_package)

    @patch(
        "manufacturing.furniture_project_manufacturing_package_builder."
        "ManufacturingPackageBuilder"
    )
    @patch(
        "manufacturing.furniture_project_manufacturing_package_builder."
        "ManufacturingRuntimePipelineBuilder"
    )
    def test_aggregates_runtime_manufacturing_packages_in_cabinet_order(
        self,
        runtime_builder_class,
        package_builder_class,
    ):
        from domain.furniture_project import FurnitureProject
        from manufacturing.furniture_project_manufacturing_package_builder import (
            FurnitureProjectManufacturingPackageBuilder,
        )

        first_graph = object()
        second_graph = object()
        first_cabinet = SimpleNamespace(graph=first_graph)
        second_cabinet = SimpleNamespace(graph=second_graph)
        first_package = self._package(
            panels=["panel-1"],
            materials=["material-1"],
            machining_operations=["machining-1"],
            edge_operations=["edge-1"],
            warnings=["warning-1"],
        )
        second_package = self._package(
            panels=["panel-2", "panel-3"],
            materials=["material-2"],
            machining_operations=["machining-2"],
            edge_operations=["edge-2", "edge-3"],
            warnings=["warning-2"],
        )
        runtime_builder_class.return_value.build.side_effect = [
            SimpleNamespace(manufacturing_package=first_package),
            SimpleNamespace(manufacturing_package=second_package),
        ]
        expected_package = object()
        package_builder_class.return_value.build.return_value = expected_package

        result = FurnitureProjectManufacturingPackageBuilder().build(
            FurnitureProject(cabinets=[first_cabinet, second_cabinet])
        )

        self.assertEqual(
            runtime_builder_class.return_value.build.call_args_list,
            [
                unittest.mock.call(first_graph),
                unittest.mock.call(second_graph),
            ],
        )
        package_builder_class.return_value.build.assert_called_once_with(
            panels=["panel-1", "panel-2", "panel-3"],
            materials=["material-1", "material-2"],
            machining_operations=["machining-1", "machining-2"],
            edge_operations=["edge-1", "edge-2", "edge-3"],
            warnings=["warning-1", "warning-2"],
        )
        self.assertIs(result, expected_package)

    @patch(
        "manufacturing.furniture_project_manufacturing_package_builder."
        "ManufacturingPackageBuilder"
    )
    @patch(
        "manufacturing.furniture_project_manufacturing_package_builder."
        "ManufacturingRuntimePipelineBuilder"
    )
    def test_builder_does_not_mutate_source_packages(
        self,
        runtime_builder_class,
        package_builder_class,
    ):
        from domain.furniture_project import FurnitureProject
        from manufacturing.furniture_project_manufacturing_package_builder import (
            FurnitureProjectManufacturingPackageBuilder,
        )

        source_package = self._package(
            panels=["panel"],
            materials=["material"],
            machining_operations=["machining"],
            edge_operations=["edge"],
            warnings=["warning"],
        )
        original_values = {
            key: list(value)
            for key, value in source_package.__dict__.items()
        }
        runtime_builder_class.return_value.build.return_value = SimpleNamespace(
            manufacturing_package=source_package
        )

        FurnitureProjectManufacturingPackageBuilder().build(
            FurnitureProject(cabinets=[SimpleNamespace(graph=object())])
        )

        self.assertEqual(source_package.__dict__, original_values)
        build_kwargs = package_builder_class.return_value.build.call_args.kwargs
        for field in original_values:
            self.assertIsNot(build_kwargs[field], getattr(source_package, field))

    @staticmethod
    def _package(
        panels,
        materials,
        machining_operations,
        edge_operations,
        warnings,
    ):
        from manufacturing.manufacturing_package import ManufacturingPackage

        return ManufacturingPackage(
            panels=panels,
            materials=materials,
            machining_operations=machining_operations,
            edge_operations=edge_operations,
            warnings=warnings,
        )


if __name__ == "__main__":
    unittest.main()
