"""Message bus module for decoupled channel-agent communication."""

from core.channels.bus.events import InboundMessage, OutboundMessage
from core.channels.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
