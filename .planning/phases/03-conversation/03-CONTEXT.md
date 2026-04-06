# Phase 3: Conversation Orchestration - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the multi-turn conversation loop that wires ExtractionService, ValidationService, and InferenceService into a coherent clinical workflow. ConversationService orchestrates each turn: extract → validate → merge state → check missing → template reply → (optionally) predict. SessionStore holds per-session state server-side. POST /chat is the single endpoint the frontend will consume.

</domain>

<decisions>
## Implementation Decisions

### Conversation Flow
- **D-01:** Python-templated replies — no extra LLM call for response generation. ExtractionService.extract() is the only LLM call per turn. Replies are built from ExtractionResult using deterministic Python templates ("I found X, Y, Z. I still need A."). This is faster, cheaper, and avoids the risk of the response-generation LLM injecting clinical opinions.
- **D-02:** Conversation phases: `"collecting"` → `"awaiting_confirmation"` → `"confirmed"`. State machine transitions:
  - `collecting`: Required/strongly-recommended fields still missing. Reply includes what was found + follow-up question.
  - `awaiting_confirmation`: Required fields present. Reply shows structured summary, asks clinician to confirm.
  - `confirmed`: Clinician confirmed. Model runs. Subsequent turns update prediction iteratively without re-confirmation.

### Confirmation Flow
- **D-03:** Confirm once before first prediction, then iterate automatically (satisfies both EXTR-08 and CHAT-05). After the clinician confirms the initial extraction, new variables update the prediction automatically — no re-confirmation needed.
- **D-04:** Hybrid confirmation: clinician can type confirmation keywords in chat ("yes", "confirm", "correct", "looks good", "run", "go") OR the frontend (Phase 4) can use the `conversation_phase: "awaiting_confirmation"` flag to render a confirm button. If the message doesn't match a confirmation keyword, treat it as new clinical input and re-extract.

### Follow-up Question Priority
- **D-05:** Only actively ask for required + strongly recommended fields: sex → age → total_bilirubin. At most 3 follow-up questions ever. Optional fields are extracted passively from the clinician's narrative but never actively requested. This minimizes friction for busy clinicians.
- **D-06:** One question per turn (CHAT-04). When multiple fields are missing, ask for the highest-priority one only. Priority order: sex (required, inference_prohibited) → age (required) → total_bilirubin (strongly_recommended).

### API Contract
- **D-07:** POST /chat request: `{ "session_id": Optional[str], "message": str }`. If session_id is null/omitted, create a new session and return the ID.
- **D-08:** POST /chat response includes full state every time (frontend is a dumb display layer):
  ```json
  {
    "session_id": "uuid",
    "message": "I found age=55, sex=Male. I still need bilirubin.",
    "extracted_features": {"sex": "Male", "age": 55.0},
    "prediction": null,
    "conversation_phase": "collecting",
    "missing_required": ["total_bilirubin"],
    "turn_number": 1
  }
  ```
  When prediction is available, the `prediction` field contains the full PredictionResult (probability, risk_tier, intervention, costs, cholangitis_flag, imputed_fields).
- **D-09:** The frontend sends only session_id + message. It never sends authoritative clinical data. The server-side session is the source of truth (INFR-03).

### Session Store
- **D-10:** In-process dict keyed by UUID (INFR-03). Each session holds: session_id, extracted_features (dict), message_history (list of {role, content}), conversation_phase, prediction (PredictionResult | None), confirmed (bool), created_at (datetime), last_accessed (datetime).
- **D-11:** TTL-based cleanup with 1-hour expiry. A background task (or lazy cleanup on access) removes sessions older than 1 hour. Simple in-process implementation — no Redis for v1, but the behavior is production-ready.
- **D-12:** Expired or unknown session_id returns a clear error, prompting the frontend to start a new session.

### State Merging
- **D-13:** Each turn, ExtractionResult is merged into the existing session state. New non-None values overwrite existing values. None values do not overwrite (the LLM not mentioning a field doesn't erase it). This prevents Pitfall 4 (multi-turn context loss).
- **D-14:** Server-side state is the source of truth for ML model input — not the LLM's interpretation of conversation history (per Pitfall 4). The LLM sees the current state + new message each turn, but the state dict is updated by Python merge logic, not by the LLM.

### Integration with Phase 2 Services
- **D-15:** ConversationService calls: SafeguardService.check_input() → ExtractionService.extract() → ValidationService.validate() → merge state → (if confirmed) InferenceService.predict(). This is the only code path that connects extraction to inference — orchestrated by Python, not by the LLM.
- **D-16:** Validation errors from extracted values are surfaced in the reply template: "The extracted AST value of -5 is outside the valid range (0-10000 U/L). Could you double-check?"

### Claude's Discretion
- Reply template exact wording and formatting
- Session dataclass field naming
- Background cleanup implementation (asyncio task vs. lazy cleanup)
- Test fixture structure for multi-turn conversation tests
- Pydantic request/response model names

</decisions>

<specifics>
## Specific Ideas

- The reply template should be structured with clear sections: "Extracted:", "Still needed:", "Follow-up question:" — so the clinician can quickly scan what happened
- The confirmation summary should show a clean table of all extracted values with their units and sources (provided vs. will be imputed)
- When in `confirmed` phase and new variables arrive, the reply should say "Updated [field]. Prediction recalculated." — short and direct
- The conversation_phase field enables the frontend to conditionally render UI elements: show confirm button during `awaiting_confirmation`, show dashboard during `confirmed`
- Message history stored in session should use OpenAI format {role, content} for potential future use in multi-turn LLM context

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 2 Outputs (extraction layer to build on)
- `backend/app/services/extraction.py` — ExtractionService.extract() returns ExtractionResult
- `backend/app/services/safeguard.py` — SafeguardService.check_input() / check_output()
- `backend/app/schemas/extraction.py` — ExtractionResult with to_feature_dict()

### Phase 1 Outputs (inference and validation)
- `backend/app/services/inference.py` — InferenceService.predict() returns PredictionResult | InsufficientInfoResult
- `backend/app/services/validation.py` — ValidationService.validate() returns list[ValidationErrorDetail]
- `backend/app/schemas/prediction.py` — PredictionResult, InsufficientInfoResult
- `backend/app/core/schema_loader.py` — FeatureSchema with get_required_features()
- `backend/main.py` — Lifespan pattern, app.state service storage
- `backend/app/dependencies.py` — Dependency injection pattern

### Research
- `.planning/research/ARCHITECTURE.md` — ConversationService design, data flow, session store pattern
- `.planning/research/PITFALLS.md` — Pitfall 4 (multi-turn context loss), Pitfall 6 (redundant questions), Pitfall 9 (automation bias)

### Project Context
- `.planning/PROJECT.md` — Core value: ML model is source of truth
- `.planning/REQUIREMENTS.md` — Phase 3 requirements: CHAT-01–05, EXTR-06–08, INFR-03

</canonical_refs>

<code_context>
## Existing Code Insights

### Interfaces to Use
- `ExtractionService.extract(user_input: str) -> ExtractionResult` — single LLM call per turn
- `ExtractionResult.to_feature_dict() -> dict` — converts to format for ValidationService/InferenceService
- `ValidationService.validate(features: dict) -> list[ValidationErrorDetail]`
- `InferenceService.predict(features: dict) -> PredictionResult | InsufficientInfoResult`
- `SafeguardService.check_input(text) -> SafeguardResult` — pre-extraction guard
- `FeatureSchema.get_required_features() -> list[str]` — returns ["sex", "age"]

### New Modules to Create
- `backend/app/services/conversation.py` — ConversationService (orchestrator)
- `backend/app/core/session_store.py` — SessionStore (in-process dict + TTL)
- `backend/app/core/reply_builder.py` — ReplyBuilder (Python templates for chat responses)
- `backend/app/schemas/chat.py` — ChatRequest, ChatResponse Pydantic models
- `backend/app/routers/chat.py` — POST /chat endpoint

### Patterns to Follow
- Service class with `__init__(schema, ...)` pattern
- Pydantic models in `backend/app/schemas/`
- FastAPI dependency injection via `backend/app/dependencies.py`
- Tests in `backend/tests/` using pytest

</code_context>

<deferred>
## Deferred Ideas

- LLM-generated natural language replies — deferred; Python templates are sufficient for v1
- Re-confirmation on subsequent turns — deferred; confirm once then iterate
- LLM-driven follow-up question selection — deferred; fixed priority is sufficient
- Streaming responses (SSE) — deferred to Phase 4 or later
- Persistent session storage (Redis) — deferred to v2 production deployment

</deferred>

---

*Phase: 03-conversation*
*Context gathered: 2026-04-06 via interactive discussion*
