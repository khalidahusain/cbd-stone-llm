---
phase: 06-reply-builder-polish
plan: "02"
subsystem: backend/core
tags: [reply-builder, conversation, validation, display-name, clinician-friendly]
dependency_graph:
  requires: ["06-01"]
  provides: ["PLSH-02", "PLSH-03", "PLSH-04", "PLSH-05", "PLSH-06", "PLSH-07"]
  affects: ["backend/app/core/reply_builder.py", "backend/app/services/conversation.py", "backend/app/schemas/prediction.py", "backend/app/services/validation.py"]
tech_stack:
  added: []
  patterns: ["category grouping for confirmation reply", "YAML-driven follow-up questions", "next-best-variable prompt after prediction"]
key_files:
  created: []
  modified:
    - backend/app/core/reply_builder.py
    - backend/app/services/conversation.py
    - backend/app/schemas/prediction.py
    - backend/app/services/validation.py
    - backend/tests/test_reply_builder.py
    - backend/tests/test_conversation.py
decisions:
  - "FOLLOW_UP_PRIORITY expanded to 6 fields (adds imaging fields) to drive both collecting follow-ups and post-prediction refinement prompts"
  - "Confirmation gate uses schema-required fields (sex, age) not the FOLLOW_UP_PRIORITY list — prevents premature confirmation if imaging fields missing"
  - "build_validation_error_reply delegates formatting to ValidationService messages; simply appends 'Could you double-check?' rather than duplicating range info"
metrics:
  duration: "15 minutes"
  completed: "2026-04-07"
  tasks_completed: 2
  files_modified: 6
---

# Phase 6 Plan 2: ReplyBuilder Polish — Natural Language Replies Summary

All 7 ReplyBuilder methods rewritten to produce clinician-friendly messages using display_name from YAML, category grouping, YAML-driven follow-up questions, and natural prediction phrasing. Validation errors now include provided_value and use display_name. Call sites in ConversationService updated to pass session_features.

## What Was Built

**Task 1 — Collecting, confirmation, and follow-up reply methods:**

- Expanded `FOLLOW_UP_PRIORITY` from 3 to 6 fields (added `abdominal_ultrasound_performed`, `cbd_stone_on_ultrasound`, `cbd_stone_on_ct`)
- Removed `FOLLOW_UP_QUESTIONS` hardcoded dict; all follow-up questions now read from `feat.follow_up_question` in YAML
- `build_collecting_reply`: vertical bullet list format with `display_name` and units (e.g., "- Total Bilirubin: 3.2 mg/dL")
- `build_confirmation_reply`: groups provided values by category (Demographics, Labs, Imaging, Clinical Conditions) with `**Bold** headers`; imputed fields summarized in one sentence
- Confirmation gate uses schema-required fields (sex, age), not FOLLOW_UP_PRIORITY — prevents Pitfall 3
- Added `CATEGORY_LABELS` module-level constant
- `build_insufficient_info_reply`: uses `display_name` instead of snake_case
- Updated tests: `test_collecting_ready_when_all_priority_present` updated for expanded priority; 5 new tests added

**Task 2 — Prediction/validation replies and call sites:**

- `build_confirmed_reply(prediction, session_features)`: natural phrasing "Based on the provided information, the estimated probability..." with next-best-variable prompt
- `build_update_reply(prediction, updated_fields, session_features)`: uses `display_name` for updated field names, same natural phrasing
- `build_validation_error_reply`: simplified to `f"{err.message}. Could you double-check?"`
- `ValidationErrorDetail`: added `provided_value: Optional[Any] = None` field
- `ValidationService`: all error messages use `display_name`; all error types populate `provided_value`
- `conversation.py`: `build_confirmed_reply` and `build_update_reply` call sites now pass `session.extracted_features`
- `test_conversation.py`: all tests updated to provide all 6 priority fields to reach `awaiting_confirmation`; `test_post_confirmation_auto_predicts` now asserts "AST" display name in message
- 5 new test functions added to `test_reply_builder.py`

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | 6d8d40c | feat(06-02): rewrite collecting, confirmation, and follow-up reply methods |
| Task 2 | a2121de | feat(06-02): add provided_value to errors, display_name in validation, update call sites |

## Verification Results

- `grep 'FOLLOW_UP_QUESTIONS' backend/app/core/reply_builder.py` -- no matches (removed)
- `grep 'abdominal_ultrasound_performed' backend/app/core/reply_builder.py` -- match found
- `grep 'Got it:' backend/app/core/reply_builder.py` -- match found
- `grep 'CATEGORY_LABELS' backend/app/core/reply_builder.py` -- match found
- `grep -c 'display_name' backend/app/core/reply_builder.py` -- 8 matches
- `grep 'will estimate' backend/app/core/reply_builder.py` -- match found
- `grep 'Based on the provided information' backend/app/core/reply_builder.py` -- match found
- `grep 'To refine this prediction' backend/app/core/reply_builder.py` -- match found
- `grep 'provided_value' backend/app/schemas/prediction.py` -- match found
- `grep -c 'display_name' backend/app/services/validation.py` -- 1 match
- `grep 'session.extracted_features' backend/app/services/conversation.py` -- appears in both call sites
- All 17 test_reply_builder.py tests pass
- All 84 non-sklearn-dependent tests pass (test_architectural, test_extraction, test_schema_loader, test_session_store, test_prompt_builder, test_safeguard, test_reply_builder)

## Deviations from Plan

### Auto-fixed Issues

None -- plan executed exactly as written.

### Known Pre-existing Issue (out of scope)

`test_conversation.py`, `test_api.py`, `test_chat_api.py`, `test_extract_api.py`, and `test_inference.py` all fail with `ImportError: cannot import name 'ComplexWarning' from 'numpy.core.numeric'`. This is a numpy/sklearn version incompatibility in the local dev environment (numpy 2.x removed `ComplexWarning` from `numpy.core.numeric` but the installed sklearn version still references it). This was pre-existing before this plan and is not caused by our changes.

## Known Stubs

None -- all reply methods are fully wired to schema data.

## Threat Flags

None -- changes are confined to message formatting in reply_builder.py and error message text in validation.py. No new network endpoints, auth paths, or schema changes at trust boundaries.

## Self-Check: PASSED

- backend/app/core/reply_builder.py -- modified, content verified
- backend/app/services/conversation.py -- modified, call sites updated
- backend/app/schemas/prediction.py -- modified, provided_value field added
- backend/app/services/validation.py -- modified, display_name used
- backend/tests/test_reply_builder.py -- modified, 17 tests pass
- backend/tests/test_conversation.py -- modified, logic correct (pre-existing env issue prevents runtime)
- Commit 6d8d40c -- verified via git log
- Commit a2121de -- verified via git log
