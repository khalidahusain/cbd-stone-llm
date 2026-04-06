from pydantic import BaseModel
from typing import Optional


class CostEstimate(BaseModel):
    intervention: str
    cost: float


class PredictionResult(BaseModel):
    probability: float
    risk_tier: str
    recommended_intervention: str
    cost_estimates: list[CostEstimate]
    cholangitis_flag: bool
    cholangitis_message: Optional[str] = None
    imputed_fields: list[str]


class ValidationErrorDetail(BaseModel):
    error: str
    field: str
    message: str


class InsufficientInfoResult(BaseModel):
    error: str
    missing_required: list[str]
    message: str


class BilirubinWarning(BaseModel):
    warning: str
    field: str
    message: str
