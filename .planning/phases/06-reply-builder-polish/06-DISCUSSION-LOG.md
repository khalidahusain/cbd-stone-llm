# Phase 6: Reply Builder Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md -- this log preserves the alternatives considered.

**Date:** 2026-04-06
**Phase:** 06-reply-builder-polish
**Areas discussed:** Display name source, Confirmation grouping, Follow-up questions, Message tone

---

## Display Name Source

| Option | Description | Selected |
|--------|-------------|----------|
| Add display_name to YAML | Add a new display_name field to each feature in features.yaml. Single source of truth. | :heavy_check_mark: |
| Mapping dict in reply_builder.py | A Python dict mapping snake_case names to display names. Splits source of truth. | |
| Derive from model_column | Reuse existing model_column values. Some are abbreviations. | |

**User's choice:** Add display_name to YAML
**Notes:** None

---

## Confirmation Grouping - Category Source

| Option | Description | Selected |
|--------|-------------|----------|
| Add category to YAML | Add a category field to each feature in features.yaml. Keeps grouping with feature definitions. | :heavy_check_mark: |
| Hardcode in reply_builder.py | Define category mappings as a Python dict. Keeps YAML simple. | |
| You decide | Let Claude pick the best approach. | |

**User's choice:** Add category to YAML
**Notes:** None

## Confirmation Grouping - Imputation Summary

| Option | Description | Selected |
|--------|-------------|----------|
| Count-based | "The model will estimate 7 remaining values." Simple, no clutter. | |
| Brief list of imputed names | "The model will estimate ALT, ALP, cholangitis, and 6 others." | |
| No mention | Just show provided values. Don't mention imputation. | |

**User's choice:** Brief list of imputed names
**Notes:** User chose to list ALL imputed field names with no truncation (not the "and N others" variant).

## Confirmation Grouping - Truncation

| Option | Description | Selected |
|--------|-------------|----------|
| 3 names then truncate | Show up to 3 imputed field names, then "and N others". | |
| All names, no truncation | List every imputed field name. | :heavy_check_mark: |
| You decide | Let Claude pick a reasonable threshold. | |

**User's choice:** All names, no truncation
**Notes:** Full visibility into imputed fields preferred.

---

## Follow-up Questions - Generation Method

| Option | Description | Selected |
|--------|-------------|----------|
| Add follow_up_question to YAML | Each feature gets a follow_up_question field with a natural question. Static but consistent. | :heavy_check_mark: |
| LLM-generated follow-ups | Let the LLM dynamically generate conversational follow-up questions. | |
| Template with display_name | Auto-generate from template like "Do you have the patient's {display_name}?" | |

**User's choice:** Add follow_up_question to YAML
**Notes:** None

## Follow-up Questions - Priority Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Keep priority subset | Only ask about clinically important missing fields (sex, age, bilirubin, imaging). Others imputed silently. | :heavy_check_mark: |
| Ask about all missing fields | Systematically ask about every missing field one at a time. | |
| You decide | Let Claude determine the right priority list. | |

**User's choice:** Keep priority subset, expanded to include imaging fields
**Notes:** Priority list expands to: sex, age, total_bilirubin, abdominal_ultrasound_performed, cbd_stone_on_ultrasound, cbd_stone_on_ct.

---

## Message Tone - Extraction Feedback

| Option | Description | Selected |
|--------|-------------|----------|
| Concise clinical | Brief and professional. "Got it: Male, 50 years old, AST 1000 U/L." | :heavy_check_mark: |
| Warm professional | Slightly warmer. "Thank you. I've noted the patient is a 50-year-old male..." | |
| Minimal | Ultra-terse. "Male, 50 y/o. AST 1000, T.Bili 3.2." | |

**User's choice:** Concise clinical
**Notes:** User specified: use structured vertical list format (one variable per line as bullet points), not compact sentences. Prioritize readability and scannability. Format: "Got it:\n\n- Sex: Male\n- Age: 50\n- Total Bilirubin: 3.2 mg/dL"

## Message Tone - Prediction Result

| Option | Description | Selected |
|--------|-------------|----------|
| Natural risk explanation | Lead with probability and risk tier, then recommended action. | :heavy_check_mark: |
| Current format is fine | Existing format is clear enough -- just fix field names. | |
| You decide | Let Claude craft the prediction message. | |

**User's choice:** Natural risk explanation
**Notes:** User specified: replace generic "You can continue providing additional clinical information" with a targeted next-best-variable prompt using priority list and YAML follow_up_question. If no priority variables remain, omit the line entirely.

---

## Claude's Discretion

- Exact wording of imputation summary line
- Exact wording of prediction result message (within the decided pattern)
- Order of category headings in confirmation summary

## Deferred Ideas

None -- discussion stayed within phase scope
