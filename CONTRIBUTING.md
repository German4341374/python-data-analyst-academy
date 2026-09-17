# Contributing

Use the README development setup. Keep changes small enough to review, preserve existing learner data, and never commit `.env`, database files, tokens or personally identifiable datasets.

For content: edit the authoring sources, increment the affected entity version for semantic changes, regenerate the catalog, validate references and inspect the rendered lesson. Every wrong answer needs its own explanation and a concrete example. New challenges need an explicit contract, at least three meaningful alternative datasets, a passing general solution, and a failing example-specific solution. Read the question and dataset guides in `docs/`.

For code: run `python scripts/verify.py`. Changes touching execution, grading, persistence or UI flow also require `python scripts/verify.py --full` with Docker and Playwright installed. Do not substitute mocked execution for sandbox verification. Check actual behavior and failure paths; do not inflate test counts with implementation copies.

Describe what changes, why, the commands run, their actual results, and any remaining limitations. Keep public docs honest about course coverage. MIT applies to original contributions; preserve dependency and dataset licensing.
