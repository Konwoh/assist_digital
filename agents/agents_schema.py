from typing import Literal
from pydantic import BaseModel, Field

class RewrittenQuery(BaseModel):
    search_query: str = Field(description="Optimierte Query für die semantische Suche")
    entity_focus: list[Literal["character", "episode", "location"]] = Field(
        default_factory=list,
        description="Welche Entitätstypen wahrscheinlich relevant sind",
    )


class ConfidenceEvaluation(BaseModel):
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Konfidenzscore zwischen 0.0 und 1.0",
    )
    label: Literal["hoch", "mittel", "niedrig"] = Field(
        description="Kurze verbale Bewertung des Scores",
    )
    explanation: str = Field(
        description="Kurze Begründung, warum dieser Score vergeben wurde",
    )
    missing_evidence: list[str] = Field(
        default_factory=list,
        description="Wichtige Aussagen, die nicht ausreichend belegt sind",
    )