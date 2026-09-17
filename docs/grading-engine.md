# Grading specification

Each submission resolves trusted content, builds deterministic cases and starts a fresh container for each one. `run` executes only the visible case; `submit` executes all cases and persists the outcome. API returns no hidden raw inputs, expected tables, stdout or tracebacks. Failed hidden cases return category-level coaching only.

DataFrame grading uses `pandas.testing.assert_frame_equal`: exact column order, task-defined row order, index ignored, equivalent numeric dtypes allowed, `rtol=1e-6`, `atol=1e-8`. Sorting ties is explicit. There is no automatic row sorting that could conceal an ordering mistake. The current tasks all specify order; a future unordered task must implement its own canonicalization.

Scalar comparison uses `math.isclose`; NumPy uses `numpy.testing.assert_allclose`; plots compare returned Figure structure, title/axes labels, x labels and y values rather than image pixels. SQL runs read-only SQLite queries against the same visible and alternative row schema and compares the resulting DataFrame.

Input mutation is checked against a deep copy inside the worker. This is an educational correctness check, not an adversarially tamper-proof attestation: a hostile program can introspect or monkeypatch its own Python process. Passing checks is evidence on the selected fixtures, not proof of arbitrary program correctness or a secure examination credential. Hidden seeds are reproducible in the public repository; hidden means omitted from normal learner UI, not secret from a repository reader.

The trusted reference implementation is never executed from user-provided source. JSON is the only output protocol; never accept pickle, Python object deserialization or a user-supplied pass verdict.
