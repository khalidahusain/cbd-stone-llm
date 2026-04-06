from fastapi import APIRouter, Depends

from backend.app.dependencies import get_conversation_service
from backend.app.services.conversation import ConversationService
from backend.app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    return await conversation_service.handle_turn(request)
