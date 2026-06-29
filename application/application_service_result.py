from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ApplicationServiceResult:
    """Standard result wrapper for every application service call.

    Fields
    ------
    success : bool
        True when the underlying component completed without error.
    data : Any | None
        The primary payload returned by the underlying component.
    errors : tuple
        Non-fatal error messages collected during execution.
    diagnostics : tuple
        Structured diagnostic items (violations, warnings, issues) forwarded
        from the underlying component without modification.
    """

    success: bool = True
    data: Any | None = None
    errors: tuple = field(default_factory=tuple)
    diagnostics: tuple = field(default_factory=tuple)

    def __bool__(self) -> bool:
        return self.success
