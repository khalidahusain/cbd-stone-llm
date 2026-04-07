import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FeatureDefinition:
    name: str
    model_column: str
    type: str
    required: bool
    description: str
    encoding: dict[str, int] = field(default_factory=dict)
    valid_range: Optional[dict] = None
    allowed_values: Optional[list] = None
    unit: Optional[str] = None
    strongly_recommended: bool = False
    triggers_fast_path: bool = False
    inference_prohibited: bool = False
    display_name: Optional[str] = None
    category: Optional[str] = None
    follow_up_question: Optional[str] = None


@dataclass
class RiskTier:
    name: str
    label: str
    min: float
    max: float
    intervention: str


@dataclass
class CostConfig:
    intervention: str
    base_cost: float
    variable_cost: float


@dataclass
class FeatureSchema:
    features: list[FeatureDefinition]
    risk_tiers: list[RiskTier]
    cost_configs: dict[str, CostConfig]
    cholangitis_message: str
    version: str

    def get_model_columns(self) -> list[str]:
        return [f.model_column for f in self.features]

    def get_required_features(self) -> list[str]:
        return [f.name for f in self.features if f.required]

    def get_feature_by_name(self, name: str) -> Optional[FeatureDefinition]:
        for f in self.features:
            if f.name == name:
                return f
        return None

    def get_feature_by_column(self, column: str) -> Optional[FeatureDefinition]:
        for f in self.features:
            if f.model_column == column:
                return f
        return None

    def get_risk_tier(self, probability: float) -> RiskTier:
        for tier in self.risk_tiers:
            if tier.min <= probability < tier.max:
                return tier
        return self.risk_tiers[-1]

    def calculate_costs(self, probability: float) -> dict[str, float]:
        return {
            name: round(cfg.base_cost + cfg.variable_cost * probability / 100, 2)
            for name, cfg in self.cost_configs.items()
        }


class SchemaLoader:
    @staticmethod
    def load(yaml_path: str | Path) -> FeatureSchema:
        yaml_path = Path(yaml_path)
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        features = []
        for feat_data in data["features"]:
            features.append(FeatureDefinition(
                name=feat_data["name"],
                model_column=feat_data["model_column"],
                type=feat_data["type"],
                required=feat_data.get("required", False),
                description=feat_data.get("description", ""),
                encoding=feat_data.get("encoding", {}),
                valid_range=feat_data.get("valid_range"),
                allowed_values=feat_data.get("allowed_values"),
                unit=feat_data.get("unit"),
                strongly_recommended=feat_data.get("strongly_recommended", False),
                triggers_fast_path=feat_data.get("triggers_fast_path", False),
                inference_prohibited=feat_data.get("inference_prohibited", False),
                display_name=feat_data.get("display_name"),
                category=feat_data.get("category"),
                follow_up_question=feat_data.get("follow_up_question"),
            ))

        risk_tiers = []
        for tier_data in data["risk_tiers"]:
            risk_tiers.append(RiskTier(
                name=tier_data["name"],
                label=tier_data["label"],
                min=tier_data["min"],
                max=tier_data["max"],
                intervention=tier_data["intervention"],
            ))

        cost_configs = {}
        for name, cost_data in data["cost_values"].items():
            cost_configs[name] = CostConfig(
                intervention=name,
                base_cost=cost_data["base_cost"],
                variable_cost=cost_data["variable_cost"],
            )

        return FeatureSchema(
            features=features,
            risk_tiers=risk_tiers,
            cost_configs=cost_configs,
            cholangitis_message=data["cholangitis_message"],
            version=data["version"],
        )

    @staticmethod
    def validate_against_model(schema: FeatureSchema, model_feature_names: list[str]) -> None:
        schema_columns = set(schema.get_model_columns())
        model_columns = set(model_feature_names)

        if schema_columns != model_columns:
            missing_in_schema = model_columns - schema_columns
            missing_in_model = schema_columns - model_columns
            parts = []
            if missing_in_schema:
                parts.append(f"In model but not in schema: {missing_in_schema}")
            if missing_in_model:
                parts.append(f"In schema but not in model: {missing_in_model}")
            raise ValueError(
                f"YAML schema does not match model feature columns. {'; '.join(parts)}"
            )
