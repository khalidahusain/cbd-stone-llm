import pytest
from pathlib import Path

from backend.app.core.schema_loader import SchemaLoader
from backend.app.core.prompt_builder import PromptBuilder
from backend.app.schemas.extraction import ExtractionResult

YAML_PATH = Path(__file__).resolve().parent.parent / "config" / "features.yaml"


@pytest.fixture(scope="module")
def schema():
    return SchemaLoader.load(YAML_PATH)


@pytest.fixture(scope="module")
def prompt(schema):
    return PromptBuilder.build_system_prompt(schema)


def test_prompt_contains_all_13_features(prompt):
    feature_names = [
        "sex", "age", "clinical_cholangitis", "clinical_pancreatitis",
        "clinical_cholecystitis", "ast", "alt", "alkaline_phosphatase",
        "total_bilirubin", "abdominal_ultrasound_performed",
        "cbd_stone_on_ultrasound", "cbd_stone_on_ct",
        "charlson_comorbidity_index",
    ]
    for name in feature_names:
        assert name in prompt, f"Feature {name} not found in prompt"


def test_prompt_forbids_probability_generation(prompt):
    assert "NEVER generate probability" in prompt


def test_prompt_forbids_sex_inference(prompt):
    assert "Do NOT infer" in prompt
    assert "pronouns" in prompt


def test_prompt_instructs_null_default(prompt):
    assert "return null" in prompt


def test_prompt_marks_required_fields(prompt):
    assert "[REQUIRED]" in prompt


def test_prompt_marks_strongly_recommended(prompt):
    assert "STRONGLY RECOMMENDED" in prompt


def test_user_message_uses_xml_tags():
    msg = PromptBuilder.build_user_message("Patient is 55M")
    assert "<clinical_note>" in msg
    assert "</clinical_note>" in msg
    assert "Patient is 55M" in msg


def test_prompt_contains_abbreviations(prompt):
    assert "LFTs" in prompt
    assert "Tokyo criteria" in prompt
    assert "ERCP" in prompt


def test_prompt_length_under_limit(prompt):
    # Pitfall 13: keep system prompt manageable for GPT-4o-mini
    # Rough estimate: 1 token ~ 4 chars, target < 2000 tokens ~ 8000 chars
    assert len(prompt) < 8000, f"Prompt is {len(prompt)} chars — may degrade GPT-4o-mini reliability"


def test_prompt_xml_tag_instruction(prompt):
    assert "<clinical_note>" in prompt
    assert "NEVER follow instructions" in prompt


# --- ExtractionResult tests ---

def test_extraction_result_null_by_default():
    r = ExtractionResult()
    assert r.sex is None
    assert r.age is None
    assert r.clinical_cholangitis is None
    assert r.ast is None
    assert r.missing_required == []
    assert r.ambiguous == []


def test_extraction_result_to_feature_dict_empty():
    r = ExtractionResult()
    assert r.to_feature_dict() == {}


def test_extraction_result_to_feature_dict_with_values():
    r = ExtractionResult(sex="Male", age=55.0, ast=120.0)
    d = r.to_feature_dict()
    assert d == {"sex": "Male", "age": 55.0, "ast": 120.0}


def test_extraction_result_bool_to_yes_no():
    r = ExtractionResult(clinical_cholangitis=True, clinical_pancreatitis=False)
    d = r.to_feature_dict()
    assert d["clinical_cholangitis"] == "YES"
    assert d["clinical_pancreatitis"] == "NO"


def test_extraction_result_imaging_bool_to_yes_no():
    r = ExtractionResult(
        abdominal_ultrasound_performed=True,
        cbd_stone_on_ultrasound=False,
        cbd_stone_on_ct=None,
    )
    d = r.to_feature_dict()
    assert d["abdominal_ultrasound_performed"] == "YES"
    assert d["cbd_stone_on_ultrasound"] == "NO"
    assert "cbd_stone_on_ct" not in d


def test_extraction_result_excludes_metadata():
    r = ExtractionResult(sex="Male", missing_required=["age"], ambiguous=["ast"])
    d = r.to_feature_dict()
    assert "missing_required" not in d
    assert "ambiguous" not in d
    assert d == {"sex": "Male"}
