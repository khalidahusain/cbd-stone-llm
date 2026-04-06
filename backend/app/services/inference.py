import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union

from backend.app.core.schema_loader import FeatureSchema
from backend.app.schemas.prediction import (
    PredictionResult, CostEstimate, InsufficientInfoResult,
)


class InferenceService:
    def __init__(self, schema: FeatureSchema):
        self.schema = schema
        self.models: dict = {}

    def load_models(self, models_dir: str | Path) -> None:
        models_path = Path(models_dir)
        self.models = {
            "initial": joblib.load(models_path / "initial.pkl"),
            "imputer": joblib.load(models_path / "iterative_imputer.pkl"),
            "ercp": joblib.load(models_path / "model_predict_if_ercp.pkl"),
            "eus": joblib.load(models_path / "model_predict_if_eus.pkl"),
            "mrcp": joblib.load(models_path / "model_predict_if_mrcp.pkl"),
            "ioc": joblib.load(models_path / "model_predict_if_ioc.pkl"),
        }

    def predict(
        self, features: dict,
    ) -> Union[PredictionResult, InsufficientInfoResult]:
        # Step 1: Check required fields
        missing_required = []
        for feat in self.schema.features:
            if feat.required and (feat.name not in features or features[feat.name] is None):
                missing_required.append(feat.name)

        if missing_required:
            return InsufficientInfoResult(
                error="insufficient_information",
                missing_required=missing_required,
                message=f"Cannot run model: missing required fields: {', '.join(missing_required)}",
            )

        # Step 2: Build row dict with model column names and track imputed fields
        row = {}
        imputed_fields = []

        for feat in self.schema.features:
            value = features.get(feat.name)

            if value is None:
                row[feat.model_column] = np.nan
                imputed_fields.append(feat.name)
            else:
                if feat.encoding and isinstance(value, str):
                    row[feat.model_column] = feat.encoding.get(value, value)
                else:
                    row[feat.model_column] = value

        # Step 3: Create DataFrame in model's expected column order, then impute
        model_columns = list(self.models["imputer"].feature_names_in_)
        patient_df = pd.DataFrame([row], columns=model_columns)
        patient_imputed = self.models["imputer"].transform(patient_df)
        patient_imputed = pd.DataFrame(patient_imputed, columns=model_columns)

        # Step 4: Run initial model prediction
        prediction = np.round(
            self.models["initial"].predict_proba(patient_imputed)[0] * 100, 2
        )
        probability = float(prediction[1])

        # Step 5: Determine risk tier and intervention
        risk_tier = self.schema.get_risk_tier(probability)

        # Step 6: Calculate costs
        costs_dict = self.schema.calculate_costs(probability)
        cost_estimates = [
            CostEstimate(intervention=name, cost=cost)
            for name, cost in costs_dict.items()
        ]

        # Step 7: Check cholangitis fast-path
        cholangitis_value = features.get("clinical_cholangitis")
        cholangitis_flag = cholangitis_value in (True, "YES", 1)
        cholangitis_msg = self.schema.cholangitis_message if cholangitis_flag else None

        return PredictionResult(
            probability=probability,
            risk_tier=risk_tier.name,
            recommended_intervention=risk_tier.intervention,
            cost_estimates=cost_estimates,
            cholangitis_flag=cholangitis_flag,
            cholangitis_message=cholangitis_msg,
            imputed_fields=imputed_fields,
        )
