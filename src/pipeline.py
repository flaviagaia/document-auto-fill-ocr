from __future__ import annotations

import json

import pandas as pd

from .classification import classify_documents
from .config import DOCUMENT_METADATA_PATH, EXTRACTED_FIELDS_PATH, PROCESSED_DIR, SUMMARY_PATH
from .data_generation import build_demo_documents
from .extraction import extract_fields
from .ocr_pipeline import run_ocr


def run_pipeline() -> dict:
    metadata = build_demo_documents()
    ocr_lines = run_ocr()
    classified = classify_documents(ocr_lines, metadata)
    extracted = extract_fields(ocr_lines, classified, metadata)

    type_accuracy = round((classified["document_type"] == classified["predicted_type"]).mean(), 4)
    avg_confidence = round(float(extracted["auto_fill_confidence"].mean()), 4)
    total_fields = int(len(extracted) * 6)
    matched_fields = int(extracted["field_match_count"].sum())
    field_accuracy = round(matched_fields / total_fields, 4) if total_fields else 0.0

    summary = {
        "documents_processed": int(len(metadata)),
        "ocr_lines": int(len(ocr_lines)),
        "document_type_accuracy": type_accuracy,
        "field_accuracy": field_accuracy,
        "average_auto_fill_confidence": avg_confidence,
        "documents_high_confidence": int((extracted["auto_fill_confidence"] >= 0.85).sum()),
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary

