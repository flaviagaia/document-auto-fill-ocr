from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import DOCUMENT_METADATA_PATH, EXTRACTED_FIELDS_PATH, RAW_DIR, SUMMARY_PATH
from src.intake import match_uploaded_document, save_uploaded_image
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


st.set_page_config(page_title="Preenchimento Automático de Documentos com OCR", layout="wide")

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
        <h1>Preenchimento Automático de Documentos com OCR</h1>
        <p>Pipeline com OCR, classificação documental, extração de campos, cálculo de confiança e pré-preenchimento automático de formulários.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Reprocessar documentos demo"):
    run_pipeline()

summary, extracted, metadata = _load_artifacts()

metrics = st.columns(5)
metrics[0].metric("Documentos", summary["documents_processed"])
metrics[1].metric("Linhas OCR", summary["ocr_lines"])
metrics[2].metric("Acurácia do tipo", f"{summary['document_type_accuracy']:.2%}")
metrics[3].metric("Acurácia dos campos", f"{summary['field_accuracy']:.2%}")
metrics[4].metric("Confiança média", f"{summary['average_auto_fill_confidence']:.2%}")

tab_docs, tab_fields, tab_metrics = st.tabs(["Documentos", "Campos Preenchidos", "Métricas de Qualidade"])

with tab_docs:
    st.subheader("Enviar imagem do documento")
    uploaded_file = st.file_uploader(
        "Faça upload de uma imagem do documento",
        type=["png", "jpg", "jpeg"],
        help="Neste MVP, enviar uma das imagens demo dispara a visualização estruturada dos campos preenchidos.",
    )
    if uploaded_file is not None:
        uploaded_path = save_uploaded_image(uploaded_file.name, uploaded_file.getvalue())
        st.image(str(uploaded_path), caption="Documento enviado", use_container_width=True)
        matched_document_id = match_uploaded_document(uploaded_path, metadata)
        if matched_document_id:
            st.success(f"Documento reconhecido como amostra demo: {matched_document_id}")
            matched_row = extracted[extracted["document_id"] == matched_document_id].iloc[0]
            structured_view = pd.DataFrame(
                [
                    {"nome_campo": "tipo_documento", "valor_campo": matched_row["predicted_type"]},
                    {"nome_campo": "numero_documento", "valor_campo": matched_row["document_number"]},
                    {"nome_campo": "fornecedor_ou_orgao", "valor_campo": matched_row["supplier_name"]},
                    {"nome_campo": "data_emissao", "valor_campo": matched_row["issue_date"]},
                    {"nome_campo": "data_vencimento", "valor_campo": matched_row["due_date"]},
                    {"nome_campo": "identificador_fiscal", "valor_campo": matched_row["tax_id"]},
                    {"nome_campo": "valor_total", "valor_campo": matched_row["total_amount"]},
                    {"nome_campo": "confianca_autofill", "valor_campo": matched_row["auto_fill_confidence"]},
                ]
            )
            st.subheader("Visão estruturada tipo banco de dados")
            st.dataframe(structured_view, use_container_width=True, hide_index=True)
        else:
            st.warning(
                "Este MVP não conseguiu associar o arquivo enviado a uma das amostras demo de OCR. "
                "Em uma versão de produção, esta etapa chamaria um motor real como PaddleOCR ou Azure Document Intelligence."
            )

    st.divider()
    st.subheader("Galeria de documentos demo")
    selected_doc = st.selectbox("Selecione um documento", options=metadata["document_id"].tolist())
    doc_row = metadata[metadata["document_id"] == selected_doc].iloc[0]
    image_path = RAW_DIR.parent / Path(doc_row["image_path"])
    st.image(str(image_path), caption=f"{doc_row['document_type']} - {doc_row['document_id']}", use_container_width=True)

with tab_fields:
    st.dataframe(extracted, use_container_width=True, hide_index=True)
    selected_row = st.selectbox("Inspecionar campos estruturados", options=extracted["document_id"].tolist(), key="structured_selector")
    row = extracted[extracted["document_id"] == selected_row].iloc[0]
    structured_view = pd.DataFrame(
        [
            {"nome_coluna": "document_id", "valor": row["document_id"]},
            {"nome_coluna": "predicted_type", "valor": row["predicted_type"]},
            {"nome_coluna": "document_number", "valor": row["document_number"]},
            {"nome_coluna": "supplier_name", "valor": row["supplier_name"]},
            {"nome_coluna": "issue_date", "valor": row["issue_date"]},
            {"nome_coluna": "due_date", "valor": row["due_date"]},
            {"nome_coluna": "tax_id", "valor": row["tax_id"]},
            {"nome_coluna": "total_amount", "valor": row["total_amount"]},
            {"nome_coluna": "classification_confidence", "valor": row["classification_confidence"]},
            {"nome_coluna": "auto_fill_confidence", "valor": row["auto_fill_confidence"]},
        ]
    )
    st.subheader("Registro estruturado")
    st.dataframe(structured_view, use_container_width=True, hide_index=True)

with tab_metrics:
    st.plotly_chart(
        px.bar(
            extracted,
            x="document_id",
            y="auto_fill_confidence",
            color="predicted_type",
            title="Confiança do preenchimento automático por documento",
        ),
        use_container_width=True,
    )
    st.plotly_chart(
        px.bar(
            extracted,
            x="document_id",
            y="field_match_count",
            color="predicted_type",
            title="Campos corretamente identificados por documento",
        ),
        use_container_width=True,
    )
