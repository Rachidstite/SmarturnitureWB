import unittest


class TestFurnitureProjectSummaryBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.furniture_project_summary_builder import (
            FurnitureProjectSummaryBuilder,
        )

        self.assertTrue(callable(FurnitureProjectSummaryBuilder().build))

    def test_builder_returns_furniture_project_summary(self):
        from manufacturing.furniture_project_summary import FurnitureProjectSummary
        from manufacturing.furniture_project_summary_builder import (
            FurnitureProjectSummaryBuilder,
        )

        summary = FurnitureProjectSummaryBuilder().build(self._project([]))

        self.assertIsInstance(summary, FurnitureProjectSummary)

    def test_empty_project_has_zero_totals(self):
        from manufacturing.furniture_project_summary_builder import (
            FurnitureProjectSummaryBuilder,
        )

        summary = FurnitureProjectSummaryBuilder().build(self._project([]))

        self.assertEqual(summary.total_cabinets, 0)
        self.assertEqual(summary.total_physical_parts, 0)
        self.assertEqual(summary.total_machining_operations, 0)

    def test_builder_aggregates_multiple_cabinets(self):
        from manufacturing.furniture_project_summary_builder import (
            FurnitureProjectSummaryBuilder,
        )

        first = self._cabinet("CABINET-1")
        second = self._cabinet("CABINET-2")
        first.graph.physical_nodes[0].machining_ops.extend([object(), object()])
        second.graph.physical_nodes[0].machining_ops.append(object())
        second.graph.physical_nodes[1].machining_ops.append(object())

        summary = FurnitureProjectSummaryBuilder().build(
            self._project([first, second])
        )

        self.assertEqual(summary.total_cabinets, 2)
        self.assertEqual(
            summary.total_physical_parts,
            len(first.graph.physical_nodes) + len(second.graph.physical_nodes),
        )
        self.assertEqual(summary.total_machining_operations, 4)

    def test_builder_does_not_mutate_furniture_project_or_cabinets(self):
        from manufacturing.furniture_project_summary_builder import (
            FurnitureProjectSummaryBuilder,
        )

        cabinet = self._cabinet("CABINET-1")
        cabinet.graph.physical_nodes[0].machining_ops.append(object())
        project = self._project([cabinet])
        original_project_values = project.__dict__.copy()
        original_cabinet_values = cabinet.__dict__.copy()
        original_machining_ops = [
            list(node.machining_ops)
            for node in cabinet.graph.physical_nodes
        ]

        FurnitureProjectSummaryBuilder().build(project)

        self.assertEqual(project.__dict__, original_project_values)
        self.assertEqual(cabinet.__dict__, original_cabinet_values)
        self.assertEqual(
            [node.machining_ops for node in cabinet.graph.physical_nodes],
            original_machining_ops,
        )

    @staticmethod
    def _project(cabinets):
        from domain.furniture_project import FurnitureProject

        return FurnitureProject(cabinets=cabinets)

    @staticmethod
    def _cabinet(uid):
        from domain.builders import WardrobeBuilder

        return WardrobeBuilder(
            uid=uid,
            width=1000,
            height=2000,
            depth=600,
        ).build()


if __name__ == "__main__":
    unittest.main()
