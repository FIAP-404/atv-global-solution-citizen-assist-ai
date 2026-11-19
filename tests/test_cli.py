import io
import json
import unittest
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from src.main import main
from backend.config import DEMO_CASES_PATH
from backend.errors import ModuleNotReadyError


class CliHandoffTests(unittest.TestCase):
    def test_pending_module_returns_nonzero_and_no_answer(self):
        output, error = io.StringIO(), io.StringIO()
        with patch(
            "backend.knowledge.load_services",
            side_effect=ModuleNotReadyError("knowledge"),
        ):
            with redirect_stdout(output), redirect_stderr(error):
                result = main(["--question", "CPF"])
        self.assertEqual(result, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("pending", error.getvalue().lower())

    def test_terminal_uses_the_shared_response_module(self):
        answer = {
            "status": "unsupported",
            "message": "No reliable guidance",
            "services": [],
            "mode": "direct",
        }
        output = io.StringIO()
        with patch("backend.knowledge.load_services", return_value=[]):
            with patch(
                "backend.assistant.answer_question", return_value=answer
            ) as respond:
                with redirect_stdout(output):
                    result = main(["--question", "weather", "--mode", "direct"])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue()), answer)
        respond.assert_called_once_with([], "weather", "direct")

    def test_evaluation_dispatches_cases_and_output_path_to_evaluation_owner(self):
        report = {"summary": {"direct": {}, "steps": {}}, "cases": []}
        output = io.StringIO()
        with patch("backend.knowledge.load_services", return_value=[]):
            with patch(
                "backend.evaluation.evaluate_questions", return_value=report
            ) as evaluate:
                with redirect_stdout(output):
                    result = main(
                        ["--evaluate", "--output", "results/test-report.json"]
                    )
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue()), report)
        cases = json.loads(DEMO_CASES_PATH.read_text(encoding="utf-8"))
        evaluate.assert_called_once_with([], cases, Path("results/test-report.json"))

    def test_invalid_question_is_rejected_before_loading_the_base(self):
        output, error = io.StringIO(), io.StringIO()
        with patch("backend.knowledge.load_services", return_value=[]) as load:
            with redirect_stdout(output), redirect_stderr(error):
                result = main(["--question", "a" * 501])
        self.assertEqual(result, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("500", error.getvalue())
        load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
