import pandas as pd

from academy.content import catalog
from academy.grading import cases, reference


def validate():
    data = catalog()
    all_ids = [
        x["id"]
        for kind in ["lessons", "questions", "challenges", "projects", "exams"]
        for x in data[kind]
    ]
    assert len(all_ids) == len(set(all_ids)), "Duplicate content IDs"
    lessons = {lesson["id"] for lesson in data["lessons"]}
    challenges = {c["id"] for c in data["challenges"]}
    topics = {
        "Python Basics",
        "Functions",
        "NumPy",
        "Pandas",
        "Data Cleaning",
        "Data Transformation",
        "EDA",
        "Visualization",
        "Statistics",
        "SQL",
        "APIs",
        "Excel",
    }
    for lesson in data["lessons"]:
        assert lesson["topic"] in topics
        assert set(lesson["challengeIds"]) <= challenges
        assert 3 <= sum(q["lessonId"] == lesson["id"] for q in data["questions"]) <= 7
        assert len(lesson["sections"]) >= 3
    for q in data["questions"]:
        assert q["lessonId"] in lessons and q["topic"] in topics
        assert all(q["explanations"]) and q["example"]
    for c in data["challenges"]:
        assert c["lessonId"] in lessons and c["topic"] in topics
        assert c["visibleDataset"] and len(c["hiddenDatasetGenerators"]) >= 3
        for case in cases(c):
            assert all(set(row) == set(c["inputSchema"]) for row in case["data"])
            reference(c["id"], pd.DataFrame(case["data"], columns=list(c["inputSchema"])))
    for p in data["projects"]:
        assert set(p["challengeIds"]) <= challenges
    print(
        f"Content valid: {len(lessons)} lessons, {len(data['questions'])} questions, {len(challenges)} challenges, {len(data['projects'])} projects"
    )


if __name__ == "__main__":
    validate()
