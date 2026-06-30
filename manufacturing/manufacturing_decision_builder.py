from __future__ import annotations

from manufacturing.manufacturing_decision import ManufacturingDecision


class ManufacturingDecisionBuilder:
    SOURCE = "manufacturing-decision"
    LEGACY_STATUS_BY_DECISION = {
        "PASS": "READY",
        "WARNING": "REVIEW",
        "FAIL": "BLOCKED",
    }

    def build(
        self,
        engineering_readiness_report=None,
        manufacturing_validation_summary_report=None,
        release_validation=None,
        project_manufacturing_readiness_report=None,
        production_evidence=None,
        source: str = SOURCE,
    ) -> ManufacturingDecision:
        blocking_reasons = []
        warning_reasons = []
        recommended_action = ""
        production_evidence = self._production_evidence(production_evidence)

        if engineering_readiness_report is not None:
            engineering_blocked = not bool(
                getattr(
                    engineering_readiness_report,
                    "ready_for_manufacturing_handoff",
                    False,
                )
            )
            if engineering_blocked:
                blocking_reasons.append(
                    self._non_empty(
                        "Engineering handoff is blocked.",
                        getattr(engineering_readiness_report, "source", ""),
                    )
                )
                recommended_action = (
                    "Resolve engineering handoff issues before production."
                )

        if manufacturing_validation_summary_report is not None:
            blocking_reasons.extend(
                self._messages(
                    getattr(
                        manufacturing_validation_summary_report,
                        "blocking_messages",
                        (),
                    )
                )
            )
            warning_reasons.extend(
                self._messages(
                    getattr(
                        manufacturing_validation_summary_report,
                        "warning_messages",
                        (),
                    )
                )
            )
            if (
                not recommended_action
                and getattr(
                    manufacturing_validation_summary_report,
                    "blocking_issue_count",
                    0,
                )
                > 0
            ):
                recommended_action = "Resolve manufacturing validation blockers."
            if (
                not recommended_action
                and getattr(
                    manufacturing_validation_summary_report,
                    "warning_count",
                    0,
                )
                > 0
            ):
                recommended_action = "Review manufacturing warnings before production."

        if release_validation is not None and not bool(
            getattr(release_validation, "get", lambda *_args, **_kwargs: True)(
                "ready",
                True,
            )
        ):
            blocking_reasons.extend(
                self._messages(
                    getattr(release_validation, "get", lambda *_args, **_kwargs: ())(
                        "warnings",
                        (),
                    )
                )
            )
            if not recommended_action:
                recommended_action = (
                    "Resolve manufacturing release warnings before production."
                )

        if project_manufacturing_readiness_report is not None:
            readiness_status = str(
                getattr(
                    project_manufacturing_readiness_report,
                    "readiness_status",
                    "",
                )
                or ""
            ).upper()
            recommendation = str(
                getattr(
                    project_manufacturing_readiness_report,
                    "manufacturing_recommendation",
                    "",
                )
                or ""
            ).strip()
            if readiness_status == "BLOCKED":
                if recommendation:
                    blocking_reasons.append(recommendation)
                if not recommended_action:
                    recommended_action = recommendation or "Manufacturing is blocked."
            elif readiness_status == "REVIEW":
                if recommendation:
                    warning_reasons.append(recommendation)
                if not recommended_action:
                    recommended_action = (
                        recommendation
                        or "Manufacturing review is required before production."
                    )

        if production_evidence is not None:
            warning_reasons.extend(
                self._production_evidence_warning_reasons(production_evidence)
            )
            if not recommended_action and warning_reasons:
                recommended_action = "Review production evidence before production."

        blocking_reasons = self._unique_messages(blocking_reasons)
        warning_reasons = self._unique_messages(
            message
            for message in warning_reasons
            if message not in blocking_reasons
        )

        if blocking_reasons:
            status = "FAIL"
        elif warning_reasons:
            status = "WARNING"
        else:
            status = "PASS"

        if status == "PASS":
            recommended_action = ""

        return ManufacturingDecision(
            status=status,
            ready_for_production=(status == "PASS"),
            blocking_reasons=tuple(blocking_reasons),
            warning_reasons=tuple(warning_reasons),
            recommended_action=recommended_action,
            legacy_readiness_status=self.LEGACY_STATUS_BY_DECISION[status],
            source=source,
        )

    @staticmethod
    def _messages(values) -> list[str]:
        messages = []
        for value in values or ():
            text = str(value or "").strip()
            if text:
                messages.append(text)
        return messages

    @staticmethod
    def _non_empty(message: str, source: str) -> str:
        source_text = str(source or "").strip()
        if source_text:
            return f"{message} source={source_text}"
        return message

    @staticmethod
    def _unique_messages(values) -> list[str]:
        ordered = []
        seen = set()
        for value in values:
            if value not in seen:
                seen.add(value)
                ordered.append(value)
        return ordered

    @staticmethod
    def _production_evidence(value):
        if value is None:
            return None
        return getattr(value, "production_evidence", value)

    def _production_evidence_warning_reasons(self, evidence) -> list[str]:
        warning_reasons = self._messages(
            getattr(evidence, "release_warnings", ()) or ()
        )
        missing_evidence = (
            ("has_cutlist_evidence", "Missing cutlist evidence"),
            ("has_machining_evidence", "Missing machining evidence"),
            ("has_edge_evidence", "Missing edge evidence"),
            ("has_hardware_evidence", "Missing hardware evidence"),
        )
        for flag_name, message in missing_evidence:
            if not bool(getattr(evidence, flag_name, False)):
                warning_reasons.append(message)
        return warning_reasons
