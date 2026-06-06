import inspect
import unittest

from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestCanonicalOperationCollectorArchitecture(
    unittest.TestCase
):

    def test_no_legacy_dependencies(self):

        source = inspect.getsource(
            CanonicalOperationCollector
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )

        self.assertNotIn(
            "PanelOperationEngine",
            source
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )
