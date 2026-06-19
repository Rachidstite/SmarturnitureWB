from dataclasses import dataclass, field


@dataclass
class FactoryGovernanceAuthorityReport:
    authority_owner: str = ""
    authority_rank: int = 0
    authority_scope: str = ""
    winning_signal: str = ""
    losing_signals: list = field(default_factory=list)
    explanation: str = ""
    warnings: list = field(default_factory=list)
