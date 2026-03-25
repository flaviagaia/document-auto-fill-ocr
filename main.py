import json

from src.pipeline import run_pipeline


if __name__ == "__main__":
    summary = run_pipeline()
    print("Document Auto Fill OCR")
    print("-" * 32)
    print(json.dumps(summary, indent=2))

