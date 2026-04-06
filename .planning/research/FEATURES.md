# Feature Landscape

**Domain:** LLM-powered clinical decision support (CBD stone risk stratification)
**Researched:** 2026-04-05

---

## Table Stakes

Features clinicians expect. Missing any of these and the system feels broken, incomplete, or unsafe for clinical use.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Natural language free-text input | Clinicians narrate cases; forcing form entry breaks workflow and eliminates the core value proposition | Low | Single textarea or chat input field is sufficient — the LLM does the heavy lifting |
| Structured extraction confirmation | Clinicians will not trust output they cannot verify; extraction errors in clinical settings are high-stakes | Medium | After extraction, display a summary of what was extracted and ask clinician to confirm before running the model. This is the human-in-the-loop checkpoint. |
| Follow-up questioning for missing required variables | Sex cannot be imputed; imaging findings should be explicit — system must proactively ask when absent | Medium | Must ask for missing required variables in plain language. Must not ask for fields already captured. Must not ask all at once — prioritize by clinical importance. |
| Input range validation with user feedback | Clinicians expect the system to catch obvious errors (age=500, bilirubin=-3) rather than silently producing wrong output | Low | Reject out-of-range values with a clear message explaining what was wrong and what the valid range is. This is table stakes for safety. |
| Probability output as a number | Clinicians need the raw prediction probability (e.g., "73% probability of CBD stone") — a score without context is not actionable | Low | Display as a percentage, not a label. The label (risk tier) augments it, does not replace it. |
| Risk stratification label | ASGE/ESGE tiers (Low/Intermediate/High) are the clinical vocabulary; clinicians think in these categories | Low | Must map probability to the correct tier with the correct threshold (CCY+/-IOC <10%, MRCP 10-44%, EUS 44-90%, ERCP >90%). Thresholds are already defined. |
| Recommended next intervention | Clinicians want to know what to DO, not just what the probability is | Low | One clear recommendation per tier: "Proceed with cholecystectomy +/- IOC", "Consider MRCP", "EUS recommended", "ERCP indicated". |
| Management guidance bar visualization | The 0-100% visual bar with labeled intervention zones is a validated representation clinicians already know from the existing app | Medium | This is the core visual artifact. Color-coded zones (green/yellow/red equivalent) with a needle or marker at the predicted probability. |
| Iterative updates as conversation progresses | Clinical cases unfold — a clinician may add a new lab value mid-conversation; the prediction must update | Medium | Each confirmed extraction triggers a new model call. Dashboard updates in place without resetting the conversation. |
| Interpretation guidance panel | Clinical AI output requires explanation; "why" matters as much as "what" — especially for a model that differs from ASGE | Low-Medium | Always-visible on desktop. Show which features drove the prediction and a brief plain-language explanation. Must be present — not behind a modal. |
| Mobile-responsive layout | Clinicians are often on phones or tablets at the point of care | Medium | Chat-first on mobile; dashboard below or collapsible. Cost table behind expand control on mobile. |
| Prompt injection defense | LLM medical advice systems are vulnerable to injection (94.4% success rate in studies); clinical output integrity depends on it | Medium | System prompts must be structured so user input is isolated from instructions. Never trust user content as system-level input. This is a safety requirement, not a nice-to-have. |
| LLM cannot override model output | The core trust guarantee of the system — the GBM is the source of truth | Low-Medium (architectural) | Enforce at the architecture level: LLM receives model output as input, never generates a probability itself. This must be documented as a design constraint, not just a prompt instruction. |

---

## Differentiators

Features that distinguish this system from generic CDSS or simple form-based tools. Not expected by default, but meaningfully improve value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cost-weighted intervention table | Probability-weighted cost estimates across IOC/MRCP/ERCP/EUS make the recommendation economically concrete — aids real-world decision-making | Medium | Show expected cost per option given current probability. Use pre-computed cost weights from the existing model assets. Expandable on mobile. |
| Cholangitis fast-path | ASGE 2019 mandates ERCP for all cholangitis — detecting this and surfacing a special-case alert before running the model short-circuits unnecessary computation and respects clinical guidelines | Low | If Tokyo criteria cholangitis = yes, display an immediate banner: "Tokyo-criteria cholangitis detected. ERCP is indicated per ASGE 2019 guidelines." Still run the model but lead with the guideline override. |
| Anatomy reference panel | Clinicians who are not gastroenterology specialists (e.g., ER physicians, surgeons) benefit from an accessible anatomy diagram and abbreviation reference | Low | Already exists as an asset. Always-visible on desktop sidebar or accessible via a persistent icon. |
| Explicit missing-variable imputation transparency | The model uses iterative imputation for missing values — showing the clinician which values were imputed vs. directly provided builds trust | Medium | Mark imputed values differently in the extraction summary (e.g., "(estimated)" badge). Let clinician override any imputed value. |
| Confidence-aware extraction with "uncertain" flagging | When the LLM is unsure about an extracted value (e.g., ambiguous narrative), flag it rather than silently guess | Medium | Include a confidence tier in the LLM's JSON output. Display uncertain extractions with a visual flag and require explicit clinician confirmation before accepting them. |
| Abbreviated case summary | After extraction and prediction, generate a 2-3 sentence plain-language summary of the case as the LLM understood it — allows clinicians to spot errors at a glance | Low (given LLM already in pipeline) | "42-year-old female with right upper quadrant pain, elevated bilirubin (4.2 mg/dL), and CBD stone visible on ultrasound. Charlson score of 2. Probability of CBD stone: 81%." |
| Persistent conversation state within a session | Clinicians may leave and return to a case; losing conversation state mid-assessment is frustrating | Medium | Session-scoped (browser tab) persistence is sufficient for v1 — full server-side session management is higher complexity and not necessary. |

---

## Anti-Features

Features to explicitly NOT build. Each carries a concrete reason — the complexity or harm outweighs the benefit at this stage.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| EHR integration (Epic, Cerner pull) | High integration complexity, HL7/FHIR compliance surface, auth/credentialing requirements. Not needed for validated de-identified workflow. | Let clinicians enter values manually from the chart. This is explicitly Out of Scope per PROJECT.md. |
| PHI handling and real names | HIPAA surface area is enormous. System is designed for de-identified clinical parameters, not patient records. | Clinicians enter parameters, not patient identifiers. Documented constraint. |
| Autonomous clinical decision-making | The LLM generating a diagnosis or recommendation without model backing is the #1 liability risk. Studies show LLM hallucination rates of 15-40% in clinical tasks. | LLM is orchestrator-only. Model outputs are authoritative. Enforce architecturally. |
| Alert interruptions / pop-up warnings | Alert fatigue is the #1 reason CDSS systems are bypassed. Only 7.3% of CPOE alerts are clinically appropriate. Each additional alert drops acceptance by 30%. | Surface all information inline and passively. No modal dialogs interrupting the workflow. No dismissible alerts that appear spontaneously. |
| User authentication and role-based access | Not needed for local-network deployment. Adding auth adds login friction, session management complexity, and token refresh handling with no clinical benefit at this stage. | Local network deployment behind institutional network. Deferred to later milestone. |
| Multi-language support | English-only clinical staff at target site. Adds translation complexity and requires clinical validation of translated terminology. | English only. Explicit Out of Scope per PROJECT.md. |
| Streaming token-by-token LLM output | Real-time streaming feels "alive" but provides no clinical value for a structured extraction task and adds WebSocket complexity. | Return full JSON extraction response. Show a loading indicator while extraction runs. |
| Diagnosis generation (LLM explains what the patient has) | LLM explaining clinical pathology goes beyond extraction into diagnosis, which requires FDA-level clinical validation. Scope creep risk is severe. | Limit LLM output to: "Here is what I extracted — please confirm." Interpretation guidance is model-driven, not LLM-generated. |
| Probability calibration display (confidence intervals) | CI visualization adds cognitive load. Clinicians need a clear signal, not uncertainty quantification. The model AUC (0.90) speaks for itself. | Show probability and tier. Let the tier and intervention recommendation carry the decision weight. |
| Automatic case saving / database logging | Server-side persistence of clinical inputs, even de-identified, raises data governance questions disproportionate to the benefit at v1 local deployment. | Session-only state. No persistence to disk. |
| Model retraining or feedback loop UI | Collecting labeled feedback sounds useful but requires IRB considerations, data governance, and a retraining pipeline. None of those exist. | Use the model as-is. Feedback collection is a future research milestone, not a product feature. |

---

## Feature Dependencies

```
Natural language input
  --> LLM extraction pipeline
      --> Input validation (range checking)
          --> Extraction confirmation display
              --> Model inference call
                  --> Risk bar visualization
                  --> Probability display + risk tier
                  --> Recommended intervention
                  --> Cost table
                  --> Interpretation guidance
                  --> Case summary

LLM extraction pipeline
  --> YAML feature schema (defines what to extract, types, ranges)
  --> Follow-up questioning (triggers when required fields are missing)

Cholangitis fast-path
  --> Runs in parallel with normal extraction path
  --> Does NOT block model inference

Imputation transparency
  --> Depends on model returning which features were imputed
  --> Depends on extraction confirmation display

Confidence-aware extraction
  --> Depends on LLM returning structured JSON with confidence field
  --> Depends on extraction confirmation display (uncertain fields flagged)

Mobile layout
  --> Depends on base dashboard components existing first
  --> Cost table expand/collapse is a mobile-specific concern
```

---

## MVP Recommendation

For the first working milestone, prioritize:

1. **Natural language input + LLM extraction** — the core differentiator. Without this, the system is just the Dash app.
2. **Extraction confirmation with range validation** — required before model can be called safely.
3. **Follow-up questioning for sex and imaging** — sex cannot be imputed; these must be asked.
4. **Model inference + probability + risk tier + recommended intervention** — the minimum viable output.
5. **Management guidance bar** — already exists as an asset; render it.
6. **Prompt injection defense + LLM architectural isolation** — must ship with the first working version, not added later. Security and clinical safety cannot be retrofitted.

Defer to subsequent iterations:
- **Cholangitis fast-path** — clinically important but the model will still run correctly without it; add immediately after MVP
- **Cost table** — assets exist; add after core dashboard is working
- **Anatomy reference panel** — low effort once dashboard is in place
- **Imputation transparency** — requires backend support; add in second pass
- **Confidence-aware extraction** — requires prompt engineering iteration; add after baseline extraction is stable
- **Mobile layout** — desktop-first; mobile pass after desktop is validated

---

## Sources

- [Evaluating LLM workflows in clinical decision support (Nature npj Digital Medicine, 2025)](https://www.nature.com/articles/s41746-025-01684-1) — MEDIUM confidence
- [Vulnerability of LLMs to Prompt Injection in Medical Advice (JAMA Network Open)](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2842987) — HIGH confidence, peer-reviewed
- [OWASP Top 10 for LLM Applications 2025 — Prompt Injection #1](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — HIGH confidence, authoritative
- [Multi-Agent LLM Defense Pipeline Against Prompt Injection (arXiv 2025)](https://arxiv.org/html/2509.14285v4) — MEDIUM confidence
- [Understanding Alert Fatigue in Primary Care (JMIR 2025)](https://www.jmir.org/2025/1/e62763) — HIGH confidence, peer-reviewed
- [Addressing Alert Fatigue with Passive CDSS (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10830237/) — HIGH confidence, peer-reviewed
- [HealthQ: LLM questioning capabilities in healthcare conversations (ScienceDirect 2025)](https://www.sciencedirect.com/article/pii/S2352648325000315) — MEDIUM confidence
- [LLMs Get Lost In Multi-Turn Conversation (arXiv 2025)](https://arxiv.org/pdf/2505.06120) — MEDIUM confidence
- [For trustworthy AI, keep the human in the loop (Nature Medicine, 2025)](https://www.nature.com/articles/s41591-025-04033-7) — HIGH confidence, peer-reviewed
- [Medical Hallucination in Foundation Models (medRxiv preprint, 2025)](https://www.medrxiv.org/content/10.1101/2025.02.28.25323115v2.full.pdf) — MEDIUM confidence (preprint)
- [Mitigating Hallucinations in LLMs for Healthcare (IEEE JBHI, 2025)](https://www.embs.org/jbhi/wp-content/uploads/sites/18/2025/11/Mitigating-Hallucinations-in-Large-Language-Models-for-Healthcare-Towards-Trustworthy-Medical-AI.pdf) — HIGH confidence, peer-reviewed
- [An overview of CDSS: benefits, risks, and strategies for success (npj Digital Medicine)](https://www.nature.com/articles/s41746-020-0221-y) — HIGH confidence, peer-reviewed
- [Harnessing CDSS: challenges and opportunities (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10685930/) — HIGH confidence, peer-reviewed
- [LLM Structured Extraction from Unstructured EHR (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11751965/) — HIGH confidence, peer-reviewed
- [Clinician typology for AI chatbot use in clinical decision-making (npj Digital Medicine, 2025)](https://www.nature.com/articles/s41746-025-02184-y) — HIGH confidence, peer-reviewed
