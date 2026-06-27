import inspect
import unittest

import manufacturing.operation_instantiator as operation_instantiator_module
from manufacturing.operation_instance import validate_operation_instance_contract
from manufacturing.operation_instantiator import ManufacturingOperationInstantiator
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)
from manufacturing.operation_realizer import ManufacturingOperationRealizer
from manufacturing.operation_vocabulary import OperationId


class TestOperationInstantiatorContract(unittest.TestCase):
    def setUp(self):
        self.requirement_builder = ManufacturingOperationRequirementBuilder()
        self.realizer = ManufacturingOperationRealizer()
        self.instantiator = ManufacturingOperationInstantiator()

    def test_instantiate_edge_band_operation_into_edge_instances(self):
        requirement = self.requirement_builder.build_for_panel("panel-1", needs_edge_band=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        instances = self.instantiator.instantiate(
            operation,
            ("TOP", "BOTTOM"),
            ("geometry-top", "geometry-bottom"),
            ("top-face", "bottom-face"),
        )
        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0].instance_label, "TOP")
        self.assertEqual(instances[1].instance_label, "BOTTOM")
        self.assertEqual(instances[0].operation_id, OperationId.EDGE_BAND)

    def test_instantiate_install_hinge_operation_into_hinge_instances(self):
        requirement = self.requirement_builder.build_for_door("door-1", needs_hinges=True)[3]
        operation = self.realizer.realize((requirement,))[0]
        instances = self.instantiator.instantiate(
            operation,
            ("HINGE_1", "HINGE_2"),
            ("hinge-1", "hinge-2"),
            ("left", "right"),
        )
        self.assertEqual([instance.instance_label for instance in instances], ["HINGE_1", "HINGE_2"])
        self.assertEqual(instances[0].operation_id, OperationId.INSTALL_HINGE)

    def test_deterministic_instance_item_id(self):
        requirement = self.requirement_builder.build_for_panel("panel-2", needs_assembly_holes=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        instance = self.instantiator.instantiate(operation, ("A",), ("geometry-a",), ("face-a",))[0]
        self.assertEqual(instance.operation_instance_item_id, f"{operation.operation_instance_id}::A")

    def test_geometry_ref_is_stored_as_reference_only(self):
        requirement = self.requirement_builder.build_for_drawer(
            "drawer-1", needs_slide=False, needs_front=True
        )[0]
        operation = self.realizer.realize((requirement,))[0]
        instance = self.instantiator.instantiate(operation, ("SLIDE",), ("geometry-ref-1",), ("side",))[0]
        self.assertEqual(instance.geometry_ref, "geometry-ref-1")

    def test_face_is_stored_as_semantic_label_only(self):
        requirement = self.requirement_builder.build_for_drawer("drawer-2", needs_slide=False, needs_front=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        instance = self.instantiator.instantiate(operation, ("FRONT",), ("geometry-ref-2",), ("front-face",))[0]
        self.assertEqual(instance.face, "front-face")

    def test_returns_tuple(self):
        requirement = self.requirement_builder.build_for_panel("panel-3", needs_edge_band=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        instances = self.instantiator.instantiate(operation, ("TOP",), ("geometry-top",), ("top",))
        self.assertIsInstance(instances, tuple)

    def test_rejects_geometry_refs_length_mismatch(self):
        requirement = self.requirement_builder.build_for_panel("panel-4", needs_edge_band=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        with self.assertRaises(ValueError):
            self.instantiator.instantiate(operation, ("TOP", "BOTTOM"), ("geometry-top",), ("top", "bottom"))

    def test_rejects_faces_length_mismatch(self):
        requirement = self.requirement_builder.build_for_panel("panel-5", needs_edge_band=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        with self.assertRaises(ValueError):
            self.instantiator.instantiate(operation, ("TOP", "BOTTOM"), ("geometry-top", "geometry-bottom"), ("top",))

    def test_all_instances_pass_validate_operation_instance_contract(self):
        requirement = self.requirement_builder.build_for_door("door-2", needs_hinges=True, needs_handle=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        instances = self.instantiator.instantiate(
            operation,
            ("HINGE_1", "HINGE_2"),
            ("geometry-1", "geometry-2"),
            ("left", "right"),
        )
        for instance in instances:
            validate_operation_instance_contract(instance)

    def test_no_freecad_import(self):
        source = inspect.getsource(operation_instantiator_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_manufacturing_production_package_import(self):
        source = inspect.getsource(operation_instantiator_module)
        self.assertNotIn("ManufacturingProductionPackage", source)
        self.assertNotIn("ProductionPackage", source)

    def test_no_placement_calculation_terms_in_implementation(self):
        source = inspect.getsource(operation_instantiator_module)
        for term in ("x=", "y=", "z=", "rotation", "offset"):
            self.assertNotIn(term, source)


if __name__ == "__main__":
    unittest.main()
