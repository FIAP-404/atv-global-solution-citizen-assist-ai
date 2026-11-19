from typing import Any

from backend.errors import ModuleNotReadyError


def answer_question(
    records: list[dict[str, Any]], question: str, mode: str = "direct"
) -> dict[str, Any]:
    """Apply source-bound instructions without external AI. Package 3 owns this body."""
    raise ModuleNotReadyError("assistant")
