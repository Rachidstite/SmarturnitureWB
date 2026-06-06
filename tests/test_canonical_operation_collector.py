import unittest

from domain.builders import WardrobeBuilder
from manufacturing.canonical_operation_collector import (
    CanonicalOperationCollector,
)


class TestCanonicalOperationCollector(
    unittest.TestCase
):

    def test_collect_returns_operations_list(self):

        project = (
            WardrobeBuilder(
                uid="CANONICAL",
                width=800,
                height=800,
                depth=400,
            ).build()
        )

        ops = CanonicalOperationCollector.collect(
            project.graph
        )

        self.assertIsInstance(
            ops,
            list
        )


if __name__ == "__main__":
    unittest.main()
