import unittest


class TestBackPanelValidationBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.back_panel_validation_builder import (
            BackPanelValidationBuilder,
        )

        self.builder = BackPanelValidationBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_back_panel_validation_report(self):
        from manufacturing.back_panel_validation_report import (
            BackPanelValidationReport,
        )

        report = self.builder.build(self._hole_rules_report(), self._intent_report())

        self.assertIsInstance(report, BackPanelValidationReport)

    def test_invalid_width_blocks_validation(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=0),
            self._intent_report(),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertEqual(report.recommended_action, "Review back panel manufacturing rules")

    def test_wide_panel_creates_medium_width_risk(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=800),
            self._intent_report(),
        )

        self.assertEqual(report.width_risk, "MEDIUM")

    def test_tall_panel_creates_medium_height_risk(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_height=1800),
            self._intent_report(),
        )

        self.assertEqual(report.height_risk, "MEDIUM")

    def test_excessive_spacing_creates_medium_spacing_risk(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=301),
            self._intent_report(),
        )

        self.assertEqual(report.spacing_risk, "MEDIUM")

    def test_wide_panel_requires_center_support(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=800),
            self._intent_report(requires_center_support=False),
        )

        self.assertTrue(report.center_support_required)

    def test_tall_panel_requires_center_support(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_height=1800),
            self._intent_report(requires_center_support=False),
        )

        self.assertTrue(report.center_support_required)

    def test_geometry_report_absent_preserves_center_support_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=10, minimum_panel_height=10),
            self._intent_report(requires_center_support=False),
        )

        self.assertFalse(report.center_support_required)

    def test_geometry_report_width_above_threshold_sets_center_support(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=10, minimum_panel_height=10),
            self._intent_report(requires_center_support=False),
            geometry_report=self._geometry_report(width=800.0, height=100.0),
        )

        self.assertTrue(report.center_support_required)

    def test_geometry_report_height_above_threshold_sets_center_support(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=10, minimum_panel_height=10),
            self._intent_report(requires_center_support=False),
            geometry_report=self._geometry_report(width=100.0, height=1800.0),
        )

        self.assertTrue(report.center_support_required)

    def test_geometry_report_below_thresholds_does_not_force_center_support(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=10, minimum_panel_height=10),
            self._intent_report(requires_center_support=False),
            geometry_report=self._geometry_report(width=799.9, height=1799.9),
        )

        self.assertFalse(report.center_support_required)

    def test_geometry_report_does_not_override_existing_hole_rules_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=800, minimum_panel_height=10),
            self._intent_report(requires_center_support=False),
            geometry_report=self._geometry_report(width=100.0, height=100.0),
        )

        self.assertTrue(report.center_support_required)

    def test_medium_risks_remain_valid(self):
        report = self.builder.build(
            self._hole_rules_report(
                minimum_panel_width=800,
                minimum_panel_height=1800,
                maximum_spacing=301,
            ),
            self._intent_report(),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")

    def test_medium_risks_create_manufacturing_warning(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_width=800),
            self._intent_report(),
        )

        self.assertEqual(
            report.manufacturing_warning,
            "Wide back panel requires structural review",
        )
        self.assertEqual(report.recommended_action, "Review back panel engineering rules")

    def test_invalid_height_blocks_validation(self):
        report = self.builder.build(
            self._hole_rules_report(minimum_panel_height=0),
            self._intent_report(),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertEqual(report.recommended_action, "Review back panel manufacturing rules")

    def test_invalid_spacing_blocks_validation(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=0),
            self._intent_report(),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertEqual(report.recommended_action, "Review back panel manufacturing rules")

    def test_center_holes_are_propagated(self):
        report = self.builder.build(
            self._hole_rules_report(requires_center_holes=True),
            self._intent_report(),
        )

        self.assertTrue(report.center_holes_required)

    def test_center_support_is_propagated(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(requires_center_support=True),
        )

        self.assertTrue(report.center_support_required)

    def test_missing_fixing_method_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(requires_groove=False, requires_fasteners=False),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.fixing_method_warning, "Back panel has no fixing method")
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertEqual(report.recommended_action, "Review back panel engineering rules")

    def test_visual_manufacturing_intent_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(visual_manufacturing_intent_required=True),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(
            report.manufacturing_warning,
            "Back panel requires visual manufacturing intent review",
        )
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertEqual(report.recommended_action, "Review back panel manufacturing intent")

    def test_valid_report_is_valid(self):
        report = self.builder.build(
            self._hole_rules_report(
                minimum_panel_width=10,
                minimum_panel_height=10,
                maximum_spacing=5,
            ),
            self._intent_report(requires_groove=True),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID")
        self.assertEqual(report.fixing_method_warning, "")
        self.assertEqual(report.manufacturing_warning, "")
        self.assertEqual(report.recommended_action, "")

    def test_hole_spacing_above_maximum_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(default_spacing=6),
            hole_pattern_report=self._pattern_report(total_hole_count=4),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn("Back panel hole spacing exceeds maximum spacing", report.manufacturing_warning)

    def test_coordinate_count_mismatch_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="TOP"),
                    self._coordinate(x=4, y=10, face="TOP"),
                ],
            ),
            hole_pattern_report=self._pattern_report(total_hole_count=3),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_coordinate_count_match_creates_no_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="TOP"),
                    self._coordinate(x=4, y=10, face="TOP"),
                ],
            ),
            hole_pattern_report=self._pattern_report(
                total_hole_count=2,
                top_edge_holes=1,
                bottom_edge_holes=1,
                left_edge_holes=1,
                right_edge_holes=1,
                pattern_type="PERIMETER",
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID")
        self.assertNotIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_placement_report_absent_preserves_existing_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(
                total_hole_count=2,
                top_edge_holes=1,
                bottom_edge_holes=1,
                left_edge_holes=1,
                right_edge_holes=1,
                pattern_type="PERIMETER",
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID")
        self.assertNotIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_pattern_report_absent_preserves_existing_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="TOP"),
                    self._coordinate(x=4, y=10, face="TOP"),
                ],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID")
        self.assertNotIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_empty_hole_positions_preserves_existing_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=6,
                hole_positions=[],
            ),
            hole_pattern_report=self._pattern_report(total_hole_count=4),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn("Back panel hole spacing exceeds maximum spacing", report.manufacturing_warning)
        self.assertNotIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_total_hole_count_zero_preserves_existing_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=6,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="TOP"),
                    self._coordinate(x=4, y=10, face="TOP"),
                ],
            ),
            hole_pattern_report=self._pattern_report(
                total_hole_count=0,
                pattern_type="PERIMETER",
            ),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertNotIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_coordinate_count_mismatch_coexists_with_spacing_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=2),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="TOP"),
                    self._coordinate(x=5, y=10, face="TOP"),
                ],
            ),
            hole_pattern_report=self._pattern_report(total_hole_count=3),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn(
            "Back panel hole coordinate spacing exceeds maximum spacing",
            report.manufacturing_warning,
        )
        self.assertIn(
            "Back panel hole coordinate count does not match pattern count",
            report.manufacturing_warning,
        )

    def test_horizontal_face_coordinate_spacing_above_maximum_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="top"),
                    self._coordinate(x=7, y=10, face="TOP"),
                ],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn(
            "Back panel hole coordinate spacing exceeds maximum spacing",
            report.manufacturing_warning,
        )

    def test_vertical_face_coordinate_spacing_above_maximum_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=10, y=0, face="left"),
                    self._coordinate(x=10, y=8, face="LEFT"),
                ],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn(
            "Back panel hole coordinate spacing exceeds maximum spacing",
            report.manufacturing_warning,
        )

    def test_coordinate_spacing_within_maximum_creates_no_coordinate_warning(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="bottom"),
                    self._coordinate(x=5, y=10, face="BOTTOM"),
                ],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID")
        self.assertNotIn(
            "Back panel hole coordinate spacing exceeds maximum spacing",
            report.manufacturing_warning,
        )

    def test_unknown_or_empty_faces_are_ignored_and_default_spacing_fallback_applies(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=6,
                hole_positions=[
                    self._coordinate(x=0, y=0, face=""),
                    self._coordinate(x=9, y=9, face="unknown"),
                    self._coordinate(x=50, y=50, face=None),
                ],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn("Back panel hole spacing exceeds maximum spacing", report.manufacturing_warning)
        self.assertNotIn(
            "Back panel hole coordinate spacing exceeds maximum spacing",
            report.manufacturing_warning,
        )

    def test_empty_hole_positions_keeps_default_spacing_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=6,
                hole_positions=[],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn("Back panel hole spacing exceeds maximum spacing", report.manufacturing_warning)

    def test_coordinate_spacing_inputs_are_not_mutated(self):
        coordinates = [
            self._coordinate(x=0, y=10, face="TOP"),
            self._coordinate(x=8, y=10, face="TOP"),
        ]
        hole_placement_report = self._placement_report(
            default_spacing=1,
            hole_positions=coordinates,
        )

        hole_rules_report = self._hole_rules_report(maximum_spacing=5)
        manufacturing_intent_report = self._intent_report()
        hole_rules_snapshot = self._snapshot(hole_rules_report)
        intent_snapshot = self._snapshot(manufacturing_intent_report)
        placement_snapshot = self._snapshot(hole_placement_report)

        self.builder.build(
            hole_rules_report,
            manufacturing_intent_report,
            hole_placement_report=hole_placement_report,
        )

        self.assertEqual(self._snapshot(hole_rules_report), hole_rules_snapshot)
        self.assertEqual(self._snapshot(manufacturing_intent_report), intent_snapshot)
        self.assertEqual(self._snapshot(hole_placement_report), placement_snapshot)
        self.assertIs(hole_placement_report.hole_positions, coordinates)

    def test_coordinate_count_inputs_are_not_mutated(self):
        coordinates = [
            self._coordinate(x=0, y=10, face="TOP"),
            self._coordinate(x=8, y=10, face="TOP"),
        ]
        hole_placement_report = self._placement_report(
            default_spacing=1,
            hole_positions=coordinates,
        )
        hole_pattern_report = self._pattern_report(total_hole_count=3)

        placement_snapshot = self._snapshot(hole_placement_report)
        pattern_snapshot = self._snapshot(hole_pattern_report)

        self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=hole_placement_report,
            hole_pattern_report=hole_pattern_report,
        )

        self.assertEqual(self._snapshot(hole_placement_report), placement_snapshot)
        self.assertEqual(self._snapshot(hole_pattern_report), pattern_snapshot)
        self.assertIs(hole_placement_report.hole_positions, coordinates)

    def test_coordinate_spacing_does_not_require_panel_dimensions(self):
        report = self.builder.build(
            self._hole_rules_report(maximum_spacing=5),
            self._intent_report(),
            hole_placement_report=self._placement_report(
                default_spacing=1,
                hole_positions=[
                    self._coordinate(x=0, y=10, face="RIGHT"),
                    self._coordinate(x=0, y=16, face="right"),
                ],
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn(
            "Back panel hole coordinate spacing exceeds maximum spacing",
            report.manufacturing_warning,
        )

    def test_required_center_holes_without_center_evidence_blocks_validation(self):
        report = self.builder.build(
            self._hole_rules_report(requires_center_holes=True),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(total_hole_count=4, center_hole_count=0),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertIn(
            "Back panel requires explicit center hole evidence",
            report.manufacturing_warning,
        )

    def test_required_center_holes_with_explicit_center_evidence_does_not_block(self):
        report = self.builder.build(
            self._hole_rules_report(requires_center_holes=True),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(
                total_hole_count=4,
                center_hole_count=2,
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertNotEqual(report.validation_status, "BLOCKED")
        self.assertNotIn(
            "Back panel requires explicit center hole evidence",
            report.manufacturing_warning,
        )

    def test_total_hole_count_alone_does_not_satisfy_center_evidence(self):
        report = self.builder.build(
            self._hole_rules_report(requires_center_holes=True),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(
                total_hole_count=4,
                center_hole_count=0,
            ),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertIn(
            "Back panel requires explicit center hole evidence",
            report.manufacturing_warning,
        )

    def test_required_center_holes_missing_pattern_report_preserves_legacy_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(requires_center_holes=True),
            self._intent_report(),
        )

        self.assertTrue(report.is_valid)
        self.assertNotEqual(report.validation_status, "BLOCKED")
        self.assertNotIn(
            "Back panel requires explicit center hole evidence",
            report.manufacturing_warning,
        )

    def test_missing_edge_coverage_creates_warning(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(
                total_hole_count=4,
                top_edge_holes=2,
                bottom_edge_holes=0,
                left_edge_holes=1,
                right_edge_holes=1,
            ),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn("Back panel hole edge coverage is incomplete", report.manufacturing_warning)

    def test_missing_pattern_type_creates_pattern_suitability_warning(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(total_hole_count=2, pattern_type=""),
        )

        self.assertTrue(report.is_valid)
        self.assertEqual(report.validation_status, "VALID_WITH_WARNINGS")
        self.assertIn("Back panel hole pattern suitability is unclear", report.manufacturing_warning)

    def test_unsupported_screw_placement_blocks_validation(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(
                requires_fasteners=True,
                fastener_type="SCREW",
                back_panel_method="SCREWED",
            ),
            hole_placement_report=self._placement_report(supports_screws=False),
            hole_pattern_report=self._pattern_report(total_hole_count=2),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertIn("Back panel screw support is required but not supported", report.fixing_method_warning)

    def test_unsupported_confirmat_placement_blocks_validation(self):
        report = self.builder.build(
            self._hole_rules_report(),
            self._intent_report(
                requires_fasteners=True,
                fastener_type="CONFIRMAT",
            ),
            hole_placement_report=self._placement_report(supports_confirmat=False),
            hole_pattern_report=self._pattern_report(total_hole_count=2),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.validation_status, "BLOCKED")
        self.assertIn("Back panel confirmat support is required but not supported", report.fixing_method_warning)

    def test_builder_does_not_mutate_inputs(self):
        hole_rules_report = self._hole_rules_report(
            minimum_panel_width=12,
            minimum_panel_height=14,
            maximum_spacing=6,
            requires_center_holes=True,
            tags=["a", "b"],
        )
        manufacturing_intent_report = self._intent_report(
            requires_groove=False,
            requires_fasteners=False,
            visual_notes={"note": "review"},
        )
        hole_placement_report = self._placement_report(
            default_spacing=5,
            supports_screws=True,
            supports_confirmat=True,
            tags=["placement"],
        )
        hole_pattern_report = self._pattern_report(
            total_hole_count=4,
            top_edge_holes=1,
            bottom_edge_holes=1,
            left_edge_holes=1,
            right_edge_holes=1,
            pattern_type="PERIMETER",
            tags=["pattern"],
        )

        hole_rules_snapshot = self._snapshot(hole_rules_report)
        intent_snapshot = self._snapshot(manufacturing_intent_report)
        placement_snapshot = self._snapshot(hole_placement_report)
        pattern_snapshot = self._snapshot(hole_pattern_report)

        self.builder.build(
            hole_rules_report,
            manufacturing_intent_report,
            hole_placement_report=hole_placement_report,
            hole_pattern_report=hole_pattern_report,
        )

        self.assertEqual(self._snapshot(hole_rules_report), hole_rules_snapshot)
        self.assertEqual(self._snapshot(manufacturing_intent_report), intent_snapshot)
        self.assertEqual(self._snapshot(hole_placement_report), placement_snapshot)
        self.assertEqual(self._snapshot(hole_pattern_report), pattern_snapshot)

    def test_geometry_report_input_is_not_mutated(self):
        geometry_report = self._geometry_report(width=1200.0, height=1800.0, tags=["geo"])
        geometry_snapshot = self._snapshot(geometry_report)

        self.builder.build(
            self._hole_rules_report(minimum_panel_width=10, minimum_panel_height=10),
            self._intent_report(),
            geometry_report=geometry_report,
        )

        self.assertEqual(self._snapshot(geometry_report), geometry_snapshot)

    def test_requires_center_holes_false_preserves_existing_behavior(self):
        report = self.builder.build(
            self._hole_rules_report(requires_center_holes=False),
            self._intent_report(),
            hole_pattern_report=self._pattern_report(total_hole_count=4),
        )

        self.assertTrue(report.is_valid)
        self.assertNotEqual(report.validation_status, "BLOCKED")
        self.assertNotIn(
            "Back panel requires explicit center hole evidence",
            report.manufacturing_warning,
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else dict(value)
            if isinstance(value, dict)
            else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _hole_rules_report(
        minimum_panel_width=10,
        minimum_panel_height=10,
        maximum_spacing=5,
        requires_center_holes=False,
        tags=None,
    ):
        from manufacturing.back_panel_hole_rule_report import (
            BackPanelHoleRuleReport,
        )

        report = BackPanelHoleRuleReport(
            minimum_panel_width=minimum_panel_width,
            minimum_panel_height=minimum_panel_height,
            maximum_spacing=maximum_spacing,
            requires_center_holes=requires_center_holes,
        )
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _intent_report(
        requires_groove=True,
        requires_fasteners=True,
        requires_center_support=False,
        fastener_type="",
        back_panel_method="",
        visual_manufacturing_intent_required=False,
        visual_notes=None,
    ):
        from manufacturing.back_panel_manufacturing_intent_report import (
            BackPanelManufacturingIntentReport,
        )

        report = BackPanelManufacturingIntentReport(
            requires_groove=requires_groove,
            requires_fasteners=requires_fasteners,
            requires_center_support=requires_center_support,
            fastener_type=fastener_type,
            back_panel_method=back_panel_method,
            visual_manufacturing_intent_required=visual_manufacturing_intent_required,
        )
        report.visual_notes = dict(visual_notes or {})
        return report

    @staticmethod
    def _placement_report(
        default_spacing=0.0,
        supports_screws=False,
        supports_confirmat=False,
        hole_positions=None,
        tags=None,
    ):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHolePlacementReport,
        )

        report = BackPanelHolePlacementReport(
            default_spacing=default_spacing,
            supports_screws=supports_screws,
            supports_confirmat=supports_confirmat,
        )
        if hole_positions is not None:
            report.hole_positions = hole_positions
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _coordinate(x=0.0, y=0.0, diameter=0.0, depth=0.0, face=""):
        from manufacturing.back_panel_hole_placement_report import (
            BackPanelHoleCoordinate,
        )

        return BackPanelHoleCoordinate(
            x=x,
            y=y,
            diameter=diameter,
            depth=depth,
            face=face,
        )

    @staticmethod
    def _pattern_report(
        total_hole_count=0,
        center_hole_count=0,
        top_edge_holes=0,
        bottom_edge_holes=0,
        left_edge_holes=0,
        right_edge_holes=0,
        pattern_type="",
        tags=None,
    ):
        from manufacturing.back_panel_hole_pattern_report import (
            BackPanelHolePatternReport,
        )

        report = BackPanelHolePatternReport(
            total_hole_count=total_hole_count,
            center_hole_count=center_hole_count,
            top_edge_holes=top_edge_holes,
            bottom_edge_holes=bottom_edge_holes,
            left_edge_holes=left_edge_holes,
            right_edge_holes=right_edge_holes,
            pattern_type=pattern_type,
        )
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _geometry_report(width=0.0, height=0.0, tags=None):
        from manufacturing.back_panel_geometry_report import (
            BackPanelGeometryReport,
        )

        report = BackPanelGeometryReport(width=width, height=height)
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
