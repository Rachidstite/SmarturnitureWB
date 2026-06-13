import unittest


class TestOffcutClassifier(unittest.TestCase):

    def _offcut(
        self,
        width,
        height,
    ):
        from cost_intelligence.offcut import Offcut

        return Offcut(
            id="OFFCUT-001",
            material="MDF",
            thickness=18,
            width=width,
            height=height,
            source_sheet="SHEET-001",
        )

    def _policy(self):
        from cost_intelligence.offcut_reuse_policy import OffcutReusePolicy

        return OffcutReusePolicy(
            material="MDF",
            thickness=18,
            min_width=150,
            min_height=150,
            min_area=22500,
        )

    def test_offcut_classifier_exists(self):

        try:
            from cost_intelligence.offcut_classifier import (
                OffcutClassifier,
            )
        except ImportError:
            self.fail(
                "OffcutClassifier does not exist"
            )

    def test_width_below_minimum_is_not_reusable(self):

        from cost_intelligence.offcut_classification import (
            OffcutClassification,
        )
        from cost_intelligence.offcut_classifier import OffcutClassifier

        result = OffcutClassifier(
            policy=self._policy(),
        ).classify(
            self._offcut(
                width=140,
                height=200,
            )
        )

        self.assertIsInstance(
            result,
            OffcutClassification,
        )
        self.assertFalse(result.reusable)
        self.assertEqual(
            result.reason,
            "Width below minimum",
        )

    def test_height_below_minimum_is_not_reusable(self):

        from cost_intelligence.offcut_classifier import OffcutClassifier

        result = OffcutClassifier(
            policy=self._policy(),
        ).classify(
            self._offcut(
                width=200,
                height=140,
            )
        )

        self.assertFalse(result.reusable)
        self.assertEqual(
            result.reason,
            "Height below minimum",
        )

    def test_offcut_at_minimums_is_reusable(self):

        from cost_intelligence.offcut_classifier import OffcutClassifier

        result = OffcutClassifier(
            policy=self._policy(),
        ).classify(
            self._offcut(
                width=150,
                height=150,
            )
        )

        self.assertTrue(result.reusable)
        self.assertEqual(
            result.reason,
            "",
        )

    def test_width_rule_has_precedence(self):

        from cost_intelligence.offcut_classifier import OffcutClassifier

        result = OffcutClassifier(
            policy=self._policy(),
        ).classify(
            self._offcut(
                width=140,
                height=140,
            )
        )

        self.assertEqual(
            result.reason,
            "Width below minimum",
        )


if __name__ == "__main__":
    unittest.main()
