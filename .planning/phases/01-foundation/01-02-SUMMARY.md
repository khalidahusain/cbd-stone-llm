# Plan 01-02 Summary: SchemaLoader, InferenceService, ValidationService

**Status:** Complete
**Completed:** 2026-04-06

## What was done

1. **SchemaLoader** (`backend/app/core/schema_loader.py`) — Parses features.yaml into typed dataclasses (FeatureDefinition, RiskTier, CostConfig, FeatureSchema). Validates schema columns against pkl model's feature_names_in_.
2. **InferenceService** (`backend/app/services/inference.py`) — Loads all 6 pkl files, runs full prediction pipeline: encoding, imputation, predict_proba, risk tier classification, cost calculation, cholangitis fast-path. Uses imputer's feature_names_in_ for column ordering.
3. **ValidationService** (`backend/app/services/validation.py`) — Validates input against YAML-defined ranges, allowed values, and types.
4. **Pydantic schemas** (`backend/app/schemas/prediction.py`) — PredictionResult, CostEstimate, ValidationErrorDetail, InsufficientInfoResult, BilirubinWarning.
5. **Unit tests** — 13 schema loader tests + 12 inference/validation tests, all passing.

## Key implementation detail

The imputer requires DataFrame columns in the exact order it was trained on. InferenceService uses `imputer.feature_names_in_` for column ordering rather than YAML feature order.

## Environment note

A venv with pinned dependencies (scikit-learn==1.5.2, numpy==1.26.4) was created at `backend/.venv/` because the base conda environment has incompatible versions.

## Artifacts

| File | Purpose |
|------|---------|
| backend/app/core/schema_loader.py | YAML parsing + pkl column validation |
| backend/app/services/inference.py | ML model loading + prediction pipeline |
| backend/app/services/validation.py | Input range checking |
| backend/app/schemas/prediction.py | Pydantic response models |
| backend/tests/test_schema_loader.py | 13 schema loader tests |
| backend/tests/test_inference.py | 12 inference + validation tests |
