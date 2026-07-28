from typing import TypedDict, List
from app.models import Claim, Evidence, Verdict

class FactCheckState(TypedDict):
    input_text: str
    claims: List[Claim]
    evidence: List[Evidence]
    verdicts: List[Verdict]
    search_iterations: int