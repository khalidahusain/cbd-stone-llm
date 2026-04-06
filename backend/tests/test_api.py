import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["features_count"] == 13


def test_predict_all_features(client):
    payload = {
        "sex": "Male", "age": 55, "ast": 120, "alt": 90,
        "alkaline_phosphatase": 200, "total_bilirubin": 3.5,
        "clinical_cholangitis": "NO", "clinical_pancreatitis": "NO",
        "clinical_cholecystitis": "NO", "abdominal_ultrasound_performed": "YES",
        "cbd_stone_on_ultrasound": "NO", "cbd_stone_on_ct": "NO",
        "charlson_comorbidity_index": 2,
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["probability"] <= 100
    assert data["risk_tier"] in ("low", "intermediate", "high", "very_high")
    assert isinstance(data["recommended_intervention"], str)
    assert len(data["cost_estimates"]) == 4
    assert data["cholangitis_flag"] is False
    assert data["imputed_fields"] == []


def test_predict_minimal(client):
    resp = client.post("/predict", json={"sex": "Male", "age": 55})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["imputed_fields"]) > 0


def test_predict_missing_sex(client):
    resp = client.post("/predict", json={"age": 55})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"] == "insufficient_information"
    assert "sex" in data["missing_required"]


def test_predict_missing_age(client):
    resp = client.post("/predict", json={"sex": "Male"})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"] == "insufficient_information"
    assert "age" in data["missing_required"]


def test_predict_age_out_of_range(client):
    resp = client.post("/predict", json={"sex": "Male", "age": 500})
    assert resp.status_code == 422
    data = resp.json()
    assert any(e["field"] == "age" for e in data["errors"])


def test_predict_ast_negative(client):
    resp = client.post("/predict", json={"sex": "Male", "age": 55, "ast": -5})
    assert resp.status_code == 422
    data = resp.json()
    assert any(e["field"] == "ast" for e in data["errors"])


def test_predict_sex_invalid(client):
    resp = client.post("/predict", json={"sex": "Invalid", "age": 55})
    assert resp.status_code == 422
    data = resp.json()
    assert any(e["field"] == "sex" for e in data["errors"])


def test_predict_cholangitis(client):
    resp = client.post("/predict", json={
        "sex": "Male", "age": 55, "clinical_cholangitis": "YES",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["cholangitis_flag"] is True
    assert "ASGE 2019" in data["cholangitis_message"]


def test_predict_bilirubin_not_imputed(client):
    resp = client.post("/predict", json={
        "sex": "Male", "age": 55, "total_bilirubin": 3.5,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "total_bilirubin" not in data["imputed_fields"]


def test_predict_empty_body(client):
    resp = client.post("/predict", json={})
    assert resp.status_code == 400
    data = resp.json()
    assert "sex" in data["missing_required"]
    assert "age" in data["missing_required"]
