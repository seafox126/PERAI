from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntentResult:
    intent: str
    parameters: dict[str, Any] = field(default_factory=dict)
