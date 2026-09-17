import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parent.parent


class Question(BaseModel):
    id: str
    version: int = 1
    lessonId: str
    topic: str
    kind: str = "single-choice"
    prompt: str
    options: list[str] = Field(min_length=2)
    correct: int = Field(ge=0)
    explanations: list[str]
    example: str

    @model_validator(mode="after")
    def valid_options(self) -> "Question":
        if self.correct >= len(self.options) or len(self.options) != len(self.explanations):
            raise ValueError("Every option needs feedback and a valid correct answer")
        return self


class Lesson(BaseModel):
    id: str
    version: int = 1
    title: str
    module: str
    topic: str
    level: int = Field(ge=0, le=10)
    minutes: int
    summary: str
    objectives: list[str]
    sections: list[dict[str, str]]
    challengeIds: list[str]


class Challenge(BaseModel):
    id: str
    version: int = 1
    title: str
    description: str
    lessonId: str
    topic: str
    library: str
    difficulty: Literal["Beginner", "Easy", "Junior", "Final Project"]
    kind: Literal["dataframe", "scalar", "array", "plot", "sql"]
    function: str
    functionSignature: str
    inputSchema: dict[str, str]
    outputSchema: str
    ordering: str
    immutable: bool = True
    starterCode: str
    visibleDataset: list[dict[str, Any]]
    visibleTests: list[str]
    hiddenDatasetGenerators: list[str] = Field(min_length=3)
    hints: list[str] = Field(min_length=3)
    solution: str
    explanation: str
    timeLimit: int = Field(default=10, ge=1, le=20)
    memoryLimit: int = Field(default=256, ge=128, le=512)
    rtol: float = 1e-6
    atol: float = 1e-8


@lru_cache
def catalog() -> dict[str, Any]:
    content = json.loads((ROOT / "content" / "catalog.json").read_text(encoding="utf-8"))
    lessons = [Lesson.model_validate(x).model_dump() for x in content["lessons"]]
    questions = [Question.model_validate(x).model_dump() for x in content["questions"]]
    challenges = [Challenge.model_validate(x).model_dump() for x in content["challenges"]]
    return {**content, "lessons": lessons, "questions": questions, "challenges": challenges}


def item(kind: str, identity: str) -> dict[str, Any]:
    return next(x for x in catalog()[kind] if x["id"] == identity)


def public_catalog() -> dict[str, Any]:
    data = catalog()
    return {
        **data,
        "questions": [
            {k: v for k, v in q.items() if k not in {"correct", "explanations", "example"}}
            for q in data["questions"]
        ],
        "challenges": [
            {k: v for k, v in c.items() if k not in {"solution", "hiddenDatasetGenerators"}}
            for c in data["challenges"]
        ],
    }
