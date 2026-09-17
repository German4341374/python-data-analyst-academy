# Alternative dataset specification

The city revenue demo includes Riga/Tallinn/Vilnius visibly and six alternative cases: unseen Berlin/Paris/Rome, shuffled row order, one row/one city, decimal prices, duplicate-looking values, and 57 rows. Duplicate positions count separately unless a task explicitly asks to deduplicate.

Fixed NumPy seeds (`431 + case index`) make data reproducible. Hidden cases preserve declared columns and valid domains. Missing values are injected only for nullable contracts. SQL gets a new SQLite database per case, never the visible database reused. Monthly plotting changes month labels and count.

Each added generator needs tests for reproducibility, schema, edge cases and the reference result. A hardcoded visible result must pass the visible fixture and fail alternatives. Literal-string scanning is not a grading method.
