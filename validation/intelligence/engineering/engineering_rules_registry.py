class EngineeringRulesRegistry:

    @staticmethod
    def get_rules():

        from validation.intelligence.engineering.rules.shelf_deflection_rule import (
            ShelfDeflectionRule,
        )

        from validation.intelligence.engineering.rules.divider_buckling_rule import (
            DividerBucklingRule,
        )

        from validation.intelligence.engineering.rules.door_sag_rule import (
            DoorSagRule,
        )

        from validation.intelligence.engineering.rules.hanging_cabinet_load_rule import (
            HangingCabinetLoadRule,
        )

        from validation.intelligence.engineering.rules.wide_drawer_deflection_rule import (
            WideDrawerDeflectionRule,
        )

        from validation.intelligence.engineering.rules.countertop_span_rule import (
            CountertopSpanRule,
        )

        from validation.intelligence.engineering.rules.long_door_hinge_rule import (
            LongDoorHingeRule,
        )

        from validation.intelligence.engineering.rules.side_panel_slenderness_rule import (
            SidePanelSlendernessRule,
        )

        from validation.intelligence.engineering.rules.vertical_shelf_support_rule import (
            VerticalShelfSupportRule,
        )

        from validation.intelligence.engineering.rules.tall_divider_stability_rule import (
            TallDividerStabilityRule,
        )

        from validation.intelligence.engineering.rules.back_panel_shear_rule import (
            BackPanelShearRule,
        )

        from validation.intelligence.engineering.rules.basekick_span_rule import (
            BaseKickSpanRule,
        )

        from validation.intelligence.engineering.rules.upper_cabinet_span_rule import (
            UpperCabinetSpanRule,
        )

        from validation.intelligence.engineering.rules.double_door_alignment_rule import (
            DoubleDoorAlignmentRule,
        )

        from validation.intelligence.engineering.rules.unsupported_top_panel_rule import (
            UnsupportedTopPanelRule,
        )

        from validation.intelligence.engineering.rules.cabinet_overturn_risk_rule import (
            CabinetOverturnRiskRule,
        )

        from validation.intelligence.engineering.rules.shelf_load_capacity_rule import (
            ShelfLoadCapacityRule,
        )

        from validation.intelligence.engineering.rules.drawer_slide_capacity_rule import (
            DrawerSlideCapacityRule,
        )

        from validation.intelligence.engineering.rules.drawer_bottom_load_rule import (
            DrawerBottomLoadRule,
        )

        from validation.intelligence.engineering.rules.confirmat_spacing_rule import (
            ConfirmatSpacingRule,
        )


        from validation.intelligence.engineering.rules.min_edge_distance_rule import (
            MinEdgeDistanceRule,
        )

        from validation.intelligence.engineering.rules.dowel_distribution_rule import (
            DowelDistributionRule,
        )

        from validation.intelligence.engineering.rules.fastener_capacity_rule import (
            FastenerCapacityRule,
        )

        from validation.intelligence.engineering.rules.connector_recommendation_rule import (
            ConnectorRecommendationRule,
        )

        return [
            ShelfDeflectionRule(),
            DividerBucklingRule(),
            DoorSagRule(),
            HangingCabinetLoadRule(),
            WideDrawerDeflectionRule(),
            CountertopSpanRule(),
            LongDoorHingeRule(),
            SidePanelSlendernessRule(),
            VerticalShelfSupportRule(),
            TallDividerStabilityRule(),
            BackPanelShearRule(),
            BaseKickSpanRule(),
            UpperCabinetSpanRule(),
            DoubleDoorAlignmentRule(),
            UnsupportedTopPanelRule(),
            CabinetOverturnRiskRule(),
            ShelfLoadCapacityRule(),
            DrawerSlideCapacityRule(),
            DrawerBottomLoadRule(),
            ConfirmatSpacingRule(),
            MinEdgeDistanceRule(),
            DowelDistributionRule(),
            FastenerCapacityRule(),
            ConnectorRecommendationRule(),
        ]
