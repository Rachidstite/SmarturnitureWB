import importlib
import inspect
import unittest


class TestOffcutReuseContract(unittest.TestCase):
    def test_offcut_extraction_feeds_active_optimization_pipeline(self):
        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_optimization_pipeline_builder"
            )
        )

        self.assertIn("OffcutExtractionService.extract", source)
        self.assertIn("OffcutReportBuilder().build", source)

    def test_offcut_classifier_uses_reuse_policy(self):
        source = inspect.getsource(
            importlib.import_module("cost_intelligence.offcut_classifier")
        )

        self.assertIn("OffcutReusePolicy", source)
        self.assertIn("min_width", source)
        self.assertIn("min_height", source)
        self.assertIn("min_area", source)

    def test_offcut_classification_must_participate_in_active_optimization_flow(self):
        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_optimization_pipeline_builder"
            )
        )

        self.assertIn("OffcutClassifier", source)

    def test_reuse_policy_must_participate_in_active_optimization_flow(self):
        combined_source = "\n".join(
            [
                inspect.getsource(
                    importlib.import_module(
                        "cost_intelligence.manufacturing_optimization_pipeline_builder"
                    )
                ),
                inspect.getsource(
                    importlib.import_module("cost_intelligence.offcut_report_builder")
                ),
            ]
        )

        self.assertRegex(
            combined_source,
            r"OffcutReusePolicy|reuse policy|reuse_policy",
        )


if __name__ == "__main__":
    unittest.main()
