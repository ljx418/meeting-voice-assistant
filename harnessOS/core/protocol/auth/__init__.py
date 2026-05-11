"""V3.5 external transport auth helpers."""

from .capabilities import get_method_capability, is_forbidden_method
from .capability_token import (
    CapabilityTokenClaims,
    issue_capability_token,
    verify_capability_token,
)
from .subscription_token import (
    SubscriptionTokenClaims,
    issue_subscription_token,
    verify_subscription_token,
)

__all__ = [
    "CapabilityTokenClaims",
    "SubscriptionTokenClaims",
    "get_method_capability",
    "is_forbidden_method",
    "issue_capability_token",
    "issue_subscription_token",
    "verify_subscription_token",
    "verify_capability_token",
]
