# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-05)

**Core value:** The ML model is the source of truth for clinical predictions — the LLM orchestrates input extraction and explanation but never generates or overrides clinical decisions.
**Current focus:** Phase 1 — Foundation

## Current Position

Phase: 1 of 5 (Foundation)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-04-05 — Roadmap created, ready for Phase 1 planning

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: scikit-learn must be pinned at 1.5.2 — pkl files serialized at this version; cross-version loading breaks GBM models
- [Init]: Build order is bottom-up: YAML schema + model loading → LLM extraction + safeguards → conversation orchestration → API surface → React frontend
- [Init]: All four safeguards (injection defense, LLM isolation, null-by-default extraction, post-generation scan) ship in Phase 2 — not retrofitted later

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: Confirm exact pkl feature column names from existing codebase before writing features.yaml — YAML/pkl mismatch is the highest-probability fatal blocker
- [Phase 2]: GPT-4o-mini structured output reliability degrades above ~800 token system prompts — prompt length must be validated during Phase 2 planning
- [Phase 2]: Medical abbreviation coverage (LFTs, Tokyo criteria, etc.) needs a brief clinician interview before finalizing the extraction system prompt

## Session Continuity

Last session: 2026-04-05
Stopped at: Roadmap written, STATE.md initialized, REQUIREMENTS.md traceability pending
Resume file: None
