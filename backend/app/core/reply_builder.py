from typing import Optional

from backend.app.core.schema_loader import FeatureSchema
from backend.app.schemas.extraction import ExtractionResult
from backend.app.schemas.prediction import PredictionResult, ValidationErrorDetail

# Fields that gate confirmation — must be collected before offering confirm
CONFIRMATION_GATE = ["sex", "age", "total_bilirubin"]

# Full priority ordering for post-prediction follow-ups (D-11)
FOLLOW_UP_PRIORITY = [
    "sex", "age", "total_bilirubin",
    "abdominal_ultrasound_performed", "cbd_stone_on_ultrasound", "cbd_stone_on_ct",
]

CATEGORY_LABELS = {
    "demographics": "Demographics",
    "labs": "Labs",
    "imaging": "Imaging",
    "clinical_conditions": "Clinical Conditions",
}


class ReplyBuilder:
    def __init__(self, schema: FeatureSchema):
        self.schema = schema

    def build_welcome_reply(self) -> str:
        return (
            "I'm ready to help assess CBD stone risk. "
            "Please describe the patient's clinical presentation — "
            "include any labs, imaging, and clinical findings you have."
        )

    def build_collecting_reply(
        self, extraction: ExtractionResult, session_features: dict
    ) -> tuple[str, bool]:
        """Build reply during collecting phase.

        Returns (reply_text, ready_for_confirmation).
        """
        parts = []

        new_features = extraction.to_feature_dict()
        if new_features:
            lines = ["Got it:\n"]
            for name, value in new_features.items():
                feat = self.schema.get_feature_by_name(name)
                display = feat.display_name or name if feat else name
                unit = f" {feat.unit}" if feat and feat.unit else ""
                lines.append(f"- {display}: {value}{unit}")
            parts.append("\n".join(lines))

        if extraction.ambiguous:
            parts.append(f"Ambiguous (needs clarification): {', '.join(extraction.ambiguous)}")

        # Confirmation gate: sex, age, bilirubin must be present before offering confirm
        missing_gate = [
            name for name in CONFIRMATION_GATE
            if name not in session_features or session_features[name] is None
        ]

        if missing_gate:
            next_field = missing_gate[0]
            feat = self.schema.get_feature_by_name(next_field)
            question = (
                feat.follow_up_question
                if feat and feat.follow_up_question
                else f"Do you have the patient's {next_field}?"
            )
            parts.append(question)
            return "\n\n".join(parts), False
        else:
            return "\n\n".join(parts), True

    def build_confirmation_reply(self, session_features: dict) -> str:
        """Build confirmation summary grouped by category."""
        provided = {}  # category -> list of formatted strings
        imputed = []   # display names of None features

        for feat in self.schema.features:
            value = session_features.get(feat.name)
            display = feat.display_name or feat.name
            category = feat.category or "other"
            if value is not None:
                unit = f" {feat.unit}" if feat.unit else ""
                provided.setdefault(category, []).append(f"- **{display}:** {value}{unit}")
            else:
                imputed.append(display)

        parts = ["Here is what I've recorded. Please confirm this is correct:\n"]
        for cat_key, label in CATEGORY_LABELS.items():
            items = provided.get(cat_key, [])
            if items:
                parts.append(f"**{label}**")
                parts.extend(items)

        if imputed:
            parts.append(f"\nThe model will estimate: {', '.join(imputed)}.")

        parts.append("\nType **confirm** to run the prediction, or provide corrections.")
        return "\n".join(parts)

    def build_confirmed_reply(self, prediction: PredictionResult, session_features: dict) -> str:
        """Build reply after prediction runs."""
        parts = [
            f"Based on the provided information, the estimated probability of a CBD stone is "
            f"**{prediction.probability}%** ({prediction.risk_tier.capitalize()} risk). "
            f"Recommended next step: **{prediction.recommended_intervention}**."
        ]

        # D-11: next-best-variable prompt from priority list
        missing_priority = [
            name for name in FOLLOW_UP_PRIORITY
            if name not in session_features or session_features[name] is None
        ]
        if missing_priority:
            feat = self.schema.get_feature_by_name(missing_priority[0])
            if feat and feat.follow_up_question:
                q = feat.follow_up_question
                parts.append(f"To refine this prediction further, {q[0].lower()}{q[1:]}")

        return "\n\n".join(parts)

    def build_update_reply(
        self, prediction: PredictionResult, updated_fields: list[str], session_features: dict
    ) -> str:
        """Build reply when prediction updates iteratively."""
        display_names = []
        for name in updated_fields:
            feat = self.schema.get_feature_by_name(name)
            display_names.append(feat.display_name or name if feat else name)
        fields_str = ", ".join(display_names)

        parts = [
            f"Updated {fields_str}. "
            f"The estimated probability of a CBD stone is now "
            f"**{prediction.probability}%** ({prediction.risk_tier.capitalize()} risk). "
            f"Recommended next step: **{prediction.recommended_intervention}**."
        ]

        missing_priority = [
            name for name in FOLLOW_UP_PRIORITY
            if name not in session_features or session_features[name] is None
        ]
        if missing_priority:
            feat = self.schema.get_feature_by_name(missing_priority[0])
            if feat and feat.follow_up_question:
                q = feat.follow_up_question
                parts.append(f"To refine this prediction further, {q[0].lower()}{q[1:]}")

        return "\n\n".join(parts)

    def build_validation_error_reply(self, errors: list[ValidationErrorDetail]) -> str:
        """Build reply when extracted values fail validation."""
        parts = []
        for err in errors:
            parts.append(f"{err.message}. Could you double-check?")
        return "\n\n".join(parts)

    def build_insufficient_info_reply(self, missing: list[str]) -> str:
        """Build reply when required fields still missing."""
        display_names = []
        for name in missing:
            feat = self.schema.get_feature_by_name(name)
            display_names.append(feat.display_name or name if feat else name)
        return f"Cannot run the model yet -- still missing required fields: {', '.join(display_names)}."
