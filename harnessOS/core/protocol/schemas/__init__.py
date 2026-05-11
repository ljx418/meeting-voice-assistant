"""V3.5 protocol schema registries."""

from .errors import ERROR_SCHEMAS, ProtocolError, get_error_schema
from .events import EVENT_SCHEMAS, get_event_schema
from .methods import METHOD_SCHEMAS, get_method_schema, list_method_schemas

__all__ = [
    "ERROR_SCHEMAS",
    "EVENT_SCHEMAS",
    "METHOD_SCHEMAS",
    "ProtocolError",
    "get_error_schema",
    "get_event_schema",
    "get_method_schema",
    "list_method_schemas",
]
