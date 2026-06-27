import unittest
from dataclasses import fields, is_dataclass

from manufacturing.operation_semantics import (
    OPERATION_SEMANTICS_V1,
    OperationIdempotency,
    OperationReversibility,
)
from manufacturing.operation_vocabulary import OPERATION_CATEGORY_BY_ID, OperationId


FORBIDDEN_TERMS = (
    "CNC",
    "MACHINE",
    "OPERATOR",
    "QUEUE",
    "JOB",
    "SCHEDULE",
    "DURATION",
    "COST",
    "WORKER",
    "GCODE",
    "TOOL",
    "STATION",
)


def _flatten_semantics_text(semantics):
    values = [
        semantics.intent,
        semantics.quality_meaning,
        *semantics.input_state,
        *semantics.output_state,
        *semantics.required_manufacturing_capabilities,
        *semantics.dependency_hints,
        *semantics.target_types,
    ]
    return [value.upper() for value in values]


class TestOperationSemanticsContract(unittest.TestCase):
    def test_operation_semantics_has_no_category_field(self):
        semantics = next(iter(OPERATION_SEMANTICS_V1.values()))
        self.assertTrue(is_dataclass(semantics))
        self.assertNotIn("category", {field.name for field in fields(semantics)})

    def test_semantics_entries_reference_valid_operation_ids_and_categories(self):
        for operation_id, semantics in OPERATION_SEMANTICS_V1.items():
            self.assertIn(operation_id, OperationId)
            self.assertEqual(semantics.operation_id, operation_id)
            self.assertIn(operation_id, OPERATION_CATEGORY_BY_ID)
            self.assertEqual(
                OPERATION_CATEGORY_BY_ID[operation_id],
                OPERATION_CATEGORY_BY_ID[semantics.operation_id],
            )

    def test_semantics_input_and_output_states_are_tuples(self):
        for semantics in OPERATION_SEMANTICS_V1.values():
            self.assertIsInstance(semantics.input_state, tuple)
            self.assertIsInstance(semantics.output_state, tuple)

    def test_required_manufacturing_capabilities_exists(self):
        semantics = OPERATION_SEMANTICS_V1[OperationId.CUT_TO_SIZE]
        self.assertTrue(hasattr(semantics, "required_manufacturing_capabilities"))
        self.assertFalse(hasattr(semantics, "required_capabilities"))

    def test_semantics_entries_do_not_include_forbidden_execution_terms(self):
        for semantics in OPERATION_SEMANTICS_V1.values():
            for text in _flatten_semantics_text(semantics):
                for term in FORBIDDEN_TERMS:
                    self.assertNotIn(term, text)

    def test_cut_to_size_contract(self):
        semantics = OPERATION_SEMANTICS_V1[OperationId.CUT_TO_SIZE]
        self.assertEqual(semantics.idempotency, OperationIdempotency.NOT_REPEATABLE)
        self.assertEqual(semantics.reversibility, OperationReversibility.IRREVERSIBLE)

    def test_edge_band_contract(self):
        semantics = OPERATION_SEMANTICS_V1[OperationId.EDGE_BAND]
        self.assertEqual(semantics.idempotency, OperationIdempotency.NOT_REPEATABLE)
        self.assertEqual(
            semantics.reversibility, OperationReversibility.DESTRUCTIVE_REVERSAL
        )

    def test_inspect_shelf_support_contract(self):
        semantics = OPERATION_SEMANTICS_V1[OperationId.INSPECT_SHELF_SUPPORT]
        self.assertEqual(semantics.idempotency, OperationIdempotency.REPEATABLE)
        self.assertEqual(semantics.reversibility, OperationReversibility.REVERSIBLE)

    def test_install_drawer_front_targets_drawer_or_drawerfront(self):
        semantics = OPERATION_SEMANTICS_V1[OperationId.INSTALL_DRAWER_FRONT]
        self.assertTrue(
            any(target in {"Drawer", "DrawerFront"} for target in semantics.target_types)
        )

    def test_inspect_hardware_alignment_belongs_to_inspection(self):
        self.assertEqual(
            OPERATION_CATEGORY_BY_ID[OperationId.INSPECT_HARDWARE_ALIGNMENT].name,
            "INSPECTION",
        )


if __name__ == "__main__":
    unittest.main()
