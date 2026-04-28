"""OpenHarness channels subsystem.

Provides a message-bus architecture for integrating chat platforms
(Telegram, Discord, Slack, etc.) with the harnessOS agent core.

Usage::

    from core.channels import BaseChannel, ChannelManager, MessageBus
"""

from core.channels.bus.events import InboundMessage, OutboundMessage
from core.channels.bus.queue import MessageBus

__all__ = [
    "BaseChannel",
    "ChannelManager",
    "InboundMessage",
    "MessageBus",
    "OutboundMessage",
]
