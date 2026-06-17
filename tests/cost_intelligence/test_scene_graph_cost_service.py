import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestSceneGraphCostService(unittest.TestCase):

    def test_service_exists(self):
        from cost_intelligence.scene_graph_cost_service import (
            SceneGraphCostService,
        )

        self.assertTrue(callable(SceneGraphCostService.estimate))

    @patch(
        "cost_intelligence.scene_graph_cost_service.ProjectCostCalculator"
    )
    @patch(
        "cost_intelligence.scene_graph_cost_service.DefaultCatalogService"
    )
    @patch(
        "cost_intelligence.scene_graph_cost_service.IndustrialNestingEngine"
    )
    @patch(
        "cost_intelligence.scene_graph_cost_service.CutListEngine"
    )
    def test_estimate_composes_existing_components(
        self,
        cutlist_engine,
        industrial_nesting_engine_class,
        default_catalog_service_class,
        project_cost_calculator_class,
    ):
        from cost_intelligence.scene_graph_cost_service import (
            SceneGraphCostService,
        )

        scene_graph = object()
        cutlist_items = [
            SimpleNamespace(identity="A", width=100),
            SimpleNamespace(identity="B", width=200),
        ]
        original_cutlist_items = copy.deepcopy(cutlist_items)
        nesting_results = {"MDF_18MM": ["sheet-result"]}
        pricing_catalog = SimpleNamespace(prices={"MDF_18MM": {"unit_price": 12}})
        cost_report = object()

        cutlist_engine.extract.return_value = cutlist_items
        industrial_nesting_engine_class.return_value.process.return_value = (
            nesting_results
        )
        default_catalog_service_class.return_value.load_default_catalog.return_value = (
            pricing_catalog
        )
        project_cost_calculator_class.return_value.estimate.return_value = (
            cost_report
        )

        result = SceneGraphCostService.estimate(scene_graph)

        cutlist_engine.extract.assert_called_once_with(scene_graph)
        industrial_nesting_engine_class.assert_called_once()
        industrial_nesting_engine_class.return_value.process.assert_called_once()
        passed_cutlist_items = (
            industrial_nesting_engine_class.return_value.process.call_args.args[0]
        )
        self.assertIsNot(passed_cutlist_items, cutlist_items)
        self.assertEqual(cutlist_items, original_cutlist_items)
        default_catalog_service_class.return_value.load_default_catalog.assert_called_once_with()
        project_cost_calculator_class.return_value.estimate.assert_called_once_with(
            cutlist_items=cutlist_items,
            nesting_results=nesting_results,
            scene_graph=scene_graph,
            pricing_catalog=pricing_catalog,
        )
        self.assertIs(result, cost_report)

    @patch(
        "cost_intelligence.scene_graph_cost_service.ProjectCostCalculator"
    )
    @patch(
        "cost_intelligence.scene_graph_cost_service.DefaultCatalogService"
    )
    @patch(
        "cost_intelligence.scene_graph_cost_service.IndustrialNestingEngine"
    )
    @patch(
        "cost_intelligence.scene_graph_cost_service.CutListEngine"
    )
    def test_estimate_uses_nesting_engine_with_cutlist_items(
        self,
        cutlist_engine,
        industrial_nesting_engine_class,
        default_catalog_service_class,
        project_cost_calculator_class,
    ):
        from cost_intelligence.scene_graph_cost_service import (
            SceneGraphCostService,
        )

        scene_graph = object()
        cutlist_items = [SimpleNamespace(identity="A", width=100)]
        nesting_results = {"MDF_18MM": ["sheet-result"]}
        pricing_catalog = SimpleNamespace(prices={})
        cost_report = object()

        cutlist_engine.extract.return_value = cutlist_items
        industrial_nesting_engine_class.return_value.process.return_value = (
            nesting_results
        )
        default_catalog_service_class.return_value.load_default_catalog.return_value = (
            pricing_catalog
        )
        project_cost_calculator_class.return_value.estimate.return_value = (
            cost_report
        )

        SceneGraphCostService.estimate(scene_graph)

        industrial_nesting_engine_class.return_value.process.assert_called_once()
        self.assertEqual(
            industrial_nesting_engine_class.return_value.process.call_args.args[0],
            cutlist_items,
        )


if __name__ == "__main__":
    unittest.main()
