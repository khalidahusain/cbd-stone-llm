from backend.app.core.schema_loader import FeatureSchema
from backend.app.schemas.prediction import ValidationErrorDetail


class ValidationService:
    def __init__(self, schema: FeatureSchema):
        self.schema = schema

    def validate(self, features: dict) -> list[ValidationErrorDetail]:
        errors = []
        for name, value in features.items():
            if value is None:
                continue
            feature_def = self.schema.get_feature_by_name(name)
            if feature_def is None:
                errors.append(ValidationErrorDetail(
                    error="unknown_field",
                    field=name,
                    message=f"Unknown feature: {name}",
                ))
                continue

            if feature_def.type == "numeric" and feature_def.valid_range:
                if not isinstance(value, (int, float)):
                    errors.append(ValidationErrorDetail(
                        error="validation_error",
                        field=name,
                        message=f"{feature_def.name} must be a number",
                    ))
                elif value < feature_def.valid_range["min"] or value > feature_def.valid_range["max"]:
                    errors.append(ValidationErrorDetail(
                        error="validation_error",
                        field=name,
                        message=f"{feature_def.name} must be between {feature_def.valid_range['min']} and {feature_def.valid_range['max']} {feature_def.unit or ''}".rstrip(),
                    ))

            if feature_def.type == "categorical" and feature_def.allowed_values:
                if value not in feature_def.allowed_values:
                    errors.append(ValidationErrorDetail(
                        error="validation_error",
                        field=name,
                        message=f"{feature_def.name} must be one of: {', '.join(feature_def.allowed_values)}",
                    ))

            if feature_def.type == "boolean" and feature_def.encoding:
                allowed = list(feature_def.encoding.keys())
                if isinstance(value, str) and value not in allowed:
                    errors.append(ValidationErrorDetail(
                        error="validation_error",
                        field=name,
                        message=f"{feature_def.name} must be one of: {', '.join(allowed)}",
                    ))

        return errors
