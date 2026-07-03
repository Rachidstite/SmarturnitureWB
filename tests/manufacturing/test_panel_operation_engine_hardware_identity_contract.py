import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)
from manufacturing.panel_operation_engine import PanelOperationEngine
from tests.pilot.test_base_cabinet_real_manufacturing_scenario import (
    _IntegrationCabinetBuilder,
    TestBaseCabinetRealManufacturingScenario,
)


class TestPanelOperationEngineHardwareIdentityContract(unittest.TestCase):
    def test_base_cabinet_minifix_identity_survives_into_runtime_bom(self):
        specification = TestBaseCabinetRealManufacturingScenario()._specification()

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            product_result = build_base_cabinet_product_workflow(specification)

        scene_graph = product_result.engineering.scene_graph
        panel_ops = PanelOperationEngine.generate(scene_graph)
        minifix_ops = [
            op
            for operations in panel_ops.values()
            for op in operations
            if getattr(op, "metadata", {}).get("hardware_intent")
            == "INTENT_MINIFIX_15"
        ]

        self.assertTrue(minifix_ops)
        self.assertTrue(
            all(getattr(op, "metadata", {}).get("hardware_family") == "MINIFIX" for op in minifix_ops)
        )
        self.assertTrue(
            all(getattr(op, "metadata", {}).get("hardware_sku") == "MINIFIX_15_V1" for op in minifix_ops)
        )

        runtime = ManufacturingRuntimePipelineBuilder().build(scene_graph)
        production_package = runtime.manufacturing_production_package

        self.assertTrue(production_package.has_hardware_evidence)
        self.assertGreater(len(getattr(production_package.hardware_report, "bom_rows", []) or []), 0)
        self.assertGreater(len(getattr(production_package.assembly_report, "rows", []) or []), 0)


if __name__ == "__main__":
    unittest.main()
