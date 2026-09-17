import hashlib
import os
import secrets
import threading
from collections import Counter
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

import black
import httpx
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from academy.content import catalog, item, public_catalog
from academy.db import Attempt, Bookmark, Progress, SessionLocal, SessionToken, User
from academy.grading import grade
from runner.docker_executor import RunnerUnavailable, available

PASSWORDS = PasswordHasher()
COOKIE = "academy_session"
SUBMIT_SLOTS = threading.BoundedSemaphore(2)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    catalog()  # Fail startup on malformed educational content.
    yield


app = FastAPI(title="Python Data Analyst Academy", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def request_guard(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        if request.headers.get("x-academy") != "1":
            return JSONResponse({"detail": "Missing same-origin request header"}, status_code=403)
        try:
            if int(request.headers.get("content-length", "0")) > 65536:
                return JSONResponse({"detail": "Request too large"}, status_code=413)
        except ValueError:
            return JSONResponse({"detail": "Invalid request length"}, status_code=400)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


def database():
    with SessionLocal() as session:
        yield session


DB = Annotated[Session, Depends(database)]


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def set_session(db: Session, user: User, response: Response) -> None:
    token = secrets.token_urlsafe(32)
    db.add(
        SessionToken(
            token_hash=token_hash(token),
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
    )
    db.commit()
    response.set_cookie(
        COOKIE,
        token,
        httponly=True,
        samesite="strict",
        secure=os.getenv("COOKIE_SECURE") == "1",
        max_age=30 * 86400,
        path="/api",
    )


def current_user(db: DB, academy_session: Annotated[str | None, Cookie()] = None) -> User:
    token = db.get(SessionToken, token_hash(academy_session or ""))
    if token is None or token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        raise HTTPException(401, "Сессия истекла. Обновите страницу.")
    user = db.get(User, token.user_id)
    if user is None:
        raise HTTPException(401, "Неизвестная сессия")
    return user


Learner = Annotated[User, Depends(current_user)]


def find(kind: str, identity: str) -> dict:
    try:
        return item(kind, identity)
    except StopIteration as exc:
        raise HTTPException(404, "Материал не найден") from exc


def complete(db: Session, user: User, identity: str, kind: str) -> None:
    if not db.get(Progress, (user.id, identity, kind)):
        db.add(Progress(user_id=user.id, content_id=identity, kind=kind))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()  # An overlapping tab already completed the same item.


@app.get("/api/session")
def session_start(
    response: Response, db: DB, academy_session: Annotated[str | None, Cookie()] = None
):
    try:
        user = current_user(db, academy_session)
    except HTTPException:
        user = User(id=secrets.token_hex(16))
        db.add(user)
        db.commit()
        set_session(db, user, response)
    return {
        "email": user.email,
        "demo": user.email is None,
        "placement": user.placement,
        "dailyMinutes": user.daily_minutes,
    }


class Credentials(BaseModel):
    email: str = Field(min_length=5, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: str = Field(min_length=12, max_length=128)


@app.post("/api/auth/register")
def register(body: Credentials, response: Response, db: DB, user: Learner):
    if user.email:
        raise HTTPException(409, "Вы уже вошли в аккаунт")
    user.email = body.email.strip().lower()
    user.password_hash = PASSWORDS.hash(body.password)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Не удалось создать аккаунт с этим адресом") from exc
    db.execute(delete(SessionToken).where(SessionToken.user_id == user.id))
    set_session(db, user, response)
    return {"email": user.email}


@app.post("/api/auth/login")
def login(
    body: Credentials,
    response: Response,
    db: DB,
    academy_session: Annotated[str | None, Cookie()] = None,
):
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    try:
        # Equal work for unknown addresses avoids a trivial password-hash timing signal.
        encoded = (
            user.password_hash
            if user and user.password_hash
            else PASSWORDS.hash(secrets.token_urlsafe(32))
        )
        PASSWORDS.verify(encoded, body.password)
        if user is None:
            raise VerificationError("Invalid")
    except VerificationError as exc:
        raise HTTPException(401, "Неверный email или пароль") from exc
    if academy_session:
        db.execute(
            delete(SessionToken).where(SessionToken.token_hash == token_hash(academy_session))
        )
    set_session(db, user, response)
    return {"email": user.email}


@app.post("/api/auth/logout")
def logout(
    response: Response,
    db: DB,
    user: Learner,
    academy_session: Annotated[str | None, Cookie()] = None,
):
    db.execute(
        delete(SessionToken).where(SessionToken.token_hash == token_hash(academy_session or ""))
    )
    db.commit()
    response.delete_cookie(COOKIE, path="/api")
    return {"ok": True}


@app.get("/api/catalog")
def get_catalog():
    return public_catalog()


@app.get("/api/health")
def health():
    broker = os.getenv("RUNNER_URL")
    runner_available = False
    if broker:
        try:
            runner_available = (
                httpx.get(
                    f"{broker}/health",
                    headers={"X-Runner-Token": os.getenv("RUNNER_TOKEN", "")},
                    timeout=6,
                )
                .json()
                .get("available", False)
            )
        except (httpx.HTTPError, ValueError):
            pass
    else:
        runner_available = available()
    return {"status": "ok", "runnerAvailable": runner_available, "version": "0.1.0"}


class Preferences(BaseModel):
    placement: Literal["new", "basics", "test"]
    dailyMinutes: Literal[30, 60, 90]


@app.post("/api/preferences")
def preferences(body: Preferences, db: DB, user: Learner):
    user.placement = body.placement
    user.daily_minutes = body.dailyMinutes
    db.commit()
    return {"ok": True}


@app.post("/api/lessons/{identity}/complete")
def finish_lesson(identity: str, db: DB, user: Learner):
    find("lessons", identity)
    complete(db, user, identity, "lesson")
    return {"ok": True}


@app.post("/api/lessons/{identity}/bookmark")
def bookmark(identity: str, db: DB, user: Learner):
    find("lessons", identity)
    saved = db.get(Bookmark, (user.id, identity))
    if saved:
        db.delete(saved)
    else:
        db.add(Bookmark(user_id=user.id, lesson_id=identity))
    db.commit()
    return {"saved": saved is None}


class Answer(BaseModel):
    option: int = Field(ge=0, le=20)


@app.post("/api/questions/{identity}/answer")
def answer(identity: str, body: Answer, db: DB, user: Learner):
    q = find("questions", identity)
    if body.option >= len(q["options"]):
        raise HTTPException(422, "Неизвестный вариант ответа")
    correct = body.option == q["correct"]
    count = len(
        db.scalars(
            select(Attempt.id).where(Attempt.user_id == user.id, Attempt.content_id == identity)
        ).all()
    )
    db.add(
        Attempt(
            user_id=user.id,
            content_id=identity,
            content_version=q["version"],
            kind="quiz",
            topic=q["topic"],
            correct=correct,
            payload={
                "option": body.option,
                "correctOption": q["correct"],
                "attemptNumber": count + 1,
            },
        )
    )
    db.commit()
    if correct:
        complete(db, user, identity, "question")
    return {
        "correct": correct,
        "yourAnswer": q["options"][body.option],
        "correctAnswer": q["options"][q["correct"]],
        "explanation": q["explanations"][body.option],
        "correctExplanation": q["explanations"][q["correct"]],
        "example": q["example"],
        "lessonId": q["lessonId"],
        "attemptNumber": count + 1,
    }


class Submission(BaseModel):
    code: str = Field(min_length=1, max_length=20000)
    mode: Literal["run", "submit"] = "run"


@app.post("/api/challenges/{identity}/execute")
def run_challenge(identity: str, body: Submission, db: DB, user: Learner):
    challenge = find("challenges", identity)
    if not SUBMIT_SLOTS.acquire(blocking=False):
        raise HTTPException(429, "Все runner заняты. Попробуйте через несколько секунд.")
    try:
        result = grade(challenge, body.code, body.mode == "submit")
    except RunnerUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    finally:
        SUBMIT_SLOTS.release()
    if body.mode == "submit":
        db.add(
            Attempt(
                user_id=user.id,
                content_id=identity,
                content_version=challenge["version"],
                kind="challenge",
                topic=challenge["topic"],
                correct=result["status"] == "passed",
                payload={"code": body.code, "result": result},
            )
        )
        db.commit()
        if result["status"] == "passed":
            complete(db, user, identity, "challenge")
    return result


@app.get("/api/challenges/{identity}/solution")
def solution(identity: str, user: Learner):
    challenge = find("challenges", identity)
    return {"solution": challenge["solution"], "explanation": challenge["explanation"]}


class FormatCode(BaseModel):
    code: str = Field(max_length=20000)


@app.post("/api/format")
def format_code(body: FormatCode, user: Learner):
    try:
        return {"code": black.format_str(body.code, mode=black.Mode())}
    except (black.InvalidInput, TokenError) as exc:
        raise HTTPException(422, "В коде синтаксическая ошибка: сначала исправьте её.") from exc


from tokenize import TokenError  # noqa: E402


@app.get("/api/progress")
def progress(db: DB, user: Learner):
    attempts = list(
        db.scalars(
            select(Attempt)
            .where(Attempt.user_id == user.id)
            .order_by(Attempt.created_at, Attempt.id)
        )
    )
    completed = list(db.scalars(select(Progress).where(Progress.user_id == user.id)))
    latest = {a.content_id: a for a in attempts}
    quiz_attempts = [a for a in attempts if a.kind == "quiz"]
    done = {
        kind: [p.content_id for p in completed if p.kind == kind]
        for kind in ["lesson", "question", "challenge", "project", "exam"]
    }
    skill_names = [
        "Python Basics",
        "Functions",
        "NumPy",
        "Pandas",
        "Data Cleaning",
        "Data Transformation",
        "EDA",
        "Visualization",
        "Statistics",
        "SQL",
        "APIs",
        "Excel",
    ]
    skills = []
    for topic in skill_names:
        theory = [q for q in catalog()["questions"] if q["topic"] == topic]
        practice = [c for c in catalog()["challenges"] if c["topic"] == topic]
        theory_score = sum(q["id"] in latest and latest[q["id"]].correct for q in theory) / max(
            len(theory), 1
        )
        practice_score = sum(c["id"] in done["challenge"] for c in practice) / max(len(practice), 1)
        skills.append(
            {
                "topic": topic,
                "score": round((0.3 * theory_score + 0.7 * practice_score) * 100),
                "available": bool(theory or practice),
                "theoryCount": len(theory),
                "challengeCount": len(practice),
            }
        )
    mistakes = []
    for identity, last in latest.items():
        failures = [a for a in attempts if a.content_id == identity and not a.correct]
        if not failures:
            continue
        streak = 0
        for a in reversed([a for a in attempts if a.content_id == identity]):
            if not a.correct:
                break
            streak += 1
        interval = [0, 1, 3, 7, 14][min(streak, 4)]
        due = last.created_at.replace(tzinfo=UTC) + timedelta(days=interval)
        mistakes.append(
            {
                "contentId": identity,
                "topic": last.topic,
                "kind": last.kind,
                "failures": len(failures),
                "resolved": last.correct,
                "due": due.isoformat(),
                "ready": due <= datetime.now(UTC),
                "lastAnswer": failures[-1].payload.get("option"),
                "correctAnswer": failures[-1].payload.get("correctOption"),
                "attemptNumber": failures[-1].payload.get("attemptNumber"),
                "timestamp": failures[-1].created_at.isoformat(),
            }
        )
    recent = [
        a
        for a in attempts
        if a.created_at.replace(tzinfo=UTC) >= datetime.now(UTC) - timedelta(days=7)
    ]
    activity = Counter(a.created_at.date().isoformat() for a in attempts)
    return {
        "completed": done,
        "quizAccuracy": round(
            sum(a.correct for a in quiz_attempts) / max(1, len(quiz_attempts)) * 100
        ),
        "questionsAnswered": len(quiz_attempts),
        "skills": skills,
        "mistakes": sorted(mistakes, key=lambda x: (-x["failures"], x["contentId"])),
        "bookmarks": list(
            db.scalars(select(Bookmark.lesson_id).where(Bookmark.user_id == user.id))
        ),
        "weekly": {
            "attempts": len(recent),
            "passed": sum(a.correct for a in recent),
            "lessons": sum(
                p.kind == "lesson"
                and p.completed_at.replace(tzinfo=UTC) >= datetime.now(UTC) - timedelta(days=7)
                for p in completed
            ),
        },
        "activity": dict(activity),
        "currentLevel": "Учебный прогресс · без профессиональной сертификации",
        "recentAttempts": [
            {
                "id": a.id,
                "contentId": a.content_id,
                "kind": a.kind,
                "correct": a.correct,
                "createdAt": a.created_at.isoformat(),
            }
            for a in attempts[-10:]
        ][::-1],
    }
