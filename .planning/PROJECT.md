# CBD Stone LLM — Conversational Clinical Decision Support

## What This Is

A conversational, LLM-powered clinical decision support system for assessing the probability of common bile duct (CBD) stones (choledocholithiasis). Clinicians describe a patient case in natural language; an LLM extracts structured clinical variables, passes them to a validated machine learning model, and returns both a natural language explanation and an interpretable clinical dashboard showing risk stratification, recommended interventions, and cost analysis. Built for gastroenterologists and physicians at Johns Hopkins.

## Core Value

The ML model is the source of truth for clinical predictions — the LLM orchestrates input extraction and explanation but never generates or overrides clinical decisions.

## Current Milestone: v1.1 Conversation Polish

**Goal:** Make every chat message human-readable and clinician-friendly — no snake_case, no code-like formatting, no verbose imputation listings.

**Target features:**
- Human-readable field labels in all chat messages (e.g., "Total Bilirubin" not "total_bilirubin")
- Smarter confirmation summary — show only provided values, group logically, brief imputation note
- Polished extraction feedback — natural phrasing
- Polished follow-up questions — conversational tone
- Polished validation errors — clear, friendly messages
- Polished prediction results — readable risk explanation

## Requirements

### Validated

- ✓ ML prediction model (GBM, AUC 0.90) trained on n=2342 patients — existing
- ✓ Feature imputation pipeline (iterative imputer) for missing values — existing
- ✓ Risk stratification thresholds (CCY±IOC <10%, MRCP 10-44%, EUS 44-90%, ERCP >90%) — existing
- ✓ Probability-weighted cost estimates for IOC/MRCP/ERCP/EUS — existing
- ✓ Management guidance bar visualization (0-100% scale with intervention zones) — existing
- ✓ Anatomy diagram and abbreviations reference panel — existing

### Active

- [ ] Natural language chat interface for clinician input (free text, not forms)
- [ ] LLM-based structured data extraction from clinical text (GPT-4o-mini)
- [ ] YAML schema defining model features, types, valid ranges, and required/optional status
- [ ] LLM follow-up questioning for missing/ambiguous variables
- [ ] Extraction verification — LLM confirms extracted values with clinician before model run
- [ ] Input validation — reject nonsensical values (e.g., age=500, bilirubin=-3)
- [ ] Prompt injection defense — prevent adversarial bypassing of clinical workflow
- [ ] LLM never overrides model — architectural safeguard ensuring LLM cannot generate predictions
- [ ] FastAPI backend serving ML model inference + OpenAI API orchestration
- [ ] React (Vite) + TypeScript frontend with chat + dashboard layout
- [ ] Desktop layout: left chat, right dashboard (~1/3 screen)
- [ ] Mobile layout: chat-first, then risk visualization on top after data collected
- [ ] Persistent clinical dashboard: probability, risk bar, next step, cost table, interpretation guidance
- [ ] Iterative prediction updates as new variables are added via conversation
- [ ] Interpretation guidance panel (always visible on desktop)
- [ ] Cost table behind expandable control on mobile

### Out of Scope

- CBD diameter measurements — not used by the model
- Gallbladder stone presence/absence — not part of this prediction workflow
- Real-time EHR integration — future consideration, not current scope
- HIPAA-compliant PHI handling — system uses de-identified data only
- Multi-language support — English only for now
- User authentication — local network deployment, no auth needed initially

## Context

**Clinical Background:**
Choledocholithiasis (CBD stones) affects 193 million patients globally with $6.2B/year US healthcare cost. Current ASGE guidelines achieve only 70-75% accuracy with 13-24% unnecessary ERCPs. This ML model (GBM) achieves 83% accuracy, 87% precision, AUC 0.90 — outperforming both ASGE (AUC 0.81) and ESGE (AUC 0.84) guidelines. The model prevents 85% of unnecessary ERCPs vs ASGE guidelines.

**Existing Assets:**
- Validated ML model with 13 features (GBM, scikit-learn): `docs/cbd app/Models/`
- Iterative imputer for missing value handling: `docs/cbd app/Models/iterative_imputer.pkl`
- Proof-of-concept Dash app with form-based input: `docs/cbd app/`
- DDW 2025 presentation with full clinical validation data: `docs/DDW 2025...pdf`
- Feature definitions and abbreviations: `docs/cbd app/assets/chosen_features_label.txt`
- Conda environment specification: `docs/environment.yml`
- Rudimentary chat-based prototype (Python UI, not to be reused): `docs/old-proof-of-concept/`

**Model Features (13 variables):**
1. Sex (required — cannot be imputed)
2. Age
3. Clinical cholangitis (Tokyo Guidelines)
4. Clinical pancreatitis
5. Clinical cholecystitis (Tokyo Guidelines 2018)
6. AST (U/L)
7. ALT (U/L)
8. Alkaline Phosphatase (U/L)
9. Total Bilirubin (mg/dL)
10. Abdominal Ultrasound performed? (yes/no)
11. CBD stone on Ultrasound (yes/no)
12. CBD stone on CT scan (yes/no)
13. Charlson Comorbidity Index

**Clinical Rules:**
- ASGE 2019: All patients with cholangitis should undergo ERCP
- Sex must be explicitly asked (cannot rely on imputation)
- Imaging findings (CBD stone on US/CT) should be explicitly asked even though model can impute

**Team:**
- Arpita Jajoo — Clinical lead, Gastroenterology, Johns Hopkins
- Khalid Husain — Developer/engineer
- Babak Moghadas — ML model development
- Venkata S. Akshintala — Senior author

## Constraints

- **Frontend stack**: React (Vite) + TypeScript — no Python UI frameworks (Dash/Streamlit)
- **Backend stack**: Python + FastAPI — serves ML model and orchestrates OpenAI API calls
- **LLM**: GPT-4o-mini via OpenAI API — API key stored server-side only
- **ML Model**: Existing scikit-learn GBM models (.pkl) — used as-is, no retraining
- **Deployment**: Local network, port 450 — public hosting deferred to later
- **Architecture**: LLM is orchestrator only, never decision-maker — model outputs are authoritative
- **YAML config**: Model features, types, ranges defined in YAML — LLM reads this to know what to extract

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| React+Vite+TS frontend over Dash | Python UI frameworks are limiting for chat+dashboard UX | — Pending |
| FastAPI backend over Flask | Modern async, auto OpenAPI docs, better for tool-calling patterns | — Pending |
| GPT-4o-mini over GPT-4o | Sufficient for structured extraction, lower cost | — Pending |
| LLM calls from Python backend | Keeps API key server-side, centralizes orchestration logic | — Pending |
| YAML schema for model features | LLM references YAML to know what to extract — decouples model from LLM prompts | — Pending |
| All 4 safeguards enabled | Clinical safety: no LLM overrides, input validation, extraction verification, injection defense | — Pending |
| De-identified data only | Avoids HIPAA complexity; clinicians enter parameters not PHI | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-06 after milestone v1.1 start*
