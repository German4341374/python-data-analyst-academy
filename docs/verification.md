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

## Clean checkout and remote CI

Clean checkout of `3f71ccf243c67bf06d00654a5f75454d30c71f21`: created a new virtual environment, installed Python dependencies and `npm ci`, installed Playwright Chromium, and built a separate Compose project with a fresh PostgreSQL volume on port 8081. Local verification passed. The complete backend suite then passed **57 tests in 281.84 seconds**; all **3 browser scenarios passed** on that clean instance. Its HTML report and final status were retained as local evidence. The temporary Compose services were stopped after verification.

[GitHub Actions run 35278004710](https://github.com/German4341374/python-data-analyst-academy/actions/runs/35278004710) passed both jobs on Linux/Python 3.12/Node 22: full verification, Docker build, **57 Python tests in 161.24 seconds**, **2 Vitest tests**, **3 Playwright tests in 41.7 seconds**, plus Python and production npm dependency audits. Two earlier runs were superseded and explicitly cancelled after newer commits were pushed; their cancellation is not a test failure.

The rebuilt sandbox image's complete installed Python package list was also checked with pip-audit: no known vulnerabilities found. This audit does not include operating-system packages or the Docker daemon.

The Windows Unicode-path launcher successfully built and started the main application. Subsequent workspace relocation preserves source/Git state and changes only the launcher's junction location to the same drive as the project; the application code remains the version exercised above.

After relocation, local source/frontend checks passed again from the new drive, and the launcher rebuilt and started the application with its Compose working directory on that drive. **Implementation commit `6db9207f02de839d1c8fcd874e31e41e25776242` passed both jobs in [final CI run 35279578566](https://github.com/German4341374/python-data-analyst-academy/actions/runs/35279578566)**. The verification job completed in 6m31s and dependency security in 37s. The following release-documentation commit only records this evidence and release status; application code is unchanged. GitHub currently reports a non-failing warning that the older action versions use its Node 24 compatibility override.

## Reproduction

Install the README development dependencies, Docker and Playwright Chromium. Run `python scripts/verify.py --full`. It executes formatting, lint, types, content validation, local tests, frontend tests/build, Compose build, all backend tests including real sandbox abuse, and browser E2E. Docker-marked tests only skip when `RUN_DOCKER_TESTS` is not enabled; enabled verification fails if Docker is unavailable.

Screenshots in `docs/screenshots/` are captured from the application. The browser suite checks that a constant visible DataFrame passes Run, fails Submit on hidden data, and an actual groupby solution passes and persists after reload. The plot suite checks a real decoded PNG, not a success notification alone. Project archive structure, synthetic data consistency and reproducibility have separate Python tests.

Audits report known dependency advisories at execution time; they do not prove absence of vulnerabilities. No full container-escape, external penetration, screen-reader or large-load audit has been performed.
