---
phase: 06-reply-builder-polish
plan: 01
subsystem: backend/schema
tags: [schema, yaml, features, display-names, metadata]
requirements: [PLSH-01, PLSH-05]

dependency_graph:
  requires: []
  provides:
    - display_name field on all 13 FeatureDefinition instances
    - category field on all 13 FeatureDefinition instances
    - follow_up_question field on all 13 FeatureDefinition instances
  affects:
    - backend/config/features.yaml
    - backend/app/core/schema_loader.py

tech_stack:
  added: []
  patterns:
    - YAML optional field with .get() parsing pattern
    - Optional[str] = None dataclass field pattern

key_files:
  created: []
  modified:
    - backend/config/features.yaml
    - backend/app/core/schema_loader.py
    - backend/tests/test_schema_loader.py

decisions:
  - "D-01: display_name added to features.yaml as single source of truth for human-readable labels"
  - "D-03: category field added (demographics/labs/imaging/clinical_conditions) for confirmation grouping"
  - "D-07: follow_up_question added as natural, conversational prompts per feature"

metrics:
  duration: "2 minutes"
  completed: "2026-04-07"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 3
---

# Phase 06 Plan 01: Feature Schema Metadata Extension Summary

**One-liner:** Added display_name, category, and follow_up_question to all 13 features in features.yaml plus FeatureDefinition dataclass fields and SchemaLoader parsing.

## What Was Built

Extended the feature schema to be the single source of truth for all user-facing field names, category groupings, and follow-up question text. This enables Plan 02 (ReplyBuilder Polish) to consume human-readable labels from YAML instead of hardcoded strings.

### Task 1: features.yaml metadata fields
Added three new fields immediately after `model_column` for all 13 features:
- `display_name`: human-readable label (e.g., "Total Bilirubin", "Alkaline Phosphatase")
- `category`: logical grouping — `demographics` (2), `labs` (4), `imaging` (3), `clinical_conditions` (4)
- `follow_up_question`: natural, clinician-friendly question text for each feature

### Task 2: FeatureDefinition dataclass + SchemaLoader + tests
- Added `display_name: Optional[str] = None`, `category: Optional[str] = None`, `follow_up_question: Optional[str] = None` to `FeatureDefinition`
- Updated `SchemaLoader.load()` to parse the three new fields via `.get()` pattern (consistent with existing optional field handling)
- Added 3 new tests to `test_schema_loader.py`: `test_display_name_loaded`, `test_category_loaded`, `test_follow_up_question_loaded`
- All 16 tests pass (13 existing + 3 new)

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | c3404ba | feat(06-01): add display_name, category, follow_up_question to all 13 features |
| Task 2 | 7df9dca | feat(06-01): extend FeatureDefinition and SchemaLoader with display_name, category, follow_up_question |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None - all 13 features have all three new fields populated with concrete values.

## Threat Flags

None - no new network endpoints, auth paths, or trust boundary changes. New fields are server-side config only, consistent with the existing YAML-as-config pattern (T-06-01 and T-06-02 in plan threat model).

## Self-Check: PASSED

- backend/config/features.yaml modified: FOUND (39 insertions confirmed by git)
- backend/app/core/schema_loader.py modified: FOUND (updated FeatureDefinition + SchemaLoader)
- backend/tests/test_schema_loader.py modified: FOUND (3 new tests added)
- Commit c3404ba: FOUND (git log confirmed)
- Commit 7df9dca: FOUND (git log confirmed)
- All 16 tests pass: CONFIRMED (pytest output 16 passed in 0.04s)
