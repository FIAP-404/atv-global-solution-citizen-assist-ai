from pathlib import Path
from typing import Any

from backend.errors import ModuleNotReadyError


def load_services(path: Path) -> list[dict[str, Any]]:
    """Load and validate the verified JSON base. Team package 1 owns this body."""
    raise ModuleNotReadyError("knowledge")
