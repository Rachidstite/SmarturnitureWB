import unittest
from types import SimpleNamespace


class TestBackPanelGrooveEmissionContract(unittest.TestCase):

    def test_missing_back_panel_validation_warning_remains_unchanged(self):
        from domain.builders import SceneGraph
        from domain.constraint_engine import CabinetConstraintValidator
        from domain.diagnostics import Severity

        project = SimpleNamespace(graph=SceneGraph())

        report = CabinetConstraintValidator(project).validate_all()
        violations = [
            violation
            for violation in report.violations
            if violation.code == "MISSING_BACK_PANEL"
        ]

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].severity, Severity.WARNING)
        self.assertIn("Cabinet has no back panel", violations[0].message)

    def test_existing_production_engine_serializes_groove_operations(self):
        from domain.manufacturing_ops import Groove
        from exports.production_engine import ProductionEngine

        scene_graph = SimpleNamespace(
            physical_nodes=[
                SimpleNamespace(
                    identity=SimpleNamespace(key="BACK_PANEL_TEST"),
                    material="HDF_3MM",
                    thickness=3.0,
                    width=1982.0,
                    height=2182.0,
                    manufacturing_ops=[
                        Groove(
                            start_x=10.0,
                            start_y=20.0,
                            width=4.0,
                            depth=8.0,
                            length=1982.0,
                            face="BACK",
                        )
                    ],
                )
            ]
        )

        cnc_data = ProductionEngine.generate_cnc_data(scene_graph)

        self.assertIn("BACK_PANEL_TEST", cnc_data)
        self.assertEqual(len(cnc_data["BACK_PANEL_TEST"].grooves), 1)
        self.assertEqual(cnc_data["BACK_PANEL_TEST"].grooves[0].face, "BACK")
        self.assertEqual(cnc_data["BACK_PANEL_TEST"].grooves[0].depth, 8.0)

    def test_future_runtime_pipeline_emits_back_panel_groove_operation(self):
        from domain.builders import WardrobeBuilder
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )

        project = WardrobeBuilder(
            "GROOVE_RUNTIME_V1",
            width=1600.0,
            height=2200.0,
            depth=600.0,
        ).build()

        runtime_result = ManufacturingRuntimePipelineBuilder().build(
            project.graph
        )

        groove_operations = [
            operation
            for operation in runtime_result.manufacturing_package.machining_operations
            if getattr(operation, "operation_type", "") == "GROOVE"
        ]

        self.assertTrue(groove_operations)

    @unittest.expectedFailure
    def test_future_groove_adapter_preserves_back_panel_metadata(self):
        from manufacturing.manufacturing_operation_adapter import (
            ManufacturingOperationAdapter,
        )

        back_panel_groove = SimpleNamespace(
            operation_type="GROOVE",
            target_panel_reference="BACK_PANEL",
            width=4.0,
            depth=8.0,
            length=1982.0,
            start_x=10.0,
            start_y=20.0,
            z=3.0,
            face="BACK",
        )

        unified = ManufacturingOperationAdapter.to_unified(back_panel_groove)

        self.assertEqual(unified.operation_type, "GROOVE")
        self.assertEqual(
            unified.metadata["target_panel_reference"],
            "BACK_PANEL",
        )
        self.assertEqual(unified.metadata["width"], 4.0)
        self.assertEqual(unified.metadata["depth"], 8.0)
        self.assertEqual(unified.metadata["length"], 1982.0)
        self.assertEqual(unified.x, 10.0)
        self.assertEqual(unified.y, 20.0)
        self.assertEqual(unified.z, 3.0)

    @unittest.expectedFailure
    def test_future_runtime_pipeline_cnc_export_includes_back_panel_groove(self):
        from domain.builders import WardrobeBuilder
        from exports.production_engine import ProductionEngine
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )

        project = WardrobeBuilder(
            "GROOVE_EXPORT_V1",
            width=1600.0,
            height=2200.0,
            depth=600.0,
        ).build()

        ManufacturingRuntimePipelineBuilder().build(project.graph)
        cnc_data = ProductionEngine.generate_cnc_data(project.graph)

        self.assertTrue(
            any(program.grooves for program in cnc_data.values())
        )


if __name__ == "__main__":
    unittest.main()
