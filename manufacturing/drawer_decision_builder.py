from manufacturing.drawer_decision_report import DrawerDecisionReport


class DrawerDecisionBuilder:

    def build(self, validation_report):
        blocking_issues = list(getattr(validation_report, "blocking_issues", None) or [])
        warnings = list(getattr(validation_report, "warnings", None) or [])

        if not getattr(validation_report, "is_valid", False):
            return DrawerDecisionReport(
                decision_status="BLOCKED",
                is_manufacturable=False,
                is_blocked=True,
                requires_review=False,
                blocking_reason=blocking_issues[0] if blocking_issues else "Drawer validation failed",
                warning_reason=warnings[0] if warnings else "",
                recommended_fix="Review drawer manufacturability before production",
                factory_visibility_message="Drawer is blocked for production",
            )

        if not getattr(validation_report, "manufacturing_ready", False):
            return DrawerDecisionReport(
                decision_status="REVIEW_REQUIRED",
                is_manufacturable=False,
                is_blocked=False,
                requires_review=True,
                blocking_reason="",
                warning_reason=warnings[0] if warnings else "Drawer manufacturing readiness requires review",
                recommended_fix="Review drawer manufacturing readiness",
                factory_visibility_message="Drawer requires manufacturing review",
            )

        if warnings:
            return DrawerDecisionReport(
                decision_status="REVIEW_REQUIRED",
                is_manufacturable=True,
                is_blocked=False,
                requires_review=True,
                blocking_reason="",
                warning_reason=warnings[0],
                recommended_fix="Review drawer warnings before production",
                factory_visibility_message="Drawer is manufacturable with warnings",
            )

        return DrawerDecisionReport(
            decision_status="APPROVED",
            is_manufacturable=True,
            is_blocked=False,
            requires_review=False,
            blocking_reason="",
            warning_reason="",
            recommended_fix="",
            factory_visibility_message="Drawer is ready for production",
        )
