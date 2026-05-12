"""Example-only tool module for instantiated connectors.

V3.5-G descriptor discovery must not import or execute this file.
"""


def run_tool(payload: dict) -> dict:
    return {"ok": True, "payload": payload}
