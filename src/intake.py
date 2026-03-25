from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from .config import RAW_DIR, UPLOADS_DIR


def _file_md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def build_document_fingerprint_map(metadata: pd.DataFrame) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in metadata.itertuples():
        image_path = RAW_DIR.parent / Path(row.image_path)
        if image_path.exists():
            mapping[_file_md5(image_path)] = row.document_id
    return mapping


def save_uploaded_image(file_name: str, content: bytes) -> Path:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    target = UPLOADS_DIR / file_name
    target.write_bytes(content)
    return target


def match_uploaded_document(uploaded_path: Path, metadata: pd.DataFrame) -> str | None:
    uploaded_hash = _file_md5(uploaded_path)
    mapping = build_document_fingerprint_map(metadata)
    return mapping.get(uploaded_hash)
