from __future__ import annotations

from domain.hardware_decision import HardwareDecision
from domain.hardware_decision_context import HardwareDecisionContext
from domain.hardware_decision_evidence import HardwareDecisionEvidence
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionImpact,
    OperationalDecisionOption,
    OperationalDecisionTraceability,
    OperationalDecisionType,
)


def build_hardware_decision(
    context: HardwareDecisionContext,
    evidence: HardwareDecisionEvidence,
) -> HardwareDecision:
    candidate_options = tuple(
        OperationalDecisionOption(
            option_id=sku,
            label=sku,
        )
        for sku in context.available_hardware_skus
    )
    evidence_refs = (
        tuple(evidence.placement_report_refs)
        + tuple(evidence.validation_report_refs)
        + tuple(evidence.compatibility_report_refs)
        + tuple(evidence.manufacturing_report_refs)
        + tuple(evidence.cost_report_refs)
    )
    source_rule = evidence.source_rules[0] if len(evidence.source_rules) == 1 else ""
    source_component = (
        evidence.source_components[0] if len(evidence.source_components) == 1 else ""
    )
    validation_messages = (
        tuple(evidence.warnings)
        + tuple(evidence.blocking_constraints)
        + tuple(evidence.evidence_notes)
    )

    decision = OperationalDecision(
        decision_id=context.context_id,
        decision_type=OperationalDecisionType.HARDWARE,
        selected_option=None,
        candidate_options=candidate_options,
        impact=OperationalDecisionImpact(),
        traceability=OperationalDecisionTraceability(
            source_component=source_component,
            source_report="",
            source_rule=source_rule,
            evidence_refs=evidence_refs,
        ),
        validation_messages=validation_messages,
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
