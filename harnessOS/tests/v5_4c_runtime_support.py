from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from apps.api import create_app
from core.policies.existing_v4_runtime_trial import ExistingV4RuntimeTrialBridge
from tests.v4_0_reference_support import SCOPE_QUERY, build_gateway


class BffV42RuntimeAdapter:
    entrypoint_id = "bff:/bff/v4_2/runtime"

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.call_count = 0

    def start_local_folder_summary(self, *, folder_path: str, source: str, user_confirmed: bool) -> dict[str, Any]:
        self.call_count += 1
        response = self.client.post(
            f"/bff/v4_2/runtime/workflows/local-folder-summary/start{SCOPE_QUERY}",
            json={"folder_path": folder_path, "source": source, "user_confirmed": user_confirmed},
        )
        response.raise_for_status()
        return response.json()

    def rerun_station(self, *, workflow_instance_id: str, station_id: str, source: str, user_confirmed: bool) -> dict[str, Any]:
        self.call_count += 1
        response = self.client.post(
            f"/bff/v4_2/runtime/instances/{workflow_instance_id}/rerun-station{SCOPE_QUERY}",
            json={"station_id": station_id, "source": source, "user_confirmed": user_confirmed},
        )
        response.raise_for_status()
        return response.json()

    def continue_downstream(self, *, workflow_instance_id: str, source: str, user_confirmed: bool) -> dict[str, Any]:
        self.call_count += 1
        response = self.client.post(
            f"/bff/v4_2/runtime/instances/{workflow_instance_id}/continue-downstream{SCOPE_QUERY}",
            json={"source": source, "user_confirmed": user_confirmed},
        )
        response.raise_for_status()
        return response.json()

    def list_evidence(self, *, workflow_instance_id: str) -> list[dict[str, Any]]:
        response = self.client.get(f"/bff/v4_2/runtime/instances/{workflow_instance_id}/evidence{SCOPE_QUERY}")
        response.raise_for_status()
        return response.json()


def make_v5_4c_bridge(monkeypatch: Any, tmp_path: Any) -> tuple[ExistingV4RuntimeTrialBridge, BffV42RuntimeAdapter]:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    client = TestClient(create_app(gateway_service=build_gateway(tmp_path)))
    adapter = BffV42RuntimeAdapter(client)
    return ExistingV4RuntimeTrialBridge(adapter), adapter
