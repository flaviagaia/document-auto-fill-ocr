import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import DOCUMENT_METADATA_PATH, EXTRACTED_FIELDS_PATH, SUMMARY_PATH
from src.pipeline import run_pipeline


class PipelineTestCase(unittest.TestCase):
    def test_pipeline_builds_demo_outputs(self):
        summary = run_pipeline()
        self.assertTrue(DOCUMENT_METADATA_PATH.exists())
        self.assertTrue(EXTRACTED_FIELDS_PATH.exists())
        self.assertTrue(SUMMARY_PATH.exists())
        self.assertEqual(summary["documents_processed"], 4)
        self.assertGreaterEqual(summary["field_accuracy"], 0.8)


if __name__ == "__main__":
    unittest.main()

