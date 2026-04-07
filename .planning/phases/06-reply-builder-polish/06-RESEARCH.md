# Phase 6: Reply Builder Polish - Research

**Researched:** 2026-04-06
**Domain:** Python string composition, YAML schema extension, clinical text formatting
**Confidence:** HIGH

## Summary

Phase 6 is a contained text-layer refactor with no new endpoints, no new UI components, and no model changes. Every user-facing string in the backend is built in a single file (`backend/app/core/reply_builder.py`), and all clinical field metadata comes from `backend/config/features.yaml` via `SchemaLoader`. The work is: (1) extend the YAML schema with three new fields per feature (`display_name`, `category`, `follow_up_question`), (2) update the `FeatureDefinition` dataclass and `SchemaLoader.load()` to parse those fields, and (3) rewrite the seven reply methods in `ReplyBuilder` to use them.

The codebase is already architected for this change. `FeatureSchema.get_feature_by_name()` gives every reply method direct access to feature metadata. `FOLLOW_UP_QUESTIONS` is a small hardcoded dict that maps directly to the new `follow_up_question` YAML field. `FOLLOW_UP_PRIORITY` is a three-element list that the decisions expand to six elements. No other file calls the affected methods — `ConversationService` is the only consumer of `ReplyBuilder`.

All seven reply methods have clear, well-scoped responsibilities and are short enough (5–30 lines each) to be rewritten individually without risk of cascading breakage.

**Primary recommendation:** Work in strict dependency order — YAML schema first, then `schema_loader.py`, then `reply_builder.py`. This order lets each subsequent step be validated against the previous one.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Display Names (PLSH-01)**
- D-01: Add a `display_name` field to each feature in `features.yaml` (e.g., `display_name: "Total Bilirubin"`). Single source of truth for human-readable field names in all user-facing chat messages.
- D-02: `ReplyBuilder` reads `display_name` instead of `name` for all user-facing text. No snake_case or internal identifiers in chat messages.

**Confirmation Summary (PLSH-02, PLSH-03)**
- D-03: Add a `category` field to each feature in `features.yaml` with values: `demographics`, `labs`, `imaging`, `clinical_conditions`. The confirmation summary groups provided values under these category headings.
- D-04: Only clinician-provided values appear in the grouped confirmation summary. Imputed fields are summarized in one line listing ALL imputed field display names (no truncation). Example: "The model will estimate ALT, Alkaline Phosphatase, Cholangitis, Pancreatitis, Cholecystitis, Charlson Comorbidity Index."

**Extraction Feedback (PLSH-04)**
- D-05: Extraction feedback uses concise clinical tone with a structured vertical list. Each extracted variable gets its own line with `display_name` and units. Format:
  ```
  Got it:

  - Sex: Male
  - Age: 50 years
  - Total Bilirubin: 3.2 mg/dL
  ```
- D-06: Prioritize readability and scannability over compact sentence formatting. No combining values into a single sentence.

**Follow-up Questions (PLSH-05)**
- D-07: Add a `follow_up_question` field to each feature in `features.yaml` with a natural-sounding, clinician-friendly question.
- D-08: Expand `FOLLOW_UP_PRIORITY` to include imaging fields: `[sex, age, total_bilirubin, abdominal_ultrasound_performed, cbd_stone_on_ultrasound, cbd_stone_on_ct]`. Only these priority fields get follow-up prompts; other missing fields are imputed silently.
- D-09: `ReplyBuilder` reads `follow_up_question` from YAML instead of using the hardcoded `FOLLOW_UP_QUESTIONS` dict.

**Prediction Result (PLSH-06)**
- D-10: Prediction message: "Based on the provided information, the estimated probability of a CBD stone is **X%** (Risk Tier). Recommended next step: **Intervention**."
- D-11: Replace the generic follow-up line with a targeted next-best-variable prompt using the priority list and the YAML `follow_up_question`. If no priority variables remain missing, omit this line.

**Validation Errors (PLSH-07)**
- D-12: Validation error messages show the clinician-provided value and explain the valid range in plain language using `display_name`. Example: "5000 is outside the valid range for Total Bilirubin (0-100 mg/dL). Could you double-check?"

### Claude's Discretion
- Exact wording of the imputation summary line (as long as it lists all imputed field display names)
- Exact wording of the prediction result message (as long as it follows the natural risk explanation pattern in D-10/D-11)
- Order of categories in confirmation summary (as long as all four are present)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PLSH-01 | All chat messages use human-readable field names (e.g., "Total Bilirubin" not "total_bilirubin") | Add `display_name` to YAML; update `FeatureDefinition`; update all 7 reply methods to use `feat.display_name` |
| PLSH-02 | Confirmation summary shows only clinician-provided values grouped by category | Add `category` to YAML; update `FeatureDefinition`; rewrite `build_confirmation_reply` to group by category and skip None values |
| PLSH-03 | Imputed fields summarized in one brief line listing all imputed display names | Rewrite `build_confirmation_reply` to collect imputed names and emit one summary sentence |
| PLSH-04 | Extraction feedback uses natural phrasing with vertical bullet list | Rewrite `build_collecting_reply` extraction block: "Got it:\n\n- Display Name: value unit" per line |
| PLSH-05 | Follow-up questions read conversationally from YAML | Add `follow_up_question` to YAML; expand `FOLLOW_UP_PRIORITY`; replace `FOLLOW_UP_QUESTIONS` dict lookup with `feat.follow_up_question` |
| PLSH-06 | Prediction result message reads naturally with clear risk explanation | Rewrite `build_confirmed_reply` and `build_update_reply` per D-10/D-11 pattern |
| PLSH-07 | Validation errors show provided value and explain valid range in plain language | Rewrite `build_validation_error_reply` to use `display_name` and show the offending value |
</phase_requirements>

---

## Standard Stack

### Core
No new packages are needed for this phase. All implementation uses Python standard library string formatting and the project's existing dependencies.

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyYAML | existing (via `yaml` import) | Parse extended features.yaml | Already used by SchemaLoader |
| pydantic | existing | `FeatureDefinition` dataclass replacement is actually a Python `dataclass` — no change needed | Already in stack |

**Installation:** None required.

---

## Architecture Patterns

### Current File Responsibilities

```
backend/
├── config/
│   └── features.yaml          # STEP 1: Add display_name, category, follow_up_question to each feature
├── app/core/
│   ├── schema_loader.py        # STEP 2: Add 3 fields to FeatureDefinition, parse them in SchemaLoader.load()
│   └── reply_builder.py        # STEP 3: Rewrite 7 reply methods; update FOLLOW_UP_PRIORITY; remove FOLLOW_UP_QUESTIONS dict
└── app/services/
    └── conversation.py         # Read-only: only consumer of ReplyBuilder — no changes needed
```

### Pattern 1: YAML Schema Extension

**What:** Add three new optional fields to every feature entry in `features.yaml`.

**When to use:** Any time feature metadata drives user-facing behavior — the YAML is the single source of truth.

**Example (one feature block after change):**
```yaml
- name: total_bilirubin
  model_column: "T. Bilirubin"
  display_name: "Total Bilirubin"          # NEW — D-01
  category: labs                            # NEW — D-03
  follow_up_question: "Do you have the patient's total bilirubin level (mg/dL)?"  # NEW — D-07
  type: numeric
  required: false
  strongly_recommended: true
  valid_range:
    min: 0
    max: 100
  unit: "mg/dL"
  description: "..."
```

**All 13 feature display_name / category / follow_up_question values must be authored in YAML (not generated at runtime). The planner should create a task that specifies all 13 values explicitly.**

### Pattern 2: FeatureDefinition Dataclass Extension

**What:** Add three new optional fields to the `FeatureDefinition` dataclass in `schema_loader.py`, with sensible defaults so existing YAML that lacks them doesn't crash.

**Example:**
```python
@dataclass
class FeatureDefinition:
    name: str
    model_column: str
    type: str
    required: bool
    description: str
    # --- existing optional fields ---
    encoding: dict[str, int] = field(default_factory=dict)
    valid_range: Optional[dict] = None
    allowed_values: Optional[list] = None
    unit: Optional[str] = None
    strongly_recommended: bool = False
    triggers_fast_path: bool = False
    inference_prohibited: bool = False
    # --- new fields (Phase 6) ---
    display_name: Optional[str] = None       # falls back to name if missing
    category: Optional[str] = None           # demographics|labs|imaging|clinical_conditions
    follow_up_question: Optional[str] = None # natural-language follow-up prompt
```

`SchemaLoader.load()` reads them with `.get()` so missing keys default to None rather than raising a KeyError. [VERIFIED: existing pattern — all optional fields in `SchemaLoader.load()` already use `feat_data.get(key)`]

### Pattern 3: ReplyBuilder Method Rewrites

**What:** Each of the seven methods is self-contained. Rewrite each individually following the locked decision for that method.

**`build_collecting_reply` (PLSH-04, PLSH-05):**
```python
# Extraction block — D-05/D-06
if new_features:
    lines = ["Got it:\n"]
    for name, value in new_features.items():
        feat = self.schema.get_feature_by_name(name)
        display = feat.display_name or name
        unit = f" {feat.unit}" if feat and feat.unit else ""
        lines.append(f"- {display}: {value}{unit}")
    parts.append("\n".join(lines))

# Follow-up block — D-07/D-08/D-09
missing_priority = [
    name for name in FOLLOW_UP_PRIORITY
    if name not in session_features or session_features[name] is None
]
if missing_priority:
    next_field = missing_priority[0]
    feat = self.schema.get_feature_by_name(next_field)
    question = feat.follow_up_question if feat and feat.follow_up_question else f"Do you have the patient's {next_field}?"
    parts.append(question)
    return "\n\n".join(parts), False
```

**`build_confirmation_reply` (PLSH-02, PLSH-03):**
```python
CATEGORY_LABELS = {
    "demographics": "Demographics",
    "labs": "Labs",
    "imaging": "Imaging",
    "clinical_conditions": "Clinical Conditions",
}
# Group provided features by category; collect imputed display names
provided = {}   # category -> list of "Display Name: value unit"
imputed = []    # display names of None features

for feat in self.schema.features:
    value = session_features.get(feat.name)
    display = feat.display_name or feat.name
    category = feat.category or "other"
    if value is not None:
        unit = f" {feat.unit}" if feat.unit else ""
        provided.setdefault(category, []).append(f"- **{display}:** {value}{unit}")
    else:
        imputed.append(display)

# Render grouped summary
parts = ["Here is what I've recorded. Please confirm this is correct:\n"]
for cat_key, label in CATEGORY_LABELS.items():
    items = provided.get(cat_key, [])
    if items:
        parts.append(f"**{label}**")
        parts.extend(items)

# Imputation line — D-04
if imputed:
    parts.append(f"\nThe model will estimate: {', '.join(imputed)}.")

parts.append("\nType **confirm** to run the prediction, or provide corrections.")
```

**`build_confirmed_reply` (PLSH-06) — D-10/D-11:**
```python
def build_confirmed_reply(self, prediction: PredictionResult, session_features: dict) -> str:
    parts = [
        f"Based on the provided information, the estimated probability of a CBD stone is "
        f"**{prediction.probability}%** ({prediction.risk_tier.capitalize()} risk). "
        f"Recommended next step: **{prediction.recommended_intervention}**."
    ]
    # D-11: next-best-variable prompt
    missing_priority = [
        name for name in FOLLOW_UP_PRIORITY
        if name not in session_features or session_features[name] is None
    ]
    if missing_priority:
        feat = self.schema.get_feature_by_name(missing_priority[0])
        question = feat.follow_up_question if feat and feat.follow_up_question else None
        if question:
            parts.append(f"To refine this prediction further, {question[0].lower()}{question[1:]}")
    return "\n\n".join(parts)
```

Note: `build_confirmed_reply` currently does not receive `session_features`. The signature must be extended, or the caller in `ConversationService._handle_confirmation` must pass it. This is a minor interface change. [VERIFIED: current signature is `build_confirmed_reply(self, prediction: PredictionResult)` — needs extension]

**`build_validation_error_reply` (PLSH-07) — D-12:**

The current `ValidationService` already constructs readable messages and stores them in `ValidationErrorDetail.message`. However, those messages use `feature_def.name` (the snake_case internal name) rather than `display_name`, and they do not prefix the provided value.

Two options:
1. Fix the message construction in `ValidationService.validate()` — requires adding `display_name` awareness there.
2. Fix it in `ReplyBuilder.build_validation_error_reply()` — re-lookup the feature and reformat the message.

**Option 1 is cleaner** (single source of readable messages) but technically outside the strict boundary of "reply_builder.py only". Option 2 keeps all text changes in `ReplyBuilder` but requires re-parsing the error to extract the offending value.

Given that D-12 specifies: "Validation errors show the clinician-provided value and explain the valid range in plain language using `display_name`", and `ValidationErrorDetail` currently carries `field` (the snake_case name) and `message` (uses internal name), the cleanest path is: update `ValidationService.validate()` to use `display_name` when constructing the message, and also store the original value in `ValidationErrorDetail`.

`ValidationErrorDetail` currently has fields: `error`, `field`, `message`. It needs a `provided_value` field (or the message must be reformatted). [VERIFIED: current schema in `backend/app/schemas/prediction.py`]

**Recommended approach:** Add `provided_value: Optional[Any]` to `ValidationErrorDetail`, populate it in `ValidationService`, and update `build_validation_error_reply` to format: `"{provided_value} is outside the valid range for {display_name} ({min}–{max} {unit}). Could you double-check?"`

### Anti-Patterns to Avoid

- **Hardcoding display names in reply_builder.py:** All display names must come from YAML, not from a second dict in Python code. Any second dict becomes a maintenance hazard.
- **Partial migration:** If `build_collecting_reply` uses `display_name` but `build_confirmation_reply` still uses `feat.name`, the user will see inconsistent labels.
- **Passing `None` as display_name:** Each reply method should guard with `feat.display_name or feat.name` so a missing YAML entry degrades gracefully rather than showing `None`.
- **Changing `ValidationErrorDetail` without updating `ValidationService`:** The two must be updated together in the same task or the app will throw Pydantic validation errors on startup.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Category ordering | Custom sort logic | Hardcode category order in a constant (`CATEGORY_ORDER = ["demographics", "labs", "imaging", "clinical_conditions"]`) and iterate over it |
| Display name lookup | Second dict in reply_builder.py | `feat.display_name or feat.name` via existing `get_feature_by_name()` |
| Follow-up question text | New dict in reply_builder.py | `feat.follow_up_question` from YAML via existing accessor |

**Key insight:** The schema accessor `get_feature_by_name()` already does the lookup. Every reply method already calls it for units. The pattern already exists — just extend it.

---

## Common Pitfalls

### Pitfall 1: build_confirmed_reply Missing session_features

**What goes wrong:** `build_confirmed_reply` needs `session_features` to implement D-11 (next-best-variable prompt), but the current signature is `build_confirmed_reply(self, prediction: PredictionResult)`. Calling it from `ConversationService._handle_confirmation` requires passing the session's extracted features.

**Why it happens:** The original method only needed the prediction result. D-11 adds a dependency on what's still missing.

**How to avoid:** Update the signature to `build_confirmed_reply(self, prediction: PredictionResult, session_features: dict) -> str` and update the two call sites in `ConversationService` (`_handle_confirmation` and `_handle_post_confirmation`). `build_update_reply` has the same issue if D-11 applies post-confirmation too — confirm whether it should.

**Warning signs:** If the planner creates a task for `reply_builder.py` only without a matching task to update `conversation.py` call sites, the app will fail with a TypeError at runtime.

### Pitfall 2: ValidationErrorDetail Missing provided_value

**What goes wrong:** D-12 requires showing the clinician-provided value in the error message ("5000 is outside the valid range for..."). `ValidationErrorDetail` currently has no `provided_value` field. If the planner adds this field to the schema without updating `ValidationService` to populate it, the field will always be None.

**Why it happens:** Schema and service are separate files updated in separate tasks.

**How to avoid:** Treat `ValidationErrorDetail` schema change and `ValidationService` update as a single atomic task or ensure strict ordering (schema change → service update → reply builder update).

### Pitfall 3: FOLLOW_UP_PRIORITY Expansion Breaking Confirmation Flow

**What goes wrong:** `FOLLOW_UP_PRIORITY` drives both the follow-up prompt selection AND the "ready for confirmation" gate in `build_collecting_reply`. Expanding it from 3 to 6 fields means the confirmation gate now requires all 6 fields — but only `sex`, `age`, `total_bilirubin` are `required: true` in the schema. The imaging fields are optional.

**Why it happens:** D-08 expands the priority list, but the `if missing_priority` branch in `build_collecting_reply` currently gates confirmation on that list.

**How to avoid:** The priority list controls WHICH follow-up question to ask, NOT whether to offer confirmation. `ready_for_confirmation` should still gate only on the schema's `required` fields (sex, age, and whatever else is `required: true`). Review the existing gate logic carefully when rewriting `build_collecting_reply`.

**Current gate logic (line 49-57 of reply_builder.py):**
```python
missing_priority = [
    name for name in FOLLOW_UP_PRIORITY
    if name not in session_features or session_features[name] is None
]
if missing_priority:
    # ask follow-up, return ready=False
else:
    return ..., True   # ready for confirmation
```
After expansion to 6 fields, this would require all 6 before offering confirmation — which contradicts the current schema where only 3 are required. The fix: separate the "ask follow-up" list (all 6) from the "gate confirmation" check (schema-required only).

### Pitfall 4: Imputed Fields Appearing in Grouped Provided Summary

**What goes wrong:** If a feature has `value = "NO"` (a valid boolean), it is provided — not imputed. But `None` check must distinguish `None` (not provided) from `"NO"` / `0` / `False` (explicitly provided as negative). The current `session_features.get(feat.name)` will return `None` for missing keys and `"NO"` for boolean negatives — so the `if value is not None` check is correct. Do not change this to `if value` (truthy check), which would wrongly treat `"NO"` and `0` as imputed.

**Warning signs:** If the summary shows "The model will estimate: Cholangitis" even though the clinician said "no cholangitis" — this pitfall has occurred.

### Pitfall 5: Missing display_name for a Feature Silently Shows None

**What goes wrong:** If any feature in YAML is missing `display_name` and the fallback guard `feat.display_name or feat.name` is omitted, the message will show `None` as the field label.

**How to avoid:** Every reply method that accesses `feat.display_name` must use `feat.display_name or feat.name`.

---

## Code Examples

### Verified Existing Patterns Used as Base

All examples are from the codebase as read in this session. [VERIFIED: codebase read]

**Feature lookup pattern (currently used for units, same pattern for display_name):**
```python
feat = self.schema.get_feature_by_name(name)
unit = f" {feat.unit}" if feat and feat.unit else ""
```

**SchemaLoader optional field parsing (existing pattern for all optional YAML keys):**
```python
strongly_recommended=feat_data.get("strongly_recommended", False),
triggers_fast_path=feat_data.get("triggers_fast_path", False),
inference_prohibited=feat_data.get("inference_prohibited", False),
# New fields follow the same pattern:
display_name=feat_data.get("display_name"),
category=feat_data.get("category"),
follow_up_question=feat_data.get("follow_up_question"),
```

**Current confirmation reply (to be replaced):**
```python
for feat in self.schema.features:
    value = session_features.get(feat.name)
    if value is not None:
        unit = f" {feat.unit}" if feat.unit else ""
        parts.append(f"- **{feat.name}**: {value}{unit}")
    else:
        parts.append(f"- **{feat.name}**: _(will be estimated by the model)_")
```

---

## Feature Display Name and Category Reference

[VERIFIED: read directly from features.yaml and decisions in CONTEXT.md]

All 13 features with the values that MUST be authored in YAML during this phase:

| Internal Name | display_name | category | follow_up_question (example) |
|---------------|-------------|----------|------------------------------|
| sex | Sex | demographics | "What is the patient's biological sex (male or female)?" |
| age | Age | demographics | "How old is the patient?" |
| clinical_cholangitis | Cholangitis | clinical_conditions | "Does the patient have signs of cholangitis?" |
| clinical_pancreatitis | Pancreatitis | clinical_conditions | "Is there clinical or lab evidence of pancreatitis?" |
| clinical_cholecystitis | Cholecystitis | clinical_conditions | "Does the patient have clinical cholecystitis?" |
| ast | AST | labs | "What is the patient's AST level (U/L)?" |
| alt | ALT | labs | "What is the patient's ALT level (U/L)?" |
| alkaline_phosphatase | Alkaline Phosphatase | labs | "Do you have the patient's alkaline phosphatase level (U/L)?" |
| total_bilirubin | Total Bilirubin | labs | "Do you have the patient's total bilirubin level (mg/dL)?" |
| abdominal_ultrasound_performed | Abdominal Ultrasound | imaging | "Was an abdominal ultrasound performed?" |
| cbd_stone_on_ultrasound | CBD Stone on Ultrasound | imaging | "Was a CBD stone seen on the abdominal ultrasound?" |
| cbd_stone_on_ct | CBD Stone on CT | imaging | "Was a CBD stone seen on CT scan?" |
| charlson_comorbidity_index | Charlson Comorbidity Index | clinical_conditions | "Do you have the patient's Charlson Comorbidity Index score?" |

The exact wording of `follow_up_question` is Claude's discretion (CONTEXT.md). The values in the table above are suggestions — the planner should specify them as concrete values in the YAML task.

---

## Interface Changes Required

[VERIFIED: codebase read]

Two call sites in `ConversationService` must be updated when `build_confirmed_reply` and potentially `build_update_reply` signatures change:

| Method | File | Line | Change |
|--------|------|------|--------|
| `build_confirmed_reply` | `conversation.py` | ~127 | Add `session.extracted_features` argument |
| `build_update_reply` | `conversation.py` | ~145 | Add `session.extracted_features` argument (if D-11 applies post-confirmation too) |

Additionally:
- `ValidationErrorDetail` in `prediction.py` needs `provided_value: Optional[Any] = None`
- `ValidationService.validate()` must populate `provided_value` when constructing numeric range errors

---

## Environment Availability

Step 2.6: SKIPPED — Phase 6 is a pure Python code and YAML configuration change. No external services, CLIs, or runtimes beyond what the existing backend already requires.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `build_update_reply` should also implement the D-11 next-best-variable prompt (same as confirmed reply) | Architecture Patterns | If wrong, planner can omit D-11 from `build_update_reply` — low impact |
| A2 | The confirmation gate (ready=True) should remain gated on schema-required fields only, not the full expanded FOLLOW_UP_PRIORITY list | Pitfall 3 | If wrong and the intent is to require all 6 priority fields before confirmation, the logic simplifies but clinician experience degrades |

---

## Open Questions

1. **Does D-11 apply to `build_update_reply` (post-confirmation iterations)?**
   - What we know: D-11 explicitly covers `build_confirmed_reply` (the initial prediction message)
   - What's unclear: Whether post-confirmation update replies should also prompt for the next missing priority field
   - Recommendation: Apply it — behavioral consistency is better than a different pattern for updates

2. **Does `ValidationErrorDetail` need a `provided_value` field, or should the message be reformatted in `build_validation_error_reply`?**
   - What we know: The current `message` field in `ValidationErrorDetail` uses the internal name and does not include the provided value
   - What's unclear: Whether to fix at the source (`ValidationService`) or at display time (`ReplyBuilder`)
   - Recommendation: Fix at the source — add `provided_value` to `ValidationErrorDetail` and populate it in `ValidationService.validate()`. This keeps messages accurate regardless of which consumer uses the error object.

---

## Sources

### Primary (HIGH confidence)
- `backend/app/core/reply_builder.py` — all 7 reply methods, exact current signatures
- `backend/config/features.yaml` — all 13 feature definitions, exact field names and values
- `backend/app/core/schema_loader.py` — `FeatureDefinition` dataclass, `SchemaLoader.load()` parsing pattern
- `backend/app/schemas/prediction.py` — `ValidationErrorDetail`, `PredictionResult` fields
- `backend/app/schemas/extraction.py` — `ExtractionResult`, `to_feature_dict()` logic
- `backend/app/services/conversation.py` — call sites for all reply methods
- `backend/app/services/validation.py` — message construction using `feature_def.name` (not display_name)
- `.planning/phases/06-reply-builder-polish/06-CONTEXT.md` — locked decisions D-01 through D-12

### Secondary (MEDIUM confidence)
None — all claims are VERIFIED from codebase read.

### Tertiary (LOW confidence)
None.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages, all existing
- Architecture: HIGH — codebase fully read, all 7 methods and all call sites examined
- Pitfalls: HIGH — identified from direct code inspection, not speculation

**Research date:** 2026-04-06
**Valid until:** 2026-05-06 (stable codebase — valid until Phase 6 implementation changes the files)
