import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from commercial_outputs.commercial_package_builder import CommercialPackageBuilder
from commercial_outputs.commercial_package_report import CommercialPackageReport
from core.material_manager import MaterialManager
from cost_intelligence.cost_package_builder import CostPackageBuilder
from cost_intelligence.cost_package_report import CostPackageReport
from domain.base_cabinet_specification import BaseCabinetSpecification
from manufacturing.factory_release_package import FactoryReleasePackage
from scene_graph.builder import SceneGraphBuilder


class _IntegrationCabinetBuilder:
    """Test-only stand-in for unavailable FreeCAD-bound CabinetBuilder."""

    def __init__(self):
        self.scene_graph = None

    def build(self, cabinet):
        self.scene_graph = SceneGraphBuilder(
            cabinet,
            MaterialManager(),
        ).build(None)
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class TestEndToEndPipeline(unittest.TestCase):
    def test_engineering_to_commercial_pipeline_is_valid(self):
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            manufacturing_result = ManufacturingApplicationService().execute(
                specification=BaseCabinetSpecification()
            )

        self.assertTrue(
            manufacturing_result.success,
            msg=f"ManufacturingApplicationService failed: {manufacturing_result.errors}",
        )

        factory_release = manufacturing_result.data["factory_release_package"]
        self.assertIsInstance(factory_release, FactoryReleasePackage)

        cost_report = CostPackageBuilder().build(factory_release)
        self.assertIsInstance(cost_report, CostPackageReport)

        commercial_report = CommercialPackageBuilder().build(cost_report)
        self.assertIsInstance(commercial_report, CommercialPackageReport)

        self.assertIs(commercial_report.cost_report, cost_report)
        self.assertEqual(cost_report.source, "CostPackageBuilder")
        self.assertEqual(commercial_report.source, "CommercialPackageBuilder")

        self.assertIs(
            factory_release.cut_list,
            manufacturing_result.data["cut_list"],
        )
        self.assertIs(
            factory_release.metadata,
            manufacturing_result.data["metadata"],
        )
        self.assertIs(
            factory_release.manufacturing_decision,
            manufacturing_result.data["manufacturing_decision"],
        )
        self.assertIs(
            factory_release.hardware_bom,
            manufacturing_result.data["manufacturing_production_package"].hardware_report,
        )
        self.assertIs(
            factory_release.cnc_package,
            manufacturing_result.data["manufacturing_production_package"].cnc_report,
        )
        self.assertIs(
            factory_release.assembly_package,
            manufacturing_result.data["manufacturing_production_package"].assembly_report,
        )

        self.assertGreater(
            len(getattr(factory_release.cut_list, "items", []) or []),
            0,
        )
        self.assertGreaterEqual(
            len(getattr(factory_release.cnc_package, "rows", []) or []),
            0,
        )

    def test_dependency_chain_is_linear_and_acyclic(self):
        dependency_graph = {
            "engineering": set(),
            "manufacturing": {"engineering"},
            "factory_release": {"manufacturing"},
            "cost": {"factory_release"},
            "commercial": {"cost"},
        }

        self.assertEqual(dependency_graph["commercial"], {"cost"})
        self.assertEqual(dependency_graph["cost"], {"factory_release"})
        self.assertEqual(dependency_graph["factory_release"], {"manufacturing"})

        visited = set()
        active = set()

        def visit(node):
            if node in active:
                return False
            if node in visited:
                return True
            active.add(node)
            for dep in dependency_graph[node]:
                if not visit(dep):
                    return False
            active.remove(node)
            visited.add(node)
            return True

        self.assertTrue(all(visit(node) for node in dependency_graph))

    def test_cost_builder_accepts_factory_release_only(self):
        signature = inspect.signature(CostPackageBuilder.build)
        self.assertEqual(list(signature.parameters), ["self", "package"])

        source = inspect.getsource(CostPackageBuilder)
        self.assertIn("FactoryReleasePackage", source)
        self.assertNotIn("CommercialPackageReport", source)
        self.assertNotIn("ManufacturingApplicationService", source)

    def test_commercial_builder_accepts_cost_report_only(self):
        signature = inspect.signature(CommercialPackageBuilder.build)
        self.assertEqual(list(signature.parameters), ["self", "cost_report"])

        source = inspect.getsource(CommercialPackageBuilder)
        self.assertIn("CostPackageReport", source)
        self.assertNotIn("FactoryReleasePackage", source)
        self.assertNotIn("ManufacturingApplicationService", source)


if __name__ == "__main__":
    unittest.main()
