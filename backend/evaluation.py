from pathlib import Path
from typing import Any

from backend.errors import ModuleNotReadyError


def evaluate_questions(
    records: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    output_path: Path,
) -> dict[str, Any]:
    """Measure both response modes and save actual evidence. Package 4 owns this body."""
    raise ModuleNotReadyError("evaluation")
