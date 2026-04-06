# Phase 1: Foundation - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the ML inference pipeline end-to-end: YAML feature schema validated against pkl model columns, all six model files loaded at FastAPI startup, and a working /predict endpoint that returns probability, risk tier, recommended intervention, cost estimates, cholangitis flag, and imputed fields list. This is the foundation that all subsequent phases build on.

</domain>

<decisions>
## Implementation Decisions

### YAML Schema Design
- **D-01:** Use human-readable clinical field names in features.yaml (e.g., `total_bilirubin`, `abdominal_ultrasound_performed`, `cbd_stone_on_ultrasound`). Map to exact model column names (e.g., `T. Bilirubin`, `Abd US`, `CBD stone on Abd US`) internally via a `model_column` field.
- **D-02:** Each feature entry includes: `name` (clinical), `model_column` (exact pkl match), `type` (numeric/boolean/categorical), `required` (boolean), `valid_range` (min/max for numeric, allowed values for categorical), `description` (for LLM context), `unit` (if applicable).
- **D-03:** Hard-required fields that block model execution: `sex` and `age`. Model will not run without these.
- **D-04:** Bilirubin is "strongly recommended" — system warns that prediction quality degrades without it, but allows clinician to explicitly override and proceed with imputation.
- **D-05:** All other fields (labs, conditions, imaging, Charlson index) are optional and can be imputed by the iterative imputer.

### API Contract Design
- **D-06:** /predict response includes: `probability` (float 0-100), `risk_tier` (string: "low"/"intermediate"/"high"/"very_high"), `recommended_intervention` (string: "CCY ± IOC"/"MRCP"/"EUS"/"ERCP"), `cost_estimates` (dict with IOC/MRCP/ERCP/EUS probability-weighted costs), `cholangitis_flag` (boolean + guideline text if true), `imputed_fields` (list of field names that were imputed rather than provided).
- **D-07:** Use standard HTTP status codes for errors: 422 for validation errors (out-of-range values), 400 for missing required fields, 200 for success. JSON error body: `{"error": "type", "field": "name", "message": "human-readable"}`.
- **D-08:** /predict accepts a flat JSON dict of feature values keyed by clinical names from the YAML schema. Backend maps to model column names before inference.

### Project Structure
- **D-09:** Monorepo with `/backend` (Python/FastAPI) and `/frontend` (React/Vite). Shared config at root. Single git repo.
- **D-10:** Extract .pkl model files and chosen_features_label.txt from `docs/cbd app/` to `backend/models/` and `backend/config/`. Leave rest of docs/ as reference material.
- **D-11:** Backend entry point: `backend/main.py`. YAML schema: `backend/config/features.yaml`. Models directory: `backend/models/`.

### Model Serving Strategy
- **D-12:** Load all .pkl files (initial.pkl, iterative_imputer.pkl, and 4 intervention models) in FastAPI lifespan context manager. Store in `app.state` for access in endpoints.
- **D-13:** Strict startup validation: assert YAML schema feature names map 1:1 with pkl model's expected feature columns. If any mismatch, server refuses to start with a clear error message listing the discrepancies.
- **D-14:** The iterative imputer handles missing non-required values. The application code fills missing optional fields with NaN before passing to the imputer, then to the model.

### Claude's Discretion
- FastAPI project scaffold (pyproject.toml vs requirements.txt, folder conventions)
- Specific Pydantic model names and internal class structure
- Test framework choice (pytest assumed)
- CORS configuration details (needed for frontend in later phases)
- Logging approach

</decisions>

<specifics>
## Specific Ideas

- The existing cost calculation formula from app.py (lines 548-562): `cost_0 + cost_1 * initial_pred / 100` where cost_values are `{'MRCP': [1215.08, 3620.92], 'EUS': [2986.58, 3566.92], 'ERCP': [4451, 0], 'IOC': [600, 4451]}`
- Risk tier thresholds from existing visualization: 0-10% = CCY ± IOC, 10-44% = MRCP, 44-90% = EUS, 90-100% = ERCP
- Cholangitis fast-path: when cholangitis=YES, the existing app blurs the management chart and overlays "ASGE 2019 guidelines recommend all patients with cholangitis undergo ERCP as clinically appropriate"
- The existing model uses these exact column names (from chosen_features_label.txt): Gender, Clinical cholangitis, Clinical pancreatitis, Clinical cholecystitis, First AST, First ALT, First Alkaline Phosphatase, First total bilirubin, Abdominal Ultrasound performed?, CBD stone on US, CBD stone on CT, Total points (Charlson), Age

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Model Assets
- `docs/cbd app/Models/` — All 6 pkl files (initial.pkl, iterative_imputer.pkl, 4 intervention models)
- `docs/cbd app/assets/chosen_features_label.txt` — Exact feature column names the model expects
- `docs/cbd app/assets/abbreviation.json` — Feature abbreviation mappings

### Existing Application Logic
- `docs/cbd app/app.py` lines 411-578 — Model inference logic, feature encoding, cost calculation, cholangitis handling
- `docs/cbd app/assets/utils.py` lines 164-233 — Risk tier thresholds and visualization logic

### Research
- `.planning/research/STACK.md` — Verified library versions, scikit-learn pinning constraint
- `.planning/research/ARCHITECTURE.md` — Component boundaries, FastAPI lifespan pattern, build order
- `.planning/research/PITFALLS.md` — Fabricated extraction values, pickle compatibility risks

### Project Context
- `.planning/PROJECT.md` — Full project context, constraints, key decisions
- `.planning/REQUIREMENTS.md` — Phase 1 requirements: INFR-01, INFR-04, INFR-05, EXTR-02, MODL-01–07
- `.planning/codebase/STACK.md` — Existing technology analysis
- `docs/environment.yml` — Conda environment with pinned versions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/cbd app/Models/*.pkl` — 6 serialized scikit-learn models, copy to backend/models/
- `docs/cbd app/assets/chosen_features_label.txt` — Feature column names (source of truth for YAML model_column values)
- `docs/cbd app/assets/abbreviation.json` — Medical abbreviation mappings
- Cost values from app.py line 8-13: hardcoded dict with MRCP/EUS/ERCP/IOC costs

### Established Patterns
- Model loading: `joblib.load(f'./Models/{f}')` — use same joblib approach
- Feature encoding: `replace({"YES": 1, "NO": 0, "Male": 1, "Female": 0})` — binary encoding
- Imputation: `models['iterative_imputer.pkl'].transform(patient_df)` — imputer expects DataFrame with same columns
- Prediction: `model.predict_proba(patient_imputed)[0]` — returns [prob_no_stone, prob_stone]

### Integration Points
- The /predict endpoint is the single integration point for Phase 2 (LLM extraction) and Phase 4 (React frontend)
- YAML schema is the integration point between model inference and LLM extraction

</code_context>

<deferred>
## Deferred Ideas

None — discussion focused on Phase 1 scope.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-04-05 via interactive discussion*
