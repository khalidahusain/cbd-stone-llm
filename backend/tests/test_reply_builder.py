import pytest
from pathlib import Path

from backend.app.core.schema_loader import SchemaLoader
from backend.app.core.reply_builder import ReplyBuilder, FOLLOW_UP_PRIORITY
from backend.app.schemas.extraction import ExtractionResult
from backend.app.schemas.prediction import PredictionResult, CostEstimate, ValidationErrorDetail

YAML_PATH = Path(__file__).resolve().parent.parent / "config" / "features.yaml"


@pytest.fixture(scope="module")
def schema():
    return SchemaLoader.load(YAML_PATH)


@pytest.fixture(scope="module")
def builder(schema):
    return ReplyBuilder(schema)


def _make_prediction(prob=45.0):
    return PredictionResult(
        probability=prob,
        risk_tier="high",
        recommended_intervention="EUS",
        cost_estimates=[CostEstimate(intervention="EUS", cost=3500.0)],
        cholangitis_flag=False,
        imputed_fields=[],
    )


def test_collecting_reply_asks_for_bilirubin(builder):
    extraction = ExtractionResult(sex="Male", age=55.0)
    session_features = {"sex": "Male", "age": 55.0}
    reply, ready = builder.build_collecting_reply(extraction, session_features)
    assert "bilirubin" in reply.lower()
    assert ready is False


def test_collecting_reply_asks_for_sex_first(builder):
    extraction = ExtractionResult()
    session_features = {}
    reply, ready = builder.build_collecting_reply(extraction, session_features)
    assert "sex" in reply.lower()
    assert ready is False


def test_confirmation_reply_shows_all_features(builder):
    features = {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2}
    reply = builder.build_confirmation_reply(features)
    assert "sex" in reply
    assert "age" in reply
    assert "confirm" in reply.lower()


def test_confirmed_reply_with_prediction(builder):
    prediction = _make_prediction()
    reply = builder.build_confirmed_reply(prediction)
    assert "45.0%" in reply
    assert "EUS" in reply


def test_validation_error_reply(builder):
    errors = [ValidationErrorDetail(error="validation_error", field="age", message="age must be between 18 and 120 years")]
    reply = builder.build_validation_error_reply(errors)
    assert "age" in reply
    assert "120" in reply


def test_welcome_reply(builder):
    reply = builder.build_welcome_reply()
    assert "CBD stone" in reply.lower() or "risk" in reply.lower()


def test_follow_up_never_asks_optional(builder):
    """Follow-up questions should only ask for sex, age, bilirubin."""
    extraction = ExtractionResult()
    # Session has sex and age but not bilirubin
    session_features = {"sex": "Male", "age": 55.0}
    reply, ready = builder.build_collecting_reply(extraction, session_features)
    # Should ask for bilirubin, not ast/alt/etc
    assert "bilirubin" in reply.lower()
    assert ready is False


def test_collecting_ready_when_all_priority_present(builder):
    extraction = ExtractionResult(total_bilirubin=3.2)
    session_features = {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2}
    reply, ready = builder.build_collecting_reply(extraction, session_features)
    assert ready is True
