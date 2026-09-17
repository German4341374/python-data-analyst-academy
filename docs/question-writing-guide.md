# Writing questions

One question tests one learning objective. Use a plausible analyst situation, name columns and units, and make exactly one option correct. Incorrect options should reflect real misconceptions: a boolean mask versus filtered rows, count versus nunique, unweighted averages, chained assignment, or correlation versus causation. Avoid trick wording and irrelevant syntax trivia.

Each option needs a different explanation: identify what that expression does, why it fails this requirement, and the corrected reasoning. Include a short executable example. A wrong answer must leave the learner knowing the next concrete step. Explain the correct answer too.

The current format is single-choice only. Do not label a question as multi-select or code execution unless its UI and evaluation semantics have been implemented. Link the question to an existing lesson/topic. Increment `version` for semantic edits, regenerate and validate the catalog. Read the lesson and all feedback in the app before committing.

Review numerical units, zero denominators, sample/population assumptions, null behavior, SQL grouping and pandas version behavior. Use descriptive examples with small tables; do not imply causal conclusions from an observational association. Independent exams must eventually use distinct questions, not relabeled lesson quizzes.
