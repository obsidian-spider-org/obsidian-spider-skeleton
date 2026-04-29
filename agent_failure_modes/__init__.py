"""agent_failure_modes — runnable detectors for common LLM-agent failure patterns."""
from .agent_failure_modes import (
    FailureModeHit,
    ALL_CHECKS,
    audit,
    audit_summary,
    check_overrefusal,
    check_verbose_low_substance,
    check_hallucinated_blocker,
    check_excessive_clarification,
    check_safety_theater,
    check_sycophancy,
    check_risk_aversion_as_ethics,
    check_appearance_over_substance,
)

__all__ = [
    "FailureModeHit", "ALL_CHECKS", "audit", "audit_summary",
    "check_overrefusal", "check_verbose_low_substance",
    "check_hallucinated_blocker", "check_excessive_clarification",
    "check_safety_theater", "check_sycophancy",
    "check_risk_aversion_as_ethics", "check_appearance_over_substance",
]
