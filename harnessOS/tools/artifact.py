"""
Artifact tools for saving and managing structured outputs.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


# In-memory artifact store for Phase 0
_artifact_store: dict[str, dict[str, Any]] = {}

# Artifact storage directory. Keep it under the project by default so imports
# from a parent cwd do not try to create files outside the repo package.
_artifact_dir = Path(
    os.getenv("ARTIFACT_DIR")
    or Path(__file__).resolve().parents[1] / "artifacts"
)


def artifact_save(name: str, content: str, artifact_type: str = "general") -> str:
    """Save a structured output as an artifact.

    Args:
        name: Name/identifier for the artifact
        content: Content to save
        artifact_type: Type of artifact (general, summary, report, email, etc.)

    Returns:
        Success message with artifact ID and path
    """
    artifact_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    # Store in memory
    _artifact_store[artifact_id] = {
        "id": artifact_id,
        "name": name,
        "type": artifact_type,
        "content": content,
        "created_at": timestamp,
    }

    # Also save to file
    _artifact_dir.mkdir(parents=True, exist_ok=True)
    file_path = _artifact_dir / f"{artifact_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({
            "id": artifact_id,
            "name": name,
            "type": artifact_type,
            "content": content,
            "created_at": timestamp,
        }, f, indent=2, ensure_ascii=False)

    return f"Artifact saved successfully.\nID: {artifact_id}\nName: {name}\nType: {artifact_type}\nPath: {file_path}"


def artifact_list() -> str:
    """List all saved artifacts.

    Returns:
        List of artifact IDs and names
    """
    if not _artifact_store:
        return "No artifacts saved yet."

    output = [f"Saved artifacts ({len(_artifact_store)}):\n"]
    for artifact_id, artifact in _artifact_store.items():
        output.append(
            f"- {artifact_id}: {artifact['name']} "
            f"({artifact['type']}) - {artifact['created_at'][:10]}"
        )

    return "\n".join(output)


def artifact_get(artifact_id: str) -> str:
    """Get a specific artifact by ID.

    Args:
        artifact_id: Artifact ID

    Returns:
        Artifact content or error
    """
    if artifact_id not in _artifact_store:
        return f"Artifact not found: {artifact_id}"

    artifact = _artifact_store[artifact_id]
    return (
        f"Name: {artifact['name']}\n"
        f"Type: {artifact['type']}\n"
        f"ID: {artifact['id']}\n"
        f"Created: {artifact['created_at']}\n\n"
        f"{artifact['content']}"
    )


def artifact_delete(artifact_id: str) -> str:
    """Delete an artifact.

    Args:
        artifact_id: Artifact ID to delete

    Returns:
        Success or error message
    """
    if artifact_id not in _artifact_store:
        return f"Artifact not found: {artifact_id}"

    # Remove from memory
    del _artifact_store[artifact_id]

    # Remove file
    file_path = _artifact_dir / f"{artifact_id}.json"
    if file_path.exists():
        file_path.unlink()

    return f"Artifact deleted: {artifact_id}"
