from typing import ClassVar, Optional

from pydantic import BaseModel


class ExtractionResult(BaseModel):
    """Structured extraction result from LLM. All clinical fields default to None (null-by-default).

    Used as response_format for OpenAI structured outputs. The flat schema
    ensures reliable constrained decoding with GPT-4o-mini (Pitfall 13).
    Boolean fields use native bool (D-20); converted to YES/NO in to_feature_dict().
    """

    # Required fields (model won't run without these)
    sex: Optional[str] = None
    age: Optional[float] = None

    # Clinical conditions (native bool per D-20)
    clinical_cholangitis: Optional[bool] = None
    clinical_pancreatitis: Optional[bool] = None
    clinical_cholecystitis: Optional[bool] = None

    # Lab values (numeric)
    ast: Optional[float] = None
    alt: Optional[float] = None
    alkaline_phosphatase: Optional[float] = None
    total_bilirubin: Optional[float] = None

    # Imaging (native bool per D-20)
    abdominal_ultrasound_performed: Optional[bool] = None
    cbd_stone_on_ultrasound: Optional[bool] = None
    cbd_stone_on_ct: Optional[bool] = None

    # Comorbidity (numeric)
    charlson_comorbidity_index: Optional[int] = None

    # LLM metadata (not clinical features)
    missing_required: list[str] = []
    ambiguous: list[str] = []

    _BOOL_FIELDS: ClassVar[set[str]] = {
        "clinical_cholangitis",
        "clinical_pancreatitis",
        "clinical_cholecystitis",
        "abdominal_ultrasound_performed",
        "cbd_stone_on_ultrasound",
        "cbd_stone_on_ct",
    }

    _CLINICAL_FIELDS: ClassVar[list[str]] = [
        "sex", "age", "clinical_cholangitis", "clinical_pancreatitis",
        "clinical_cholecystitis", "ast", "alt", "alkaline_phosphatase",
        "total_bilirubin", "abdominal_ultrasound_performed",
        "cbd_stone_on_ultrasound", "cbd_stone_on_ct",
        "charlson_comorbidity_index",
    ]

    def to_feature_dict(self) -> dict:
        """Convert to feature dict for ValidationService and InferenceService.

        Only includes non-None clinical features. Converts bool -> YES/NO per D-20.
        """
        result = {}
        for name in self._CLINICAL_FIELDS:
            value = getattr(self, name)
            if value is not None:
                if name in self._BOOL_FIELDS:
                    result[name] = "YES" if value else "NO"
                else:
                    result[name] = value
        return result
