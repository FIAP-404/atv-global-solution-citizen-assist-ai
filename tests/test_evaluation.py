import json
import tempfile
import unittest
from itertools import count
from pathlib import Path
from unittest.mock import patch

from backend import evaluation
from backend.config import DEMO_CASES_PATH
from backend.knowledge import load_services

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "services.demo.json"


def fake_clock(step=0.002):
    """Relógio determinístico: cada consulta leva exatamente ``step`` segundos."""
    ticks = count()
    return lambda: next(ticks) * step / 2


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_services(DATA)
        cls.cases = json.loads(DEMO_CASES_PATH.read_text(encoding="utf-8"))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "nested" / "evaluation.json"

    def run_case(self, case, mode="direct"):
        return evaluation.run_case(self.records, case, mode, clock=fake_clock())

    # --- conjunto de casos -----------------------------------------------

    def test_case_set_meets_the_assignment(self):
        evaluation.validate_cases(self.cases)
        categories = [c["category"] for c in self.cases]
        self.assertGreaterEqual(len(self.cases), 12)
        self.assertGreaterEqual(categories.count("reformulation"), 5)
        self.assertGreaterEqual(categories.count("out-of-scope"), 5)
        statuses = {c["expectedStatus"] for c in self.cases}
        self.assertTrue({"empty", "ambiguous", "unsupported", "matched", "error"} <= statuses)
        self.assertTrue(any(len(c["question"]) > 500 for c in self.cases))
        self.assertTrue(any("requestMode" in c for c in self.cases))

    def test_malformed_cases_are_rejected(self):
        invalid = [
            [],
            [{"question": "CPF", "expectedStatus": "matched"}],
            [{"id": "a", "question": 1, "expectedStatus": "empty"}],
            [{"id": "a", "question": "CPF", "expectedStatus": "talvez"}],
            [{"id": "a", "question": "CPF", "expectedStatus": "matched"}],
            [{"id": "a", "question": " ", "expectedStatus": "empty"}] * 2,
        ]
        for cases in invalid:
            with self.subTest(cases=cases):
                with self.assertRaises(ValueError):
                    evaluation.evaluate_questions(self.records, cases, self.out)
        self.assertFalse(self.out.exists())

    # --- classificação ---------------------------------------------------

    def test_correct_match_records_expected_actual_and_time(self):
        case = {
            "id": "fgts",
            "question": "Como consultar FGTS?",
            "expectedStatus": "matched",
            "expectedServiceId": "fgts",
            "expectedFacts": ["Caixa Econômica Federal"],
        }
        row = self.run_case(case)
        self.assertTrue(row["retrievalCorrect"])
        self.assertTrue(row["responseCorrect"])
        self.assertEqual(row["expected"]["serviceId"], "fgts")
        self.assertEqual(row["actual"]["serviceIds"], ["fgts"])
        self.assertIn("Fonte:", row["actual"]["message"])
        self.assertEqual(row["durationMs"], 1.0)

    def test_wrong_service_is_a_retrieval_error(self):
        case = {"id": "x", "question": "FGTS", "expectedStatus": "matched", "expectedServiceId": "cpf"}
        row = self.run_case(case)
        self.assertFalse(row["retrievalCorrect"])
        self.assertFalse(row["responseCorrect"])
        self.assertIn("orientação fgts", row["problems"][0])

    def test_missing_fact_is_a_response_error_not_a_retrieval_error(self):
        case = {
            "id": "x",
            "question": "FGTS",
            "expectedStatus": "matched",
            "expectedServiceId": "fgts",
            "expectedFacts": ["valor de R$ 1.000"],
        }
        row = self.run_case(case)
        self.assertTrue(row["retrievalCorrect"])
        self.assertFalse(row["responseCorrect"])
        self.assertEqual(row["problems"], ["fato ausente: valor de R$ 1.000"])

    def test_facts_ignore_case_and_accents(self):
        case = {
            "id": "x",
            "question": "FGTS",
            "expectedStatus": "matched",
            "expectedServiceId": "fgts",
            "expectedFacts": ["CAIXA ECONOMICA FEDERAL"],
        }
        self.assertTrue(self.run_case(case)["responseCorrect"])

    def test_expected_errors_and_unexpected_errors(self):
        long_case = {"id": "long", "question": "a" * 501, "expectedStatus": "error"}
        mode_case = {"id": "mode", "question": "CPF", "requestMode": "audio", "expectedStatus": "error"}
        for case in (long_case, mode_case):
            with self.subTest(case=case["id"]):
                row = self.run_case(case)
                self.assertTrue(row["responseCorrect"])
                self.assertEqual(row["actual"]["status"], "error")
        wrong = self.run_case({**long_case, "expectedStatus": "unsupported"})
        self.assertFalse(wrong["responseCorrect"])
        self.assertIn("erro inesperado", wrong["problems"][0])
        not_error = self.run_case({"id": "x", "question": "CPF", "expectedStatus": "error"})
        self.assertFalse(not_error["responseCorrect"])

    def test_response_checks_for_other_statuses(self):
        good = {"status": "unsupported", "message": "Não encontrei. Temas: Trabalho.", "services": [], "mode": "direct"}
        self.assertEqual(evaluation._check_response({}, good), [])
        bad = {"status": "unsupported", "message": "Sem dados.", "services": [], "mode": "direct"}
        self.assertEqual(len(evaluation._check_response({}, bad)), 2)
        empty = {"status": "empty", "message": "Escolha um tema.", "services": [], "mode": "direct"}
        self.assertEqual(evaluation._check_response({}, empty), ["não pede a pergunta"])

    def test_contract_violation_is_an_error(self):
        broken = {"status": "matched", "message": "ok", "services": [], "mode": "direct"}
        with patch("backend.assistant.answer_question", return_value=broken):
            row = self.run_case({"id": "x", "question": "CPF", "expectedStatus": "matched", "expectedServiceId": "cpf"})
        self.assertFalse(row["responseCorrect"])
        self.assertIn("fora do contrato", row["problems"][0])

    # --- relatório -------------------------------------------------------

    def test_report_is_saved_and_returned(self):
        report = evaluation.evaluate_questions(self.records, self.cases, self.out)
        self.assertEqual(json.loads(self.out.read_text(encoding="utf-8")), report)
        self.assertFalse(report["externalAi"])
        self.assertEqual(set(report["summary"]), {"direct", "steps"})
        self.assertEqual(len(report["cases"]), 2 * len(self.cases))
        for mode, summary in report["summary"].items():
            with self.subTest(mode=mode):
                rows = [r for r in report["cases"] if r["mode"] == mode]
                self.assertEqual(summary["total"], len(self.cases))
                self.assertEqual(summary["correct"], sum(r["responseCorrect"] for r in rows))
                self.assertAlmostEqual(summary["accuracy"], summary["correct"] / summary["total"], places=4)
                self.assertGreater(summary["meanDurationMs"], 0)
                self.assertEqual(
                    sum(b["total"] for b in summary["byCategory"].values()), summary["total"]
                )

    def test_summary_math(self):
        rows = [
            {"mode": "direct", "category": "a", "caseId": "1", "responseCorrect": True, "retrievalCorrect": True, "durationMs": 1.0},
            {"mode": "direct", "category": "a", "caseId": "2", "responseCorrect": False, "retrievalCorrect": True, "durationMs": 3.0},
            {"mode": "direct", "category": "b", "caseId": "3", "responseCorrect": False, "retrievalCorrect": False, "durationMs": 2.0},
        ]
        summary = evaluation.summarize(rows)["direct"]
        self.assertEqual(summary["accuracy"], 0.3333)
        self.assertEqual(summary["retrievalAccuracy"], 0.6667)
        self.assertEqual(summary["meanDurationMs"], 2.0)
        self.assertEqual(summary["maxDurationMs"], 3.0)
        self.assertEqual(summary["failedCases"], ["2", "3"])
        self.assertEqual(summary["byCategory"]["a"], {"total": 2, "correct": 1, "accuracy": 0.5})

    def test_known_limitations_fail_in_both_modes(self):
        report = evaluation.evaluate_questions(self.records, self.cases, self.out)
        for mode in ("direct", "steps"):
            self.assertEqual(
                report["summary"][mode]["failedCases"],
                ["reform-registry-typo", "reform-registry-long"],
            )


if __name__ == "__main__":
    unittest.main()
