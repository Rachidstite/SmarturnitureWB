import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from domain.hardware_library import HardwareRegistry
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
        hardware_rows = [
            row
            for row in production_package.hardware_report.bom_rows
            if row.hardware_sku == "HINGE_BLUM_110_V1"
        ]
        door_ids = {
            str(getattr(node, "identity", "") or "")
            for node in result.manufacturing_package.panels
            if node.role == NodeRole.DOOR_PANEL
        }
        side_ids = {
            str(getattr(node, "identity", "") or "")
            for node in result.manufacturing_package.panels
            if node.role == NodeRole.SIDE_PANEL
        }
        fallback_identities = {"FaceDrill", "EdgeDrill", "MachiningOperation", ""}
        hinge_source_references = {
            str(item.get("source_operation_reference", "") or "")
            for item in hinge_items
        }
        door_hinge_items = [
            item
            for item in hinge_items
            if str(item.get("panel_identity", "") or "") in door_ids
        ]
        host_hinge_items = [
            item
            for item in hinge_items
            if str(item.get("panel_identity", "") or "") in side_ids
        ]
        door_hinge_rows = [
            row for row in hinge_rows if str(getattr(row, "panel_identity", "") or "") in door_ids
        ]
        host_hinge_rows = [
            row for row in hinge_rows if str(getattr(row, "panel_identity", "") or "") in side_ids
        ]

        self.assertTrue(hinge_items)
        self.assertTrue(hinge_rows)
        self.assertEqual(len(assembly_rows), 1)
        self.assertEqual(len(hardware_rows), 1)
        self.assertTrue(
            hinge_source_references
        )
        self.assertTrue(
            all(reference.startswith("CAB-") for reference in hinge_source_references)
        )
        self.assertTrue(
            all(
                str(item.get("panel_identity", "") or "").strip()
                not in fallback_identities
                for item in hinge_items
            )
        )
        self.assertTrue(
            all(
                str(getattr(row, "panel_identity", "") or "").strip()
                not in fallback_identities
                for row in hinge_rows
            )
        )
        self.assertTrue(door_hinge_items)
        self.assertTrue(host_hinge_items)
        self.assertTrue(door_hinge_rows)
        self.assertTrue(host_hinge_rows)
        self.assertEqual(
            {str(item.get("source_operation_reference", "") or "") for item in door_hinge_items},
            hinge_source_references,
        )
        self.assertEqual(
            {str(item.get("source_operation_reference", "") or "") for item in host_hinge_items},
            hinge_source_references,
        )
        self.assertEqual(
            {str(getattr(row, "source_operation_reference", "") or "") for row in door_hinge_rows},
            hinge_source_references,
        )
        self.assertEqual(
            {str(getattr(row, "source_operation_reference", "") or "") for row in host_hinge_rows},
            hinge_source_references,
        )
        self.assertTrue(
            all(
                str(getattr(row, "operation_type", "") or "") == "DRILL"
                and float(getattr(row, "diameter", 0.0) or 0.0) in {2.5, 5.0, 35.0}
                and float(getattr(row, "depth", 0.0) or 0.0) in {10.0, 12.0, 12.5}
                for row in hinge_rows
            )
        )
        self.assertTrue(
            any(
                float(getattr(row, "diameter", 0.0) or 0.0) == 35.0
                for row in door_hinge_rows
            ),
            "Door-side hinge cup rows must remain on door identities",
        )
        self.assertTrue(
            any(
                float(getattr(row, "diameter", 0.0) or 0.0) == 2.5
                for row in door_hinge_rows
            ),
            "Door-side hinge pilot rows must remain on door identities",
        )
        self.assertTrue(
            all(
                float(getattr(row, "diameter", 0.0) or 0.0) == 5.0
                and float(getattr(row, "depth", 0.0) or 0.0) == 12.0
                for row in host_hinge_rows
            ),
            "Host-side hinge rows must match authoritative host-hole geometry",
        )
        self.assertEqual(
            int(getattr(hardware_rows[0], "quantity", 0) or 0),
            4,
        )
        self.assertEqual(
            {
                required.source_operation_reference
                for required in assembly_rows[0].required_machining
            },
            set(assembly_rows[0].source_operation_references),
        )
        self.assertEqual(
            set(assembly_rows[0].source_operation_references),
            hinge_source_references,
        )
        self.assertTrue(
            any(
                str(getattr(required, "panel_identity", "") or "") in door_ids
                for required in assembly_rows[0].required_machining
            )
        )
        self.assertTrue(
            any(
                str(getattr(required, "panel_identity", "") or "") in side_ids
                for required in assembly_rows[0].required_machining
            )
        )

    def test_base_cabinet_hinge_runtime_distributes_machining_across_door_and_side_panel_identities(self):
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

        cnc_rows = list(
            getattr(getattr(production_package, "cnc_report", None), "rows", ()) or ()
        )
        door_ids = {
            str(getattr(node, "identity", "") or "")
            for node in result.manufacturing_package.panels
            if node.role == NodeRole.DOOR_PANEL
        }
        side_ids = {
            str(getattr(node, "identity", "") or "")
            for node in result.manufacturing_package.panels
            if node.role == NodeRole.SIDE_PANEL
        }
        hinge_rows = [
            row
            for row in cnc_rows
            if "::hinge-" in str(getattr(row, "source_operation_reference", "") or "")
        ]

        self.assertTrue(hinge_rows)
        self.assertTrue(
            any(row.panel_identity in door_ids for row in hinge_rows),
            "Door-side hinge machining must remain on door panel identities",
        )
        self.assertTrue(
            any(row.panel_identity in side_ids for row in hinge_rows),
            "Host-side hinge machining must appear on cabinet side-panel identities",
        )
        self.assertTrue(
            all(
                str(getattr(row, "panel_identity", "") or "").strip()
                not in {"FaceDrill", "EdgeDrill", "MachiningOperation", ""}
                for row in hinge_rows
            ),
            "Hinge CNC rows must not fall back to generic operation identities",
        )

    def test_base_cabinet_hinge_host_side_rows_match_authoritative_hardware_spec_hole_dimensions(self):
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

        side_ids = {
            str(getattr(node, "identity", "") or "")
            for node in result.manufacturing_package.panels
            if node.role == NodeRole.SIDE_PANEL
        }
        hinge_rows = [
            row
            for row in getattr(production_package.cnc_report, "rows", ()) or ()
            if "::hinge-" in str(getattr(row, "source_operation_reference", "") or "")
            and str(getattr(row, "panel_identity", "") or "") in side_ids
        ]
        hardware = HardwareRegistry().get_hardware("HINGE_BLUM_110_V1")
        expected_host_holes = {
            (
                float(getattr(hole, "diameter", 0.0) or 0.0),
                float(getattr(hole, "depth", 0.0) or 0.0),
            )
            for hole in getattr(hardware, "host_holes", ()) or ()
        }

        self.assertTrue(hinge_rows, "Expected cabinet-side hinge host-hole CNC rows")
        self.assertEqual(
            {
                (
                    float(getattr(row, "diameter", 0.0) or 0.0),
                    float(getattr(row, "depth", 0.0) or 0.0),
                )
                for row in hinge_rows
            },
            expected_host_holes,
            "Cabinet-side hinge rows must match authoritative host_holes from HardwareSpec",
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
