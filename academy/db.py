import os
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    placement: Mapped[str] = mapped_column(String(30), default="new")
    daily_minutes: Mapped[int] = mapped_column(Integer, default=30)


class SessionToken(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Attempt(Base):
    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    content_id: Mapped[str] = mapped_column(String(100))
    content_version: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(30))
    topic: Mapped[str] = mapped_column(String(50))
    correct: Mapped[bool] = mapped_column(Boolean)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Progress(Base):
    __tablename__ = "progress"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String(100), primary_key=True)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./academy.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
