# Plan 02-03 Summary: FastAPI Wiring + Architectural Tests

**Status:** Complete
**Completed:** 2026-04-06

## What was done

1. **main.py** — Updated lifespan to initialize OpenAI client, SafeguardService, ExtractionService. Graceful degradation when OPENAI_API_KEY not set (D-17).
2. **extract router** (`backend/app/routers/extract.py`) — POST /extract accepts `{"text": "..."}`, returns ExtractionResult. 400 for safeguard rejection, 502 for API failure, 503 when extraction unavailable.
3. **health router** — Updated to include `extraction_ready: bool` field.
4. **dependencies.py** — Added `get_extraction_service` and `get_safeguard_service`.
5. **Architectural tests** (`backend/tests/test_architectural.py`) — 8 tests proving SAFE-01 (no LLM-to-inference path) and INFR-02 (no API key leakage).
6. **Integration tests** (`backend/tests/test_extract_api.py`) — 4 tests for /extract and /health endpoints with mocked OpenAI.

## Full test suite

83/83 tests passing across 8 test files (Phase 1 + Phase 2, zero regressions).

## Artifacts

| File | Purpose |
|------|---------|
| backend/main.py | Updated lifespan with extraction services |
| backend/app/routers/extract.py | POST /extract endpoint |
| backend/app/routers/health.py | Updated with extraction_ready |
| backend/app/dependencies.py | New DI wrappers |
| backend/tests/test_extract_api.py | 4 integration tests |
| backend/tests/test_architectural.py | 8 architectural tests |
