from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.app.dependencies import get_schema
from backend.app.core.schema_loader import FeatureSchema

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    features_count: int
    extraction_ready: bool
    conversation_ready: bool


@router.get("/health", response_model=HealthResponse)
def health(request: Request, schema: FeatureSchema = Depends(get_schema)):
    extraction_ready = getattr(request.app.state, "extraction_service", None) is not None
    conversation_ready = getattr(request.app.state, "conversation_service", None) is not None
    return HealthResponse(
        status="ok",
        model_loaded=True,
        features_count=len(schema.features),
        extraction_ready=extraction_ready,
        conversation_ready=conversation_ready,
    )
