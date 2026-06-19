from cost_intelligence.factory_governance_state import FactoryGovernanceState


class LegacyThreeStateAdapter:

    _MAPPING = {
        FactoryGovernanceState.APPROVED.value: "APPROVED",
        FactoryGovernanceState.REPRICE.value: "REVIEW_REQUIRED",
        FactoryGovernanceState.SCHEDULE_LATER.value: "REVIEW_REQUIRED",
        FactoryGovernanceState.REVIEW_REQUIRED.value: "REVIEW_REQUIRED",
        FactoryGovernanceState.REJECTED.value: "BLOCKED",
    }

    def adapt(self, governance_state):
        state_value = getattr(governance_state, "value", governance_state)
        if state_value not in self._MAPPING:
            raise ValueError(f"Unknown governance state: {governance_state!r}")
        return self._MAPPING[state_value]
