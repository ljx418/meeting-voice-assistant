"""Example-only health check module for instantiated connectors.

V3.5-G descriptor discovery must not import or execute this file.
"""


def check_health() -> dict[str, str]:
    return {"status": "available", "message": "Example health check."}
