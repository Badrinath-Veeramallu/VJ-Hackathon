from typing import Optional

from pydantic import BaseModel, Field


class PrescriptionCheckRequest(BaseModel):

    drugs: list[str] = Field(
        ...,
        description="Drug names as typed by the prescriber (brand or generic)"
    )

    allergies: list[str] = Field(
        default_factory=list,
        description="Patient's documented allergies"
    )

    diagnoses: list[str] = Field(
        default_factory=list,
        description="Patient's active diagnoses"
    )


class ResolvedDrug(BaseModel):

    input: str

    generic: Optional[str]

    match_type: str

    confidence: float

    matched_against: Optional[str] = None


class PrescriptionCheckResponse(BaseModel):

    resolved_drugs: list[ResolvedDrug]

    overall_severity: str

    alert_count: int

    alerts: list[dict]