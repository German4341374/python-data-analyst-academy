import hmac
import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from academy.content import item
from runner.docker_executor import RunnerUnavailable, available, execute

app = FastAPI(docs_url=None, redoc_url=None)


class Job(BaseModel):
    challengeId: str
    code: str = Field(max_length=20000)
    caseIndex: int = Field(ge=0, le=20)


class PlaygroundJob(BaseModel):
    code: str = Field(max_length=20000)


@app.post("/playground")
def playground(job: PlaygroundJob, x_runner_token: str = Header(default="")):
    authorize(x_runner_token)
    challenge = item("challenges", "revenue-city")
    try:
        return execute(
            {
                "kind": "playground",
                "function": "",
                "code": job.code,
                "data": challenge["visibleDataset"],
            },
            timeout=12,
        )
    except RunnerUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc


def authorize(token: str) -> None:
    expected = os.getenv("RUNNER_TOKEN", "")
    if not expected or not hmac.compare_digest(token, expected):
        raise HTTPException(403, "Forbidden")


@app.get("/health")
def health(x_runner_token: str = Header(default="")):
    authorize(x_runner_token)
    return {"available": available()}


@app.post("/execute")
def run(job: Job, x_runner_token: str = Header(default="")):
    from academy.grading import cases

    authorize(x_runner_token)
    try:
        challenge = item("challenges", job.challengeId)
        case = cases(challenge)[job.caseIndex]
    except (StopIteration, IndexError) as exc:
        raise HTTPException(404, "Unknown challenge or case") from exc
    try:
        return execute(
            {
                "kind": challenge["kind"],
                "function": challenge["function"],
                "code": job.code,
                "data": case["data"],
                "columns": list(challenge["inputSchema"]),
            },
            challenge["timeLimit"],
            challenge["memoryLimit"],
        )
    except RunnerUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
