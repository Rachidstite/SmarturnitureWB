from cost_intelligence.default_catalog_service import DefaultCatalogService
from cost_intelligence.project_cost_calculator import ProjectCostCalculator
from exports.cutlist_engine import CutListEngine
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy


class SceneGraphCostService:
    """
    Modern cost intelligence wrapper for scene_graph inputs.
    """

    @staticmethod
    def estimate(scene_graph):
        cutlist_items = CutListEngine.extract(scene_graph)
        nesting_input = list(cutlist_items)
        nesting_results = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(nesting_input)
        pricing_catalog = DefaultCatalogService().load_default_catalog()

        return ProjectCostCalculator().estimate(
            cutlist_items=cutlist_items,
            nesting_results=nesting_results,
            scene_graph=scene_graph,
            pricing_catalog=pricing_catalog,
        )
