from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    duration_minutes: int = Field(ge=1, le=30)


class SessionCreateResponse(BaseModel):
    session_id: str
    seed: int
