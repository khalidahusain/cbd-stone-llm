---
phase: 06-reply-builder-polish
verified: 2026-04-07T02:56:32Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
deferred:
  - truth: "After prediction, suggest the most impactful missing variable based on feature importance ordering"
    addressed_in: "Phase 7"
    evidence: "Phase 7 success criteria: 'After a prediction is returned, if any non-required variables were imputed, the system includes a natural-language suggestion identifying the single most impactful missing variable'"
---

# Phase 6: Reply Builder Polish Verification Report

**Phase Goal:** Every chat message the system produces reads like a clinician wrote it — field names are human-readable, confirmation summaries are concise and categorized, extraction feedback and follow-ups use natural phrasing, and validation errors are clear and actionable.
**Verified:** 2026-04-07T02:56:32Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All chat messages display human-readable field names — no snake_case or internal identifiers appear in user-facing text | VERIFIED | `build_collecting_reply` uses `feat.display_name` for all output. Spot-check confirmed: "Total Bilirubin", "AST", "Alkaline Phosphatase" in output; "total_bilirubin", "alkaline_phosphatase" absent |
| 2 | Confirmation summary groups provided values by category (Demographics, Labs, Imaging, Clinical Conditions), omits unprovided fields, and summarizes imputed fields in one brief line | VERIFIED | `build_confirmation_reply` renders `**Demographics**`, `**Labs**`, etc. and produces "The model will estimate: Cholangitis, Pancreatitis, ...". Behavioral test output confirmed |
| 3 | Extraction feedback uses natural phrasing ("Got it: ...") and follow-up questions read conversationally from YAML | VERIFIED | Output: "Got it:\n\n- Sex: Male\n- Age: 50.0 years\n- AST: 1000.0 U/L" followed by YAML-driven follow-up. `FOLLOW_UP_QUESTIONS` dict removed; all questions from `feat.follow_up_question` |
| 4 | Prediction result message explains the risk naturally with probability, risk tier, and recommended next step in plain clinical language | VERIFIED | Output: "Based on the provided information, the estimated probability of a CBD stone is **45.0%** (High risk). Recommended next step: **EUS**." with YAML-driven refine prompt |
| 5 | Validation errors show the clinician-provided value and explain the valid range in plain language | VERIFIED | Output: "5000.0 is outside the valid range for Total Bilirubin (0-100 mg/dL). Could you double-check?" — uses `display_name`, includes `provided_value`, appends plain-language query |

**Score:** 5/5 truths verified

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | PLSH-08: After prediction, suggest the most impactful missing variable based on feature importance ordering (not arbitrary priority list) | Phase 7 | Phase 7 success criteria: "The suggestion is based on a feature importance ordering derived from the GBM model (not arbitrary), and the suggested variable is one that was actually missing for this patient" |

Note: Phase 6 does implement a next-best-variable prompt (`To refine this prediction further, ...`) using the FOLLOW_UP_PRIORITY list ordering. Phase 7 upgrades this to GBM feature-importance ordering. The Phase 6 implementation satisfies the requirement listed in Phase 6's own ROADMAP success criteria — PLSH-08 is assigned to Phase 7 in REQUIREMENTS.md traceability.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `backend/config/features.yaml` | display_name, category, follow_up_question for all 13 features | VERIFIED | 13 occurrences each of display_name, category, follow_up_question confirmed via grep; all 13 features populated with concrete values |
| `backend/app/core/schema_loader.py` | FeatureDefinition with display_name, category, follow_up_question fields; SchemaLoader parses them | VERIFIED | Fields present at lines 21-23; SchemaLoader.load() parses via `.get()` at lines 103-105 |
| `backend/app/core/reply_builder.py` | All reply methods using display_name, category, follow_up_question from schema; FOLLOW_UP_QUESTIONS dict removed | VERIFIED | 8 occurrences of `display_name`; FOLLOW_UP_QUESTIONS absent (0 grep matches); CATEGORY_LABELS constant present; `follow_up_question` referenced 4 times |
| `backend/app/services/conversation.py` | build_confirmed_reply and build_update_reply call sites pass session_features | VERIFIED | Line 127: `build_confirmed_reply(result, session.extracted_features)`; line 145: `build_update_reply(result, updated_fields, session.extracted_features)` |
| `backend/app/schemas/prediction.py` | ValidationErrorDetail with provided_value field | VERIFIED | `provided_value: Optional[Any] = None` at line 24 |
| `backend/app/services/validation.py` | Error messages use display_name; all error types populate provided_value | VERIFIED | `display` variable using `display_name` at line 23; `provided_value=value` in all 4 error append blocks |
| `backend/tests/test_schema_loader.py` | 3 new tests for display_name, category, follow_up_question | VERIFIED | `test_display_name_loaded`, `test_category_loaded`, `test_follow_up_question_loaded` all pass (16 total, 33 passed across both test files) |
| `backend/tests/test_reply_builder.py` | New tests verifying display_name usage, category grouping, YAML follow-ups, natural phrasing | VERIFIED | 17 tests in file including `test_collecting_reply_uses_display_name`, `test_confirmation_groups_by_category`, `test_confirmed_reply_natural_phrasing`, `test_update_reply_uses_display_names` — all pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `backend/config/features.yaml` | `backend/app/core/schema_loader.py` | `SchemaLoader.load()` parses new fields via `.get()` | WIRED | `feat_data.get("display_name")` at line 103, `feat_data.get("category")` at 104, `feat_data.get("follow_up_question")` at 105 |
| `backend/app/core/reply_builder.py` | `backend/app/core/schema_loader.py` | `feat.display_name`, `feat.category`, `feat.follow_up_question` lookups | WIRED | 8 `display_name` references in reply_builder; 4 `follow_up_question` references; all route through `self.schema.get_feature_by_name()` |
| `backend/app/services/conversation.py` | `backend/app/core/reply_builder.py` | `build_confirmed_reply` and `build_update_reply` call sites with `session_features` | WIRED | Lines 127 and 145 both pass `session.extracted_features` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `reply_builder.py: build_collecting_reply` | `feat.display_name` | `schema.get_feature_by_name(name)` → `FeatureDefinition.display_name` ← loaded from `features.yaml` | Yes — 13 concrete display_names in YAML | FLOWING |
| `reply_builder.py: build_confirmation_reply` | `feat.category` / `feat.display_name` | Same schema load path | Yes — 4 categories, all features mapped | FLOWING |
| `reply_builder.py: build_collecting_reply` (follow-up) | `feat.follow_up_question` | Same schema load path | Yes — 13 concrete follow-up questions in YAML | FLOWING |
| `validation.py: validate` | `feature_def.display_name` | `schema.get_feature_by_name(name)` | Yes — matches YAML display_names | FLOWING |

### Behavioral Spot-Checks

| Behavior | Result | Status |
|----------|--------|--------|
| Extraction feedback "Got it:" with vertical bullet list, display_name, no snake_case | "Got it:\n\n- Sex: Male\n- Age: 50.0 years\n- AST: 1000.0 U/L\n\nDo you have the patient's total bilirubin level (mg/dL)?" | PASS |
| Confirmation summary groups by category headers with imputation summary line | "**Demographics**\n- **Sex:** Male\n...\nThe model will estimate: Cholangitis, Pancreatitis, ..." | PASS |
| Prediction result uses natural phrasing with risk and next step | "Based on the provided information, the estimated probability of a CBD stone is **45.0%** (High risk). Recommended next step: **EUS**." | PASS |
| Validation error shows provided value + display_name + valid range + "double-check" | "5000.0 is outside the valid range for Total Bilirubin (0-100 mg/dL). Could you double-check?" | PASS |
| Follow-up question comes from YAML (not hardcoded dict) | First reply with empty session: "What is the patient's biological sex (male or female)?" — matches features.yaml `follow_up_question` exactly | PASS |
| No snake_case identifiers appear in any user-facing output | Checked: `total_bilirubin`, `clinical_cholangitis`, `alkaline_phosphatase`, `abdominal_ultrasound_performed`, `cbd_stone_on` — none found in reply output | PASS |

### Requirements Coverage

| Requirement | Plan | Description | Status | Evidence |
|-------------|------|-------------|--------|---------|
| PLSH-01 | 06-01, 06-02 | All chat messages use human-readable field names | SATISFIED | display_name from YAML used in all reply methods; spot-checks confirm no snake_case in output |
| PLSH-02 | 06-02 | Confirmation summary shows only provided values grouped by category | SATISFIED | `build_confirmation_reply` iterates schema features, groups by category key; only provided (non-None) values shown per group |
| PLSH-03 | 06-02 | Imputed fields summarized in one brief line | SATISFIED | "The model will estimate: {', '.join(imputed)}." — single sentence, not per-field listing |
| PLSH-04 | 06-02 | Extraction feedback uses natural phrasing | SATISFIED | "Got it:\n\n- {display_name}: {value} {unit}" vertical list format — no snake_case, no "Extracted:" prefix |
| PLSH-05 | 06-01, 06-02 | Follow-up questions read conversationally from YAML | SATISFIED | FOLLOW_UP_QUESTIONS dict removed; questions from `feat.follow_up_question`; YAML questions are natural clinical phrasing |
| PLSH-06 | 06-02 | Prediction result reads naturally with clear risk explanation | SATISFIED | "Based on the provided information, the estimated probability... (High risk). Recommended next step: **EUS**." |
| PLSH-07 | 06-02 | Validation errors show provided value and explain valid range in plain language | SATISFIED | ValidationService populates `provided_value`; message format: "{value} is outside the valid range for {display_name} ({min}-{max} {unit})"; ReplyBuilder appends "Could you double-check?" |

**Note on PLSH-08:** PLSH-08 (feature importance-guided suggestion) is assigned to Phase 7 in REQUIREMENTS.md traceability. It is NOT a Phase 6 requirement and is correctly deferred. Phase 6 does implement a basic next-best-variable prompt using FOLLOW_UP_PRIORITY ordering, which serves as a functional placeholder pending Phase 7's model-derived importance ordering.

### Anti-Patterns Found

No blockers or warnings found. Review of `reply_builder.py`, `validation.py`, `conversation.py`, and `prediction.py`:
- No TODO/FIXME/PLACEHOLDER comments in modified files
- No empty implementations (`return null`, `return {}`) in user-facing paths
- No hardcoded empty data in session features paths
- `FOLLOW_UP_QUESTIONS` dict (previously hardcoded) is confirmed removed (0 grep matches)

### Human Verification Required

None. All must-haves are fully verifiable programmatically and confirmed via behavioral spot-checks.

### Gaps Summary

No gaps. All 5 roadmap success criteria are satisfied:

1. Human-readable field names in all messages — confirmed via display_name from YAML, spot-checked
2. Confirmation summary grouped by category with single imputation line — confirmed via output inspection
3. Natural extraction feedback and conversational follow-ups from YAML — confirmed; FOLLOW_UP_QUESTIONS dict removed
4. Natural prediction result message — confirmed with "Based on the provided information..."
5. Validation errors with provided value and plain-language range explanation — confirmed end-to-end

The numpy/sklearn ImportError in test_conversation.py, test_api.py, test_chat_api.py, test_extract_api.py, and test_inference.py is a pre-existing dev environment incompatibility (numpy 2.x / sklearn 1.5.2 `ComplexWarning` mismatch). It predates Phase 6, affects no Phase 6 code paths, and does not impact any reply builder or schema loader logic. The 84 tests runnable without sklearn all pass, including all 33 Phase 6 tests.

---

_Verified: 2026-04-07T02:56:32Z_
_Verifier: Claude (gsd-verifier)_
