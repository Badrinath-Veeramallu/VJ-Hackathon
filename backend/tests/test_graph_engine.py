import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.graph_engine import InteractionGraph


class TestInteractionGraph(unittest.TestCase):
    def setUp(self):
        self.graph = InteractionGraph()

    def test_known_drug_pair_flags_critical(self):
        result = self.graph.check_all(
            generics=["warfarin", "aspirin"], allergies=[], diagnoses=[]
        )
        self.assertEqual(result["overall_severity"], "critical")
        self.assertEqual(result["alert_count"], 1)
        self.assertEqual(result["alerts"][0]["type"], "drug_drug")

    def test_no_interaction_returns_none_severity(self):
        result = self.graph.check_all(
            generics=["paracetamol"], allergies=[], diagnoses=[]
        )
        self.assertEqual(result["overall_severity"], "none")
        self.assertEqual(result["alert_count"], 0)

    def test_allergy_flagged_as_critical(self):
        result = self.graph.check_all(
            generics=["metformin"], allergies=["metformin"], diagnoses=[]
        )
        self.assertEqual(result["alert_count"], 1)
        self.assertEqual(result["alerts"][0]["type"], "drug_allergy")

    def test_duplicate_therapy_detected(self):
        result = self.graph.check_all(
            generics=["paracetamol", "paracetamol"], allergies=[], diagnoses=[]
        )
        self.assertEqual(result["alert_count"], 1)
        self.assertEqual(result["alerts"][0]["type"], "duplicate_therapy")

    def test_drug_disease_contraindication(self):
        result = self.graph.check_all(
            generics=["ibuprofen"], allergies=[], diagnoses=["renal impairment"]
        )
        self.assertEqual(result["alert_count"], 1)
        self.assertEqual(result["alerts"][0]["type"], "drug_disease")


if __name__ == "__main__":
    unittest.main()
