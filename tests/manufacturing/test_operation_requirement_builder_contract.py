import inspect
import unittest

import manufacturing.operation_requirement_builder as operation_requirement_builder_module
from manufacturing.operation_requirement import (
    ManufacturingOperationRequirement,
    validate_operation_requirement_contract,
)
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)
from manufacturing.operation_vocabulary import OperationId


class TestOperationRequirementBuilderContract(unittest.TestCase):
    def setUp(self):
        self.builder = ManufacturingOperationRequirementBuilder()

    def test_panel_with_edge_band_returns_edge_band_requirement(self):
        requirements = self.builder.build_for_panel("panel-1", needs_edge_band=True)
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].operation_id, OperationId.EDGE_BAND)

    def test_panel_with_assembly_holes_returns_drill_assembly_holes_requirement(self):
        requirements = self.builder.build_for_panel(
            "panel-2", needs_assembly_holes=True
        )
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].operation_id, OperationId.DRILL_ASSEMBLY_HOLES)

    def test_door_with_hinges_returns_hinge_requirements(self):
        requirements = self.builder.build_for_door("door-1", needs_hinges=True)
        self.assertEqual(
            [requirement.operation_id for requirement in requirements],
            [
                OperationId.EDGE_BAND,
                OperationId.DRILL_HINGE_CUP,
                OperationId.DRILL_HINGE_SCREW_HOLES,
                OperationId.INSTALL_HINGE,
            ],
        )

    def test_door_with_handle_returns_handle_requirements(self):
        requirements = self.builder.build_for_door(
            "door-2", needs_hinges=False, needs_handle=True
        )
        self.assertEqual(
            [requirement.operation_id for requirement in requirements],
            [
                OperationId.EDGE_BAND,
                OperationId.DRILL_HANDLE_HOLES,
                OperationId.INSTALL_HANDLE,
            ],
        )

    def test_drawer_with_slide_returns_slide_requirements(self):
        requirements = self.builder.build_for_drawer("drawer-1", needs_slide=True)
        self.assertEqual(
            [requirement.operation_id for requirement in requirements],
            [
                OperationId.DRILL_DRAWER_SLIDE_HOLES,
                OperationId.INSTALL_DRAWER_SLIDE,
                OperationId.INSTALL_DRAWER_FRONT,
            ],
        )

    def test_drawer_with_front_returns_install_drawer_front_requirement(self):
        requirements = self.builder.build_for_drawer(
            "drawer-2", needs_slide=False, needs_front=True
        )
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].operation_id, OperationId.INSTALL_DRAWER_FRONT)

    def test_all_requirement_ids_are_deterministic(self):
        requirements = (
            self.builder.build_for_panel("panel-3", needs_edge_band=True, needs_assembly_holes=True)
            + self.builder.build_for_door("door-3", needs_edge_band=True, needs_hinges=True, needs_handle=True)
            + self.builder.build_for_drawer("drawer-3", needs_slide=True, needs_front=True)
        )
        for requirement in requirements:
            expected_id = f"{requirement.target_id}::{requirement.operation_id.value}"
            self.assertEqual(requirement.requirement_id, expected_id)

    def test_builder_returns_tuple(self):
        self.assertIsInstance(self.builder.build_for_panel("panel-4"), tuple)
        self.assertIsInstance(self.builder.build_for_door("door-4"), tuple)
        self.assertIsInstance(self.builder.build_for_drawer("drawer-4"), tuple)

    def test_all_returned_requirements_pass_validation(self):
        requirements = (
            self.builder.build_for_panel("panel-5", needs_edge_band=True, needs_assembly_holes=True)
            + self.builder.build_for_door("door-5", needs_edge_band=True, needs_hinges=True, needs_handle=True)
            + self.builder.build_for_drawer("drawer-5", needs_slide=True, needs_front=True)
        )
        for requirement in requirements:
            self.assertIsInstance(requirement, ManufacturingOperationRequirement)
            validate_operation_requirement_contract(requirement)

    def test_builder_does_not_create_dependency_graph_order_job_runtime_fields(self):
        field_names = set(vars(ManufacturingOperationRequirementBuilder))
        for forbidden in (
            "dependency_graph",
            "order",
            "job",
            "runtime",
            "queue",
            "machine",
        ):
            self.assertNotIn(forbidden, field_names)

    def test_no_import_from_freecad(self):
        source = inspect.getsource(operation_requirement_builder_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_import_from_production_package(self):
        source = inspect.getsource(operation_requirement_builder_module)
        self.assertNotIn("ProductionPackage", source)
        self.assertNotIn("ManufacturingProductionPackage", source)


if __name__ == "__main__":
    unittest.main()
