from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class TranscriptTurn(BaseModel):
    speaker: str
    text: str
    timestamp: datetime


class MetadataQuestionnaire(BaseModel):
    purpose_of_visit_asked: bool
    experience_assessed: bool
    risk_acknowledged: bool
    gear_discussed: bool
    any_items_to_dispose_of_asked: bool


class Metadata(BaseModel):
    questionnaire: MetadataQuestionnaire
    visitor_interest_level: str
    potential_issue: str
    mount_doom_permit_status: str
    language: str


class Transcript(BaseModel):
    transcript_id: str
    session_id: str
    timestamp: datetime
    agent_type: str
    duration_seconds: int
    participants: Dict[str, str]
    transcript_text: List[TranscriptTurn]
    metadata: Metadata


class VisitorDetails(BaseModel):
    ring_bearer: bool
    gear_prepared: bool
    hazard_knowledge: str
    fitness_level: str
    permit_status: str


class QuestionnaireCompletion(BaseModel):
    purpose_of_visit: bool
    experience_level: bool
    risk_acknowledgment: bool
    gear_assessment: bool
    item_disposal_intent: bool


class StructuredData(BaseModel):
    visitor_details: VisitorDetails
    questionnaire_completion: QuestionnaireCompletion


class Analysis(BaseModel):
    sentiment: float
    interest_level: str
    preparedness_level: str
    action_items: List[str]


class ProcessedResult(BaseModel):
    transcript_id: str
    summary: str
    structured_data: StructuredData
    analysis: Analysis
    processing_timestamp: datetime

    @validator("summary")
    def summary_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Summary must not be empty")
        return v

    @validator("analysis")
    def valid_sentiment(cls, v):
        if not (0.0 <= v.sentiment <= 1.0):
            raise ValueError("Sentiment must be between 0 and 1")
        return v
