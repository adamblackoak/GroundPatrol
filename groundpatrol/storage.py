from __future__ import annotations

import os
import tempfile
from pathlib import Path


STATE_ROOT_ENV = "GROUNDPATROL_STATE_ROOT"


def _is_writable_directory(path: Path) -> bool:
    """Return True when *path* can actually accept a new file."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        fd, probe = tempfile.mkstemp(prefix=".groundpatrol-write-", dir=path)
    except OSError:
        return False
    else:
        os.close(fd)
        try:
            Path(probe).unlink()
        except OSError:
            pass
        return True


def runtime_state_directory(name: str) -> Path:
    """Resolve a writable directory for ephemeral GroundPatrol runtime state.

    Resolution order:
    1. GROUNDPATROL_STATE_ROOT/<name> when explicitly configured.
    2. ./<name> for the local developer/UI experience.
    3. <system temp>/groundpatrol/<name> for read-only packaged runtimes such as
       AgentCore CodeZip.

    Persistent production state should use a configured AgentCore filesystem mount
    (for example /mnt/workspace) via GROUNDPATROL_STATE_ROOT rather than relying on
    the temporary fallback.
    """
    configured_root = os.getenv(STATE_ROOT_ENV)
    if configured_root:
        configured = Path(configured_root) / name
        configured.mkdir(parents=True, exist_ok=True)
        if not _is_writable_directory(configured):
            raise PermissionError(
                f"Configured {STATE_ROOT_ENV} is not writable: {configured}"
            )
        return configured

    local = Path(name)
    if _is_writable_directory(local):
        return local

    fallback = Path(tempfile.gettempdir()) / "groundpatrol" / name
    fallback.mkdir(parents=True, exist_ok=True)
    if not _is_writable_directory(fallback):
        raise PermissionError(f"No writable GroundPatrol state directory: {fallback}")
    return fallback
