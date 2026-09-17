# Verification evidence

Local environment: Windows, Python 3.14.4 for developer checks; Node 24.14.1; Docker Desktop 29.7.2 with Linux containers and WSL 2.7.14. The isolated worker and Compose API use Python 3.12. GitHub CI also targets Python 3.12 and Node 22.

## Completed checks

| Check | Actual result |
|---|---|
| Ruff format / lint | Passed |
| mypy | Passed, 11 application/runner source files |
| Content/schema validation | Passed: 12 lessons, 60 questions, 15 challenges, 4 project briefs |
| Backend without Docker | 30 passed, 27 Docker tests excluded |
| Real grading + security targeted suite | 31 passed, including every reference solution, sample-hardcoding rejection for DataFrame/SQL/plot, mutation, timeout, memory, PID, network and raw stdout controls |
| ESLint / TypeScript | Passed |
| Vitest | 2 passed: DataFrame preview behavior and plot accessibility data |
| Vite production build | Passed; CodeMirror loaded as a separate lazy chunk |
| Playwright on Compose | 3 passed: learning/retry/hidden-data/progress flow; mobile/theme; real plot/playground/project download |
| Docker Compose | Images built; frontend, backend and PostgreSQL running, backend/database health checks passed |
| npm dependency audit | 0 vulnerabilities after updating Vitest to 4.1.11 |
| pip-audit, local non-editable packages | No known vulnerabilities after updating pip to 26.2.1 |

The first expanded Docker run had one failure while images were rebuilding. The task passed on reproduction and the complete grading/security subset then passed. Release verification serializes image build before execution. Two dependency deprecation warnings from FastAPI/Starlette's test client remain; they do not change test results.

Clean-checkout and remote CI results are recorded below when actually completed. They are not inferred from the local runs.

## Reproduction

Install the README development dependencies, Docker and Playwright Chromium. Run `python scripts/verify.py --full`. It executes formatting, lint, types, content validation, local tests, frontend tests/build, Compose build, all backend tests including real sandbox abuse, and browser E2E. Docker-marked tests only skip when `RUN_DOCKER_TESTS` is not enabled; enabled verification fails if Docker is unavailable.

Screenshots in `docs/screenshots/` are captured from the application. The browser suite checks that a constant visible DataFrame passes Run, fails Submit on hidden data, and an actual groupby solution passes and persists after reload. The plot suite checks a real decoded PNG, not a success notification alone. Project archive structure, synthetic data consistency and reproducibility have separate Python tests.

Audits report known dependency advisories at execution time; they do not prove absence of vulnerabilities. No full container-escape, external penetration, screen-reader or large-load audit has been performed.
