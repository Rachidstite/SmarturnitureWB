from dataclasses import dataclass


@dataclass(frozen=True)
class UnifiedDashboardResult:

    report: object

    viewmodel: object

    state: object
