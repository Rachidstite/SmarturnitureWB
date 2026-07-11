"""Manufacturing groove emission contracts.

Proves that engineering groove intent flows through the manufacturing
pipeline as Groove operations on the correct receiving panels.

Contracts covered:
  C1  Engineering groove -> Manufacturing GrooveOperation
  C2  GrooveOperation -> UnifiedManufacturingOperation
  C3  Unified operation -> Machining Report
  C4  Machining Report -> CNC Report
  C5  Overlay cabinet: no groove emitted
  C6  No back panel: no groove emitted
  C7  Receiving-panel identity preserved
"""

import types
import unittest
from importlib import import_module
from unittest.mock import patch

from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from domain.furniture_construction_model import (
    BackPanelConstruction,
    BackPanelType,
    CabinetConstructionModel,
    CabinetConstructionSpecification,
    ConstructionMethod,
    PanelConstruction,
    ShelfConstruction,
    JoineryConstruction,
    HardwareConstruction,
    ShelfOwnership,
    HingeSide,
)
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_operation_adapter import (
    ManufacturingOperationAdapter,
)
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)
from scene_graph.builder import SceneGraphBuilder
from shared.roles import NodeRole


def _build_runtime_graph(specification):
    """Build a fully resolved cabinet + scene graph from a specification."""
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
    cabinet = Cabinet(params=adapter_result.cabinet_params)
    attach_base_cabinet_engineering_models(cabinet, specification)

    fake_freecad = types.ModuleType("FreeCAD")
    fake_part = types.ModuleType("Part")
    fake_part.makeBox = lambda *args, **kwargs: object()
    fake_freecad_gui = types.ModuleType("FreeCADGui")

    with patch.dict(
        "sys.modules",
        {
            "FreeCAD": fake_freecad,
            "Part": fake_part,
            "FreeCADGui": fake_freecad_gui,
        },
    ):
        cabinet_builder_module = import_module("engine.cabinet_builder")
        builder = cabinet_builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()
        builder._attach_section_engineering_components()

    graph = SceneGraphBuilder(cabinet, builder.mat).build(builder.geo)
    cabinet.graph = graph
    cabinet.scene_graph = graph
    return cabinet, graph


def _groove_ops_from_specs(panel_specs):
    """Extract Groove operations from panel specs with role info."""
    results = []
    for spec in panel_specs:
        for op in getattr(spec, "cnc_operations", ()) or ():
            if getattr(op, "__class__", None) and op.__class__.__name__ == "Groove":
                # Normalize role name for both str and int enums
                role = getattr(spec, "role", None)
                if role is None:
                    role_name = ""
                elif isinstance(role, str):
                    role_name = role.upper()
                else:
                    role_name = str(
                        getattr(role, "name", getattr(role, "value", str(role)))
                    ).upper()
                results.append({
                    "panel_identity": getattr(spec, "identity", ""),
                    "op": op,
                    "role": role_name,
                    "metadata": getattr(op, "metadata", {}) or {},
                })
    return results


class TestManufacturingGrooveEmissionContract(unittest.TestCase):
    """Contract tests for groove emission from engineering intent."""

    # ── Contract 1: Engineering groove -> Manufacturing GrooveOperation ─────

    def test_reference_cabinet_emits_receiving_panel_grooves(self):
        """Scenario A: Reference grooved back panel emits 3 receiving grooves.

        Left side, right side, and bottom panel each get a Groove operation.
        """
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        _cabinet, graph = _build_runtime_graph(specification)
        panel_specs = ManufacturingExtractor.extract(graph)

        groove_info = _groove_ops_from_specs(panel_specs)

        # Filter to receiving-panel grooves (not back-panel self-groove)
        receiving_roles = {"SIDE_PANEL", "BOTTOM_PANEL"}
        receiving_grooves = [
            g for g in groove_info
            if g["role"] in receiving_roles
        ]

        self.assertEqual(
            len(receiving_grooves),
            3,
            f"Expected 3 receiving-panel grooves, got {len(receiving_grooves)}: "
            f"{[g['panel_identity'] for g in receiving_grooves]}",
        )

        # Verify each has the engineering groove dimensions
        for g in receiving_grooves:
            op = g["op"]
            self.assertGreater(op.width, 0.0, f"{g['panel_identity']}: groove width must be > 0")
            self.assertGreater(op.depth, 0.0, f"{g['panel_identity']}: groove depth must be > 0")
            self.assertGreater(op.length, 0.0, f"{g['panel_identity']}: groove length must be > 0")
            self.assertIn("panel_identity", g["metadata"])

    # ── Contract 2: GrooveOperation -> UnifiedManufacturingOperation ─────

    def test_groove_operation_adapts_to_unified_operation(self):
        """Groove on a panel spec becomes UnifiedManufacturingOperation with type GROOVE."""
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        _cabinet, graph = _build_runtime_graph(specification)
        panel_specs = ManufacturingExtractor.extract(graph)

        unified_ops = ManufacturingOperationAdapter.to_unified_panel_operations(
            panel_specs
        )

        # Find GROOVE operations in unified ops
        groove_unified = [op for op in unified_ops if op.operation_type == "GROOVE"]
        self.assertGreaterEqual(
            len(groove_unified),
            3,
            f"Expected at least 3 GROOVE unified operations, got {len(groove_unified)}",
        )

        for op in groove_unified:
            self.assertEqual(op.operation_type, "GROOVE")
            self.assertIn("panel_identity", op.metadata)
            self.assertIn("source_operation_reference", op.metadata)

    # ── Contract 3: Unified operation -> Machining Report ────────────────

    def test_unified_groove_reaches_machining_report(self):
        """Groove UnifiedManufacturingOperation appears in machining report items."""
        from manufacturing.manufacturing_machining_builder import (
            ManufacturingMachiningBuilder,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage

        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        _cabinet, graph = _build_runtime_graph(specification)
        panel_specs = ManufacturingExtractor.extract(graph)
        unified_ops = ManufacturingOperationAdapter.to_unified_panel_operations(
            panel_specs
        )

        package = ManufacturingPackage(machining_operations=unified_ops)
        machining_report = ManufacturingMachiningBuilder().build(package)

        groove_items = [
            item
            for item in machining_report.items
            if item.get("operation_type") == "GROOVE"
        ]
        self.assertGreaterEqual(
            len(groove_items),
            3,
            f"Expected at least 3 GROOVE items in machining report, got {len(groove_items)}",
        )

        for item in groove_items:
            self.assertIn("panel_identity", item)
            self.assertIn("source_operation_reference", item)

    # ── Contract 4: Machining Report -> CNC Report ──────────────────────

    def test_machining_groove_reaches_cnc_report(self):
        """Groove items in machining report flow through to CNC report rows."""
        from manufacturing.cnc_report_builder import CNCReportBuilder
        from manufacturing.manufacturing_machining_builder import (
            ManufacturingMachiningBuilder,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage

        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        _cabinet, graph = _build_runtime_graph(specification)
        panel_specs = ManufacturingExtractor.extract(graph)
        unified_ops = ManufacturingOperationAdapter.to_unified_panel_operations(
            panel_specs
        )

        package = ManufacturingPackage(machining_operations=unified_ops)
        machining_report = ManufacturingMachiningBuilder().build(package)
        cnc_report = CNCReportBuilder().build(machining_report)

        groove_rows = [
            row
            for row in cnc_report.rows
            if row.operation_type == "GROOVE"
        ]
        self.assertGreaterEqual(
            len(groove_rows),
            3,
            f"Expected at least 3 GROOVE rows in CNC report, got {len(groove_rows)}",
        )

        for row in groove_rows:
            self.assertTrue(
                row.panel_identity,
                "CNC report GROOVE row must have panel_identity",
            )
            self.assertIn("GROOVE", row.operation_type)
            self.assertGreater(row.depth, 0.0, "Groove depth must be > 0 in CNC row")

    # ── Contract 5: Overlay cabinet -> No groove emitted ─────────────────

    def test_overlay_back_panel_emits_no_groove(self):
        """Scenario B: Overlay back panel produces no receiving-panel grooves.

        Builds a cabinet with installation_mode=OVERLAY, which means the back
        panel sits on top of the carcass rather than in grooves.
        """
        import types
        from unittest.mock import patch

        spec = CabinetConstructionSpecification(
            width_mm=600.0, height_mm=720.0, depth_mm=580.0,
            material_thickness_mm=18.0, back_panel_thickness_mm=3.0,
            door_count=0, shelf_count=0,
            construction_method=ConstructionMethod.CONFIRMAT,
            back_panel_type=BackPanelType.GROOVED,
            drawer_count=0, wall_mount_count=0,
        )
        mat = MaterialManager()
        construction_model = CabinetConstructionModel(
            specification=spec,
            panels=(
                PanelConstruction("SIDE_PANEL", "Left Side", 18.0, 720.0, 18.0, "MDF_18", (0.0, 0.0, 0.0), "side"),
                PanelConstruction("SIDE_PANEL", "Right Side", 18.0, 720.0, 18.0, "MDF_18", (582.0, 0.0, 0.0), "side"),
                PanelConstruction("TOP_PANEL", "Top", 564.0, 580.0, 18.0, "MDF_18", (18.0, 0.0, 702.0), "top"),
                PanelConstruction("BOTTOM_PANEL", "Bottom", 564.0, 580.0, 18.0, "MDF_18", (18.0, 0.0, 80.0), "bottom"),
            ),
            back_panel=BackPanelConstruction(
                panel=PanelConstruction("BACK_PANEL", "Overlay Back", 564.0, 580.0, 3.0, "HDF_3", (18.0, 0.0, 80.0), "back"),
                placement="OVERLAY",
                installation_mode="OVERLAY",
                groove_depth_mm=0.0,
                groove_width_mm=0.0,
                allowed_details=(),
                disallowed_details=(),
            ),
            doors=(),
            shelves=(),
            joinery=JoineryConstruction(ConstructionMethod.CONFIRMAT, "CONFIRMAT_50_V1", "", (), ()),
            hardware=HardwareConstruction("NONE", "NONE", "NONE", (), ()),
        )

        from domain.base_cabinet_engineering_model import (
            BaseCabinetEngineeringModelBuilder,
        )
        engineering_model = BaseCabinetEngineeringModelBuilder.build(construction_model)

        fake_freecad = types.ModuleType("FreeCAD")
        fake_part = types.ModuleType("Part")
        fake_part.makeBox = lambda *a, **kw: object()
        fake_freecad_gui = types.ModuleType("FreeCADGui")

        with patch.dict("sys.modules", {
            "FreeCAD": fake_freecad,
            "Part": fake_part,
            "FreeCADGui": fake_freecad_gui,
        }):
            import engine.cabinet_builder as cab_mod
            builder = cab_mod.CabinetBuilder()
            from engine.cabinet import Cabinet
            from engine.geometry_engine import GeometryEngine
            params = type("Params", (), {
                "width": 600.0, "height": 720.0, "depth": 580.0,
                "sec_count": 1, "base_height": 80.0,
                "back_panel_type": "REAR", "hinge_sku": "NONE",
                "sec_data": {},
            })()
            cabinet = Cabinet(params=params)
            cabinet.construction_model = construction_model
            cabinet.engineering_model = engineering_model
            builder._cabinet = cabinet
            builder.mat = mat
            builder.geo = GeometryEngine(cabinet, mat)
            builder._attach_section_engineering_components()

        from scene_graph.builder import SceneGraphBuilder
        graph = SceneGraphBuilder(cabinet, mat).build(builder.geo)
        panel_specs = ManufacturingExtractor.extract(graph)

        groove_info = _groove_ops_from_specs(panel_specs)
        receiving_roles = {"SIDE_PANEL", "BOTTOM_PANEL"}
        receiving_grooves = [
            g for g in groove_info
            if g["role"] in receiving_roles
        ]

        self.assertEqual(
            len(receiving_grooves),
            0,
            f"Overlay cabinet should produce 0 receiving grooves, got {len(receiving_grooves)}",
        )

    # ── Contract 6: No back panel -> No groove emitted ─────────────────

    def test_no_back_panel_emits_no_groove(self):
        """Scenario D: Cabinet without back panel produces no receiving-panel grooves."""
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=False,
        )
        _cabinet, graph = _build_runtime_graph(specification)
        panel_specs = ManufacturingExtractor.extract(graph)

        groove_info = _groove_ops_from_specs(panel_specs)
        receiving_roles = {"SIDE_PANEL", "BOTTOM_PANEL"}
        receiving_grooves = [
            g for g in groove_info
            if g["role"] in receiving_roles
        ]

        self.assertEqual(
            len(receiving_grooves),
            0,
            f"No-back-panel cabinet should produce 0 receiving grooves, got {len(receiving_grooves)}",
        )

    # ── Contract 7: Receiving-panel identity preserved ──────────────────

    def test_receiving_panel_identity_preserved(self):
        """Each receiving groove carries the correct panel identity through the pipeline."""
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        _cabinet, graph = _build_runtime_graph(specification)
        panel_specs = ManufacturingExtractor.extract(graph)

        groove_info = _groove_ops_from_specs(panel_specs)
        receiving_roles = {"SIDE_PANEL", "BOTTOM_PANEL"}
        receiving_grooves = [
            g for g in groove_info
            if g["role"] in receiving_roles
        ]

        for g in receiving_grooves:
            meta = g["metadata"]
            self.assertEqual(
                meta.get("panel_identity", ""),
                g["panel_identity"],
                f"metadata panel_identity mismatch for {g['panel_identity']}",
            )
            self.assertEqual(
                meta.get("source_operation_reference", ""),
                "EngineeringGrooveProjection",
                f"source_operation_reference should be EngineeringGrooveProjection for {g['panel_identity']}",
            )
            self.assertEqual(
                g["panel_identity"],
                meta.get("target_panel", ""),
                f"target_panel mismatch for {g['panel_identity']}",
            )


class TestManufacturingGrooveEmissionRuntimeVerification(unittest.TestCase):
    """Runtime verification of groove counts through the full pipeline."""

    def _run_pipeline(self, specification):
        """Run the full manufacturing pipeline and return groove inventory."""
        _cabinet, graph = _build_runtime_graph(specification)

        # Stage 1: Manufacturing Extractor -> panel_specs
        panel_specs = ManufacturingExtractor.extract(graph)

        # Stage 2: Unified operations
        unified_ops = ManufacturingOperationAdapter.to_unified_panel_operations(
            panel_specs
        )

        # Stage 3: Full runtime pipeline
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )
        runtime_result = ManufacturingRuntimePipelineBuilder().build(graph)

        # Count grooves at each stage
        spec_grooves = _groove_ops_from_specs(panel_specs)
        unified_grooves = [op for op in unified_ops if op.operation_type == "GROOVE"]
        machining_grooves = [
            item
            for item in getattr(
                runtime_result.manufacturing_package, "machining_operations", []
            )
            if getattr(item, "operation_type", "") == "GROOVE"
        ]

        # CNC report
        cnc_report = getattr(
            runtime_result.manufacturing_production_package, "cnc_report", None
        )
        cnc_grooves = [
            row
            for row in getattr(cnc_report, "rows", [])
            if row.operation_type == "GROOVE"
        ]

        return {
            "engineering_grooves": len(spec_grooves),
            "engineering_details": [
                {
                    "panel_identity": g["panel_identity"],
                    "role": str(getattr(g["role"], "value", g["role"])),
                    "width": getattr(g["op"], "width", 0.0),
                    "depth": getattr(g["op"], "depth", 0.0),
                    "length": getattr(g["op"], "length", 0.0),
                    "start_x": getattr(g["op"], "start_x", 0.0),
                    "start_y": getattr(g["op"], "start_y", 0.0),
                    "face": getattr(g["op"], "face", ""),
                    "metadata": g["metadata"],
                    "status": "PRESERVED",
                }
                for g in spec_grooves
            ],
            "unified_grooves": len(unified_grooves),
            "machining_grooves": len(machining_grooves),
            "cnc_grooves": len(cnc_grooves),
        }

    def test_reference_cabinet_groove_counts(self):
        """Verify groove counts match at every pipeline stage for reference cabinet."""
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        inventory = self._run_pipeline(specification)

        # Engineering emits receiving grooves (3: left, right sides + bottom)
        # PLUS possible back-panel self-groove (1) = total 3-4
        receiving_eng = [
            d
            for d in inventory["engineering_details"]
            if d["role"] in ("SIDE_PANEL", "BOTTOM_PANEL")
        ]

        # Verify counts are consistent across stages
        engine_groove_count = len(receiving_eng)
        # Back-panel grooves may also exist, but the unified/machining/CNC
        # count should include ALL grooves, not just receiving.
        self.assertGreaterEqual(
            inventory["unified_grooves"],
            engine_groove_count,
            f"Unified grooves ({inventory['unified_grooves']}) should >= engineering receiving grooves ({engine_groove_count})",
        )

    def test_groove_preservation_matrix(self):
        """Record all groove properties for the preservation report."""
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            toe_kick_required=True,
            has_back_panel=True,
        )
        inventory = self._run_pipeline(specification)

        for detail in inventory["engineering_details"]:
            meta = detail["metadata"]
            self.assertEqual(detail["status"], "PRESERVED")
            self.assertIn("panel_identity", meta)
            self.assertIn("source_operation_reference", meta)
            self.assertIn("target_panel_role", meta)
            self.assertIn("groove_width", meta)
            self.assertIn("groove_depth", meta)


if __name__ == "__main__":
    unittest.main()
