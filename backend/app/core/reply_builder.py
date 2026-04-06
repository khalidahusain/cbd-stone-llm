from typing import Optional

from backend.app.core.schema_loader import FeatureSchema
from backend.app.schemas.extraction import ExtractionResult
from backend.app.schemas.prediction import PredictionResult, ValidationErrorDetail

FOLLOW_UP_PRIORITY = ["sex", "age", "total_bilirubin"]

FOLLOW_UP_QUESTIONS = {
    "sex": "What is the patient's biological sex (male or female)?",
    "age": "How old is the patient?",
    "total_bilirubin": "What is the patient's total bilirubin level (mg/dL)? This significantly improves prediction accuracy.",
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
            extracted_items = []
            for name, value in new_features.items():
                feat = self.schema.get_feature_by_name(name)
                unit = f" {feat.unit}" if feat and feat.unit else ""
                extracted_items.append(f"**{name}**: {value}{unit}")
            parts.append("Extracted: " + ", ".join(extracted_items))

        if extraction.ambiguous:
            parts.append(f"Ambiguous (needs clarification): {', '.join(extraction.ambiguous)}")

        missing_priority = [
            name for name in FOLLOW_UP_PRIORITY
            if name not in session_features or session_features[name] is None
        ]

        if missing_priority:
            next_field = missing_priority[0]
            parts.append(FOLLOW_UP_QUESTIONS[next_field])
            return "\n\n".join(parts), False
        else:
            return "\n\n".join(parts), True

    def build_confirmation_reply(self, session_features: dict) -> str:
        """Build confirmation summary."""
        parts = ["Here is what I've extracted. Please confirm this is correct:\n"]

        for feat in self.schema.features:
            value = session_features.get(feat.name)
            if value is not None:
                unit = f" {feat.unit}" if feat.unit else ""
                parts.append(f"- **{feat.name}**: {value}{unit}")
            else:
                parts.append(f"- **{feat.name}**: _(will be estimated by the model)_")

        parts.append("\nType **confirm** to run the prediction, or provide corrections.")
        return "\n".join(parts)

    def build_confirmed_reply(self, prediction: PredictionResult) -> str:
        """Build reply after prediction runs."""
        return (
            f"Prediction complete. "
            f"The probability of a CBD stone is **{prediction.probability}%** "
            f"({prediction.risk_tier} risk). "
            f"Recommended next step: **{prediction.recommended_intervention}**.\n\n"
            f"You can continue providing additional clinical information to refine the prediction."
        )

    def build_update_reply(self, prediction: PredictionResult, updated_fields: list[str]) -> str:
        """Build reply when prediction updates iteratively."""
        fields_str = ", ".join(updated_fields)
        return (
            f"Updated {fields_str}. Prediction recalculated: "
            f"**{prediction.probability}%** ({prediction.risk_tier} risk), "
            f"recommended: **{prediction.recommended_intervention}**."
        )

    def build_validation_error_reply(self, errors: list[ValidationErrorDetail]) -> str:
        """Build reply when extracted values fail validation."""
        parts = ["Some extracted values are outside valid ranges:\n"]
        for err in errors:
            parts.append(f"- **{err.field}**: {err.message}")
        parts.append("\nCould you double-check these values?")
        return "\n".join(parts)

    def build_insufficient_info_reply(self, missing: list[str]) -> str:
        """Build reply when required fields still missing."""
        return f"Cannot run the model yet — still missing required fields: {', '.join(missing)}."
