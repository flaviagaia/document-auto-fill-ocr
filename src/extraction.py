from __future__ import annotations

import json
import re

import pandas as pd

from .config import EXTRACTED_FIELDS_PATH, PROCESSED_DIR


PATTERNS = {
    "document_number": [
        re.compile(r"(?:Invoice No|Receipt ID|Service Form|Form ID):\s*(.+)", re.I),
    ],
    "supplier_name": [
        re.compile(r"(?:Supplier|Vendor|Client|Organization):\s*(.+)", re.I),
    ],
    "issue_date": [
        re.compile(r"(?:Issue Date|Purchase Date|Service Date|Submission Date):\s*(\d{4}-\d{2}-\d{2})", re.I),
    ],
    "due_date": [
        re.compile(r"Due Date:\s*(\d{4}-\d{2}-\d{2})", re.I),
    ],
    "tax_id": [
        re.compile(r"(?:Tax ID|Document ID):\s*([\d\.\-/]+)", re.I),
    ],
    "total_amount": [
        re.compile(r"(?:Total Amount|Total|Estimated Value):\s*BRL\s*([\d,]+\.\d{2})", re.I),
    ],
}


def _extract_field(text: str, patterns: list[re.Pattern]) -> str:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip().replace(",", "")
    return ""


def extract_fields(ocr_lines: pd.DataFrame, classified_docs: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    grouped = ocr_lines.groupby("document_id")["ocr_text"].apply(lambda values: "\n".join(values)).reset_index()
    extracted_rows = []

    for row in grouped.itertuples():
        text = row.ocr_text
        doc_info = classified_docs[classified_docs["document_id"] == row.document_id].iloc[0]
        metadata_row = metadata[metadata["document_id"] == row.document_id].iloc[0]
        ground_truth = json.loads(metadata_row["ground_truth_json"])

        extracted = {field: _extract_field(text, patterns) for field, patterns in PATTERNS.items()}
        field_matches = sum(1 for key, value in extracted.items() if value == ground_truth.get(key, ""))
        coverage = sum(1 for value in extracted.values() if value)
        confidence = round((field_matches / len(PATTERNS)) * 0.7 + (coverage / len(PATTERNS)) * 0.3, 4)

        extracted_rows.append(
            {
                "document_id": row.document_id,
                "document_type": doc_info["document_type"],
                "predicted_type": doc_info["predicted_type"],
                "classification_confidence": doc_info["classification_confidence"],
                "document_number": extracted["document_number"],
                "supplier_name": extracted["supplier_name"],
                "issue_date": extracted["issue_date"],
                "due_date": extracted["due_date"],
                "tax_id": extracted["tax_id"],
                "total_amount": extracted["total_amount"],
                "field_match_count": field_matches,
                "field_coverage_count": coverage,
                "auto_fill_confidence": confidence,
            }
        )

    df = pd.DataFrame(extracted_rows)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(EXTRACTED_FIELDS_PATH, index=False)
    return df

