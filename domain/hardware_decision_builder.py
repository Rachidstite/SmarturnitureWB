from __future__ import annotations

from domain.hardware_decision import HardwareDecision
from domain.hardware_decision_context import HardwareDecisionContext
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionImpact,
    OperationalDecisionOption,
    OperationalDecisionTraceability,
    OperationalDecisionType,
)


def build_hardware_decision(
    context: HardwareDecisionContext,
) -> HardwareDecision:
    candidate_options = tuple(
        OperationalDecisionOption(
            option_id=sku,
            label=sku,
        )
        for sku in context.available_hardware_skus
    )

    decision = OperationalDecision(
        decision_id=context.context_id,
        decision_type=OperationalDecisionType.HARDWARE,
        selected_option=None,
        candidate_options=candidate_options,
        impact=OperationalDecisionImpact(),
        traceability=OperationalDecisionTraceability(),
        validation_messages=(),
    )

    return HardwareDecision(
        decision=decision,
        selected_hardware_sku="",
        candidate_hardware_skus=tuple(context.available_hardware_skus),
        rejected_hardware_skus=(),
        manufacturing_impact_note="",
        cost_impact_note="",
        quality_impact_note="",
        replacement_allowed=False,
        replacement_reason="",
    )
