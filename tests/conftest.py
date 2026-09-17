import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from academy.api import app, database
from academy.db import Base


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)

    def override():
        with factory() as db:
            yield db

    app.dependency_overrides[database] = override
    with TestClient(app, headers={"X-Academy": "1"}) as test_client:
        test_client.get("/api/session")
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def docker_ready():
    if os.getenv("RUN_DOCKER_TESTS") != "1":
        pytest.skip("Set RUN_DOCKER_TESTS=1 to run real sandbox/security tests")
    from runner.docker_executor import available

    assert available(), "Docker tests requested, but sandbox image/engine is unavailable"
