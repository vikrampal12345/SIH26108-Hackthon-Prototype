# Define request and response schemas for text and document-based recommendations.

from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Procurement requirement or user query"
    )


class RelatedStandard(BaseModel):
    is_number: str
    title: str
    status: str
    source_url: str
    relationship_type: str
    direction: str


class Recommendation(BaseModel):
    rank: int
    is_number: str
    title: str

    hybrid_score: float
    semantic_score: float
    classification_score: float

    status: str
    certification: str

    department: str
    technical_committee: str

    group: str
    sub_group: str
    sub_sub_group: str

    type_of_standard: str
    reviewed_in: str

    number_of_revisions: str
    number_of_amendments: str
    reaffirmation_year: str

    superseding_is: str

    relevant_ministries: str
    short_common_man_title: str

    source_url: str

    related_standards: List[RelatedStandard]


class RecommendationResponse(BaseModel):
    query: str
    input_type: str
    filename: Optional[str] = None
    extracted_text_length: int

    candidates_retrieved: int
    unique_candidates: int
    recommendation_count: int

    recommendations: List[Recommendation]