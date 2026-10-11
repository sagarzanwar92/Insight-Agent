
from datetime import datetime, timedelta, timezone

from src.conversation.state import ConversationState


SESSION_TIMEOUT = timedelta(minutes=15)


class ConversationManager:
    def __init__(self):
        self._sessions: dict[str, ConversationState] = {}

    def get_or_create(self, conversation_id: str) -> ConversationState:
        now = datetime.now(timezone.utc)

        state = self._sessions.get(conversation_id)

        if state is not None:
            inactive_for = now - state.last_activity_at

            if inactive_for < SESSION_TIMEOUT:
                state.last_activity_at = now
                return state

            del self._sessions[conversation_id]

        state = ConversationState(conversation_id=conversation_id)
        self._sessions[conversation_id] = state

        return state

    def save(self, state: ConversationState) -> None:
        state.last_activity_at = datetime.now(timezone.utc)
        self._sessions[state.conversation_id] = state

    def clear(self, conversation_id: str) -> None:
        self._sessions.pop(conversation_id, None)
