---
phase: 06-reply-builder-polish
reviewed: 2026-04-06T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - backend/app/core/reply_builder.py
  - backend/app/core/schema_loader.py
  - backend/app/schemas/prediction.py
  - backend/app/services/conversation.py
  - backend/app/services/validation.py
  - backend/config/features.yaml
  - backend/tests/test_conversation.py
  - backend/tests/test_reply_builder.py
  - backend/tests/test_schema_loader.py
findings:
  critical: 0
  warning: 5
  info: 4
  total: 9
status: issues_found
---

# Phase 06: Code Review Report

**Reviewed:** 2026-04-06T00:00:00Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

The phase-06 reply-builder-polish codebase is generally well-structured. The `ReplyBuilder`, `SchemaLoader`, `ValidationService`, and `ConversationService` are cleanly separated, the YAML-driven schema is a solid coupling point, and the test suite covers the main conversation paths. No security vulnerabilities or data-loss risks were found.

Five warnings were found. The most impactful is a boundary-gap in `get_risk_tier` where probability exactly equal to 100 falls off all tier ranges and silently falls back to the last tier instead of matching `very_high` by its definition. Three additional warnings cover logic gaps: boolean values stored as Python `bool` in `session.extracted_features` after confirmation bypass the `ValidationService` type check (stored as `True`/`False` while validators expect `"YES"`/`"NO"`), an `awaiting_confirmation` non-keyword turn that re-extracts can reach `build_collecting_reply` with a stale `ready=True` result that immediately re-enters confirmation without user seeing the injected data, and the `SchemaLoader` makes no distinction between a missing YAML key that has a schema-level default and one that should be mandatory, silently constructing `FeatureDefinition` with empty `description`. Four info items cover minor code quality points.

---

## Warnings

### WR-01: `get_risk_tier` boundary gap — probability = 100.0 never matches any tier

**File:** `backend/app/core/schema_loader.py:68-72`

**Issue:** The very-high tier is defined as `min: 90, max: 100` and the loop condition is `tier.min <= probability < tier.max`. When `probability == 100.0` (a valid boundary value the ML model could theoretically return), no tier matches the `< 100` condition. The fallback `return self.risk_tiers[-1]` happens to return the correct tier, but it is a silent fallback that will silently break if tier order ever changes or if a tier is appended after `very_high`.

**Fix:**
```python
def get_risk_tier(self, probability: float) -> RiskTier:
    for tier in self.risk_tiers:
        if tier.min <= probability <= tier.max:  # inclusive upper bound
            return tier
    # Explicit guard — never rely on list-ordering coincidence
    raise ValueError(f"Probability {probability} is outside all defined risk tiers (0–100).")
```

Alternatively, define `max: 100.01` in the YAML to absorb the boundary, but the code fix is more robust.

---

### WR-02: Boolean fields stored as Python `bool` in session state bypass validation type check

**File:** `backend/app/services/conversation.py:91-95` and `backend/app/services/validation.py:50-58`

**Issue:** `ExtractionResult.to_feature_dict()` converts bool fields to `"YES"` / `"NO"` strings before they enter `ValidationService`. However, the merge loop at `conversation.py:91-95` stores values directly from `new_features` — which at that point are already strings — into `session.extracted_features`. That path is fine on first entry.

The problem is in `_handle_post_confirmation` (line 140): `self.inference.predict(session.extracted_features)` runs directly without going through `ValidationService` again, meaning any value that was bypassed — e.g., if a future code path ever inserts raw bool values directly into `session.extracted_features` — will silently reach the inference layer. More concretely: the test helper `_all_priority_extraction` creates `ExtractionResult` with `abdominal_ultrasound_performed=True` (Python bool). `to_feature_dict()` converts this to `"YES"` correctly, but the session dict test fixture at `test_reply_builder.py:100-103` stores `"YES"` / `"NO"` as strings. Any caller that bypasses `to_feature_dict()` and writes raw booleans will pass `ValidationService`'s boolean check (line 52: `isinstance(value, str)`) silently because a Python `bool` is not a `str` and the check is only applied to strings — so it won't error, but also won't catch the wrong type.

**Fix:** Add a type guard in `ValidationService.validate` for boolean fields that also catches native Python bools:
```python
if feature_def.type == "boolean" and feature_def.encoding:
    allowed = list(feature_def.encoding.keys())
    if not isinstance(value, str) or value not in allowed:
        errors.append(ValidationErrorDetail(
            error="validation_error",
            field=name,
            message=f"{display} must be one of: {', '.join(allowed)} (got {type(value).__name__}: {value!r})",
            provided_value=value,
        ))
```

---

### WR-03: Non-keyword turn during `awaiting_confirmation` can silently skip back to confirmation without showing newly added data

**File:** `backend/app/services/conversation.py:58-62` and `101-108`

**Issue:** When the session is in `awaiting_confirmation` and the user sends a non-keyword message (e.g., a correction), the code at line 61 immediately resets `session.conversation_phase = "collecting"` before extraction happens. Then at line 101, `build_collecting_reply` is called. If all 6 priority fields are already present in `session_features` (they were — that's why confirmation was triggered), `ready` is immediately `True` and line 107 sends the reply back to `awaiting_confirmation`, calling `build_confirmation_reply` again. The new extraction data from the correction is merged into `session_features` (lines 91-95) and shown in the confirmation, but the "Got it:" acknowledgment from `build_collecting_reply` (which is the `reply` at line 101) is discarded — line 108 overwrites it with `build_confirmation_reply`. The user sees the updated confirmation but no acknowledgment that their correction was heard.

This is a UX logic issue that could be confusing in a clinical setting where feedback is critical.

**Fix:** When `ready` is `True` and a non-keyword turn came in during `awaiting_confirmation`, prepend the "Got it:" acknowledgment to the confirmation reply:
```python
if ready:
    session.conversation_phase = "awaiting_confirmation"
    confirmation = self.replies.build_confirmation_reply(session.extracted_features)
    # If we had extracted new data, acknowledge it before showing updated confirmation
    if new_features:
        reply = reply + "\n\n" + confirmation
    else:
        reply = confirmation
```

---

### WR-04: `SchemaLoader` silently accepts YAML features with empty `description`

**File:** `backend/app/core/schema_loader.py:94-95`

**Issue:** `description=feat_data.get("description", "")` silently accepts a missing `description` key by defaulting to `""`. The `description` field is the primary documentation string used to guide the LLM extractor. A feature with an empty description will cause the LLM extraction prompt to have blank guidance for that field, which can lead to incorrect or missing extractions in a clinical context. No warning is raised at load time.

**Fix:**
```python
description = feat_data.get("description", "")
if not description:
    import warnings
    warnings.warn(
        f"Feature '{feat_data['name']}' has no description — LLM extraction quality may degrade.",
        UserWarning,
        stacklevel=2,
    )
```

Or log at WARNING level using the application logger rather than `warnings.warn`, since this runs at startup.

---

### WR-05: `build_confirmation_reply` silently drops features whose `category` is not in `CATEGORY_LABELS`

**File:** `backend/app/core/reply_builder.py:98-108`

**Issue:** The method iterates `CATEGORY_LABELS` (which contains four hard-coded categories: `demographics`, `labs`, `imaging`, `clinical_conditions`) to build the confirmation summary. If a feature's `category` is absent from `CATEGORY_LABELS` — for example, a future YAML feature assigned `category: other` — its value is stored in `provided` under the key `"other"` but is never rendered in the output. The clinician would see no acknowledgment of that field, but the model would still receive it. This is a silent omission in a clinical safety context.

The current YAML has no such feature, but `CATEGORY_LABELS` is not validated against the schema at startup.

**Fix:**
```python
# After building provided dict, check for unrendered categories
rendered_categories = set(CATEGORY_LABELS.keys())
for cat_key, items in provided.items():
    if cat_key not in rendered_categories and items:
        # Fallback: render under "Other"
        parts.append("**Other**")
        parts.extend(items)
```

Or add an assertion at startup that all YAML feature categories are present in `CATEGORY_LABELS`.

---

## Info

### IN-01: `FOLLOW_UP_PRIORITY` list is duplicated across two modules

**File:** `backend/app/core/reply_builder.py:7-10` and `backend/app/services/conversation.py:152-155`

**Issue:** The priority-field logic in `_build_response` (conversation.py:152-154) re-implements the same "find fields missing from `FOLLOW_UP_PRIORITY`" pattern that exists in `reply_builder.py`. `FOLLOW_UP_PRIORITY` is imported from `reply_builder` into `conversation.py` (line 5), but the list-comprehension to compute `missing` is copy-pasted. If the priority list or the missing-check logic changes, it must be updated in two places.

**Fix:** Extract a helper method on `ReplyBuilder` or a standalone function:
```python
# In reply_builder.py
def get_missing_priority(self, session_features: dict) -> list[str]:
    return [
        name for name in FOLLOW_UP_PRIORITY
        if name not in session_features or session_features[name] is None
    ]
```
Then call `self.replies.get_missing_priority(session.extracted_features)` in `conversation.py`.

---

### IN-02: `get_feature_by_name` and `get_feature_by_column` are O(n) linear scans

**File:** `backend/app/core/schema_loader.py:56-66`

**Issue:** Both lookup methods iterate the full feature list on every call. With 13 features this is negligible, but these methods are called on every turn of every conversation (multiple times per `build_collecting_reply`, `build_confirmation_reply`, etc.). A lookup dict would be more correct and slightly more legible.

**Fix:**
```python
# In FeatureSchema.__post_init__ or SchemaLoader.load:
self._by_name = {f.name: f for f in self.features}
self._by_column = {f.model_column: f for f in self.features}

def get_feature_by_name(self, name: str) -> Optional[FeatureDefinition]:
    return self._by_name.get(name)
```

Note: `FeatureSchema` is a `@dataclass`, so use `__post_init__` or convert to a class with an `__init__`.

---

### IN-03: Magic string `"other"` used as default category in `build_confirmation_reply`

**File:** `backend/app/core/reply_builder.py:91`

**Issue:** `category = feat.category or "other"` uses a bare string literal as the fallback category key. This same string is not defined in `CATEGORY_LABELS`, so it quietly feeds the WR-05 bug described above. It should be a named constant.

**Fix:**
```python
CATEGORY_FALLBACK = "other"

# in build_confirmation_reply:
category = feat.category or CATEGORY_FALLBACK
```

---

### IN-04: `test_conversation.py` `test_full_multi_turn_scenario` does not assert probability changes after AST update

**File:** `backend/tests/test_conversation.py:235-266`

**Issue:** The test captures `prob1 = r3.prediction.probability` but never asserts that `r4.prediction.probability` differs from `prob1`. The intent of the test ("add AST → auto-update") implies the probability should change, but this is left unverified. A regression that broke inference re-computation would pass the test as written.

**Fix:**
```python
# After r4 assertions:
assert r4.prediction.probability != prob1, "Prediction should change after adding AST"
```

Note: This assertion is probabilistic — AST at 120 U/L could theoretically produce no change in this model — but in practice for this dataset it will always shift. If the team prefers a model-agnostic test, assert that the inference service was called a second time using a spy/mock instead.

---

_Reviewed: 2026-04-06T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
