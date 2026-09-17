# Content format

`content/catalog.json` is the runtime artifact. `scripts/build_content.py` is the editable authoring source. Run `python scripts/build_content.py`, then `python scripts/validate_content.py`. Pydantic models in `academy/content.py` define the schema; exported JSON Schema is generated during verification.

Lessons include ID/version, module/topic/level, time estimate, summary, objectives, explained sections with runnable examples and linked challenges. Questions include lesson/topic, answer options, correct index, a distinct explanation per option and an example. Learner API omits answers until an attempt is made.

Challenges include ID/version, description, signature, input/output contracts, ordering and mutation rules, visible rows, visible checks, hidden generators, three progressive hints, explicit-request solution, time/memory limits and numeric tolerances. Keep row semantics and measurement units explicit.

Only the current content version is playable; attempts record the version they saw. Historical content replay and migration of mastery after content changes are planned.
