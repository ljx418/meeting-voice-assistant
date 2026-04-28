"""
Workspace tools for file and directory operations.
"""

import os
from typing import Any


def workspace_ls(directory: str = ".") -> str:
    """List files in the workspace directory.

    Args:
        directory: Directory path to list (relative to workspace root)

    Returns:
        List of files and directories as string
    """
    workspace_root = os.getenv("WORKSPACE_ROOT", "./workspace")

    # Resolve full path
    if os.path.isabs(directory):
        full_path = directory
    else:
        full_path = os.path.join(workspace_root, directory)

    if not os.path.exists(full_path):
        return f"Directory not found: {directory}"

    if not os.path.isdir(full_path):
        return f"Not a directory: {directory}"

    entries = os.listdir(full_path)
    if not entries:
        return "Directory is empty"

    result = []
    for entry in sorted(entries):
        full_entry = os.path.join(full_path, entry)
        if os.path.isdir(full_entry):
            result.append(f"{entry}/")
        else:
            size = os.path.getsize(full_entry)
            result.append(f"{entry} ({size} bytes)")

    return "\n".join(result)


def workspace_read_file(file_path: str) -> str:
    """Read contents of a file in the workspace.

    Args:
        file_path: Path to the file (relative to workspace root or absolute)

    Returns:
        File contents as string
    """
    workspace_root = os.getenv("WORKSPACE_ROOT", "./workspace")

    # Resolve full path
    if os.path.isabs(file_path):
        full_path = file_path
    else:
        full_path = os.path.join(workspace_root, file_path)

    if not os.path.exists(full_path):
        return f"File not found: {file_path}"

    if not os.path.isfile(full_path):
        return f"Not a file: {file_path}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except UnicodeDecodeError:
        with open(full_path, "rb") as f:
            content = f.read()
        return f"Binary file ({len(content)} bytes)"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def workspace_write_file(file_path: str, content: str) -> str:
    """Write content to a file in the workspace.

    Args:
        file_path: Path to the file (relative to workspace root or absolute)
        content: Content to write

    Returns:
        Success message or error
    """
    workspace_root = os.getenv("WORKSPACE_ROOT", "./workspace")

    # Resolve full path
    if os.path.isabs(file_path):
        full_path = file_path
    else:
        full_path = os.path.join(workspace_root, file_path)

    # Ensure parent directory exists
    parent_dir = os.path.dirname(full_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path} ({len(content)} characters)"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def workspace_mkdir(directory: str) -> str:
    """Create a directory in the workspace.

    Args:
        directory: Directory path to create (relative to workspace root)

    Returns:
        Success message or error
    """
    workspace_root = os.getenv("WORKSPACE_ROOT", "./workspace")

    if os.path.isabs(directory):
        full_path = directory
    else:
        full_path = os.path.join(workspace_root, directory)

    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Directory created: {directory}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"
