import unittest

from manufacturing.operation_vocabulary import (
    CATEGORY_TO_OPERATION_IDS,
    OPERATION_CATEGORY_BY_ID,
    OPERATION_VOCABULARY_V1,
    OperationCategory,
    OperationId,
)


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


class TestOperationVocabularyContract(unittest.TestCase):
    def test_operation_ids_are_unique(self):
        values = [operation_id.value for operation_id in OperationId]
        self.assertEqual(len(values), len(set(values)))

    def test_every_operation_belongs_to_exactly_one_category(self):
        self.assertEqual(
            set(OPERATION_CATEGORY_BY_ID.keys()),
            set(OperationId),
        )

        all_mapped_ids = []
        for category, operation_ids in CATEGORY_TO_OPERATION_IDS.items():
            self.assertIsInstance(category, OperationCategory)
            all_mapped_ids.extend(operation_ids)
            for operation_id in operation_ids:
                self.assertEqual(OPERATION_CATEGORY_BY_ID[operation_id], category)

        self.assertEqual(len(all_mapped_ids), len(set(all_mapped_ids)))
        self.assertEqual(set(all_mapped_ids), set(OperationId))

    def test_operation_ids_do_not_contain_forbidden_execution_terms(self):
        for operation_id in OPERATION_VOCABULARY_V1:
            text = operation_id.value.upper()
            for term in FORBIDDEN_TERMS:
                self.assertNotIn(term, text)

    def test_categories_do_not_contain_execution_concepts(self):
        for category in OperationCategory:
            text = category.value.upper()
            for term in FORBIDDEN_TERMS:
                self.assertNotIn(term, text)


if __name__ == "__main__":
    unittest.main()

