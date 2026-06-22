from manufacturing.back_panel_decision_report import BackPanelDecisionReport


class BackPanelDecisionBuilder:

    def build(self, validation_report):
        recommended_action = getattr(validation_report, "recommended_action", "")
        manufacturing_warning = getattr(validation_report, "manufacturing_warning", "")
        fixing_method_warning = getattr(validation_report, "fixing_method_warning", "")

        if not getattr(validation_report, "is_valid", False):
            return BackPanelDecisionReport(
                decision_status="BLOCKED",
                is_manufacturable=False,
                is_blocked=True,
                requires_review=False,
                blocking_reason=recommended_action or "Back panel validation failed",
                warning_reason=manufacturing_warning or fixing_method_warning or "",
                recommended_fix=(
                    recommended_action
                    or "Review back panel manufacturability before production"
                ),
                manufacturing_priority="HIGH",
                factory_visibility_message="Back panel is blocked for production",
            )

        if getattr(validation_report, "center_support_required", False):
            return BackPanelDecisionReport(
                decision_status="REVIEW_REQUIRED",
                is_manufacturable=True,
                is_blocked=False,
                requires_review=True,
                blocking_reason="",
                warning_reason="Back panel requires center support",
                recommended_fix=recommended_action or "Review center support requirement",
                manufacturing_priority="MEDIUM",
                factory_visibility_message="Back panel requires manufacturing review",
            )

        if getattr(validation_report, "center_holes_required", False):
            return BackPanelDecisionReport(
                decision_status="REVIEW_REQUIRED",
                is_manufacturable=True,
                is_blocked=False,
                requires_review=True,
                blocking_reason="",
                warning_reason="Back panel requires center fixing holes",
                recommended_fix=recommended_action or "Review center fixing hole requirement",
                manufacturing_priority="MEDIUM",
                factory_visibility_message="Back panel requires manufacturing review",
            )

        if fixing_method_warning:
            return BackPanelDecisionReport(
                decision_status="REVIEW_REQUIRED",
                is_manufacturable=True,
                is_blocked=False,
                requires_review=True,
                blocking_reason="",
                warning_reason=fixing_method_warning,
                recommended_fix=recommended_action or "Review back panel fixing method",
                manufacturing_priority="MEDIUM",
                factory_visibility_message="Back panel requires manufacturing review",
            )

        if manufacturing_warning:
            return BackPanelDecisionReport(
                decision_status="REVIEW_REQUIRED",
                is_manufacturable=True,
                is_blocked=False,
                requires_review=True,
                blocking_reason="",
                warning_reason=manufacturing_warning,
                recommended_fix=recommended_action or "Review back panel manufacturing warning",
                manufacturing_priority="MEDIUM",
                factory_visibility_message="Back panel requires manufacturing review",
            )

        return BackPanelDecisionReport(
            decision_status="APPROVED",
            is_manufacturable=True,
            is_blocked=False,
            requires_review=False,
            blocking_reason="",
            warning_reason="",
            recommended_fix="",
            manufacturing_priority="LOW",
            factory_visibility_message="Back panel is ready for production",
        )
