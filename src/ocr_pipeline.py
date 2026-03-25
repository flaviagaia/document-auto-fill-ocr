from __future__ import annotations

import pandas as pd

from .config import OCR_LINES_PATH


def run_ocr() -> pd.DataFrame:
    return pd.read_csv(OCR_LINES_PATH)

