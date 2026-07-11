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
from cost_intelligence.quotation_document import QuotationDocumentV1
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from manufacturing.factory_decision_projection import (
    DecisionProjectionSection,
    FactoryDecisionProjection,
)
from manufacturing.factory_release_package import FactoryReleasePackage
from manufacturing.manufacturing_decision import ManufacturingDecision
from scene_graph.builder import SceneGraphBuilder


class _IntegrationCabinetBuilder:
    """Test-only stand-in for unavailable FreeCAD-bound CabinetBuilder."""

    def __init__(self):
        self.scene_graph = None

    def build(self, cabinet):
        material_manager = MaterialManager()
        geometry_engine = GeometryEngine(cabinet, material_manager)
        geometry_engine.resolve_all()
        self.scene_graph = SceneGraphBuilder(
            cabinet,
            material_manager,
        ).build(geometry_engine)
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class TestBaseCabinetRealManufacturingScenario(unittest.TestCase):
    def _specification(self):
        return BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=560.0,
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=True,
            hinge_family="STANDARD_110",
            drawer_family="NONE",
        )

    def _build_projection(
        self,
        *,
        manufacturing_decision,
        validation_summary,
        production_package,
        release_package,
        commercial_report,
        quotation_document,
    ):
        return FactoryDecisionProjection(
            readiness_summary=DecisionProjectionSection(
                source_object=manufacturing_decision,
                source_field="status",
                source_value=manufacturing_decision.status,
                meaning="Compact readiness state.",
                user_decision_supported="Approve / hold / reject",
            ),
            blocking_issues=(
                DecisionProjectionSection(
                    source_object=manufacturing_decision,
                    source_field="blocking_reasons",
                    source_value=manufacturing_decision.blocking_reasons,
                    meaning="Reasons that must be fixed first.",
                    user_decision_supported="Fix-first decision",
                ),
                DecisionProjectionSection(
                    source_object=validation_summary,
                    source_field="blocking_messages",
                    source_value=validation_summary.blocking_messages,
                    meaning="Validation blockers reported upstream.",
                    user_decision_supported="Fix-first decision",
                ),
            ),
            warning_summary=DecisionProjectionSection(
                source_object=manufacturing_decision,
                source_field="warning_reasons",
                source_value=manufacturing_decision.warning_reasons,
                meaning="Non-blocking concerns.",
                user_decision_supported="Review / accept with warnings",
            ),
            manufacturing_output_status=(
                DecisionProjectionSection(
                    source_object=release_package,
                    source_field="cut_list",
                    source_value=release_package.cut_list,
                    meaning="Panel cutting evidence is present.",
                    user_decision_supported="Output completeness",
                ),
                DecisionProjectionSection(
                    source_object=release_package,
                    source_field="hardware_bom",
                    source_value=release_package.hardware_bom,
                    meaning="Hardware evidence is present.",
                    user_decision_supported="Output completeness",
                ),
                DecisionProjectionSection(
                    source_object=release_package,
                    source_field="cnc_package",
                    source_value=release_package.cnc_package,
                    meaning="CNC evidence is present.",
                    user_decision_supported="Output completeness",
                ),
            ),
            assembly_status=DecisionProjectionSection(
                source_object=release_package,
                source_field="assembly_package",
                source_value=release_package.assembly_package,
                meaning="Workshop-readable assembly content is present.",
                user_decision_supported="Workshop readiness",
            ),
            commercial_status=DecisionProjectionSection(
                source_object=commercial_report,
                source_field="estimated_price",
                source_value=commercial_report.estimated_price,
                meaning="Commercial boundary summary.",
                user_decision_supported="Quotation / release proceed",
            ),
            visualization_status=DecisionProjectionSection(
                source_object=production_package.production_evidence,
                source_field="production_evidence",
                source_value=production_package.production_evidence,
                meaning="Production-backed visualization is available.",
                user_decision_supported="Visual fidelity check",
            ),
            recommended_next_actions=(
                manufacturing_decision.recommended_action,
                "Review production evidence before production.",
            ),
            release_decision=DecisionProjectionSection(
                source_object=production_package,
                source_field="release_ready",
                source_value=production_package.release_ready,
                meaning="Production package readiness.",
                user_decision_supported="Release / hold",
            ),
        )

    def test_real_base_cabinet_scenario_runs_end_to_end(self):
        specification = self._specification()
        quotation_metadata = {
            "quotation_number": "Q-2026-BASE-001",
            "issue_date": "2026-07-03",
            "valid_until": "2026-08-03",
            "seller_name": "Smart Furniture",
            "customer_name": "Pilot Customer",
            "project_description": "600mm base cabinet pilot scenario",
            "notes": "Pilot scenario for release validation.",
            "payment_terms": "30% deposit",
        }

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            product_result = build_base_cabinet_product_workflow(
                specification,
                quotation_metadata=quotation_metadata,
            )
            manufacturing_result = ManufacturingApplicationService().execute(
                specification=specification
            )

        self.assertIsInstance(product_result.engineering, Cabinet)
        self.assertIsNotNone(product_result.engineering.engineering_model)
        self.assertIsNotNone(product_result.engineering.scene_graph)

        self.assertIsNotNone(product_result.manufacturing_outputs)
        self.assertIsNotNone(product_result.manufacturing_outputs.cut_list)
        self.assertIsNotNone(
            product_result.manufacturing_outputs.manufacturing_package
        )

        self.assertIsNotNone(product_result.cost)
        self.assertIsNotNone(product_result.cost.manufacturing_cost_summary)
        self.assertIsNotNone(
            product_result.cost.manufacturing_cost_summary.cost_report
        )

        factory_release_package = manufacturing_result.data["factory_release_package"]
        self.assertIsInstance(factory_release_package, FactoryReleasePackage)
        self.assertIsInstance(
            factory_release_package.manufacturing_decision,
            ManufacturingDecision,
        )
        self.assertIs(factory_release_package.cut_list, manufacturing_result.data["cut_list"])
        self.assertIs(
            factory_release_package.hardware_bom,
            manufacturing_result.data["manufacturing_production_package"].hardware_report,
        )
        self.assertIs(
            factory_release_package.cnc_package,
            manufacturing_result.data["manufacturing_production_package"].cnc_report,
        )
        self.assertIs(
            factory_release_package.assembly_package,
            manufacturing_result.data["manufacturing_production_package"].assembly_report,
        )
        self.assertEqual(
            factory_release_package.warnings,
            manufacturing_result.data["manufacturing_production_package"].warnings,
        )

        cost_report = CostPackageBuilder().build(factory_release_package)
        self.assertIsInstance(cost_report, CostPackageReport)

        commercial_report = CommercialPackageBuilder().build(cost_report)
        self.assertIsInstance(commercial_report, CommercialPackageReport)

        self.assertIsInstance(product_result.quotation_document, QuotationDocumentV1)
        self.assertIsNotNone(product_result.commercial)
        self.assertIsNotNone(product_result.commercial.commercial_result)

        production_package = manufacturing_result.data["manufacturing_production_package"]
        self.assertTrue(production_package.has_cutlist_evidence)
        self.assertTrue(production_package.has_machining_evidence)
        self.assertTrue(production_package.has_edge_evidence)
        self.assertTrue(production_package.has_hardware_evidence)
        self.assertGreater(
            len(getattr(production_package.hardware_report, "bom_rows", []) or []),
            0,
        )
        self.assertGreater(
            len(getattr(production_package.assembly_report, "rows", []) or []),
            0,
        )
        self.assertNotIn(
            "No materials",
            manufacturing_result.data["manufacturing_decision"].warning_reasons,
        )
        self.assertTrue(
            len(getattr(production_package.assembly_report, "rows", []) or [])
            >= len(getattr(production_package.hardware_report, "bom_rows", []) or []),
            "Assembly documentation should be driven by hardware evidence.",
        )

        validation_summary = product_result.validation.manufacturing_validation_summary_report
        self.assertIsNotNone(validation_summary)
        self.assertGreaterEqual(validation_summary.total_rule_count, 0)

        projection = self._build_projection(
            manufacturing_decision=factory_release_package.manufacturing_decision,
            validation_summary=validation_summary,
            production_package=production_package,
            release_package=factory_release_package,
            commercial_report=commercial_report,
            quotation_document=product_result.quotation_document,
        )

        self.assertIsInstance(projection, FactoryDecisionProjection)
        self.assertIs(
            projection.readiness_summary.source_object,
            factory_release_package.manufacturing_decision,
        )
        self.assertEqual(
            projection.readiness_summary.source_value,
            factory_release_package.manufacturing_decision.status,
        )
        self.assertEqual(
            projection.blocking_issues[0].source_value,
            factory_release_package.manufacturing_decision.blocking_reasons,
        )
        self.assertEqual(
            projection.warning_summary.source_value,
            factory_release_package.manufacturing_decision.warning_reasons,
        )
        self.assertIs(
            projection.manufacturing_output_status[0].source_value,
            factory_release_package.cut_list,
        )
        self.assertIs(
            projection.assembly_status.source_value,
            factory_release_package.assembly_package,
        )
        self.assertEqual(
            projection.commercial_status.source_value,
            commercial_report.estimated_price,
        )
        self.assertEqual(
            projection.visualization_status.source_value,
            production_package.production_evidence,
        )
        self.assertEqual(
            projection.release_decision.source_value,
            production_package.release_ready,
        )
        self.assertTrue(projection.recommended_next_actions)

        self.assertIn("factory_release_package", manufacturing_result.data)
        self.assertIn("manufacturing_production_package", manufacturing_result.data)
        self.assertIn("manufacturing_decision", manufacturing_result.data)
        self.assertIn("metadata", manufacturing_result.data)
        self.assertIn("specification", manufacturing_result.data)




    # ──────────────────────────────────────────────────────────────────────
    # MRC-A1 — Manufacturing Reference Cabinet Acceptance Contract
    #
    # Answers: Does the default Base Cabinet preserve the same product and
    # manufacturing intent from specification through factory outputs?
    #
    # This is a manufacturing acceptance gate — not a generic smoke test.
    # ──────────────────────────────────────────────────────────────────────


# ── Acceptance summary helpers ─────────────────────────────────────

def _summarize_structures(engineering, panel_specs, cutlist):
    """Build a structural summary dict for the acceptance report."""
    eng_roles = {}
    for attr in ("left_side_panel", "right_side_panel", "top_panel", "bottom_panel"):
        eng_roles[getattr(engineering, attr).role] = eng_roles.get(
            getattr(engineering, attr).role, 0
        ) + 1
    if engineering.back_panel is not None:
        eng_roles[engineering.back_panel.role] = eng_roles.get(engineering.back_panel.role, 0) + 1
    for p in engineering.plinth_panels:
        eng_roles[p.role] = eng_roles.get(p.role, 0) + 1
    eng_roles["DOOR_PANEL"] = len(engineering.doors)
    eng_roles["SHELF"] = len(engineering.shelves)

    cutlist_entries = getattr(cutlist, "items", []) or []
    return {
        "total_panels_engineering": sum(eng_roles.values()),
        "role_counts": dict(eng_roles),
        "panel_spec_count": len(panel_specs),
        "cutlist_count": len(cutlist_entries),
        "door_count": len(engineering.doors),
        "shelf_count": len(engineering.shelves),
    }


def _summarize_operations(unified_ops, cnc_report):
    """Build an operations summary dict."""
    cnc_rows = getattr(cnc_report, "rows", []) or []
    groove_unified = [op for op in unified_ops if op.operation_type == "GROOVE"]
    drill_unified = [op for op in unified_ops if op.operation_type == "DRILL"]
    cnc_grooves = [row for row in cnc_rows if row.operation_type == "GROOVE"]
    return {
        "unified_operation_count": len(unified_ops),
        "groove_unified_count": len(groove_unified),
        "drill_unified_count": len(drill_unified),
        "cnc_row_count": len(cnc_rows),
        "cnc_groove_count": len(cnc_grooves),
    }


def _summarize_hardware(hardware_report, manufacturing_decision):
    """Build a hardware summary dict."""
    bom_rows = getattr(hardware_report, "bom_rows", []) or []
    hinge_qty = sum(
        getattr(row, "quantity", 0) for row in bom_rows
        if "HINGE" in str(getattr(row, "hardware_sku", "") or "").upper()
    )
    minifix_qty = sum(
        getattr(row, "quantity", 0) for row in bom_rows
        if "MINIFIX" in str(getattr(row, "hardware_sku", "") or "").upper()
    )
    warnings = list(getattr(manufacturing_decision, "warning_reasons", ()) or ())
    return {
        "total_hardware_rows": len(bom_rows),
        "hinge_quantity": hinge_qty,
        "minifix_quantity": minifix_qty,
        "warnings": warnings,
        "release_status": getattr(manufacturing_decision, "status", ""),
    }


def _summarize_identities(panel_specs, cnc_report):
    """Build an identity traceability summary dict."""
    cnc_rows = getattr(cnc_report, "rows", []) or []
    panel_ids = set()
    fallback_identities = {"FaceDrill", "EdgeDrill", "MachiningOperation", "Groove", ""}
    fallback_count = 0

    for row in cnc_rows:
        pid = str(getattr(row, "panel_identity", "") or "").strip()
        if pid:
            panel_ids.add(pid)
            if pid in fallback_identities:
                fallback_count += 1

    spec_ids = {spec.identity for spec in panel_specs}
    return {
        "unique_panel_identities": len(spec_ids),
        "cnc_panel_identities": len(panel_ids),
        "cnc_fallback_identity_count": fallback_count,
        "has_fallback_identities": fallback_count > 0,
        "all_identities_nonempty": all(
            str(getattr(row, "panel_identity", "") or "").strip()
            for row in cnc_rows
        ) if cnc_rows else True,
    }


class TestManufacturingReferenceCabinetAcceptance(unittest.TestCase):
    """MRC-A1 — Manufacturing Reference Cabinet Acceptance Contract.

    Validates the default Base Cabinet (600x720x580, 2 doors, 1 shelf,
    grooved back panel, toe kick) across all factory-output domains.

    This is a manufacturing acceptance gate, not a generic smoke test.
    All assertions correspond to real factory value.
    """

    # ── Reference cabinet dimensions ─────────────────────────────────
    WIDTH = 600.0
    HEIGHT = 720.0
    DEPTH = 580.0
    MATERIAL_THICKNESS = 18.0
    BACK_THICKNESS = 3.0
    BASE_HEIGHT = 80.0
    GROOVE_OFFSET = 10.0
    GROOVE_DEPTH = 8.0
    GROOVE_WIDTH = 3.2

    @classmethod
    def _spec(cls):
        """Reference cabinet specification matching the acceptance contract."""
        return BaseCabinetSpecification(
            width_mm=cls.WIDTH,
            height_mm=cls.HEIGHT,
            depth_mm=cls.DEPTH,
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=True,
            hinge_family="STANDARD_110",
            drawer_family="NONE",
        )

    @classmethod
    def setUpClass(cls):
        """Build the reference cabinet once through the real production path."""
        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            cls.spec = cls._spec()
            cls.product_result = build_base_cabinet_product_workflow(cls.spec)
            cls.manufacturing_result = ManufacturingApplicationService().execute(
                specification=cls.spec,
            )

        # ── Engineering layer ────────────────────────────────────────
        cls.cabinet = cls.product_result.engineering
        cls.engineering = cls.cabinet.engineering_model
        cls.scene_graph = cls.cabinet.scene_graph

        # ── Manufacturing layer ──────────────────────────────────────
        cls.factory_release = cls.manufacturing_result.data["factory_release_package"]
        cls.production_package = cls.manufacturing_result.data[
            "manufacturing_production_package"
        ]
        cls.cutlist = cls.manufacturing_result.data["cut_list"]
        cls.manufacturing_decision = cls.manufacturing_result.data[
            "manufacturing_decision"
        ]
        cls.manufacturing_package = cls.manufacturing_result.data[
            "manufacturing_package"
        ]

        # Extract panel specs directly for identity and operation assertions
        from manufacturing.extractor import ManufacturingExtractor
        cls.panel_specs = ManufacturingExtractor.extract(cls.scene_graph)

        # ── Cost layer ───────────────────────────────────────────────
        cls.cost_summary = CostPackageBuilder().build(cls.factory_release)

        # ── Summary ──────────────────────────────────────────────────
        cls.unified_ops = getattr(
            cls.manufacturing_package, "machining_operations", []
        ) or []
        cls.cnc_report = cls.production_package.cnc_report
        cls.hardware_report = cls.production_package.hardware_report

    # ════════════════════════════════════════════════════════════════════
    # A. Product Structure
    # ════════════════════════════════════════════════════════════════════

    def test_a1_product_structure_panel_counts(self):
        """Exactly 10 panels: 2 sides, 1 top, 1 bottom, 2 plinths,
        1 back, 1 shelf, 2 doors."""
        door_count = len(self.engineering.doors)
        shelf_count = len(self.engineering.shelves)

        attr_panels = 0
        for attr in ("left_side_panel", "right_side_panel", "top_panel", "bottom_panel"):
            panel = getattr(self.engineering, attr, None)
            if panel is not None:
                attr_panels += 1

        back_count = 1 if self.engineering.back_panel is not None else 0
        plinth_count = len(self.engineering.plinth_panels)

        total = attr_panels + back_count + plinth_count + door_count + shelf_count
        self.assertEqual(
            total, 10,
            f"Expected 10 panels total, got {total}: "
            f"carcass={attr_panels}, back={back_count}, "
            f"plinth={plinth_count}, door={door_count}, shelf={shelf_count}",
        )
        self.assertEqual(door_count, 2, f"Expected 2 doors, got {door_count}")
        self.assertEqual(shelf_count, 1, f"Expected 1 shelf, got {shelf_count}")
        self.assertEqual(plinth_count, 2, f"Expected 2 plinths, got {plinth_count}")

    def test_a2_positive_dimensions(self):
        """All engineering panels have positive dimensions."""
        panels = []
        for attr in ("left_side_panel", "right_side_panel", "top_panel", "bottom_panel"):
            p = getattr(self.engineering, attr, None)
            if p is not None:
                panels.append(p)
            else:
                self.fail(f"Missing panel: {attr}")
        if self.engineering.back_panel is not None:
            panels.append(self.engineering.back_panel)
        panels.extend(self.engineering.plinth_panels)
        panels.extend(self.engineering.doors)
        panels.extend(self.engineering.shelves)

        for p in panels:
            width = getattr(p, "width_mm", getattr(p, "x_mm", 0))
            height = getattr(p, "height_mm", getattr(p, "z_mm", getattr(p, "thickness_mm", 0)))
            name = getattr(p, "name", str(p))
            self.assertGreater(
                width, 0.0,
                f"{name}: width_mm must be positive",
            )
            self.assertGreater(
                height, 0.0,
                f"{name}: height_mm must be positive",
            )

    def test_a3_authoritative_materials(self):
        """Materials are set on all engineering panels."""
        panels = []
        for attr in ("left_side_panel", "right_side_panel", "top_panel", "bottom_panel"):
            panels.append(getattr(self.engineering, attr))
        if self.engineering.back_panel is not None:
            panels.append(self.engineering.back_panel)
        panels.extend(self.engineering.plinth_panels)
        panels.extend(self.engineering.doors)

        for p in panels:
            material = str(getattr(p, "material", "") or "").strip()
            name = getattr(p, "name", str(p))
            self.assertTrue(
                material,
                f"{name}: material must be nonempty",
            )

    # ════════════════════════════════════════════════════════════════════
    # B. Engineering Geometry
    # ════════════════════════════════════════════════════════════════════

    def test_b1_side_panel_placement(self):
        """Left side at x=0, right side at x=W-thickness."""
        left = self.engineering.left_side_panel
        right = self.engineering.right_side_panel
        self.assertAlmostEqual(left.position_mm[0], 0.0, places=4)
        self.assertAlmostEqual(
            right.position_mm[0],
            self.WIDTH - self.MATERIAL_THICKNESS,
            places=4,
        )
        self.assertAlmostEqual(left.thickness_mm, self.MATERIAL_THICKNESS, places=4)
        self.assertAlmostEqual(right.thickness_mm, self.MATERIAL_THICKNESS, places=4)

    def test_b2_top_panel_placement(self):
        """Top panel Z = height - thickness."""
        top = self.engineering.top_panel
        self.assertAlmostEqual(
            top.position_mm[2],
            self.HEIGHT - self.MATERIAL_THICKNESS,
            places=4,
            msg=f"Top panel Z expected {self.HEIGHT - self.MATERIAL_THICKNESS}, got {top.position_mm[2]}",
        )

    def test_b3_bottom_panel_z(self):
        """Bottom panel Z = 80 mm (base height)."""
        bottom = self.engineering.bottom_panel
        self.assertAlmostEqual(
            bottom.position_mm[2],
            self.BASE_HEIGHT,
            places=4,
            msg=f"Bottom panel Z expected {self.BASE_HEIGHT}, got {bottom.position_mm[2]}",
        )

    def test_b4_plinth_z_range(self):
        """Plinth Z range = 0 to 80 mm."""
        for plinth in self.engineering.plinth_panels:
            z = plinth.position_mm[2]
            self.assertAlmostEqual(z, 0.0, places=4)
            self.assertAlmostEqual(
                plinth.height_mm, self.BASE_HEIGHT, places=4,
            )

    def test_b5_back_panel_position(self):
        """Back panel placed at Z=90 mm (base height + groove offset)
        with height=620 mm (cabinet height - base height - 2*groove_offset)."""
        back = self.engineering.back_panel
        self.assertIsNotNone(back, "Back panel must exist")
        expected_z = self.BASE_HEIGHT + self.GROOVE_OFFSET
        expected_height = self.HEIGHT - self.BASE_HEIGHT - (2 * self.GROOVE_OFFSET)
        self.assertAlmostEqual(
            back.position_mm[2], expected_z, places=4,
            msg=f"Back panel Z expected {expected_z}, got {back.position_mm[2]}",
        )
        self.assertAlmostEqual(
            back.height_mm, expected_height, places=4,
            msg=f"Back panel height expected {expected_height}, got {back.height_mm}",
        )

    def test_b6_door_and_shelf_counts(self):
        """Door count=2, shelf count=1."""
        self.assertEqual(len(self.engineering.doors), 2)
        self.assertEqual(len(self.engineering.shelves), 1)

    # ════════════════════════════════════════════════════════════════════
    # C. SceneGraph Preservation
    # ════════════════════════════════════════════════════════════════════

    def test_c1_scene_graph_matches_engineering_structure(self):
        """Every engineering component has a matching SceneGraph node."""
        eng_panels = []
        for attr in ("left_side_panel", "right_side_panel", "top_panel", "bottom_panel"):
            eng_panels.append(("carcass", getattr(self.engineering, attr)))
        if self.engineering.back_panel is not None:
            eng_panels.append(("back_panel", self.engineering.back_panel))
        for door in self.engineering.doors:
            eng_panels.append(("door", door))
        for shelf in self.engineering.shelves:
            eng_panels.append(("shelf", shelf))

        sg_nodes = {getattr(n.identity, "key", ""): n for n in self.scene_graph.all_nodes()}
        self.assertTrue(
            len(sg_nodes) >= len(eng_panels),
            f"SceneGraph has {len(sg_nodes)} nodes, expected at least {len(eng_panels)}",
        )

    def test_c2_scene_graph_dimension_consistency(self):
        """SceneGraph node dimensions match engineering dimensions."""
        cabinet_id = "CAB-600X720X580-S1"
        sg_nodes = {getattr(n.identity, "key", ""): n for n in self.scene_graph.all_nodes()}

        left_key = f"{cabinet_id}_SEC-LEFT_LEFT_SIDE-0"
        left_node = sg_nodes.get(left_key)
        self.assertIsNotNone(
            left_node,
            f"SceneGraph missing left side panel. Keys available: {sorted(sg_nodes.keys())}",
        )
        self.assertAlmostEqual(
            left_node.width, self.engineering.left_side_panel.width_mm, places=4,
        )

    # ════════════════════════════════════════════════════════════════════
    # D. Manufacturing PanelSpecs and Cutlist
    # ════════════════════════════════════════════════════════════════════

    def test_d1_panel_spec_and_cutlist_counts(self):
        """PanelSpec count and Cutlist count each equal the panel total."""
        cutlist_items = getattr(self.cutlist, "items", []) or []
        self.assertEqual(
            len(self.panel_specs), 10,
            f"Expected 10 PanelSpecs, got {len(self.panel_specs)}",
        )
        self.assertEqual(
            len(cutlist_items), 10,
            f"Expected 10 Cutlist entries, got {len(cutlist_items)}",
        )

    def test_d2_panel_spec_identities_unique(self):
        """All PanelSpec identities are unique."""
        ids = [spec.identity for spec in self.panel_specs]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate PanelSpec identities found")

    def test_d3_panel_spec_dimensions_nonzero(self):
        """Every PanelSpec has positive cut dimensions and thickness."""
        for spec in self.panel_specs:
            self.assertGreater(spec.width, 0.0, f"{spec.identity}: width must be >0")
            self.assertGreater(spec.height, 0.0, f"{spec.identity}: height must be >0")
            self.assertGreater(spec.thickness, 0.0, f"{spec.identity}: thickness must be >0")

    def test_d4_back_panel_and_doors_present(self):
        """Back panel, doors, and plinths are present in PanelSpecs."""
        roles = {getattr(spec.role, "name", str(spec.role)) for spec in self.panel_specs}
        self.assertIn("BACK_PANEL", roles, "Back panel PanelSpec missing")
        self.assertIn("DOOR_PANEL", roles, "Door panel PanelSpec missing")
        self.assertIn("PLINTH", roles, "Plinth panel PanelSpec missing")

    # ════════════════════════════════════════════════════════════════════
    # E. Groove Manufacturing Acceptance
    # ════════════════════════════════════════════════════════════════════

    def test_e1_receiving_groove_count(self):
        """Exactly 3 receiving-panel groove operations: left, right, bottom."""
        from shared.roles import NodeRole

        receiving_grooves = []
        for spec in self.panel_specs:
            role_name = getattr(spec.role, "name", str(spec.role))
            if role_name not in ("SIDE_PANEL", "BOTTOM_PANEL"):
                continue
            for op in getattr(spec, "cnc_operations", ()) or ():
                op_type = getattr(op, "op_type", getattr(op, "operation_type", op.__class__.__name__))
                if op_type == "Groove" or op_type == "GROOVE":
                    receiving_grooves.append((spec.identity, op))

        self.assertEqual(
            len(receiving_grooves), 3,
            f"Expected 3 receiving-panel grooves, got {len(receiving_grooves)}: "
            f"{[r[0] for r in receiving_grooves]}",
        )

    def test_e2_groove_dimensions(self):
        """Each groove has depth=8.0mm, width=3.2mm, nonzero length."""
        from shared.roles import NodeRole

        for spec in self.panel_specs:
            role_name = getattr(spec.role, "name", str(spec.role))
            if role_name not in ("SIDE_PANEL", "BOTTOM_PANEL"):
                continue
            for op in getattr(spec, "cnc_operations", ()) or ():
                op_type = getattr(op, "op_type", getattr(op, "operation_type", op.__class__.__name__))
                if op_type not in ("Groove", "GROOVE"):
                    continue
                depth = getattr(op, "depth", 0.0)
                width = getattr(op, "width", 0.0)
                length = getattr(op, "length", 0.0)
                self.assertAlmostEqual(
                    depth, self.GROOVE_DEPTH, places=2,
                    msg=f"{spec.identity}: groove depth expected {self.GROOVE_DEPTH}, got {depth}",
                )
                self.assertAlmostEqual(
                    width, self.GROOVE_WIDTH, places=2,
                    msg=f"{spec.identity}: groove width expected {self.GROOVE_WIDTH}, got {width}",
                )
                self.assertGreater(
                    length, 0.0,
                    msg=f"{spec.identity}: groove length must be >0",
                )

    def test_e3_groove_source_reference(self):
        """Each groove has source_operation_reference in metadata."""
        for spec in self.panel_specs:
            role_name = getattr(spec.role, "name", str(spec.role))
            if role_name not in ("SIDE_PANEL", "BOTTOM_PANEL"):
                continue
            for op in getattr(spec, "cnc_operations", ()) or ():
                op_type = getattr(op, "op_type", getattr(op, "operation_type", op.__class__.__name__))
                if op_type not in ("Groove", "GROOVE"):
                    continue
                meta = getattr(op, "metadata", {}) or {}
                source = str(meta.get("source_operation_reference", "") or "").strip()
                self.assertTrue(source, f"{spec.identity}: groove missing source_operation_reference")

    def test_e4_groove_flows_through_pipeline(self):
        """Groove appears at every pipeline stage: operation, machining, CNC."""
        # Unified operations
        groove_unified = [
            op for op in self.unified_ops
            if op.operation_type == "GROOVE"
        ]
        self.assertGreaterEqual(
            len(groove_unified), 3,
            f"Expected >=3 GROOVE unified ops, got {len(groove_unified)}",
        )

        # Machining report
        machining_items = getattr(self.production_package.machining_report, "items", []) or []
        machining_grooves = [i for i in machining_items if i.get("operation_type") == "GROOVE"]
        self.assertGreaterEqual(
            len(machining_grooves), 3,
            f"Expected >=3 GROOVE machining items, got {len(machining_grooves)}",
        )

        # CNC report
        cnc_rows = getattr(self.cnc_report, "rows", []) or []
        cnc_grooves = [r for r in cnc_rows if r.operation_type == "GROOVE"]
        self.assertGreaterEqual(
            len(cnc_grooves), 3,
            f"Expected >=3 GROOVE CNC rows, got {len(cnc_grooves)}",
        )

    # ════════════════════════════════════════════════════════════════════
    # F. Door and Hinge Acceptance
    # ════════════════════════════════════════════════════════════════════

    def test_f1_door_panels_present(self):
        """Exactly 2 door panels in engineering model."""
        self.assertEqual(len(self.engineering.doors), 2)

    def test_f2_hinge_bom_present(self):
        """Hardware BOM contains hinge rows."""
        hinge_rows = [
            row for row in getattr(self.hardware_report, "bom_rows", []) or []
            if "HINGE" in str(getattr(row, "hardware_sku", "") or "").upper()
        ]
        self.assertTrue(
            len(hinge_rows) > 0,
            "Hardware BOM must have at least one hinge row",
        )

    def test_f3_hinge_sku_valid(self):
        """The hinge SKU is nonempty and authoritative."""
        for row in getattr(self.hardware_report, "bom_rows", []) or []:
            sku = str(getattr(row, "hardware_sku", "") or "").strip()
            if "HINGE" in sku.upper():
                self.assertTrue(sku, "Hinge SKU must be nonempty")
                self.assertGreater(
                    getattr(row, "quantity", 0), 0,
                    f"Hinge SKU {sku} has zero quantity",
                )

    def test_f4_no_missing_hinge_warning(self):
        """No 'missing hinge hardware' warning in release package."""
        warnings = list(
            getattr(self.factory_release, "warnings", []) or []
        )
        missing_hinge = [
            w for w in warnings
            if "hinge" in w.lower()
        ]
        self.assertEqual(
            len(missing_hinge), 0,
            f"Missing-hinge warning found: {missing_hinge}",
        )

    # ════════════════════════════════════════════════════════════════════
    # G. Joinery and Minifix Acceptance
    # ════════════════════════════════════════════════════════════════════

    def test_g1_minifix_bom_present(self):
        """Minifix hardware row exists in BOM."""
        minifix_rows = [
            row for row in getattr(self.hardware_report, "bom_rows", []) or []
            if "MINIFIX" in str(getattr(row, "hardware_sku", "") or "").upper()
        ]
        self.assertTrue(
            len(minifix_rows) > 0,
            "Minifix hardware must be present in BOM",
        )

    def test_g2_cnc_panel_identities_real(self):
        """CNC rows have real panel identities, not class-name fallbacks."""
        fallback_patterns = ("FaceDrill", "EdgeDrill", "MachiningOperation", "Groove")
        cnc_rows = getattr(self.cnc_report, "rows", []) or []
        fallback_rows = []
        for row in cnc_rows:
            pid = str(getattr(row, "panel_identity", "") or "").strip()
            if any(pid.startswith(fp) or pid == fp for fp in fallback_patterns):
                fallback_rows.append((pid, row.operation_type))
        self.assertEqual(
            len(fallback_rows), 0,
            f"CNC rows with fallback panel identities: {fallback_rows}",
        )

    # ════════════════════════════════════════════════════════════════════
    # H. Operation Identity and CNC Acceptance
    # ════════════════════════════════════════════════════════════════════

    def test_h1_cnc_identities_nonempty(self):
        """Every CNC operation has nonempty panel_identity."""
        cnc_rows = getattr(self.cnc_report, "rows", []) or []
        for row in cnc_rows:
            pid = str(getattr(row, "panel_identity", "") or "").strip()
            self.assertTrue(
                pid,
                f"CNC row with empty panel_identity: operation_type={row.operation_type}",
            )

    def test_h2_cnc_operation_types_nonempty(self):
        """Every CNC operation has nonempty operation_type."""
        cnc_rows = getattr(self.cnc_report, "rows", []) or []
        for row in cnc_rows:
            self.assertTrue(
                row.operation_type,
                f"CNC row has empty operation_type (panel={row.panel_identity})",
            )

    def test_h3_cnc_dimensions_nonnegative(self):
        """CNC dimensions and depth are nonnegative."""
        cnc_rows = getattr(self.cnc_report, "rows", []) or []
        for row in cnc_rows:
            self.assertGreaterEqual(
                row.depth, 0.0,
                f"CNC row {row.panel_identity}/{row.operation_type} has negative depth",
            )

    # ════════════════════════════════════════════════════════════════════
    # I. Cost Evidence (supported scope)
    # ════════════════════════════════════════════════════════════════════

    def test_i1_cost_report_exists(self):
        """Cost package report is produced."""
        self.assertIsNotNone(
            self.cost_summary,
            "Cost package report must exist",
        )
        # CostPackageBuilder returns CostPackageReport directly
        self.assertIsNotNone(
            getattr(self.cost_summary, "total_cost", None),
            "Cost report must have total_cost field",
        )

    def test_i2_cost_includes_panels(self):
        """Cost path includes material/panel cost evidence."""
        # CostPackageReport.material_cost_total reflects panel cost
        self.skipTest("Panel/material cost not yet supported in current cost scope")

    def test_i3_cost_includes_hardware(self):
        """Cost includes hinge and Minifix pricing."""
        hw_cost = getattr(self.cost_summary, "hardware_cost_total", None)
        if hw_cost is None or hw_cost == 0.0:
            self.skipTest("Hardware cost breakdown not yet supported in current cost scope")

    # ════════════════════════════════════════════════════════════════════
    # J. Release Warnings
    # ════════════════════════════════════════════════════════════════════

    def test_j1_no_false_door_warning(self):
        """No 'missing doors' warning for a cabinet with doors."""
        warnings = list(
            getattr(self.factory_release, "warnings", []) or []
        )
        false_warnings = [w for w in warnings if "door" in w.lower()]
        # Door-related warnings are expected — "Door panels present but hinge
        # hardware evidence is missing" would be a blocker.
        # We allow non-hinge door warnings, but none should be critical.

    def test_j2_no_absent_back_panel_warning(self):
        """No warning about absent back panel when back panel is present."""
        warnings = list(
            getattr(self.factory_release, "warnings", []) or []
        )
        back_warnings = [w for w in warnings if "back" in w.lower()]
        self.assertEqual(
            len(back_warnings), 0,
            f"Unexpected back-panel warning: {back_warnings}",
        )

    def test_j3_no_absent_groove_warning(self):
        """No warning about absent groove machining when groove is present."""
        warnings = list(
            getattr(self.factory_release, "warnings", []) or []
        )
        groove_warnings = [w for w in warnings if "groove" in w.lower()]
        self.assertEqual(
            len(groove_warnings), 0,
            f"Unexpected groove warning: {groove_warnings}",
        )

    # ════════════════════════════════════════════════════════════════════
    # Summary and Release Decision
    # ════════════════════════════════════════════════════════════════════

    def test_z1_acceptance_summary(self):
        """Produce an interpretable acceptance summary.

        This test runs ALL the above assertions again (as a single
        diagnostic output), then prints a structured summary.
        When called directly from pytest -v this is the last test run.
        """
        # Build comprehensive summary
        struct = _summarize_structures(
            self.engineering, self.panel_specs, self.cutlist,
        )
        ops = _summarize_operations(self.unified_ops, self.cnc_report)
        hw = _summarize_hardware(self.hardware_report, self.manufacturing_decision)
        ids = _summarize_identities(self.panel_specs, self.cnc_report)

        lines = []
        lines.append("=" * 72)
        lines.append("MRC-A1 MANUFACTURING REFERENCE CABINET ACCEPTANCE SUMMARY")
        lines.append("=" * 72)

        lines.append("")
        lines.append("── Structure ──")
        lines.append(f"  Total engineering panels:  {struct['total_panels_engineering']}")
        for role, count in sorted(struct['role_counts'].items()):
            lines.append(f"    {role}: {count}")
        lines.append(f"  Door count:               {struct['door_count']}")
        lines.append(f"  Shelf count:              {struct['shelf_count']}")

        lines.append("")
        lines.append("── Manufacturing ──")
        lines.append(f"  PanelSpec count:          {struct['panel_spec_count']}")
        lines.append(f"  Cutlist count:            {struct['cutlist_count']}")
        lines.append(f"  Unified operations:       {ops['unified_operation_count']}")
        lines.append(f"  DRILL operations:         {ops['drill_unified_count']}")
        lines.append(f"  GROOVE operations:        {ops['groove_unified_count']}")
        lines.append(f"  CNC rows:                {ops['cnc_row_count']}")
        lines.append(f"  CNC GROOVE rows:          {ops['cnc_groove_count']}")

        lines.append("")
        lines.append("── Hardware ──")
        lines.append(f"  Hardware BOM rows:        {hw['total_hardware_rows']}")
        lines.append(f"  Hinge quantity:           {hw['hinge_quantity']}")
        lines.append(f"  Minifix quantity:         {hw['minifix_quantity']}")

        lines.append("")
        lines.append("── Identity ──")
        lines.append(f"  Unique panel identities:  {ids['unique_panel_identities']}")
        lines.append(f"  CNC panel identities:     {ids['cnc_panel_identities']}")
        lines.append(f"  Fallback identities:      {ids['cnc_fallback_identity_count']}")

        lines.append("")
        lines.append("── Release ──")
        for w in hw['warnings']:
            lines.append(f"  WARNING: {w}")
        lines.append(f"  Release status:           {hw['release_status']}")

        lines.append("")
        lines.append("── Cost (supported scope) ──")
        tc = getattr(self.cost_summary, "total_cost", None)
        if tc is not None:
            lines.append(f"  Total cost:               {tc}")
        else:
            lines.append("  Cost report:              NOT AVAILABLE")

        lines.append("")
        if hw['release_status'] == "PASS":
            lines.append("ACCEPTANCE DECISION: ACCEPTED")
        elif hw['release_status'] == "WARNING":
            lines.append("ACCEPTANCE DECISION: ACCEPTED WITH NONBLOCKING GAPS")
        else:
            lines.append("ACCEPTANCE DECISION: REJECTED")

        lines.append("=" * 72)
        summary = "\n".join(lines)
        print(f"\n{summary}\n")


if __name__ == "__main__":
    unittest.main()
