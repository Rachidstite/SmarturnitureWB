import unittest

from domain.builders import WardrobeBuilder
from domain.hardware_library import HardwareRegistry
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, ShelfSupportRule
from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class TestShelfPinRuntimePackageContract(unittest.TestCase):

    def test_shelf_pin_drilling_survives_into_runtime_manufacturing_package(self):
        project = WardrobeBuilder(
            uid="SHELF_PIN_RUNTIME_PACKAGE_CONTRACT",
            width=800.0,
            height=2000.0,
            depth=580.0,
        )
        project.add_shelves(count=1, section_id="ROOT")
        project = project.build()

        context = RuleContext()
        registry = HardwareRegistry()
        hardware = registry.get_hardware("SHELF_PIN_5MM")

        self.assertIsNotNone(hardware)
        self.assertTrue(hardware.host_holes or hardware.target_holes)

        project.placements.extend(ShelfSupportRule().apply(project, context))
        self.assertTrue(project.placements)
        self.assertTrue(
            any(
                placement.hardware_intent == "INTENT_SHELF_PIN"
                for placement in project.placements
            )
        )

        ManufacturingCompiler().compile(project, context)

        source_ops = self._shelf_pin_ops_from_nodes(project)
        self.assertTrue(source_ops)

        panel_specs = ManufacturingExtractor.extract(project.graph)
        extracted_ops = [
            op
            for spec in panel_specs
            for op in spec.cnc_operations
            if self._is_shelf_pin_drill(op)
        ]
        self.assertTrue(extracted_ops)
        self.assertEqual(
            self._operation_signatures(extracted_ops),
            self._operation_signatures(source_ops),
        )

        runtime = ManufacturingRuntimePipelineBuilder().build(project.graph)
        runtime_ops = [
            op
            for op in runtime.manufacturing_package.machining_operations
            if self._is_shelf_pin_runtime_operation(op)
        ]

        self.assertTrue(runtime_ops)
        self.assertEqual(
            self._operation_signatures(runtime_ops),
            self._operation_signatures(source_ops),
        )

    @staticmethod
    def _shelf_pin_ops_from_nodes(project):
        return [
            op
            for node in project.graph.physical_nodes
            for op in getattr(node, "machining_ops", [])
            if TestShelfPinRuntimePackageContract._is_shelf_pin_drill(op)
        ]

    @staticmethod
    def _is_shelf_pin_drill(operation):
        if getattr(operation, "op_type", "") != "DRILL":
            return False

        return (
            abs(float(getattr(operation, "diameter", 0.0)) - 5.0) < 0.1
            and abs(float(getattr(operation, "depth", 0.0)) - 12.0) < 0.1
            and str(getattr(operation, "face", "")).split(".")[-1] == "LEFT"
        )

    @staticmethod
    def _is_shelf_pin_runtime_operation(operation):
        if getattr(operation, "operation_type", "") != "DRILL":
            return False

        return (
            abs(float(getattr(operation, "diameter", 0.0)) - 5.0) < 0.1
            and abs(float(getattr(operation, "depth", 0.0)) - 12.0) < 0.1
            and str(getattr(operation, "face", "")).split(".")[-1] == "LEFT"
        )

    @staticmethod
    def _operation_signatures(operations):
        return sorted(
            {
                (
                    getattr(operation, "operation_type", getattr(operation, "op_type", "")),
                    round(float(getattr(operation, "diameter", 0.0)), 3),
                    round(float(getattr(operation, "depth", 0.0)), 3),
                    str(getattr(operation, "face", "")).split(".")[-1],
                    round(
                        float(
                            getattr(
                                operation,
                                "x",
                                getattr(operation, "local_x", 0.0),
                            )
                        ),
                        3,
                    ),
                    round(
                        float(
                            getattr(
                                operation,
                                "y",
                                getattr(operation, "local_y", 0.0),
                            )
                        ),
                        3,
                    ),
                    str(getattr(operation, "axis", "Z")).upper(),
                )
                for operation in operations
            }
        )


if __name__ == "__main__":
    unittest.main()
