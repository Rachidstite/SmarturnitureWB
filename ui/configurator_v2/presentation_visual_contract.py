# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Presentation-Aware Visual Contract
#
# Derives symbolic visual hints from FurniturePresentationState.
# These are abstract tokens for a future renderer — no concrete
# colours, no Qt, no FreeCAD, no drawing, no canvas.
#
# This is NOT a rendering engine.
# This is NOT a UI renderer.
# This does NOT mutate scene graphs.
#
# The contract layer reuses:
#   - FurniturePresentationState (flags, severity, dominant flag)
#   - interactive_components (for optional integration)
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .presentation_state import FurniturePresentationState


# ── Symbolic visual hint constants ───────────────────────────────────

# Emphasis levels — how strongly the component is visually emphasised
EMPHASIS_NONE: str = "NONE"
EMPHASIS_LOW: str = "LOW"
EMPHASIS_MEDIUM: str = "MEDIUM"
EMPHASIS_HIGH: str = "HIGH"
EMPHASIS_CRITICAL: str = "CRITICAL"

EMPHASIS_LEVELS: tuple[str, ...] = (
    EMPHASIS_NONE,
    EMPHASIS_LOW,
    EMPHASIS_MEDIUM,
    EMPHASIS_HIGH,
    EMPHASIS_CRITICAL,
)

# Outline intents — what kind of outline/border treatment is needed
OUTLINE_NONE: str = "NONE"
OUTLINE_SELECTED: str = "SELECTED"
OUTLINE_HOVERED: str = "HOVERED"
OUTLINE_FOCUSED: str = "FOCUSED"
OUTLINE_WARNING: str = "WARNING"
OUTLINE_ERROR: str = "ERROR"
OUTLINE_DISABLED: str = "DISABLED"

OUTLINE_INTENTS: tuple[str, ...] = (
    OUTLINE_NONE,
    OUTLINE_SELECTED,
    OUTLINE_HOVERED,
    OUTLINE_FOCUSED,
    OUTLINE_WARNING,
    OUTLINE_ERROR,
    OUTLINE_DISABLED,
)

# Opacity intents — how the component's opacity should be treated
OPACITY_NORMAL: str = "NORMAL"
OPACITY_DIM: str = "DIM"
OPACITY_HIDDEN: str = "HIDDEN"

OPACITY_INTENTS: tuple[str, ...] = (
    OPACITY_NORMAL,
    OPACITY_DIM,
    OPACITY_HIDDEN,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _ensure_emphasis(value: Any, field_name: str) -> str:
    s = str(value).upper()
    if s not in EMPHASIS_LEVELS:
        raise TypeError(
            f"{field_name} must be one of {EMPHASIS_LEVELS}, got {value!r}"
        )
    return s


def _ensure_outline(value: Any, field_name: str) -> str:
    s = str(value).upper()
    if s not in OUTLINE_INTENTS:
        raise TypeError(
            f"{field_name} must be one of {OUTLINE_INTENTS}, got {value!r}"
        )
    return s


def _ensure_opacity(value: Any, field_name: str) -> str:
    s = str(value).upper()
    if s not in OPACITY_INTENTS:
        raise TypeError(
            f"{field_name} must be one of {OPACITY_INTENTS}, got {value!r}"
        )
    return s


def _ensure_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int, got {type(value).__name__}")
    return value


# ── Value-object dataclass ───────────────────────────────────────────


@dataclass(frozen=True)
class PresentationVisualContract:
    """Symbolic visual hints derived from FurniturePresentationState.

    All fields are abstract tokens — a renderer would map these to
    concrete colours, line widths, opacity values, etc.

    No concrete rendering concepts (Qt, FreeCAD, canvas, drawing).
    No domain, manufacturing, cost, or commercial concepts.
    """

    emphasis_level: str = EMPHASIS_NONE
    outline_intent: str = OUTLINE_NONE
    opacity_intent: str = OPACITY_NORMAL
    interaction_priority: int = 0
    dominant_flag: str = "neutral"
    visual_severity: int = 0

    def __post_init__(self):
        object.__setattr__(
            self, "emphasis_level", _ensure_emphasis(self.emphasis_level, "emphasis_level")
        )
        object.__setattr__(
            self, "outline_intent", _ensure_outline(self.outline_intent, "outline_intent")
        )
        object.__setattr__(
            self, "opacity_intent", _ensure_opacity(self.opacity_intent, "opacity_intent")
        )
        object.__setattr__(
            self,
            "interaction_priority",
            _ensure_int(self.interaction_priority, "interaction_priority"),
        )
        object.__setattr__(self, "dominant_flag", str(self.dominant_flag))
        object.__setattr__(self, "visual_severity", _ensure_int(self.visual_severity, "visual_severity"))

    @property
    def is_neutral(self) -> bool:
        return (
            self.emphasis_level == EMPHASIS_NONE
            and self.outline_intent == OUTLINE_NONE
            and self.opacity_intent == OPACITY_NORMAL
            and self.interaction_priority == 0
        )


# ── Severity-to-emphasis mapping ────────────────────────────────────

_SEVERITY_TO_EMPHASIS: dict[int, str] = {
    0: EMPHASIS_NONE,
    1: EMPHASIS_LOW,
    5: EMPHASIS_LOW,
    10: EMPHASIS_MEDIUM,
    20: EMPHASIS_MEDIUM,
    25: EMPHASIS_HIGH,
    30: EMPHASIS_HIGH,
    40: EMPHASIS_HIGH,
    50: EMPHASIS_CRITICAL,
}


def _severity_to_emphasis(severity: int) -> str:
    if severity <= 0:
        return EMPHASIS_NONE
    severity = (severity // 5) * 5  # floor to nearest 5
    return _SEVERITY_TO_EMPHASIS.get(severity, EMPHASIS_MEDIUM)


# ── Dominant-flag to outline mapping ────────────────────────────────

_FLAG_TO_OUTLINE: dict[str, str] = {
    "selected": OUTLINE_SELECTED,
    "hovered": OUTLINE_HOVERED,
    "focused": OUTLINE_FOCUSED,
    "warning": OUTLINE_WARNING,
    "error": OUTLINE_ERROR,
    "disabled": OUTLINE_DISABLED,
}


def _dominant_to_outline(dominant_flag: str) -> str:
    return _FLAG_TO_OUTLINE.get(dominant_flag, OUTLINE_NONE)


# ── Opacity from state ──────────────────────────────────────────────


def _state_to_opacity(state: FurniturePresentationState) -> str:
    if state.disabled or state.muted:
        return OPACITY_DIM
    if state.is_neutral:
        return OPACITY_NORMAL
    return OPACITY_NORMAL


# ── Resolver ─────────────────────────────────────────────────────────


def resolve_visual_contract(
    state: FurniturePresentationState | None,
) -> PresentationVisualContract:
    """Derive a PresentationVisualContract from a FurniturePresentationState.

    Parameters
    ----------
    state : The presentation state to convert, or None.

    Returns
    -------
    A PresentationVisualContract with symbolic visual hints.

    The resolver is deterministic and side-effect free.
    """
    if state is None or state.is_neutral:
        return PresentationVisualContract()

    severity = state.visual_severity
    dominant = state.dominant_flag

    return PresentationVisualContract(
        emphasis_level=_severity_to_emphasis(severity),
        outline_intent=_dominant_to_outline(dominant),
        opacity_intent=_state_to_opacity(state),
        interaction_priority=severity,
        dominant_flag=dominant,
        visual_severity=severity,
    )


def resolve_visual_contracts(
    states: tuple[FurniturePresentationState | None, ...],
) -> tuple[PresentationVisualContract, ...]:
    """Batch-resolve visual contracts for many presentation states.

    Preserves order and cardinality.
    """
    return tuple(resolve_visual_contract(s) for s in states)


# ── Integration helper ──────────────────────────────────────────────


def visual_contract_descriptor_pairs(
    contract: PresentationVisualContract | None,
) -> tuple[tuple[str, str], ...]:
    """Flatten a visual contract into display metadata pairs.

    Returns () for None or neutral.
    """
    if contract is None or contract.is_neutral:
        return ()
    pairs: list[tuple[str, str]] = [
        ("vc_emphasis", contract.emphasis_level),
        ("vc_outline", contract.outline_intent),
        ("vc_opacity", contract.opacity_intent),
        ("vc_priority", str(contract.interaction_priority)),
        ("vc_dominant", contract.dominant_flag),
        ("vc_severity", str(contract.visual_severity)),
    ]
    return tuple(pairs)


__all__ = [
    # Emphasis constants
    "EMPHASIS_NONE",
    "EMPHASIS_LOW",
    "EMPHASIS_MEDIUM",
    "EMPHASIS_HIGH",
    "EMPHASIS_CRITICAL",
    "EMPHASIS_LEVELS",
    # Outline constants
    "OUTLINE_NONE",
    "OUTLINE_SELECTED",
    "OUTLINE_HOVERED",
    "OUTLINE_FOCUSED",
    "OUTLINE_WARNING",
    "OUTLINE_ERROR",
    "OUTLINE_DISABLED",
    "OUTLINE_INTENTS",
    # Opacity constants
    "OPACITY_NORMAL",
    "OPACITY_DIM",
    "OPACITY_HIDDEN",
    "OPACITY_INTENTS",
    # Value-object
    "PresentationVisualContract",
    # Resolvers
    "resolve_visual_contract",
    "resolve_visual_contracts",
    # Helpers
    "visual_contract_descriptor_pairs",
]
