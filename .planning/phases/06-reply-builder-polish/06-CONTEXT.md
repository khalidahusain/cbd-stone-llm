# Phase 6: Reply Builder Polish - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Make every chat message the system produces read like a clinician wrote it. All changes are in the reply-building layer (`backend/app/core/reply_builder.py`) and the feature schema (`backend/config/features.yaml`). No new endpoints, no new UI components, no model changes.

Requirements: PLSH-01, PLSH-02, PLSH-03, PLSH-04, PLSH-05, PLSH-06, PLSH-07.

</domain>

<decisions>
## Implementation Decisions

### Display Names (PLSH-01)
- **D-01:** Add a `display_name` field to each feature in `features.yaml` (e.g., `display_name: "Total Bilirubin"`). This is the single source of truth for human-readable field names in all user-facing chat messages.
- **D-02:** `ReplyBuilder` reads `display_name` instead of `name` for all user-facing text. No snake_case or internal identifiers in chat messages.

### Confirmation Summary (PLSH-02, PLSH-03)
- **D-03:** Add a `category` field to each feature in `features.yaml` with values: `demographics`, `labs`, `imaging`, `clinical_conditions`. The confirmation summary groups provided values under these category headings.
- **D-04:** Only clinician-provided values appear in the grouped confirmation summary. Imputed fields are summarized in one line listing all imputed field display names (no truncation). Example: "The model will estimate ALT, Alkaline Phosphatase, Cholangitis, Pancreatitis, Cholecystitis, Charlson Comorbidity Index."

### Extraction Feedback (PLSH-04)
- **D-05:** Extraction feedback uses concise clinical tone with a structured vertical list. Each extracted variable gets its own line with `display_name` and units. Format:
  ```
  Got it:

  - Sex: Male
  - Age: 50 years
  - Total Bilirubin: 3.2 mg/dL
  ```
- **D-06:** Prioritize readability and scannability over compact sentence formatting. No combining values into a single sentence.

### Follow-up Questions (PLSH-05)
- **D-07:** Add a `follow_up_question` field to each feature in `features.yaml` with a natural-sounding, clinician-friendly question (e.g., `"Do you have the patient's alkaline phosphatase level?"` for labs, `"Was a CBD stone seen on the abdominal ultrasound?"` for imaging booleans).
- **D-08:** Expand `FOLLOW_UP_PRIORITY` to include imaging fields: `[sex, age, total_bilirubin, abdominal_ultrasound_performed, cbd_stone_on_ultrasound, cbd_stone_on_ct]`. Only these priority fields get follow-up prompts; other missing fields are imputed silently.
- **D-09:** `ReplyBuilder` reads `follow_up_question` from YAML instead of using the hardcoded `FOLLOW_UP_QUESTIONS` dict.

### Prediction Result (PLSH-06)
- **D-10:** Prediction message uses natural risk explanation: "Based on the provided information, the estimated probability of a CBD stone is **X%** (Risk Tier). Recommended next step: **Intervention**."
- **D-11:** Replace the generic "You can continue providing additional clinical information" follow-up with a targeted next-best-variable prompt using the priority list and the YAML `follow_up_question`. Example: "To refine this prediction further, do you have the patient's alkaline phosphatase level?" If no priority variables remain missing, omit this line.

### Validation Errors (PLSH-07)
- **D-12:** Validation error messages show the clinician-provided value and explain the valid range in plain language using `display_name`. Example: "5000 is outside the valid range for Total Bilirubin (0-100 mg/dL). Could you double-check?"

### Claude's Discretion
- Exact wording of the imputation summary line (as long as it lists all imputed field display names)
- Exact wording of the prediction result message (as long as it follows the natural risk explanation pattern in D-10/D-11)
- Order of categories in confirmation summary (as long as all four are present)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Feature Schema
- `backend/config/features.yaml` -- Defines all 13 model features; will receive new `display_name`, `category`, and `follow_up_question` fields

### Reply Builder
- `backend/app/core/reply_builder.py` -- All 7 reply methods that produce user-facing text; primary file being modified

### Schema Loader
- `backend/app/core/schema_loader.py` -- Loads and parses features.yaml; must be updated to expose new fields

### Requirements
- `.planning/REQUIREMENTS.md` section "v1.1 Requirements" -- PLSH-01 through PLSH-07 acceptance criteria

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ReplyBuilder` class with 7 methods covering all message types (welcome, collecting, confirmation, confirmed, update, validation error, insufficient info)
- `FeatureSchema` / `SchemaLoader` already parses features.yaml and provides `get_feature_by_name()` accessor
- `FOLLOW_UP_PRIORITY` list and `FOLLOW_UP_QUESTIONS` dict already implement the priority follow-up pattern

### Established Patterns
- All user-facing text is built in `reply_builder.py` -- no text constructed in routes or services
- Feature metadata comes from `features.yaml` via `SchemaLoader` -- single source of truth pattern
- `ReplyBuilder` receives `FeatureSchema` at init and uses it to look up units and feature info

### Integration Points
- `ReplyBuilder` is instantiated in the FastAPI lifespan and injected into `ConversationService`
- `SchemaLoader` is used by `ReplyBuilder`, `ValidationService`, `ExtractionService`, and `PromptBuilder`
- Adding fields to YAML requires updating the feature dataclass in `schema_loader.py`

</code_context>

<specifics>
## Specific Ideas

- Extraction feedback must use vertical bullet list format (one variable per line) for clinical scannability -- user was explicit about this
- After prediction, replace generic follow-up with targeted next-best-variable prompt from priority list -- bridges naturally to Phase 7's feature importance work
- Imputation summary lists ALL imputed field names (no truncation) -- user preferred full visibility

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 06-reply-builder-polish*
*Context gathered: 2026-04-06*
