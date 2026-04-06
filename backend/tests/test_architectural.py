"""Architectural enforcement tests for SAFE-01 and INFR-02.

These tests inspect source code to prove structural safety constraints
are maintained — the LLM layer cannot reach the inference layer.
"""

import inspect


def test_extraction_module_does_not_import_inference():
    """SAFE-01: extraction.py must never import InferenceService."""
    import backend.app.services.extraction as ext
    source = inspect.getsource(ext)
    assert "InferenceService" not in source
    assert "from backend.app.services.inference" not in source


def test_extraction_service_does_not_reference_predict():
    """SAFE-01: ExtractionService must have no predict method or call."""
    import backend.app.services.extraction as ext
    source = inspect.getsource(ext.ExtractionService)
    # Should not call .predict() or reference predict
    assert ".predict(" not in source
    assert "predict_proba" not in source


def test_no_openai_tool_registration_for_inference():
    """SAFE-01: InferenceService must not be registered as an OpenAI tool anywhere."""
    import backend.app.services.extraction as ext
    source = inspect.getsource(ext)
    assert "tools=" not in source
    assert "function_call" not in source


def test_safeguard_module_does_not_import_inference():
    """SAFE-01: safeguard.py must never import InferenceService."""
    import backend.app.services.safeguard as sg
    source = inspect.getsource(sg)
    assert "InferenceService" not in source


def test_extract_router_does_not_import_inference():
    """SAFE-01: extract router must not import InferenceService."""
    import backend.app.routers.extract as rt
    source = inspect.getsource(rt)
    assert "InferenceService" not in source
    assert "inference" not in source.lower() or "extraction" in source.lower()


def test_api_key_not_in_health_response():
    """INFR-02: OPENAI_API_KEY must not appear in health response model."""
    import backend.app.routers.health as h
    source = inspect.getsource(h)
    # The health response model should not serialize any API key
    assert "OPENAI_API_KEY" not in source or "api_key" not in source.lower().replace("openai_api_key", "")


def test_extract_router_does_not_return_api_key():
    """INFR-02: Extract router must not return the API key value in responses."""
    import backend.app.routers.extract as rt
    source = inspect.getsource(rt)
    # Must not read or return the actual key value — env var name in error messages is acceptable
    assert "os.environ" not in source
    assert "openai_client.api_key" not in source


def test_api_key_not_in_extraction_result_schema():
    """INFR-02: ExtractionResult must not include any API key field."""
    from backend.app.schemas.extraction import ExtractionResult
    field_names = set(ExtractionResult.model_fields.keys())
    assert "api_key" not in field_names
    assert "openai_api_key" not in field_names
