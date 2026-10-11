
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from datetime import timedelta


@dataclass
class ConversationState:
    conversation_id: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    last_activity_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    messages: list[dict[str, str]] = field(default_factory=list)

    context: dict[str, Any] = field(default_factory=dict)

    findings: list[dict[str, Any]] = field(default_factory=list)
