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
    # display_name capitalized: "Sex", "Age", "Total Bilirubin"
    assert "Sex" in reply
    assert "Age" in reply
    assert "confirm" in reply.lower()
    assert "Demographics" in reply
    assert "will estimate" in reply.lower()


def test_confirmed_reply_with_prediction(builder):
    prediction = _make_prediction()
    reply = builder.build_confirmed_reply(prediction, {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2})
    assert "45.0%" in reply
    assert "EUS" in reply
    assert "Based on" in reply


def test_validation_error_reply(builder):
    errors = [ValidationErrorDetail(
        error="validation_error",
        field="age",
        message="500 is outside the valid range for Age (18-120 years)",
        provided_value=500,
    )]
    reply = builder.build_validation_error_reply(errors)
    assert "500" in reply
    assert "Age" in reply
    assert "double-check" in reply.lower()


def test_welcome_reply(builder):
    reply = builder.build_welcome_reply()
    assert "CBD stone" in reply.lower() or "risk" in reply.lower()


def test_follow_up_never_asks_optional(builder):
    """Follow-up questions should only ask for priority fields (sex, age, bilirubin, imaging)."""
    extraction = ExtractionResult()
    # Session has sex and age but not bilirubin
    session_features = {"sex": "Male", "age": 55.0}
    reply, ready = builder.build_collecting_reply(extraction, session_features)
    # Should ask for bilirubin (next in priority after sex and age)
    assert "bilirubin" in reply.lower()
    assert ready is False


def test_collecting_ready_when_all_priority_present(builder):
    extraction = ExtractionResult(total_bilirubin=3.2)
    session_features = {
        "sex": "Male", "age": 55.0, "total_bilirubin": 3.2,
        "abdominal_ultrasound_performed": "YES",
        "cbd_stone_on_ultrasound": "NO",
        "cbd_stone_on_ct": "NO",
    }
    reply, ready = builder.build_collecting_reply(extraction, session_features)
    assert ready is True


# --- New tests for Task 1 ---

def test_collecting_reply_uses_display_name(builder):
    extraction = ExtractionResult(sex="Male", age=55.0, total_bilirubin=3.2)
    session_features = {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2}
    reply, _ = builder.build_collecting_reply(extraction, session_features)
    assert "Total Bilirubin" in reply
    assert "total_bilirubin" not in reply


def test_collecting_reply_vertical_list(builder):
    extraction = ExtractionResult(sex="Male", age=55.0)
    session_features = {"sex": "Male", "age": 55.0}
    reply, _ = builder.build_collecting_reply(extraction, session_features)
    assert "Got it:" in reply
    assert "- Sex:" in reply or "- Age:" in reply


def test_confirmation_groups_by_category(builder):
    features = {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2}
    reply = builder.build_confirmation_reply(features)
    assert "**Demographics**" in reply
    assert "**Labs**" in reply
    assert "will estimate" in reply.lower()


def test_follow_up_from_yaml(builder):
    extraction = ExtractionResult()
    session_features = {}
    reply, _ = builder.build_collecting_reply(extraction, session_features)
    # Should use the YAML follow_up_question for sex
    assert "sex" in reply.lower() or "male or female" in reply.lower()


def test_no_snake_case_in_confirmation(builder):
    features = {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2}
    reply = builder.build_confirmation_reply(features)
    assert "total_bilirubin" not in reply
    assert "Total Bilirubin" in reply


# --- New tests for Task 2 ---

def test_confirmed_reply_natural_phrasing(builder):
    prediction = _make_prediction()
    reply = builder.build_confirmed_reply(prediction, {"sex": "Male", "age": 55.0})
    assert "Based on the provided information" in reply
    assert "estimated probability" in reply
    assert "Recommended next step" in reply


def test_confirmed_reply_next_best_variable(builder):
    prediction = _make_prediction()
    # Missing total_bilirubin from priority list
    reply = builder.build_confirmed_reply(prediction, {"sex": "Male", "age": 55.0})
    assert "refine" in reply.lower() or "bilirubin" in reply.lower()


def test_confirmed_reply_no_followup_when_all_priority_present(builder):
    prediction = _make_prediction()
    session_features = {
        "sex": "Male", "age": 55.0, "total_bilirubin": 3.2,
        "abdominal_ultrasound_performed": "YES",
        "cbd_stone_on_ultrasound": "NO",
        "cbd_stone_on_ct": "NO",
    }
    reply = builder.build_confirmed_reply(prediction, session_features)
    assert "refine" not in reply.lower()


def test_update_reply_uses_display_names(builder):
    prediction = _make_prediction()
    reply = builder.build_update_reply(
        prediction, ["total_bilirubin"],
        {"sex": "Male", "age": 55.0, "total_bilirubin": 3.2}
    )
    assert "Total Bilirubin" in reply
    assert "total_bilirubin" not in reply
