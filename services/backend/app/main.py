from random import randint
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.models import Base, SessionRecord
from app.schemas import SessionCreate, SessionCreateResponse, SessionReadResponse

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionCreateResponse, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> SessionCreateResponse:
    session = SessionRecord(
        session_id=str(uuid4()),
        seed=randint(1, 10_000_000),
        duration_minutes=payload.duration_minutes,
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
        created_at=session.created_at,
    )
