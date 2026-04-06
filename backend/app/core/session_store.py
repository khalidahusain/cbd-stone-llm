import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

from backend.app.schemas.prediction import PredictionResult


@dataclass
class Session:
    session_id: str
    extracted_features: dict = field(default_factory=dict)
    message_history: list[dict] = field(default_factory=list)
    conversation_phase: str = "collecting"
    prediction: Optional[PredictionResult] = None
    confirmed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)


class SessionStore:
    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: dict[str, Session] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def create_session(self) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if datetime.utcnow() - session.last_accessed > self._ttl:
            del self._sessions[session_id]
            return None
        session.last_accessed = datetime.utcnow()
        return session

    def update_session(self, session: Session) -> None:
        session.last_accessed = datetime.utcnow()
        self._sessions[session.session_id] = session

    def cleanup(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        now = datetime.utcnow()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.last_accessed > self._ttl
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    @property
    def session_count(self) -> int:
        return len(self._sessions)
