# Plan 02-02 Summary: ExtractionService + SafeguardService

**Status:** Complete
**Completed:** 2026-04-06

## What was done

1. **SafeguardService** (`backend/app/services/safeguard.py`) — Pre-LLM injection detection (14 regex patterns) and post-LLM output scanning (8 probability/recommendation patterns). Returns SafeguardResult dataclass.
2. **ExtractionService** (`backend/app/services/extraction.py`) — Calls OpenAI `beta.chat.completions.parse()` with ExtractionResult as response_format. Integrates SafeguardService pre/post. Handles model refusal (D-19). Temperature=0 for deterministic extraction.
3. **19 tests** — 11 safeguard tests (injection detection, output blocking, no false positives) + 8 extraction tests (mocked OpenAI, injection blocking, refusal handling, architectural enforcement).

## Key design points

- ExtractionService has NO reference to InferenceService (SAFE-01, verified by test)
- Injection patterns tuned to avoid false positives on legitimate clinical text
- Model refusal raises ExtractionError (D-19)

## Artifacts

| File | Purpose |
|------|---------|
| backend/app/services/safeguard.py | Injection defense + output scanning |
| backend/app/services/extraction.py | OpenAI structured output extraction |
| backend/tests/test_safeguard.py | 11 safeguard tests |
| backend/tests/test_extraction.py | 8 extraction tests |
