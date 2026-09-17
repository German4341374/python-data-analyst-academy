# Writing datasets

All shipped data is generated, synthetic and reproducible. `academy/datasets.py` contains sales, customers, marketing, support-ticket and multi-table e-commerce generators. Four project downloads package CSV files, a data dictionary and analysis instructions. The support generator is currently available to developers rather than a fifth project.

Use a seeded NumPy generator; do not depend on global randomness or the current date. Declare row grain, primary/foreign keys, date range, currency and null semantics. Test referential integrity, funnel constraints and reproducibility. Document intentional defects such as duplicate order IDs, missing cities, inconsistent case or invalid prices so cleaning remains an analytical decision.

`GeneratorConfig` supplies rows, seed, null/duplicate ratios and scenario parameters, but each generator implements its own applicable subset. Customer count is derived from the requested scale; marketing enforces funnel consistency rather than applying generic corruption ratios. Do not advertise universal controls without adding behavior and tests.

Challenge datasets in `academy/grading.py` are separate small fixtures. At least three alternatives must materially exercise the task: new categories, reordered rows, fractional values, missing values when allowed, duplicates with explicit semantics, one group, more rows, or different dates. A named generator is not evidence of coverage if it leaves that task's relevant values unchanged. Review the produced cases and trusted reference for every task.

Never ship a hidden expected result to a worker. Never return hidden rows, stdout or exception details to the browser. Publish only failure categories useful for learning. The public fixtures are not exam secrets; do not claim that they prove authorship or rule out deliberate cheating.
