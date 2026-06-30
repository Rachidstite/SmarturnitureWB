import importlib
import inspect
import sys
import types
import unittest
from unittest.mock import patch

from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from manufacturing.manufacturing_decision_builder import (
    ManufacturingDecisionBuilder,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)
from scene_graph.builder import SceneGraphBuilder
from shared.contracts import CabinetParams, SectionConfig
from shared.roles import NodeRole


def _import_cabinet_builder_module():
    fake_freecad = types.ModuleType("FreeCAD")
    fake_part = types.ModuleType("Part")
    fake_part.makeBox = lambda *args, **kwargs: object()
    fake_freecad_gui = types.ModuleType("FreeCADGui")
    fake_freecad_gui.listCommands = lambda: []
    fake_freecad_gui.addCommand = lambda *args, **kwargs: None
    fake_freecad_gui.addWorkbench = lambda *args, **kwargs: None
    with patch.dict(
        sys.modules,
        {
            "FreeCAD": fake_freecad,
            "Part": fake_part,
            "FreeCADGui": fake_freecad_gui,
        },
    ):
        return importlib.import_module("engine.cabinet_builder")


class TestCapabilityCompletionFrameworkValidation(unittest.TestCase):
    def test_drawer_path_reuses_framework_through_production_decision(self):
        cabinet = self._drawer_cabinet()
        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()

        builder._attach_section_engineering_components()

        self.assertEqual(len(cabinet.engineering_model.drawer_boxes), 1)
        self.assertEqual(len(cabinet.engineering_model.drawer_faces), 1)

        graph = SceneGraphBuilder(
            cabinet,
            builder.mat,
            cabinet_id="DRAWER-FRAMEWORK-CAB",
        ).build(builder.geo)
        graph_roles = {node.role for node in graph.all_nodes()}

        self.assertIn(NodeRole.DRAWER_FACE, graph_roles)
        self.assertIn(NodeRole.DRAWER_BOX_SIDE, graph_roles)
        self.assertIn(NodeRole.DRAWER_BOX_BACK, graph_roles)
        self.assertIn(NodeRole.DRAWER_BOX_BOTTOM, graph_roles)

        runtime_result = ManufacturingRuntimePipelineBuilder().build(graph)
        panel_roles = {
            panel.role for panel in runtime_result.manufacturing_package.panels
        }

        self.assertIn(NodeRole.DRAWER_FACE, panel_roles)
        self.assertIn(NodeRole.DRAWER_BOX_SIDE, panel_roles)
        self.assertIn(NodeRole.DRAWER_BOX_BACK, panel_roles)
        self.assertIn(NodeRole.DRAWER_BOX_BOTTOM, panel_roles)

        production_package = runtime_result.manufacturing_production_package
        cutlist_identities = [
            item["identity"] for item in production_package.cutlist_report.items
        ]

        self.assertTrue(
            any("DRAWER_FACE" in identity for identity in cutlist_identities)
        )
        self.assertTrue(
            any("DRAWER_BOX_SIDE" in identity for identity in cutlist_identities)
        )
        self.assertTrue(production_package.has_cutlist_evidence)

        decision = ManufacturingDecisionBuilder().build(
            production_evidence=production_package.production_evidence
        )

        self.assertIn(decision.status, ("PASS", "WARNING"))
        self.assertIn(decision.legacy_readiness_status, ("READY", "REVIEW"))
        self.assertEqual(decision.blocking_reasons, ())

    def test_production_evidence_view_is_entity_agnostic(self):
        import manufacturing.manufacturing_production_package as module

        source = inspect.getsource(module)

        for token in ("DOOR", "DRAWER", "Door", "Drawer", "door", "drawer"):
            self.assertNotIn(token, source)

    def test_manufacturing_decision_builder_is_entity_agnostic(self):
        import manufacturing.manufacturing_decision_builder as module

        source = inspect.getsource(module)

        for token in ("DOOR", "DRAWER", "Door", "Drawer", "door", "drawer"):
            self.assertNotIn(token, source)

    def test_no_drawer_specific_framework_builder_was_introduced(self):
        import application.manufacturing_application_service as application_service
        import manufacturing.manufacturing_decision_builder as decision_builder
        import manufacturing.manufacturing_production_package_builder as package_builder

        combined_source = "\n".join(
            inspect.getsource(module)
            for module in (
                application_service,
                decision_builder,
                package_builder,
            )
        )

        for token in (
            "DrawerDecisionBuilder",
            "DrawerHardwareEvidenceBuilder",
            "DrawerEvidenceBuilder",
            "DrawerProductionPackage",
        ):
            self.assertNotIn(token, combined_source)

    @staticmethod
    def _drawer_cabinet():
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2200.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={
                    0: SectionConfig(
                        drawers=1,
                        shelves=0,
                        doors="None",
                        door_count=1,
                        drawer_type="Inset",
                    ),
                },
            )
        )
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet


if __name__ == "__main__":
    unittest.main()
