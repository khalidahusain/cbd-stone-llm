from typing import Optional

from backend.app.core.schema_loader import FeatureSchema
from backend.app.core.session_store import SessionStore, Session
from backend.app.core.reply_builder import ReplyBuilder, FOLLOW_UP_PRIORITY
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.extraction import ExtractionResult
from backend.app.schemas.prediction import PredictionResult, InsufficientInfoResult
from backend.app.services.extraction import ExtractionService, ExtractionError
from backend.app.services.inference import InferenceService
from backend.app.services.validation import ValidationService

CONFIRMATION_KEYWORDS = {"yes", "confirm", "correct", "looks good", "run", "go", "ok", "okay"}


class ConversationService:
    def __init__(
        self,
        schema: FeatureSchema,
        session_store: SessionStore,
        extraction_service: Optional[ExtractionService],
        inference_service: InferenceService,
        validation_service: ValidationService,
        reply_builder: ReplyBuilder,
    ):
        self.schema = schema
        self.sessions = session_store
        self.extraction = extraction_service
        self.inference = inference_service
        self.validation = validation_service
        self.replies = reply_builder

    async def handle_turn(self, request: ChatRequest) -> ChatResponse:
        """Handle one conversation turn."""
        # Step 1: Get or create session
        session = None
        if request.session_id:
            session = self.sessions.get_session(request.session_id)
            if session is None:
                return ChatResponse(
                    session_id=request.session_id,
                    message="Session expired or not found. Please start a new conversation.",
                    extracted_features={},
                    conversation_phase="collecting",
                    missing_required=list(FOLLOW_UP_PRIORITY),
                    turn_number=0,
                )

        is_new_session = session is None
        if is_new_session:
            session = self.sessions.create_session()

        # Step 2: Record user message
        session.message_history.append({"role": "user", "content": request.message})
        turn_number = len([m for m in session.message_history if m["role"] == "user"])

        # Step 3: Check for confirmation keyword
        if session.conversation_phase == "awaiting_confirmation":
            if request.message.strip().lower() in CONFIRMATION_KEYWORDS:
                return await self._handle_confirmation(session, turn_number)
            session.conversation_phase = "collecting"

        # Step 4: Check extraction service availability
        if self.extraction is None:
            reply = "Extraction service unavailable. Please configure OPENAI_API_KEY."
            session.message_history.append({"role": "assistant", "content": reply})
            self.sessions.update_session(session)
            return self._build_response(session, reply, turn_number)

        # Step 5: Extract
        try:
            extraction = await self.extraction.extract(request.message)
        except ExtractionError as e:
            reply = str(e)
            session.message_history.append({"role": "assistant", "content": reply})
            self.sessions.update_session(session)
            return self._build_response(session, reply, turn_number)

        # Step 6: Validate extracted values
        new_features = extraction.to_feature_dict()
        if new_features:
            errors = self.validation.validate(new_features)
            if errors:
                reply = self.replies.build_validation_error_reply(errors)
                session.message_history.append({"role": "assistant", "content": reply})
                self.sessions.update_session(session)
                return self._build_response(session, reply, turn_number)

        # Step 7: Merge into session state
        updated_fields = []
        for name, value in new_features.items():
            if value is not None:
                if session.extracted_features.get(name) != value:
                    updated_fields.append(name)
                session.extracted_features[name] = value

        # Step 8: Phase-dependent reply
        if session.conversation_phase == "confirmed":
            return await self._handle_post_confirmation(session, updated_fields, turn_number)

        reply, ready = self.replies.build_collecting_reply(extraction, session.extracted_features)

        if is_new_session and not new_features:
            reply = self.replies.build_welcome_reply()

        if ready:
            session.conversation_phase = "awaiting_confirmation"
            reply = self.replies.build_confirmation_reply(session.extracted_features)

        session.message_history.append({"role": "assistant", "content": reply})
        self.sessions.update_session(session)
        return self._build_response(session, reply, turn_number)

    async def _handle_confirmation(self, session: Session, turn_number: int) -> ChatResponse:
        """Handle clinician confirmation — run prediction."""
        session.confirmed = True
        session.conversation_phase = "confirmed"

        result = self.inference.predict(session.extracted_features)

        if isinstance(result, InsufficientInfoResult):
            reply = self.replies.build_insufficient_info_reply(result.missing_required)
            session.conversation_phase = "collecting"
            session.confirmed = False
        else:
            session.prediction = result
            reply = self.replies.build_confirmed_reply(result)

        session.message_history.append({"role": "assistant", "content": reply})
        self.sessions.update_session(session)
        return self._build_response(session, reply, turn_number)

    async def _handle_post_confirmation(
        self, session: Session, updated_fields: list[str], turn_number: int
    ) -> ChatResponse:
        """Handle turn after confirmation — auto-predict with updated data."""
        if not updated_fields:
            reply = "No new information extracted. The current prediction is unchanged."
        else:
            result = self.inference.predict(session.extracted_features)
            if isinstance(result, InsufficientInfoResult):
                reply = self.replies.build_insufficient_info_reply(result.missing_required)
            else:
                session.prediction = result
                reply = self.replies.build_update_reply(result, updated_fields)

        session.message_history.append({"role": "assistant", "content": reply})
        self.sessions.update_session(session)
        return self._build_response(session, reply, turn_number)

    def _build_response(self, session: Session, message: str, turn_number: int) -> ChatResponse:
        missing = [
            name for name in FOLLOW_UP_PRIORITY
            if name not in session.extracted_features or session.extracted_features[name] is None
        ]
        return ChatResponse(
            session_id=session.session_id,
            message=message,
            extracted_features=session.extracted_features,
            prediction=session.prediction,
            conversation_phase=session.conversation_phase,
            missing_required=missing,
            turn_number=turn_number,
        )
