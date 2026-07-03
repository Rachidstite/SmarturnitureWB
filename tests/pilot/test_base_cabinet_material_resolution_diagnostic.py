import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from tests.pilot.test_base_cabinet_real_manufacturing_scenario import (
    _IntegrationCabinetBuilder,
    TestBaseCabinetRealManufacturingScenario,
)


class TestBaseCabinetMaterialResolutionDiagnostic(unittest.TestCase):
    def test_material_exists_in_engineering_but_is_not_transferred_to_manufacturing(self):
        specification = TestBaseCabinetRealManufacturingScenario()._specification()

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            product_result = build_base_cabinet_product_workflow(specification)
            manufacturing_result = ManufacturingApplicationService().execute(
                specification=specification
            )

        engineering_model = product_result.engineering.engineering_model
        self.assertTrue(engineering_model.left_side_panel.material)
        self.assertTrue(engineering_model.right_side_panel.material)
        self.assertTrue(engineering_model.top_panel.material)
        self.assertTrue(engineering_model.bottom_panel.material)
        self.assertTrue(engineering_model.back_panel.material)

        scene_graph = product_result.engineering.scene_graph
        self.assertTrue(
            all(
                getattr(node, "material", "")
                for node in scene_graph.all_nodes()
            )
        )

        manufacturing_package = manufacturing_result.data["manufacturing_package"]
        self.assertGreater(len(manufacturing_package.materials), 0)
        self.assertEqual(
            [material.name for material in manufacturing_package.materials],
            ["MDF_MR_18MM", "HDF_3MM"],
        )
        self.assertTrue(manufacturing_package.machining_operations)
        self.assertTrue(
            any(
                getattr(operation, "metadata", {}).get("hardware_intent")
                == "INTENT_MINIFIX_15"
                for operation in manufacturing_package.machining_operations
            ),
            "Base cabinet runtime machining ops should preserve hardware identity.",
        )
        self.assertNotIn(
            "No materials",
            manufacturing_result.data["manufacturing_decision"].warning_reasons,
        )

        production_package = manufacturing_result.data[
            "manufacturing_production_package"
        ]
        self.assertTrue(production_package.has_hardware_evidence)
        self.assertGreater(
            len(getattr(production_package.hardware_report, "bom_rows", []) or []),
            0,
        )
        self.assertGreater(
            len(getattr(production_package.assembly_report, "rows", []) or []),
            0,
        )

        # Material is still missing from the runtime package, but hardware
        # identity now survives the manufacturing pipeline and drives BOM/assembly.


if __name__ == "__main__":
    unittest.main()
