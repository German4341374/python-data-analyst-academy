# Product requirements — v0.1

Python Data Analyst Academy is a Russian-language learning application for people starting Python for data analysis. It teaches concepts, provides explained quizzes, and runs real analytical code on both visible and alternative datasets.

The first acceptance path is lesson → wrong quiz answer with explanation → retry → pandas editor → visible run → hardcoded solution rejection on hidden inputs → general solution acceptance → persisted progress. A passing visible run must never award challenge completion. Errors must never award progress.

The initial delivery is v0.1, not the full 71-module curriculum or professional certification. Available content is fully reachable; planned material is explicitly labelled. The v1 target is 40 reviewed lessons, 200 varied questions, 70 challenges, 7 independent exams, 4 projects and a practical final assessment. Quantity must not be achieved with duplicate questions or empty content.

Required foundations: React/TypeScript/Vite, FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL in Compose, isolated Python 3.12 execution, versioned repository content, deterministic hidden fixtures, demo sessions, email/password accounts, keyboard access and dark/light themes.

The local deployment binds only to loopback. Multi-tenant internet hosting requires operational hardening and an independent security review. The runner must fail closed if Docker is unavailable.
