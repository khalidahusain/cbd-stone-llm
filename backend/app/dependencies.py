from fastapi import Request

from backend.app.core.schema_loader import FeatureSchema
from backend.app.services.inference import InferenceService
from backend.app.services.validation import ValidationService
from backend.app.services.extraction import ExtractionService
from backend.app.services.safeguard import SafeguardService
from backend.app.services.conversation import ConversationService


def get_schema(request: Request) -> FeatureSchema:
    return request.app.state.schema


def get_inference_service(request: Request) -> InferenceService:
    return request.app.state.inference_service


def get_validation_service(request: Request) -> ValidationService:
    return request.app.state.validation_service


def get_extraction_service(request: Request) -> ExtractionService:
    return request.app.state.extraction_service


def get_safeguard_service(request: Request) -> SafeguardService:
    return request.app.state.safeguard_service


def get_conversation_service(request: Request) -> ConversationService:
    return request.app.state.conversation_service
