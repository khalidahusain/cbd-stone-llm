from typing import Optional

from pydantic import BaseModel

from backend.app.schemas.prediction import PredictionResult


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    message: str
    extracted_features: dict
    prediction: Optional[PredictionResult] = None
    conversation_phase: str
    missing_required: list[str] = []
    turn_number: int
