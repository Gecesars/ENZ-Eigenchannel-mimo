#!/usr/bin/env python3
from __future__ import annotations

import base64
import io
import shutil
import subprocess
import tarfile
from pathlib import Path


def main() -> None:
    root = Path.cwd().resolve()
    chunk_dir = root / "tools" / "bootstrap_chunks"
    chunks = sorted(chunk_dir.glob("part*.txt"))
    if len(chunks) != 9:
        raise RuntimeError(f"Esperados 9 fragmentos; encontrados {len(chunks)}.")

    payload = "".join(path.read_text(encoding="utf-8").strip() for path in chunks)
    raw = base64.b64decode(payload, validate=True)

    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive.getmembers():
            target = (root / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"Caminho inseguro no pacote: {member.name}")
        archive.extractall(root, filter="data")

    for transient in (
        root / "tools" / "bootstrap_corpus.py",
        root / ".github" / "workflows" / "bootstrap_corpus.yml",
    ):
        try:
            transient.unlink()
        except FileNotFoundError:
            pass

    shutil.rmtree(chunk_dir, ignore_errors=True)
    for directory in (
        root / "tools",
        root / ".github" / "workflows",
        root / ".github",
    ):
        try:
            directory.rmdir()
        except OSError:
            pass

    subprocess.run(["git", "config", "user.name", "enz-research-bootstrap"], check=True)
    subprocess.run(
        ["git", "config", "user.email", "actions@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add", "-A"], check=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        subprocess.run(
            ["git", "commit", "-m", "docs: publica corpus científico pós-doc inicial"],
            check=True,
        )
        subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
    print("Corpus científico publicado.")


if __name__ == "__main__":
    main()
