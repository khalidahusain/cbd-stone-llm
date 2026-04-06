# Requirements: CBD Stone LLM

**Defined:** 2026-04-05
**Core Value:** The ML model is the source of truth for clinical predictions — the LLM orchestrates input extraction and explanation but never generates or overrides clinical decisions.

## v1 Requirements

### Chat Interface

- [ ] **CHAT-01**: Clinician can enter a free-text description of a patient case in a chat input
- [ ] **CHAT-02**: System displays LLM responses as chat messages with natural language explanations
- [ ] **CHAT-03**: System asks targeted follow-up questions when required variables are missing (sex, imaging)
- [ ] **CHAT-04**: System asks one clear question at a time (not all missing fields at once)
- [ ] **CHAT-05**: Conversation updates prediction iteratively as new variables are added

### Extraction Pipeline

- [ ] **EXTR-01**: LLM extracts structured variables from free-text clinical descriptions (age, sex, labs, conditions, imaging)
- [ ] **EXTR-02**: YAML schema defines all 13 model features with names, types, valid ranges, and required/optional status
- [ ] **EXTR-03**: LLM references YAML schema to determine what to extract and validate
- [ ] **EXTR-04**: Extracted values are validated against defined ranges (reject age=500, bilirubin=-3) with clear error feedback
- [ ] **EXTR-05**: System maintains a persistent structured state object across conversation turns tracking all extracted variables
- [ ] **EXTR-06**: Each new message updates the state object; system uses it to determine what is missing and what to ask next
- [ ] **EXTR-07**: System presents a structured summary of extracted patient data for clinician confirmation before running model
- [ ] **EXTR-08**: Clinician must explicitly confirm extracted values before model execution (separate confirmation step)

### Model Inference

- [ ] **MODL-01**: FastAPI backend loads existing scikit-learn GBM models (.pkl) at startup
- [ ] **MODL-02**: Model executes only when minimum required inputs are present (age, sex, bilirubin) AND clinician has confirmed
- [ ] **MODL-03**: Missing non-required values are handled by the existing iterative imputer
- [ ] **MODL-04**: Model returns probability of choledocholithiasis (0-100%)
- [ ] **MODL-05**: Probability maps to recommended intervention (CCY±IOC <10%, MRCP 10-44%, EUS 44-90%, ERCP >90%)
- [ ] **MODL-06**: If required variables cannot be obtained, system clearly states insufficient information and does not run model
- [ ] **MODL-07**: Cholangitis fast-path: when Tokyo criteria cholangitis is detected, display ERCP guideline banner per ASGE 2019

### Safety & Safeguards

- [ ] **SAFE-01**: LLM has no code path to generate probability predictions — architectural enforcement, not just prompt instruction
- [ ] **SAFE-02**: Prompt injection defense: user input is isolated from system instructions (XML/JSON wrapping)
- [ ] **SAFE-03**: Post-generation assertion scan ensures LLM output contains no probability values or clinical recommendations
- [ ] **SAFE-04**: LLM uses direct extraction prompts (not chain-of-thought) for the extraction call to minimize hallucination
- [ ] **SAFE-05**: Null-by-default extraction schema — LLM returns null for fields not explicitly stated, never fabricates values

### Dashboard

- [ ] **DASH-01**: Probability of CBD stone displayed as a clear percentage, dynamically updated
- [ ] **DASH-02**: Risk stratification label (Low/Intermediate/High) mapped to probability
- [ ] **DASH-03**: Management guidance bar: horizontal 0-100% scale with labeled intervention zones and visual pointer
- [ ] **DASH-04**: Recommended next intervention displayed as explicit text ("Suggested next step in management")
- [ ] **DASH-05**: Cost-weighted intervention table showing probability-weighted cost for IOC, MRCP, ERCP, EUS
- [ ] **DASH-06**: Interpretation guidance panel always visible on desktop — explains probability ranges and intervention thresholds
- [ ] **DASH-07**: Abbreviations/reference panel with definitions for MRCP, EUS, ERCP, IOC, etc.

### Frontend & Layout

- [ ] **FRNT-01**: React (Vite) + TypeScript single-page application
- [ ] **FRNT-02**: Desktop layout: left side chat interface, right side (~1/3) clinical dashboard
- [ ] **FRNT-03**: All dashboard elements visible simultaneously on desktop (probability, risk bar, cost table, guidance, abbreviations)
- [ ] **FRNT-04**: Mobile layout: chat-first initially, risk visualization on top after data collected
- [ ] **FRNT-05**: Cost table behind expandable control on mobile
- [ ] **FRNT-06**: Loading indicator while LLM extraction and model inference run

### Backend & Infrastructure

- [ ] **INFR-01**: FastAPI Python backend serving ML model inference and OpenAI API orchestration
- [ ] **INFR-02**: OpenAI API key stored server-side only (never exposed to frontend)
- [ ] **INFR-03**: Server-side session state (in-process dict keyed by session UUID) for conversation persistence
- [ ] **INFR-04**: Application served on local network port 450
- [ ] **INFR-05**: scikit-learn pinned at 1.5.2 to maintain pkl compatibility

## v2 Requirements

### Enhanced Extraction

- **EXTR-V2-01**: Confidence-aware extraction with "uncertain" flagging for ambiguous values
- **EXTR-V2-02**: Imputation transparency — mark which values were imputed vs directly provided
- **EXTR-V2-03**: Abbreviated case summary generated after extraction and prediction

### Enhanced Dashboard

- **DASH-V2-01**: Anatomy reference panel (biliary anatomy diagram) — asset exists
- **DASH-V2-02**: SHAP-based feature importance visualization for individual predictions

### Infrastructure

- **INFR-V2-01**: User authentication for public deployment
- **INFR-V2-02**: HTTPS/TLS for production deployment
- **INFR-V2-03**: Persistent session storage (Redis) for multi-server deployment

## Out of Scope

| Feature | Reason |
|---------|--------|
| EHR integration (Epic, Cerner) | High complexity, HL7/FHIR compliance; not needed for de-identified workflow |
| PHI handling / real patient names | System uses de-identified parameters only; avoids HIPAA surface area |
| Autonomous clinical decision-making | LLM must never generate diagnoses or recommendations without model backing |
| Alert interruptions / pop-up warnings | Alert fatigue is the #1 reason CDSS systems fail; all info surfaced inline |
| Multi-language support | English-only clinical staff at target site |
| Streaming token-by-token LLM output | No clinical value for structured extraction; adds WebSocket complexity |
| Diagnosis generation by LLM | Goes beyond extraction into diagnosis requiring FDA-level validation |
| Model retraining / feedback loop UI | Requires IRB, data governance, retraining pipeline — future research milestone |
| Automatic case saving / database | Data governance questions disproportionate to v1 local deployment benefit |
| CBD diameter measurements | Not used by the prediction model |
| Gallbladder stone presence/absence | Not part of this prediction workflow |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFR-01 | Phase 1 | Pending |
| INFR-04 | Phase 1 | Pending |
| INFR-05 | Phase 1 | Pending |
| EXTR-02 | Phase 1 | Pending |
| MODL-01 | Phase 1 | Pending |
| MODL-02 | Phase 1 | Pending |
| MODL-03 | Phase 1 | Pending |
| MODL-04 | Phase 1 | Pending |
| MODL-05 | Phase 1 | Pending |
| MODL-06 | Phase 1 | Pending |
| MODL-07 | Phase 1 | Pending |
| EXTR-01 | Phase 2 | Pending |
| EXTR-03 | Phase 2 | Pending |
| EXTR-04 | Phase 2 | Pending |
| EXTR-05 | Phase 2 | Pending |
| SAFE-01 | Phase 2 | Pending |
| SAFE-02 | Phase 2 | Pending |
| SAFE-03 | Phase 2 | Pending |
| SAFE-04 | Phase 2 | Pending |
| SAFE-05 | Phase 2 | Pending |
| INFR-02 | Phase 2 | Pending |
| CHAT-01 | Phase 3 | Pending |
| CHAT-02 | Phase 3 | Pending |
| CHAT-03 | Phase 3 | Pending |
| CHAT-04 | Phase 3 | Pending |
| CHAT-05 | Phase 3 | Pending |
| EXTR-06 | Phase 3 | Pending |
| EXTR-07 | Phase 3 | Pending |
| EXTR-08 | Phase 3 | Pending |
| INFR-03 | Phase 3 | Pending |
| FRNT-01 | Phase 4 | Pending |
| FRNT-02 | Phase 4 | Pending |
| FRNT-03 | Phase 4 | Pending |
| FRNT-06 | Phase 4 | Pending |
| DASH-01 | Phase 4 | Pending |
| DASH-02 | Phase 4 | Pending |
| DASH-03 | Phase 4 | Pending |
| DASH-04 | Phase 4 | Pending |
| DASH-05 | Phase 4 | Pending |
| DASH-06 | Phase 4 | Pending |
| DASH-07 | Phase 4 | Pending |
| FRNT-04 | Phase 5 | Pending |
| FRNT-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 43 total
- Mapped to phases: 43
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-05*
*Last updated: 2026-04-05 after roadmap creation — traceability populated*
