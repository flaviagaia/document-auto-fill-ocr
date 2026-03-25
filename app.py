from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import DOCUMENT_METADATA_PATH, EXTRACTED_FIELDS_PATH, RAW_DIR, SUMMARY_PATH
from src.pipeline import run_pipeline


def _load_artifacts() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    try:
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        extracted = pd.read_csv(EXTRACTED_FIELDS_PATH)
        metadata = pd.read_csv(DOCUMENT_METADATA_PATH)
        if extracted.empty or "document_id" not in extracted.columns:
            raise ValueError("missing extracted fields")
        return summary, extracted, metadata
    except Exception:
        summary = run_pipeline()
        extracted = pd.read_csv(EXTRACTED_FIELDS_PATH)
        metadata = pd.read_csv(DOCUMENT_METADATA_PATH)
        return summary, extracted, metadata


st.set_page_config(page_title="Document Auto Fill OCR", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #08111f; color: #e8edf5; }
    .hero {
        background: linear-gradient(135deg, rgba(13, 25, 45, 0.95), rgba(20, 46, 81, 0.92));
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 24px;
        padding: 1.4rem;
        margin-bottom: 1rem;
    }
    .hero h1, .hero p { color: #e8edf5; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Document Auto Fill OCR</h1>
        <p>OCR-driven pipeline for document classification, field extraction, confidence scoring, and automatic form pre-filling.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Reprocess demo documents"):
    run_pipeline()

summary, extracted, metadata = _load_artifacts()

metrics = st.columns(5)
metrics[0].metric("Documents", summary["documents_processed"])
metrics[1].metric("OCR lines", summary["ocr_lines"])
metrics[2].metric("Type accuracy", f"{summary['document_type_accuracy']:.2%}")
metrics[3].metric("Field accuracy", f"{summary['field_accuracy']:.2%}")
metrics[4].metric("Avg. confidence", f"{summary['average_auto_fill_confidence']:.2%}")

tab_docs, tab_fields, tab_metrics = st.tabs(["Documents", "Auto-filled Fields", "Quality Metrics"])

with tab_docs:
    selected_doc = st.selectbox("Select document", options=metadata["document_id"].tolist())
    doc_row = metadata[metadata["document_id"] == selected_doc].iloc[0]
    image_path = RAW_DIR.parent / Path(doc_row["image_path"])
    st.image(str(image_path), caption=f"{doc_row['document_type']} - {doc_row['document_id']}", use_container_width=True)

with tab_fields:
    st.dataframe(extracted, use_container_width=True, hide_index=True)

with tab_metrics:
    st.plotly_chart(
        px.bar(
            extracted,
            x="document_id",
            y="auto_fill_confidence",
            color="predicted_type",
            title="Auto-fill confidence by document",
        ),
        use_container_width=True,
    )
    st.plotly_chart(
        px.bar(
            extracted,
            x="document_id",
            y="field_match_count",
            color="predicted_type",
            title="Correctly matched fields by document",
        ),
        use_container_width=True,
    )

