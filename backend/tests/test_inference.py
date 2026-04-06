import pytest
from pathlib import Path

from backend.app.core.schema_loader import SchemaLoader, FeatureSchema
from backend.app.services.inference import InferenceService
from backend.app.services.validation import ValidationService
from backend.app.schemas.prediction import PredictionResult, InsufficientInfoResult

BASE_DIR = Path(__file__).resolve().parent.parent
YAML_PATH = BASE_DIR / "config" / "features.yaml"
MODELS_DIR = BASE_DIR / "models"


@pytest.fixture(scope="module")
def schema() -> FeatureSchema:
    return SchemaLoader.load(YAML_PATH)


@pytest.fixture(scope="module")
def inference_service(schema) -> InferenceService:
    svc = InferenceService(schema)
    svc.load_models(MODELS_DIR)
    return svc


@pytest.fixture(scope="module")
def validation_service(schema) -> ValidationService:
    return ValidationService(schema)


def test_load_models(inference_service):
    assert len(inference_service.models) == 6
    assert "initial" in inference_service.models
    assert "imputer" in inference_service.models


def test_predict_all_features(inference_service):
    features = {
        "sex": "Male", "age": 55, "ast": 120, "alt": 90,
        "alkaline_phosphatase": 200, "total_bilirubin": 3.5,
        "clinical_cholangitis": "NO", "clinical_pancreatitis": "NO",
        "clinical_cholecystitis": "NO", "abdominal_ultrasound_performed": "YES",
        "cbd_stone_on_ultrasound": "NO", "cbd_stone_on_ct": "NO",
        "charlson_comorbidity_index": 2,
    }
    result = inference_service.predict(features)
    assert isinstance(result, PredictionResult)
    assert 0 <= result.probability <= 100
    assert result.risk_tier in ("low", "intermediate", "high", "very_high")
    assert result.imputed_fields == []


def test_predict_minimal_features(inference_service):
    features = {"sex": "Male", "age": 55}
    result = inference_service.predict(features)
    assert isinstance(result, PredictionResult)
    assert 0 <= result.probability <= 100
    assert "total_bilirubin" in result.imputed_fields


def test_predict_missing_sex(inference_service):
    features = {"age": 55}
    result = inference_service.predict(features)
    assert isinstance(result, InsufficientInfoResult)
    assert "sex" in result.missing_required


def test_predict_missing_age(inference_service):
    features = {"sex": "Male"}
    result = inference_service.predict(features)
    assert isinstance(result, InsufficientInfoResult)
    assert "age" in result.missing_required


def test_predict_cholangitis_flag(inference_service):
    features = {"sex": "Male", "age": 55, "clinical_cholangitis": "YES"}
    result = inference_service.predict(features)
    assert isinstance(result, PredictionResult)
    assert result.cholangitis_flag is True
    assert "ASGE 2019" in result.cholangitis_message


def test_predict_imputed_fields(inference_service):
    features = {"sex": "Male", "age": 55}
    result = inference_service.predict(features)
    assert isinstance(result, PredictionResult)
    assert "total_bilirubin" in result.imputed_fields
    assert "sex" not in result.imputed_fields
    assert "age" not in result.imputed_fields


def test_cost_estimates(inference_service):
    features = {"sex": "Male", "age": 55}
    result = inference_service.predict(features)
    assert isinstance(result, PredictionResult)
    interventions = {c.intervention for c in result.cost_estimates}
    assert interventions == {"IOC", "MRCP", "ERCP", "EUS"}


def test_validate_valid_input(validation_service):
    errors = validation_service.validate({"sex": "Male", "age": 45})
    assert errors == []


def test_validate_age_out_of_range(validation_service):
    errors = validation_service.validate({"age": 500})
    assert len(errors) == 1
    assert errors[0].field == "age"
    assert "120" in errors[0].message


def test_validate_ast_negative(validation_service):
    errors = validation_service.validate({"ast": -5})
    assert len(errors) == 1
    assert errors[0].field == "ast"
    assert "0" in errors[0].message


def test_validate_sex_invalid(validation_service):
    errors = validation_service.validate({"sex": "Unknown"})
    assert len(errors) == 1
    assert errors[0].field == "sex"
    assert "Male" in errors[0].message or "Female" in errors[0].message
