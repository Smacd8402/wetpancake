from random import randint
from uuid import uuid4

from fastapi import FastAPI

from app.schemas import SessionCreate, SessionCreateResponse

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionCreateResponse, status_code=201)
def create_session(payload: SessionCreate) -> SessionCreateResponse:
    return SessionCreateResponse(
        session_id=str(uuid4()),
        seed=randint(1, 10_000_000),
    )
