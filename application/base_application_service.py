from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from application.application_service_result import ApplicationServiceResult


class BaseApplicationService(ABC):
    """Abstract base for all application-layer services.

    Subclasses implement ``_execute(**kwargs)`` which must call at least one
    real existing component and return an ``ApplicationServiceResult``.  The
    public ``execute(**kwargs)`` method provides common error wrapping; it
    catches *unexpected* exceptions and reconstructs them as a failed result
    so callers never see raw exceptions from the service layer.
    """

    @abstractmethod
    def _execute(self, **kwargs: Any) -> ApplicationServiceResult:
        """Execute the service using only real, existing components.

        Must NOT introduce mock values, fake fallback logic, or
        ``REAL_ENGINE_AVAILABLE`` guards.
        """

    def execute(self, **kwargs: Any) -> ApplicationServiceResult:
        """Public entry point — wraps ``_execute`` in uniform error handling."""
        try:
            return self._execute(**kwargs)
        except Exception as exc:
            return ApplicationServiceResult(
                success=False,
                data=None,
                errors=(f"{type(exc).__name__}: {exc}",),
                diagnostics=(),
            )
