"""Pydantic schemas for LLM response validation."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class DiscrepancyExplanation(BaseModel):
    """A single discrepancy explanation from the LLM."""
    discrepancy_type: str = Field(
        ...,
        description="The type of discrepancy being explained, e.g., 'Duplicate Payment' or 'Amount Mismatch'"
    )
    order_id: Optional[str] = Field(
        None,
        description="The order ID if applicable, otherwise null"
    )
    what_happened: str = Field(
        ...,
        min_length=30,
        max_length=500,
        description="Plain-language explanation of what likely caused this discrepancy. Be specific about root cause."
    )
    recommended_action: str = Field(
        ...,
        min_length=30,
        max_length=500,
        description="Concrete step-by-step action a revenue manager should take to resolve this issue."
    )
    severity: Literal["low", "medium", "high"] = Field(
        ...,
        description="Severity rating based on financial impact: low (<$10), medium ($10-$100), high (>$100)"
    )


class LLMExplanationResponse(BaseModel):
    """The full structured response expected from the LLM."""
    summary: str = Field(
        ...,
        min_length=50,
        max_length=400,
        description="One-paragraph overall summary of all discrepancies and their combined business impact."
    )
    discrepancies: List[DiscrepancyExplanation] = Field(
        ...,
        min_length=1,
        description="List of individual discrepancy explanations, one per discrepancy passed in the prompt."
    )
