from enum import Enum


class FactoryGovernanceState(str, Enum):
    APPROVED = "APPROVED"
    REPRICE = "REPRICE"
    SCHEDULE_LATER = "SCHEDULE_LATER"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
