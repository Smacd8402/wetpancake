from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SessionRecord(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    industry: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    primary_objection: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
