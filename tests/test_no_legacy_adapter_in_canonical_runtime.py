import inspect
import unittest

from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestNoLegacyAdapterInCanonicalRuntime(
    unittest.TestCase
):

    def test_collector_does_not_reference_legacy_adapter(self):

        source = inspect.getsource(
            CanonicalOperationCollector
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )


if __name__ == "__main__":
    unittest.main()
