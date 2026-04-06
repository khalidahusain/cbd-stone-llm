import pytest
from pathlib import Path

from backend.app.core.schema_loader import SchemaLoader, FeatureSchema

YAML_PATH = Path(__file__).resolve().parent.parent / "config" / "features.yaml"


@pytest.fixture(scope="module")
def schema() -> FeatureSchema:
    return SchemaLoader.load(YAML_PATH)


def test_load_returns_13_features(schema):
    assert len(schema.features) == 13


def test_get_model_columns(schema):
    cols = schema.get_model_columns()
    assert len(cols) == 13
    expected = [
        "Sex", "Cholangitis", "Pancreatitis", "Cholecystitis",
        "AST", "ALT", "ALP", "T. Bilirubin", "Abd US",
        "CBD stone on Abd US", "CBD stone on CT scan",
        "Charlson Comorbidity Index", "Age",
    ]
    assert set(cols) == set(expected)


def test_get_required_features(schema):
    required = schema.get_required_features()
    assert set(required) == {"sex", "age"}


def test_validate_against_model_success(schema):
    model_cols = schema.get_model_columns()
    SchemaLoader.validate_against_model(schema, model_cols)


def test_validate_against_model_failure(schema):
    with pytest.raises(ValueError, match="does not match"):
        SchemaLoader.validate_against_model(schema, ["Wrong", "Columns"])


def test_get_feature_by_name_bilirubin(schema):
    feat = schema.get_feature_by_name("total_bilirubin")
    assert feat is not None
    assert feat.strongly_recommended is True


def test_get_risk_tier_low(schema):
    tier = schema.get_risk_tier(5.0)
    assert tier.name == "low"
    assert tier.intervention == "CCY +/- IOC"


def test_get_risk_tier_high(schema):
    tier = schema.get_risk_tier(50.0)
    assert tier.name == "high"
    assert tier.intervention == "EUS"


def test_get_risk_tier_very_high(schema):
    tier = schema.get_risk_tier(95.0)
    assert tier.name == "very_high"
    assert tier.intervention == "ERCP"


def test_calculate_costs(schema):
    costs = schema.calculate_costs(25.0)
    assert "IOC" in costs
    assert "MRCP" in costs
    assert "ERCP" in costs
    assert "EUS" in costs
    # IOC: 600 + 4451 * 25 / 100 = 600 + 1112.75 = 1712.75
    assert costs["IOC"] == 1712.75
    # MRCP: 1215.08 + 3620.92 * 25 / 100 = 1215.08 + 905.23 = 2120.31
    assert costs["MRCP"] == 2120.31
    # ERCP: 4451 + 0 * 25 / 100 = 4451.0
    assert costs["ERCP"] == 4451.0
    # EUS: 2986.58 + 3566.92 * 25 / 100 = 2986.58 + 891.73 = 3878.31
    assert costs["EUS"] == 3878.31


def test_get_risk_tier_intermediate(schema):
    tier = schema.get_risk_tier(25.0)
    assert tier.name == "intermediate"
    assert tier.intervention == "MRCP"


def test_cholangitis_has_fast_path(schema):
    feat = schema.get_feature_by_name("clinical_cholangitis")
    assert feat is not None
    assert feat.triggers_fast_path is True


def test_sex_has_inference_prohibited(schema):
    feat = schema.get_feature_by_name("sex")
    assert feat is not None
    assert feat.inference_prohibited is True
