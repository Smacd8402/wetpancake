from random import randint
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.dialogue import ProspectState, generate_prospect_turn
from app.models import Base, SessionRecord
from app.persona import PersonaGenerator
from app.schemas import (
    DialogueRequest,
    DialogueResponse,
    ScoringRequest,
    ScoringResponse,
    SessionCreate,
    SessionCreateResponse,
    SessionReadResponse,
)
from app.scoring import score_session

app = FastAPI()
Base.metadata.create_all(bind=engine)
persona_generator = PersonaGenerator()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionCreateResponse, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> SessionCreateResponse:
    recent_rows = db.execute(
        select(SessionRecord.primary_objection).order_by(SessionRecord.created_at.desc()).limit(20)
    ).all()
    recent_sessions = [{"primary_objection": row[0]} for row in recent_rows]

    seed = randint(1, 10_000_000)
    persona = persona_generator.generate(seed=seed, recent_sessions=recent_sessions)

    session = SessionRecord(
        session_id=str(uuid4()),
        seed=seed,
        duration_minutes=payload.duration_minutes,
        industry=persona.industry,
        role=persona.role,
        primary_objection=persona.primary_objection,
    )
    db.add(session)
    db.commit()
    return SessionCreateResponse(session_id=session.session_id, seed=session.seed)


@app.get("/sessions/{session_id}", response_model=SessionReadResponse)
def get_session(session_id: str, db: Session = Depends(get_db)) -> SessionReadResponse:
    session = db.get(SessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return SessionReadResponse(
        session_id=session.session_id,
        seed=session.seed,
        duration_minutes=session.duration_minutes,
        industry=session.industry,
        role=session.role,
        primary_objection=session.primary_objection,
        created_at=session.created_at,
    )


@app.post("/dialogue/turn", response_model=DialogueResponse)
def dialogue_turn(payload: DialogueRequest) -> DialogueResponse:
    turn = generate_prospect_turn(
        state=ProspectState(trust=payload.trust, resistance=payload.resistance),
        trainee_text=payload.trainee_text,
        persona={"primary_objection": payload.primary_objection},
    )
    return DialogueResponse(
        text=turn.text,
        trust=turn.next_state.trust,
        resistance=turn.next_state.resistance,
    )


@app.post("/sessions/score", response_model=ScoringResponse)
def session_score(payload: ScoringRequest) -> ScoringResponse:
    return ScoringResponse(**score_session(payload.transcript, payload.outcomes))
