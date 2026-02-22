from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    duration_minutes: int = Field(ge=1, le=30)


class SessionCreateResponse(BaseModel):
    session_id: str
    seed: int


class SessionReadResponse(BaseModel):
    session_id: str
    seed: int
    duration_minutes: int
    industry: str
    role: str
    primary_objection: str
    created_at: datetime


class DialogueRequest(BaseModel):
    trust: float = Field(ge=0.0, le=1.0)
    resistance: float = Field(ge=0.0, le=1.0)
    trainee_text: str
    primary_objection: str = "busy"


class DialogueResponse(BaseModel):
    text: str
    trust: float
    resistance: float


class ScoringRequest(BaseModel):
    transcript: list[dict]
    outcomes: dict


class ScoringResponse(BaseModel):
    total_score: int
    dimensions: dict
    misses: list[str]
    replacement_phrasing: dict


class STTResponse(BaseModel):
    text: str


class TTSRequest(BaseModel):
    text: str
