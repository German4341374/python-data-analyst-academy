import pytest

from academy.content import item


def test_catalog_keeps_answers_private(client):
    data = client.get("/api/catalog").json()
    assert len(data["lessons"]) >= 5
    assert all("correct" not in q and "explanations" not in q for q in data["questions"])
    assert all(
        "solution" not in c and "hiddenDatasetGenerators" not in c for c in data["challenges"]
    )


def test_wrong_answer_explanation_and_review(client):
    identity = "pandas-filtering-q1"
    response = client.post(f"/api/questions/{identity}/answer", json={"option": 0})
    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is False
    assert body["yourAnswer"] != body["correctAnswer"]
    assert body["explanation"] and body["correctExplanation"] and body["example"]
    progress = client.get("/api/progress").json()
    assert progress["mistakes"][0]["ready"] is True
    response = client.post(f"/api/questions/{identity}/answer", json={"option": 1})
    assert response.json()["attemptNumber"] == 2
    mistake = client.get("/api/progress").json()["mistakes"][0]
    assert mistake["resolved"] and not mistake["ready"]


def test_lesson_progress_is_idempotent_and_isolated(client):
    for _ in range(2):
        assert client.post("/api/lessons/python-start/complete", json={}).status_code == 200
    assert client.get("/api/progress").json()["completed"]["lesson"] == ["python-start"]
    client.cookies.clear()
    client.get("/api/session")
    assert client.get("/api/progress").json()["completed"]["lesson"] == []


def test_invalid_question_option(client):
    assert (
        client.post("/api/questions/pandas-filtering-q1/answer", json={"option": 9}).status_code
        == 422
    )
    assert client.post("/api/questions/missing/answer", json={"option": 0}).status_code == 404


def test_csrf_header_required(client):
    assert (
        client.post(
            "/api/lessons/python-start/complete", json={}, headers={"X-Academy": ""}
        ).status_code
        == 403
    )


def test_auth_preserves_demo_progress_and_rotates_cookie(client):
    client.post("/api/lessons/python-start/complete", json={})
    old_cookie = client.cookies.get("academy_session")
    credentials = {"email": "student@example.test", "password": "testing-academy-2026"}
    assert client.post("/api/auth/register", json=credentials).status_code == 200
    assert client.cookies.get("academy_session") != old_cookie
    assert client.get("/api/progress").json()["completed"]["lesson"] == ["python-start"]
    assert client.post("/api/auth/logout", json={}).status_code == 200
    assert client.get("/api/progress").status_code == 401
    assert (
        client.post(
            "/api/auth/login", json={**credentials, "password": "incorrect-password"}
        ).status_code
        == 401
    )
    assert client.post("/api/auth/login", json=credentials).status_code == 200
    assert client.get("/api/session").json()["email"] == credentials["email"]


def test_format_does_not_execute(client, tmp_path):
    path = tmp_path / "must-not-exist.txt"
    result = client.post("/api/format", json={"code": f"open({str(path)!r}, 'w').write('bad')"})
    assert result.status_code == 200
    assert not path.exists()
    assert client.post("/api/format", json={"code": "def ???"}).status_code == 422


def test_runner_unavailable_does_not_award_progress(client, monkeypatch):
    from runner.docker_executor import RunnerUnavailable

    def fail(*_args, **_kwargs):
        raise RunnerUnavailable("offline")

    monkeypatch.setattr("academy.api.grade", fail)
    response = client.post(
        "/api/challenges/revenue-city/execute", json={"code": "pass", "mode": "submit"}
    )
    assert response.status_code == 503
    assert client.get("/api/progress").json()["completed"]["challenge"] == []


@pytest.mark.docker
def test_real_submission_progress(client, docker_ready):
    c = item("challenges", "revenue-city")
    result = client.post(
        "/api/challenges/revenue-city/execute", json={"code": c["solution"], "mode": "run"}
    )
    assert result.status_code == 200
    assert result.json()["status"] == "passed"
    assert client.get("/api/progress").json()["completed"]["challenge"] == []
    result = client.post(
        "/api/challenges/revenue-city/execute", json={"code": c["solution"], "mode": "submit"}
    )
    assert result.json()["hiddenTestsPassed"] >= 5
    assert client.get("/api/progress").json()["completed"]["challenge"] == ["revenue-city"]
