import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.schema_loader import SchemaLoader
from backend.app.services.inference import InferenceService
from backend.app.services.validation import ValidationService
from backend.app.routers import predict, health, extract, chat

logger = logging.getLogger("cbd-stone-llm")

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Step 1: Load and validate schema
    schema = SchemaLoader.load(BASE_DIR / "config" / "features.yaml")
    logger.info(f"Loaded feature schema: {len(schema.features)} features")

    # Step 2: Load models
    inference_service = InferenceService(schema)
    inference_service.load_models(BASE_DIR / "models")
    logger.info("All 6 pkl models loaded successfully")

    # Step 3: Validate YAML matches pkl columns
    model = inference_service.models["initial"]
    if hasattr(model, "feature_names_in_"):
        model_feature_names = list(model.feature_names_in_)
        SchemaLoader.validate_against_model(schema, model_feature_names)
        logger.info("Schema validated against model feature columns")
    else:
        logger.warning("Model does not expose feature_names_in_; skipping column validation")

    # Step 4: Store Phase 1 services in app.state
    app.state.schema = schema
    app.state.inference_service = inference_service
    app.state.validation_service = ValidationService(schema)

    # Step 5: Initialize Phase 2 extraction services (D-17: graceful degradation)
    try:
        from backend.app.core.openai_client import create_openai_client
        from backend.app.services.safeguard import SafeguardService
        from backend.app.services.extraction import ExtractionService

        openai_client = create_openai_client()
        safeguard_service = SafeguardService()
        extraction_service = ExtractionService(schema, openai_client, safeguard_service)

        app.state.openai_client = openai_client
        app.state.safeguard_service = safeguard_service
        app.state.extraction_service = extraction_service
        logger.info("Extraction services initialized (OpenAI client ready)")
    except ValueError as e:
        logger.warning(f"Extraction services unavailable: {e}")
        app.state.openai_client = None
        app.state.safeguard_service = None
        app.state.extraction_service = None

    # Step 6: Initialize Phase 3 conversation services
    from backend.app.core.session_store import SessionStore
    from backend.app.core.reply_builder import ReplyBuilder
    from backend.app.services.conversation import ConversationService

    session_store = SessionStore(ttl_seconds=3600)
    reply_builder = ReplyBuilder(schema)
    conversation_service = ConversationService(
        schema=schema,
        session_store=session_store,
        extraction_service=app.state.extraction_service,
        inference_service=inference_service,
        validation_service=app.state.validation_service,
        reply_builder=reply_builder,
    )
    app.state.session_store = session_store
    app.state.reply_builder = reply_builder
    app.state.conversation_service = conversation_service

    logger.info("CBD Stone LLM backend ready")
    yield


app = FastAPI(
    title="CBD Stone LLM",
    description="Clinical decision support for choledocholithiasis risk stratification",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.17.67.98:450"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(predict.router, tags=["predict"])
app.include_router(extract.router, tags=["extract"])
app.include_router(chat.router, tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=451,
        reload=True,
        log_level="info",
    )
