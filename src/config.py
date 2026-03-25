from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = DATA_DIR / "uploads"

DOCUMENT_METADATA_PATH = RAW_DIR / "document_metadata.csv"
OCR_LINES_PATH = RAW_DIR / "ocr_lines.csv"
DOCUMENTS_DIR = RAW_DIR / "documents"

EXTRACTED_FIELDS_PATH = PROCESSED_DIR / "extracted_fields.csv"
SUMMARY_PATH = PROCESSED_DIR / "summary.json"
