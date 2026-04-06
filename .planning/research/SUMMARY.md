# Project Research Summary

**Project:** CBD Stone LLM — Conversational Clinical Decision Support
**Domain:** LLM-orchestrated clinical decision support (choledocholithiasis risk stratification)
**Researched:** 2026-04-05
**Confidence:** HIGH

---

## Executive Summary

CBD Stone LLM is a conversational CDSS that wraps a validated GBM ensemble (AUC 0.90, 6 scikit-learn pkl files) in an LLM extraction layer, allowing clinicians to describe a patient in natural language rather than filling out a form. The correct architectural pattern — validated by multiple clinical AI studies — is: LLM extracts features, Python code decides when inference runs, the GBM produces the probability, and the LLM explains nothing quantitative. The validated model is the irreplaceable asset; the LLM is a data-entry accelerator, not a clinical reasoner.

The recommended stack is Python 3.11 / FastAPI / React 19 / TypeScript. The three most critical version constraints are non-negotiable: scikit-learn must stay at 1.5.2, joblib at 1.4.2, and numpy at 1.26.4, because the pkl files were serialized under those exact versions and cross-version loading is documented to fail. Everything else in the stack is current stable with no unusual constraints. The build order must go bottom-up: YAML schema and model loading first, then the LLM extraction layer, then the conversation orchestration layer, then the API surface, then the frontend. This order means ML inference is verified before any LLM code is written.

The top risks are not implementation bugs — they are trust failures. LLM hallucination of extraction values, multi-turn context loss, and prompt injection are all documented failure modes in clinical AI deployments with peer-reviewed evidence. Each must be addressed architecturally before any clinical user testing, not retrofitted afterward. The extraction verification step (the moment where the clinician confirms what was extracted before the model runs) is the single most important UX element in the system — it is simultaneously the human-in-the-loop checkpoint, the hallucination audit gate, and the automation bias mitigation.

---

## Key Findings

### Recommended Stack

The backend is Python 3.11 / FastAPI 0.135.3 / Pydantic 2.12.5 / OpenAI SDK 2.30.0, serving the existing scikit-learn pkl models via joblib. The frontend is Vite 8 / React 19 / TypeScript 5 / Tailwind CSS 4 / shadcn/ui, with Zustand 5 for client state and TanStack Query 5 for server state. All versions are verified against PyPI and npm as of 2026-04-05.

The single most important constraint in the entire stack: the 4 pinned backend packages below must not be upgraded without retraining all 6 models.

**Core technologies:**

- **Python 3.11.x**: Runtime — must match the conda env that trained the pkl files; 3.12+ risks model loading failure
- **FastAPI 0.135.3**: API framework — async, auto-docs, native Pydantic v2 integration; `fastapi[standard]` installs uvicorn and python-multipart
- **scikit-learn 1.5.2 (pinned)**: ML inference — pkl files serialized at this version; cross-version loading breaks GBM models (`ModuleNotFoundError: _loss`)
- **joblib 1.4.2 (pinned)**: Model deserialization — must match the serialization environment
- **numpy 1.26.4 (pinned)**: Numerical arrays — scikit-learn 1.5.2 was built against 1.26.x; numpy 2.x is untested
- **openai 2.30.0**: LLM client — use `client.beta.chat.completions.parse()` with a Pydantic model as `response_format`; do not use legacy `ChatCompletion` or manual JSON mode
- **React 19 / Vite 8 / Tailwind CSS 4**: Frontend — current stable series; Tailwind v4 installs via `@tailwindcss/vite` plugin, no `tailwind.config.js` needed
- **Zustand 5 + TanStack Query 5**: State — Zustand for conversation/session state; TanStack Query for API call loading/error/cache management
- **shadcn/ui (CLI-managed)**: Components — `ScrollArea`, `Card`, `Badge`, `Table`, `Collapsible`, `Button` needed

### Expected Features

**Must have (table stakes) — ship with MVP:**

- Natural language free-text input — eliminates the form-entry friction that is the core value proposition
- Structured extraction confirmation — clinicians will not trust output they cannot verify; this is the human-in-the-loop checkpoint
- Follow-up questioning for missing required variables — sex cannot be imputed; must ask explicitly
- Input range validation with user-facing error messages — safety requirement; out-of-range values must not reach the model silently
- Probability output as a number (percentage) — the raw GBM output, not a label
- Risk stratification label — ASGE/ESGE tiers (Low/Intermediate/High) with correct thresholds
- Recommended next intervention — one clear action per tier (CCY+/-IOC, MRCP, EUS, ERCP)
- Management guidance bar visualization — the 0-100% color-coded zone bar; already a known visual artifact
- Iterative dashboard updates as conversation progresses — prediction updates in place without resetting conversation
- Interpretation guidance panel — always visible on desktop; explains which features drove the prediction
- Prompt injection defense — 94.4% injection success rate documented in clinical LLMs; must ship with v1
- LLM architectural isolation from inference — enforced at code level, not just in the prompt

**Should have (differentiators) — add after MVP:**

- Cholangitis fast-path alert — ASGE 2019 mandates ERCP for Tokyo-criteria cholangitis; banner before model output
- Cost-weighted intervention table — probability-weighted cost estimates across IOC/MRCP/ERCP/EUS
- Imputation transparency — mark imputed values with "(estimated)" badge; allow clinician override
- Abbreviated case summary — 2-3 sentence plain-language confirmation of what the LLM understood
- Confidence-aware extraction flagging — flag ambiguous extractions; require explicit confirmation
- Anatomy reference panel — existing asset; persistent sidebar on desktop
- Mobile-responsive layout — desktop-first; mobile pass after desktop is validated

**Defer (v2+) — do not build:**

- EHR integration (Epic/Cerner) — HL7/FHIR compliance and auth are out of scope per PROJECT.md
- PHI handling and real patient identifiers — HIPAA surface area; system is for de-identified parameters
- Autonomous LLM clinical reasoning — #1 liability risk; LLM hallucination rate 15-40% in clinical tasks
- Alert interruptions / modal dialogs — alert fatigue kills CDSS adoption; passive inline display only
- User authentication and role-based access — not needed for local-network deployment at this stage
- Streaming token-by-token LLM output — adds WebSocket complexity with no clinical value for extraction tasks
- Automatic case saving / database logging — data governance questions at v1 local deployment
- Model retraining or feedback loop UI — requires IRB and retraining pipeline; future research milestone

### Architecture Approach

The system is a two-panel single-page app (ChatPanel left, DashboardPanel right) backed by a service-layered FastAPI monolith. The defining architectural constraint is the strict separation between the LLM path and the inference path: `ExtractionService` calls OpenAI; `InferenceService` runs scikit-learn; `ConversationService` orchestrates both; the LLM never triggers inference directly and is never registered as an OpenAI function/tool. State lives server-side in a `SessionStore` dict keyed by UUID; the client sends a sessionId, never authoritative state. Every `/chat` response returns `{message, prediction, extracted_features}` in one round-trip — no separate polling.

**Major components:**

1. **SchemaLoader** — parses `features.yaml` at startup; the YAML is the coupling point between the ML model and the LLM; single source of truth for feature names, types, valid ranges, and required flags
2. **InferenceService** — loads all 6 pkl files once at startup via FastAPI lifespan; runs imputer + GBM ensemble + ASGE override rule; called only by ConversationService, never by the LLM
3. **ExtractionService** — calls `client.beta.chat.completions.parse()` with a flat Pydantic `ExtractionResult` schema; system prompt is built programmatically from the YAML schema
4. **ValidationService** — range/type checks against the YAML schema; rejects implausible values before inference; generates user-facing error messages
5. **SafeguardService** — pre-input injection scan; post-output check that LLM reply contains no probability numbers or clinical verdicts
6. **ConversationService** — orchestrates one turn: guard → extract → validate → merge state → (if complete) infer → reply; owns the phase decision logic
7. **SessionStore** — in-process dict; server owns authoritative state; client sends sessionId only
8. **ChatPanel / DashboardPanel** — frontend components; frontend owns zero business logic; dashboard updates from `prediction` field in every `/chat` response

### Critical Pitfalls

1. **LLM fabricates extraction values** — Use OpenAI Structured Outputs with `null` as explicit "not mentioned"; instruct "do not infer absent fields"; build server-side logging of every extraction with the source utterance. Warning sign: full extraction with no nulls after a brief, vague description.

2. **LLM generates its own clinical probability** — Enforce architecturally: never register InferenceService as an OpenAI tool; LLM system prompt explicitly prohibits prediction language; automated test confirms LLM never returns a numeric probability. This is a code constraint, not a prompt instruction.

3. **Prompt injection bypasses clinical workflow** — 94.4% injection success rate in clinical LLMs (JAMA Network Open, 2025). Wrap all user input with explicit role labeling ("CLINICIAN INPUT (untrusted):"); scan for instruction-pattern keywords before LLM call; post-generation scan for out-of-scope content.

4. **Multi-turn conversation loses clinical state** — LLM performance drops 39% in multi-turn conversations (arXiv, 2025). Server-side Python dict is the source of truth; LLM returns only diffs (`{"updated_fields": {...}}`); pass current state JSON back into every LLM call; never rely on the LLM to "remember" values.

5. **YAML schema drifts from pkl feature list** — Write a startup validation test that loads the YAML and the pkl feature columns and asserts exact match; fail fast. Treat the YAML and pkl files as a single version-locked artifact.

---

## Implications for Roadmap

The architecture's dependency layers map directly to build phases. The research is unambiguous: the ML inference pipeline must be verified before any LLM code is written. Security and clinical safety constraints must be built in from Phase 1, not added later.

### Phase 1: Foundation — YAML Schema, Model Loading, and Bare Inference

**Rationale:** All downstream work depends on knowing the pkl files load correctly and the YAML schema matches them. This phase has no LLM dependency, so it can be built and tested independently. Failures here are fatal; fix them before adding complexity.
**Delivers:** Working `/predict` endpoint that accepts a feature dict and returns a probability + risk tier + cost table. YAML schema validated against pkl feature columns at startup. ValidationService with range checks for all 13 variables.
**Addresses:** Input range validation, model inference, risk stratification label, recommended intervention, management guidance bar data
**Avoids:** YAML schema drift (Pitfall 5), implausible values passing silently (Pitfall 7), scikit-learn cross-version loading failure

### Phase 2: LLM Extraction Engine and Security Hardening

**Rationale:** The extraction layer sits on top of the verified inference foundation. Building it second means extraction failures can be isolated from inference failures. Security constraints (injection defense, LLM architectural isolation) must ship in this phase — they cannot be retrofitted before clinical user testing.
**Delivers:** ExtractionService calling `client.beta.chat.completions.parse()` with a Pydantic `ExtractionResult` schema built from the YAML. SafeguardService with input sanitization and post-generation output scan. Automated test confirming LLM never returns a numeric probability.
**Uses:** `openai==2.30.0` structured outputs, Pydantic `ExtractionResult` model, `features.yaml` system prompt builder
**Implements:** ExtractionService, SafeguardService, SchemaLoader
**Avoids:** LLM fabrication (Pitfall 1), LLM self-prediction (Pitfall 2), prompt injection (Pitfall 3), chain-of-thought hallucination (Pitfall 10), sex inferred from pronouns (Pitfall 12)

### Phase 3: Conversation Orchestration and Session State

**Rationale:** Multi-turn conversation management is where the most insidious failures occur (context loss, state divergence). Building the server-side SessionStore and ConversationService as a discrete phase makes state management testable before adding the full API and frontend.
**Delivers:** ConversationService orchestrating the full turn loop (guard → extract → validate → merge state → infer → reply). SessionStore keyed by UUID. Follow-up questioning for missing required variables. Extraction confirmation message generation.
**Implements:** ConversationService, SessionStore, conversation phase logic, missing-variable detection
**Avoids:** Multi-turn context loss (Pitfall 4), frontend/backend state divergence (Pitfall 11), redundant follow-up questions (Pitfall 6)

### Phase 4: Full API Surface and Integration

**Rationale:** Wire all services behind the FastAPI router layer only after services are independently tested. Adds the POST /chat endpoint returning `{message, prediction, extracted_features}`, CORS configuration, and the lifespan model-loading pattern. The `/predict` debug endpoint from Phase 1 remains for direct testing.
**Delivers:** POST /chat endpoint with full turn handling. GET /health liveness probe. CORS configured for dev (`:5173`) and production (`:450`). Pydantic request/response schemas matching the frontend type definitions. `asyncio.run_in_executor` wrapping for scikit-learn inference to avoid blocking the event loop.
**Uses:** FastAPI 0.135.3, Uvicorn 0.43.0, Pydantic 2.12.5, CORSMiddleware
**Avoids:** Monolithic endpoint anti-pattern, scikit-learn blocking the async event loop (Pitfall Anti-Pattern 5)

### Phase 5: React Frontend — Core Desktop Layout

**Rationale:** Build the frontend last, against a fully working API. Desktop-first. Two-panel layout: ChatPanel (left) + DashboardPanel (right). The backend owns all business logic; the frontend is a display layer that replaces its state from every server response.
**Delivers:** ChatPanel with MessageList, InputBox, typing indicator. DashboardPanel with ProbabilityBar, RiskCategory, CostTable, InterpretationGuidance. Zustand SessionStore with UUID. TanStack Query wrapping POST /chat. Extraction state always visible in dashboard (automation bias mitigation).
**Uses:** Vite 8, React 19, TypeScript 5, Tailwind CSS 4, shadcn/ui (ScrollArea, Card, Badge, Table, Button), Zustand 5, TanStack Query 5
**Avoids:** Frontend state divergence from backend (Pitfall 11), automation bias (Pitfall 9)

### Phase 6: Differentiators and UX Polish

**Rationale:** Clinically important features that do not block the core workflow. Add after the desktop baseline is validated with real clinical users.
**Delivers:** Cholangitis fast-path alert (ASGE 2019 override). Imputation transparency badges. Abbreviated case summary. Confidence-aware extraction flagging. Anatomy reference panel. Mobile-responsive layout (chat-first on mobile, cost table behind expand control).
**Addresses:** Cholangitis fast-path, imputation transparency, case summary, confidence-aware extraction, anatomy panel, mobile layout (all from the "Should Have" list)

### Phase Ordering Rationale

- Layer 0-1 (schema + inference) before Layer 2 (LLM) ensures the foundation is validated independently — failures are isolatable
- Security hardening ships in Phase 2, not Phase 5: injection defense and LLM architectural isolation cannot be retrofitted before clinician testing
- Server-side state architecture (Phase 3) is designed before the conversation loop is built, not inferred from it — this directly addresses the multi-turn context loss risk
- Frontend (Phase 5) is last because it has no logic of its own; it waits on a stable API contract

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (LLM Extraction):** Exact prompt wording for null-by-default behavior and medical abbreviation handling needs iteration with real clinical text; system prompt length vs. structured output reliability tradeoff (GPT-4o-mini degrades above ~800 tokens)
- **Phase 3 (Conversation Orchestration):** Multi-turn conversation degradation is a documented research problem; the server-side diff pattern is the recommended mitigation but prompt engineering details need testing with realistic case narratives
- **Phase 6 (Mobile Layout):** Standard responsive patterns; no research needed — well-documented Tailwind + shadcn patterns apply

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation):** FastAPI lifespan, joblib loading, Pydantic validation — all thoroughly documented; no novel patterns
- **Phase 4 (API Surface):** Standard FastAPI routing, CORS, and async executor patterns — HIGH confidence, well-documented
- **Phase 5 (Frontend Core):** Vite + React + Zustand + TanStack Query patterns are widely documented; component structure is straightforward

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI and npm on 2026-04-05; version constraints for pkl files are documented by scikit-learn maintainers |
| Features | HIGH | Table stakes derived from peer-reviewed CDSS adoption studies; anti-features grounded in documented CDSS failure patterns (alert fatigue, automation bias) |
| Architecture | HIGH | Core patterns (lifespan singletons, structured outputs, server-side state) verified against official docs; SSE specifics are MEDIUM (community tutorials) |
| Pitfalls | HIGH | All critical pitfalls supported by peer-reviewed 2025 sources; quantitative evidence cited (94.4% injection rate, 39% multi-turn degradation) |

**Overall confidence:** HIGH

### Gaps to Address

- **Exact LLM prompt wording**: The system prompt template in ARCHITECTURE.md is directionally correct but will require iteration with real clinician inputs and realistic case narratives before it is production-ready. Plan for prompt engineering as a distinct sub-task in Phase 2.
- **Medical abbreviation coverage**: The system prompt must include an abbreviation/synonym mapping (LFTs → AST/ALT/ALP, Tokyo criteria → cholangitis, etc.). The full list of abbreviations in use at the target institution is not in the research; this needs a brief clinician interview during Phase 2 planning.
- **Latency baseline**: GPT-4o-mini structured output latency under realistic load (multi-turn, 200-word inputs) has not been benchmarked on the specific deployment network. Establish this early in Phase 2 testing before deciding whether synchronous POST /chat is sufficient or SSE streaming is needed for MVP.
- **YAML schema completeness**: The YAML schema `features.yaml` must be written and validated against the pkl feature columns as the first artifact in Phase 1. The exact column names expected by the pkl files need to be confirmed from the existing codebase before writing the YAML.

---

## Sources

### Primary (HIGH confidence)
- FastAPI PyPI / official docs — lifespan events, CORS, routing patterns
- OpenAI Structured Outputs docs — `.parse()` API, schema constraints, null handling
- scikit-learn model persistence docs + GitHub issue #30062 — cross-version pkl loading failure
- JAMA Network Open (2025) — prompt injection: 94.4% success rate in clinical LLMs
- OWASP LLM Top 10 2025 — prompt injection #1 vulnerability
- Nature Medicine (2025) — automation bias: diagnostic accuracy drop from 84.9% to 73.3%
- Nature npj Digital Medicine (2025) — CDSS adoption patterns; alert fatigue evidence
- PMC / multiple peer-reviewed sources — hallucination rates in clinical LLM tasks

### Secondary (MEDIUM confidence)
- arXiv:2505.06120 (2025) — multi-turn LLM degradation: 39% performance drop, +112% unreliability (preprint, but consistent with other sources)
- OpenAI community forums (2024-2025) — GPT-4o-mini structured output reliability degradation with complex schemas
- Multiple FastAPI implementation tutorials — SSE streaming patterns, singleton dependency patterns
- medRxiv preprints (2025) — chain-of-thought hallucination in clinical tasks; automation bias quantification

### Tertiary (LOW confidence / needs validation)
- Exact prompt wording for the system prompt — directionally validated, but specific text will need empirical iteration
- Latency characteristics of GPT-4o-mini under production load on the target deployment network — untested

---

*Research completed: 2026-04-05*
*Ready for roadmap: yes*
