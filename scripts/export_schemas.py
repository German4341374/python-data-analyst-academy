"""Export the authoritative content models for editors and external authors."""

import json
from pathlib import Path

from academy.content import Challenge, Lesson, Question

root = Path(__file__).resolve().parent.parent / "content"
for name, model in [("challenge", Challenge), ("lesson", Lesson), ("question", Question)]:
    (root / f"{name}.schema.json").write_text(
        json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
