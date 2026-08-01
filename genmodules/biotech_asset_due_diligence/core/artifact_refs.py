"""Immutable upstream artifact references and checksum verification."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import os
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_path(path: str, root_env: str | None = None, workspace_root: Path | None = None) -> Path:
    expanded = os.path.expandvars(path)
    candidate = Path(expanded)
    if not candidate.is_absolute():
        if root_env:
            root_value = os.environ.get(root_env)
            if root_value:
                candidate = Path(root_value) / candidate
        if not candidate.is_absolute() and workspace_root is not None:
            candidate = workspace_root / candidate
    return candidate.resolve()


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    path: str
    sha256: str
    bytes: int
    producer_contract: str
    root_env: str | None = None
    immutable: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def verify(self, workspace_root: Path | None = None) -> Path:
        if workspace_root is None:
            raise ValueError("an external workspace_root is required for artifact verification")
        root = workspace_root.resolve()
        if not root.is_dir():
            raise ValueError(f"external workspace root does not exist: {root}")
        path = resolve_path(self.path, self.root_env, workspace_root)
        if not _within(path, root):
            raise ValueError(f"artifact path escapes external workspace root: {self.artifact_id}")
        if not path.is_file():
            raise ValueError(f"artifact does not exist: {path}")
        actual_bytes = path.stat().st_size
        actual_hash = _sha256(path)
        if actual_bytes != self.bytes:
            raise ValueError(f"artifact byte count mismatch for {self.artifact_id}")
        if actual_hash != self.sha256:
            raise ValueError(f"artifact checksum mismatch for {self.artifact_id}")
        return path


def ref_from_manifest(record: dict[str, Any], artifact_id: str, producer_contract: str, root_env: str | None = None) -> ArtifactRef:
    return ArtifactRef(
        artifact_id=artifact_id,
        path=str(record["path"]),
        sha256=str(record["sha256"]),
        bytes=int(record["bytes"]),
        producer_contract=producer_contract,
        root_env=root_env,
    )
