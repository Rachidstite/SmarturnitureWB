import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from domain.base_cabinet_manufacturing_outputs_entry import (
    build_base_cabinet_manufacturing_outputs_entry,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.builders import WardrobeBuilder
from domain.core_types import NodeCategory
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, System32JoineryRule
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)
from shared.roles import NodeRole
from tests.domain.test_base_cabinet_manufacturing_outputs_entry_contract import (
    IntegrationCabinetBuilder,
)


class TestOperationIdentityRuntimeContract(unittest.TestCase):
    def test_base_cabinet_minifix_panel_identity_survives_into_cnc_rows(self):
        specification = BaseCabinetSpecification()

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=IntegrationCabinetBuilder,
        ):
            cabinet = engineering_entry_module.build_base_cabinet_engineering_cabinet(
                specification
            )

        runtime = ManufacturingRuntimePipelineBuilder().build(cabinet.graph)
        side_ids = {
            node.identity.key
            for node in cabinet.graph.all_nodes()
            if node.role == NodeRole.SIDE_PANEL
        }
        minifix_rows = [
            row
            for row in runtime.manufacturing_production_package.cnc_report.rows
            if row.source_operation_reference in {"FaceDrill", "EdgeDrill"}
        ]

        self.assertTrue(minifix_rows)
        self.assertTrue(
            all(row.panel_identity not in {"FaceDrill", "EdgeDrill", ""} for row in minifix_rows)
        )
        self.assertTrue(
            all(row.panel_identity in side_ids for row in minifix_rows)
        )

    def test_base_cabinet_hinge_identity_survives_through_report_cnc_and_assembly(self):
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

        hinge_items = [
            item
            for item in production_package.machining_report.items
            if item.get("hardware_intent") == "INTENT_HINGE"
        ]
        hinge_rows = [
            row
            for row in production_package.cnc_report.rows
            if "::hinge-" in row.source_operation_reference
        ]
        assembly_rows = [
            row
            for row in production_package.assembly_report.rows
            if row.hardware_required == "HINGE_BLUM_110_V1"
        ]

        self.assertTrue(hinge_items)
        self.assertTrue(hinge_rows)
        self.assertEqual(len(assembly_rows), 1)
        self.assertTrue(
            all(str(item.get("panel_identity", "")).endswith(("_DOOR-1", "_DOOR-2")) for item in hinge_items)
        )
        self.assertTrue(
            all(str(item.get("source_operation_reference", "")).startswith("CAB-") for item in hinge_items)
        )
        self.assertTrue(
            all(row.panel_identity.endswith(("_DOOR-1", "_DOOR-2")) for row in hinge_rows)
        )
        self.assertEqual(
            {
                required.source_operation_reference
                for required in assembly_rows[0].required_machining
            },
            set(assembly_rows[0].source_operation_references),
        )

    def test_confirmat_panel_identity_survives_runtime_pipeline_to_cnc_rows(self):
        project = WardrobeBuilder(
            uid="CONFIRMAT_IDENTITY_RUNTIME_CONTRACT",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )
        project.add_divider(x_offset=400.0)
        project = project.build()

        context = RuleContext()
        placements = [
            placement
            for placement in System32JoineryRule().apply(project, context)
            if placement.hardware_intent == "INTENT_CONFIRMAT_50"
        ]
        project.placements.extend(placements)
        ManufacturingCompiler().compile(project, context)

        runtime = ManufacturingRuntimePipelineBuilder().build(project.graph)
        physical_ids = {
            node.identity.key
            for node in project.graph.physical_nodes
            if node.category == NodeCategory.PHYSICAL
        }
        confirmat_rows = [
            row
            for row in runtime.manufacturing_production_package.cnc_report.rows
            if self._is_confirmat_row(row)
        ]

        self.assertTrue(confirmat_rows)
        self.assertTrue(
            all(row.panel_identity not in {"MachiningOperation", ""} for row in confirmat_rows)
        )
        self.assertTrue(
            all(row.panel_identity in physical_ids for row in confirmat_rows)
        )

    @staticmethod
    def _is_confirmat_row(row):
        return (
            row.operation_type == "DRILL"
            and (
                (
                    abs(float(row.diameter) - 7.0) < 0.1
                    and abs(float(row.depth) - 18.0) < 0.1
                )
                or (
                    abs(float(row.diameter) - 5.0) < 0.1
                    and abs(float(row.depth) - 34.0) < 0.1
                    and str(row.axis).upper() == "X"
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
