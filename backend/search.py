from typing import Any

from backend.errors import ModuleNotReadyError


def search_services(
    records: list[dict[str, Any]], query: str, topic: str = "all"
) -> list[dict[str, Any]]:
    """Rank orientations and filter themes. Team package 2 owns this body."""
    raise ModuleNotReadyError("search")
