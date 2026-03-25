from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from .config import DOCUMENTS_DIR, DOCUMENT_METADATA_PATH, OCR_LINES_PATH, RAW_DIR


DOCUMENTS = [
    {
        "document_id": "DOC-001",
        "document_type": "invoice",
        "file_name": "invoice_001.png",
        "lines": [
            "Invoice No: INV-2026-001",
            "Supplier: Nova Industrial Services",
            "Issue Date: 2026-03-10",
            "Due Date: 2026-04-09",
            "Tax ID: 12.345.678/0001-90",
            "Total Amount: BRL 18,540.75",
        ],
        "ground_truth": {
            "document_number": "INV-2026-001",
            "supplier_name": "Nova Industrial Services",
            "issue_date": "2026-03-10",
            "due_date": "2026-04-09",
            "tax_id": "12.345.678/0001-90",
            "total_amount": "18540.75",
        },
    },
    {
        "document_id": "DOC-002",
        "document_type": "receipt",
        "file_name": "receipt_001.png",
        "lines": [
            "Receipt ID: RC-7782",
            "Vendor: Mercado Central Ltda",
            "Purchase Date: 2026-03-14",
            "Payment Method: Credit Card",
            "Total: BRL 428.90",
        ],
        "ground_truth": {
            "document_number": "RC-7782",
            "supplier_name": "Mercado Central Ltda",
            "issue_date": "2026-03-14",
            "due_date": "",
            "tax_id": "",
            "total_amount": "428.90",
        },
    },
    {
        "document_id": "DOC-003",
        "document_type": "service_form",
        "file_name": "service_form_001.png",
        "lines": [
            "Service Form: OS-4419",
            "Client: Prefeitura de Aurora",
            "Service Date: 2026-03-18",
            "Location: Rua das Palmeiras, 120",
            "Responsible: Equipe Alfa",
            "Estimated Value: BRL 6,700.00",
        ],
        "ground_truth": {
            "document_number": "OS-4419",
            "supplier_name": "Prefeitura de Aurora",
            "issue_date": "2026-03-18",
            "due_date": "",
            "tax_id": "",
            "total_amount": "6700.00",
        },
    },
    {
        "document_id": "DOC-004",
        "document_type": "registration_form",
        "file_name": "registration_form_001.png",
        "lines": [
            "Form ID: REG-1088",
            "Organization: Instituto Horizonte",
            "Submission Date: 2026-03-20",
            "Contact: Ana Beatriz Lima",
            "Document ID: 22.456.789/0001-44",
        ],
        "ground_truth": {
            "document_number": "REG-1088",
            "supplier_name": "Instituto Horizonte",
            "issue_date": "2026-03-20",
            "due_date": "",
            "tax_id": "22.456.789/0001-44",
            "total_amount": "",
        },
    },
]


def _render_document_image(file_path: Path, lines: list[str]) -> None:
    width, height = 1200, 850
    image = Image.new("RGB", (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=26, outline=(120, 132, 155), width=2)
    y = 95
    for line in lines:
        draw.text((90, y), line, fill=(15, 23, 42), font=font)
        y += 80
    image.save(file_path)


def build_demo_documents() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    metadata_rows = []
    ocr_rows = []

    for doc in DOCUMENTS:
        image_path = DOCUMENTS_DIR / doc["file_name"]
        _render_document_image(image_path, doc["lines"])

        metadata_rows.append(
            {
                "document_id": doc["document_id"],
                "document_type": doc["document_type"],
                "file_name": doc["file_name"],
                "image_path": str(image_path.relative_to(RAW_DIR.parent)),
                "ground_truth_json": json.dumps(doc["ground_truth"]),
            }
        )

        for idx, line in enumerate(doc["lines"], start=1):
            ocr_rows.append(
                {
                    "document_id": doc["document_id"],
                    "line_number": idx,
                    "ocr_text": line,
                }
            )

    metadata = pd.DataFrame(metadata_rows)
    ocr = pd.DataFrame(ocr_rows)
    metadata.to_csv(DOCUMENT_METADATA_PATH, index=False)
    ocr.to_csv(OCR_LINES_PATH, index=False)
    return metadata

