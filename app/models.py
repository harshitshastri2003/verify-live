from pydantic import BaseModel, Field
from typing import List, Literal

class Claim(BaseModel):
    text: str = Field(description="The claim itself, phrased as a standalone checkable statement")
    original_context: str = Field(description="The original sentence/snippet this claim came from")

class ExtractedClaims(BaseModel):
    claims: List[Claim] = Field(description="All atomic checkable claims found in the input. Empty list if none.")


class Evidence(BaseModel):
    source_url: str
    snippet: str
    supports_claim: bool


class Verdict(BaseModel):
    claim: str
    label: Literal["Supported", "Refuted", "Insufficient Evidence"]
    confidence: Literal["Low", "Medium", "High"]
    reasoning: str
    citations: List[str] = []


class SufficiencyCheck(BaseModel):
    is_sufficient: bool
    refined_query: str = ""