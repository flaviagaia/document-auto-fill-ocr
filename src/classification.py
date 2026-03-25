from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def classify_documents(ocr_lines: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    grouped = ocr_lines.groupby("document_id")["ocr_text"].apply(lambda values: " ".join(values)).reset_index()
    labeled = grouped.merge(metadata[["document_id", "document_type"]], on="document_id", how="left")

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    X = vectorizer.fit_transform(labeled["ocr_text"])
    y = labeled["document_type"]
    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X, y)

    labeled["predicted_type"] = model.predict(X)
    labeled["classification_confidence"] = model.predict_proba(X).max(axis=1)
    return labeled[["document_id", "document_type", "predicted_type", "classification_confidence", "ocr_text"]]

