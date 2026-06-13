import unittest
from dataclasses import fields, is_dataclass


class TestOffcutClassificationContract(unittest.TestCase):

    def test_offcut_classification_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.offcut_classification import (
                OffcutClassification,
            )
        except ImportError:
            self.fail(
                "OffcutClassification does not exist"
            )

        self.assertTrue(
            is_dataclass(OffcutClassification),
        )

    def test_offcut_classification_contains_required_fields(self):

        from cost_intelligence.offcut_classification import (
            OffcutClassification,
        )

        field_names = {
            field.name
            for field in fields(OffcutClassification)
        }

        self.assertEqual(
            field_names,
            {
                "offcut_id",
                "reusable",
                "reason",
            },
        )

    def test_offcut_classification_has_reusable_defaults(self):

        from cost_intelligence.offcut_classification import (
            OffcutClassification,
        )

        classification = OffcutClassification(
            offcut_id="OFFCUT-001",
        )

        self.assertTrue(
            classification.reusable,
        )
        self.assertEqual(
            classification.reason,
            "",
        )

    def test_offcut_classification_accepts_non_reusable_reason(self):

        from cost_intelligence.offcut_classification import (
            OffcutClassification,
        )

        classification = OffcutClassification(
            offcut_id="OFFCUT-002",
            reusable=False,
            reason="Too small",
        )

        self.assertFalse(
            classification.reusable,
        )
        self.assertEqual(
            classification.reason,
            "Too small",
        )


if __name__ == "__main__":
    unittest.main()
