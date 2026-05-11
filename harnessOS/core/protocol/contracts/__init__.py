"""V3.5 protocol contract inventories.

non-runtime contract metadata only; no handler registration; no behavior change
"""

from __future__ import annotations

from .error_inventory import ERROR_INVENTORY
from .event_inventory import EVENT_INVENTORY
from .method_inventory import METHOD_INVENTORY

__all__ = ["ERROR_INVENTORY", "EVENT_INVENTORY", "METHOD_INVENTORY"]
