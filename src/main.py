import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from backend import assistant, evaluation, knowledge
from backend.config import DATA_PATH, DEMO_CASES_PATH, EVALUATION_PATH
from backend.contracts import AnswerResponse
from backend.errors import ModuleNotReadyError


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Consult source-bound public-service guidance without external AI."
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--question", help="Question to look up in the verified knowledge base."
    )
    action.add_argument(
        "--evaluate",
        action="store_true",
        help="Run both response modes against the evaluation cases.",
    )
    parser.add_argument("--mode", choices=["direct", "steps"], default="direct")
    parser.add_argument("--cases", type=Path, default=DEMO_CASES_PATH)
    parser.add_argument("--output", type=Path, default=EVALUATION_PATH)
    args = parser.parse_args(argv)
    try:
        records = knowledge.load_services(DATA_PATH)
        if args.evaluate:
            cases = json.loads(args.cases.read_text(encoding="utf-8"))
            if not isinstance(cases, list):
                raise ValueError("Evaluation cases must be a JSON array.")
            result = evaluation.evaluate_questions(records, cases, args.output)
        else:
            question = (
                args.question
                if args.question is not None
                else input("Enter your question: ")
            )
            if len(question) > 500:
                raise ValueError("Questions must contain at most 500 characters.")
            result = AnswerResponse.model_validate(
                assistant.answer_question(records, question, args.mode)
            ).model_dump(mode="json")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ModuleNotReadyError, OSError, ValueError, EOFError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
