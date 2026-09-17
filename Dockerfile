FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1
WORKDIR /app
COPY pyproject.toml ./
COPY academy ./academy
COPY runner ./runner
RUN pip install --no-cache-dir --upgrade pip==26.2.1 && pip install --no-cache-dir . && useradd --uid 10001 --create-home academy
COPY content ./content
COPY migrations ./migrations
COPY alembic.ini ./
COPY scripts ./scripts

FROM base AS backend
USER 10001:10001
CMD ["sh", "-c", "alembic upgrade head && uvicorn academy.api:app --host 0.0.0.0 --port 8000"]

FROM docker:29-cli AS dockercli
FROM base AS broker
COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
CMD ["uvicorn", "runner.broker:app", "--host", "0.0.0.0", "--port", "8001"]
