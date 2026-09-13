from pathlib import Path

import groundpatrol.storage as storage


def test_runtime_state_directory_falls_back_to_system_temp(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    fallback_root = tmp_path / "system-temp"
    monkeypatch.setattr(storage.tempfile, "gettempdir", lambda: str(fallback_root))

    original = storage._is_writable_directory

    def writable(path: Path) -> bool:
        if path == Path("receipts"):
            return False
        return original(path)

    monkeypatch.setattr(storage, "_is_writable_directory", writable)

    resolved = storage.runtime_state_directory("receipts")

    assert resolved == fallback_root / "groundpatrol" / "receipts"
    assert resolved.is_dir()


def test_configured_state_root_is_used(monkeypatch, tmp_path):
    configured_root = tmp_path / "mounted-state"
    monkeypatch.setenv(storage.STATE_ROOT_ENV, str(configured_root))

    resolved = storage.runtime_state_directory("executions")

    assert resolved == configured_root / "executions"
    assert resolved.is_dir()
