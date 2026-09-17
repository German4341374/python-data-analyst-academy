# Project status — v0.1

This release delivers a verified learning application and a reviewed first section of the curriculum. It does not satisfy the full zero-to-Junior content target. Counts below distinguish functioning features from the remaining scope.

| Area | Status | Delivered / remaining |
|---|---|---|
| Learning workspace | Implemented | Dashboard, roadmap, lessons, quiz explanations, practice filters, challenges, playground, daily practice, mistake review, skill map, project briefs, topic reviews |
| Responsive UI | Implemented | Dark/light themes, mobile navigation, keyboard buttons, labels, real tables and plots; comprehensive accessibility audit remains planned |
| Identity and storage | Implemented | Separate demo sessions; registration, login/logout, Argon2 passwords; PostgreSQL/Alembic, SQLite development; attempts, progress, bookmarks |
| Authoring | Implemented | Versioned JSON content, Pydantic/JSON schemas, integrity validator, authoring guidance |
| Curriculum | In Progress | 12 substantive lessons across 8 grouped areas; requested 40+ lessons / full 71-module depth remains incomplete |
| Quizzes | In Progress | 60 single-choice questions, feedback for every option, examples; requested 200+ and additional question types remain planned |
| Executable practice | In Progress | 15 Python/NumPy/pandas/SQL/plot tasks with alternative data; requested 70+ and broader contracts remain planned |
| Grading | Implemented | Trusted references; scalar/array/DataFrame/SQL/line-plot comparisons; input mutation check; run versus submit; sample-only solutions rejected |
| Execution | Implemented | Disposable restricted Docker per case, bounded validated JSON, private broker, real time/memory/network/PID tests |
| Four projects | In Progress | Four complete briefs, synthetic downloadable CSV archives, data dictionaries, self-review checklists, linked practice. No notebook upload, teacher review or project score |
| Seven exams | Planned | Seven topic review sets currently reuse lesson questions; no independent exam bank, timing or exam attempts |
| Final assessment | Planned | E-commerce brief and a cleaning/aggregation task exist; unknown-dataset comprehensive assessment and analytical-writing evaluation do not |
| Skill scoring | Implemented | Transparent 30% latest quiz correctness + 70% completed practical tasks; descriptive learning indicators, not competence certification |
| Mistake review | Implemented | Attempt history and due-date intervals; no external reminder or notification delivery |
| Shared public hosting | Planned | Requires dedicated runner operations, quotas, retention/deletion, TLS, secret provisioning and security review |
| GitHub CI | Implemented | Public repository, full passing Linux verification and dependency audit; see verification report for exact run |
| Prerelease | In Progress | v0.1 packaging; full v1 curriculum remains incomplete |

No external dependency is currently marked Blocked. Email verification/recovery, historical content replay, full localization, arbitrary user dataset uploads, multi-axis plot grading, Series/multi-table task contracts, and automatic portfolio evaluation are Planned.

Browser drafts and project checklists stay in localStorage. Account-backed attempts and completion persist in the database. The catalog and hidden dataset generators are public: they resist accidental example-specific code, not a determined examination attacker.
