# Roadmap: CBD Stone LLM

## Overview

The build goes bottom-up: the validated scikit-learn GBM model is the foundation — nothing else runs until model loading is confirmed. From there, the LLM extraction engine and all four safety safeguards are built as one unit (security cannot be retrofitted before clinical use). Conversation orchestration and session state come next, followed by the full FastAPI API surface that wires all services together. The React desktop frontend is built last, against a stable API contract. Mobile responsive behavior closes out v1 once the desktop baseline is validated.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - YAML schema, model loading, and bare /predict inference endpoint
- [ ] **Phase 2: Extraction & Safeguards** - LLM extraction engine, input validation, and all four clinical safety safeguards
- [ ] **Phase 3: Conversation Orchestration** - Multi-turn conversation loop, session state, follow-up questioning, and extraction confirmation
- [ ] **Phase 4: Frontend & Dashboard** - React desktop SPA with two-panel layout and full clinical dashboard
- [ ] **Phase 5: Mobile Layout** - Responsive mobile layout with chat-first flow and collapsible cost table

## Phase Details

### Phase 1: Foundation
**Goal**: The ML inference pipeline is verified end-to-end — the YAML schema is validated against pkl feature columns, all six model files load at startup, and a working /predict endpoint returns probability, risk tier, and recommended intervention for a given feature dict.
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-04, INFR-05, EXTR-02, MODL-01, MODL-02, MODL-03, MODL-04, MODL-05, MODL-06, MODL-07
**Success Criteria** (what must be TRUE):
  1. POST /predict accepts a feature dict and returns a probability percentage, risk label, and recommended next intervention
  2. The YAML schema defines all 13 model features (names, types, valid ranges, required/optional status) and a startup assertion confirms it matches the pkl feature columns exactly
  3. Missing non-required variables are handled by the iterative imputer without error; missing required variables (sex) cause the endpoint to return a clear "insufficient information" response rather than running the model
  4. When clinical cholangitis (Tokyo criteria) is present, the endpoint returns a cholangitis fast-path indicator alongside the ASGE ERCP recommendation
  5. The FastAPI application starts on port 450 with scikit-learn pinned at 1.5.2 and all six pkl files loaded in the lifespan event
**Plans:** 3 plans

Plans:
- [ ] 01-01-PLAN.md — Project scaffold, YAML feature schema, model file copy, and dependency configuration
- [ ] 01-02-PLAN.md — SchemaLoader, InferenceService, and ValidationService with unit tests
- [ ] 01-03-PLAN.md — FastAPI application with lifespan, /predict and /health endpoints, integration tests

### Phase 2: Extraction & Safeguards
**Goal**: The LLM extraction layer runs on top of the verified inference foundation, and all four clinical safety safeguards are enforced architecturally — the LLM cannot generate predictions, user input is isolated from system instructions, the schema drives null-by-default extraction, and every LLM output is scanned before it reaches the user.
**Depends on**: Phase 1
**Requirements**: EXTR-01, EXTR-03, EXTR-04, EXTR-05, SAFE-01, SAFE-02, SAFE-03, SAFE-04, SAFE-05, INFR-02
**Success Criteria** (what must be TRUE):
  1. ExtractionService calls OpenAI structured outputs with a Pydantic ExtractionResult schema built from features.yaml; fields not mentioned in the input are returned as null (never fabricated)
  2. An automated test confirms the LLM has no code path to return a numeric probability — InferenceService is not registered as an OpenAI tool and the post-generation scan blocks any LLM response containing probability numbers
  3. User input containing injection patterns (e.g., "ignore previous instructions") is detected pre-LLM-call and rejected with a safe error message before reaching the system prompt
  4. Extracted values outside valid YAML-defined ranges (e.g., age=500, bilirubin=-3) are rejected by ValidationService with a user-facing error message before the state object is updated
  5. The OpenAI API key is stored and used server-side only; the frontend has no path to retrieve or observe it
**Plans**: TBD
**UI hint**: no

### Phase 3: Conversation Orchestration
**Goal**: A complete multi-turn clinical conversation works end-to-end — clinicians can describe a patient in free text, the system asks targeted follow-up questions one at a time for missing required variables, maintains a persistent state object across turns, and presents a structured extraction summary for clinician confirmation before the model runs.
**Depends on**: Phase 2
**Requirements**: CHAT-01, CHAT-02, CHAT-03, CHAT-04, CHAT-05, EXTR-06, EXTR-07, EXTR-08, INFR-03
**Success Criteria** (what must be TRUE):
  1. A clinician can enter a free-text patient description and receive a natural language LLM response that identifies what was extracted and what is still needed
  2. When required variables are missing, the system asks exactly one targeted question per turn — it does not enumerate all missing fields at once
  3. A server-side session dict (keyed by UUID) holds the authoritative state object; the frontend sends only a session ID and never authoritative clinical data
  4. Before the model runs, the system presents a structured summary of all extracted variables and requires explicit clinician confirmation; the model does not execute without that confirmation
  5. As the conversation progresses and new variables are confirmed, the prediction updates iteratively in the same session without resetting the conversation history
**Plans**: TBD

### Phase 4: Frontend & Dashboard
**Goal**: A working React desktop application presents the two-panel clinical interface — chat on the left, full dashboard on the right — and all dashboard elements (probability, risk bar, cost table, interpretation guidance, abbreviations) are visible simultaneously and update from every server response.
**Depends on**: Phase 3
**Requirements**: FRNT-01, FRNT-02, FRNT-03, FRNT-06, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07
**Success Criteria** (what must be TRUE):
  1. The application loads as a React (Vite) + TypeScript SPA with a left chat panel and a right dashboard panel (~1/3 screen width) visible simultaneously on desktop
  2. The dashboard displays probability as a percentage, a risk stratification label (Low/Intermediate/High), a horizontal management guidance bar with labeled intervention zones and a visual pointer, and the recommended next step as explicit text
  3. The cost-weighted intervention table (IOC, MRCP, ERCP, EUS with probability-weighted costs) is visible in the dashboard without any expansion action on desktop
  4. The interpretation guidance panel and abbreviations reference panel are always visible on desktop without scrolling or expanding
  5. A loading indicator is shown while LLM extraction and model inference are running; the dashboard updates in place when the response arrives without resetting the chat
**Plans**: TBD
**UI hint**: yes

### Phase 5: Mobile Layout
**Goal**: The application is usable on mobile — chat is the primary entry point, risk visualization appears above the conversation after data is collected, and the cost table is accessible behind an expandable control to avoid information overload on small screens.
**Depends on**: Phase 4
**Requirements**: FRNT-04, FRNT-05
**Success Criteria** (what must be TRUE):
  1. On mobile viewports, the interface opens in a chat-first layout with no dashboard panel visible initially; after the clinician has confirmed extracted data, a risk visualization panel appears above the chat
  2. The cost-weighted intervention table on mobile is hidden behind a clearly labeled expandable control and expands/collapses without breaking the layout or losing conversation state
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Planning complete | - |
| 2. Extraction & Safeguards | 0/TBD | Not started | - |
| 3. Conversation Orchestration | 0/TBD | Not started | - |
| 4. Frontend & Dashboard | 0/TBD | Not started | - |
| 5. Mobile Layout | 0/TBD | Not started | - |
