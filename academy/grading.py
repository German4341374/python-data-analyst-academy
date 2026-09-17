import json
import math
import os
from typing import Any

import httpx
import numpy as np
import pandas as pd

from runner.docker_executor import RunnerUnavailable


def frame(rows: list[dict], columns: list[str] | None = None) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)


def cases(challenge: dict) -> list[dict]:
    visible = challenge["visibleDataset"]
    result = [{"category": "Пример из условия", "data": visible}]
    for i, category in enumerate(challenge["hiddenDatasetGenerators"]):
        rng = np.random.default_rng(431 + i)
        rows = [dict(row) for row in visible]
        if category == "unseen-categories":
            cities = ["Berlin", "Paris", "Rome"]
            for j, row in enumerate(rows):
                if "city" in row:
                    row["city"] = cities[j % 3]
        elif category == "shuffled":
            rng.shuffle(rows)
        elif category == "one-group":
            rows = rows[:1]
            if "city" in rows[0]:
                rows[0]["city"] = "Oslo"
        elif category == "decimals":
            for row in rows:
                for key in ("price", "revenue", "sales", "value"):
                    if key in row and row[key] is not None:
                        row[key] = round(float(rng.uniform(1, 90)), 2)
        elif category == "duplicates":
            rows = rows + [dict(rows[0]), dict(rows[0])]
        elif category == "missing":
            rows[0]["value"] = None
        elif category == "different-months":
            rows = rows + [dict(rows[0]), dict(rows[-1])]
            for j, row in enumerate(rows):
                row["month"] = f"2025-{j % 7 + 1:02d}"
                row["revenue"] = float(rng.integers(50, 700))
        elif category == "larger":
            rows = [dict(rows[j % len(rows)]) for j in range(57)]
            for j, row in enumerate(rows):
                if "quantity" in row:
                    row["quantity"] = int(rng.integers(1, 12))
                if "value" in row and row["value"] is not None:
                    row["value"] = float(rng.integers(2, 100))
                if "order_id" in row:
                    row["order_id"] = j + 100
        else:
            raise ValueError(f"Unknown generator: {category}")
        result.append({"category": category, "data": rows})
    return result


def reference(identity: str, df: pd.DataFrame) -> Any:
    if identity in {"revenue-city", "sql-revenue"}:
        return (
            df.assign(revenue=df.quantity * df.price)
            .groupby("city", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values(["revenue", "city"], ascending=[False, True])
            .reset_index(drop=True)
        )
    if identity == "filter-orders":
        return df.loc[(df.price > 100) & (df.quantity >= 2)].reset_index(drop=True)
    if identity == "conversion":
        return 0.0 if df.visits.sum() == 0 else float(df.purchases.sum() / df.visits.sum())
    if identity == "clean-cities":
        return (
            df.assign(city=df.city.str.strip().str.title()).drop_duplicates().reset_index(drop=True)
        )
    if identity == "numpy-mask":
        values = df.value.to_numpy(dtype=float)
        return values[values > 10] * 2
    if identity == "median":
        return float(np.nanmedian(df.value.to_numpy(dtype=float)))
    if identity == "monthly-plot":
        monthly = (
            df.groupby("month", as_index=False).agg(revenue=("revenue", "sum")).sort_values("month")
        )
        return {"x": monthly.month.tolist(), "y": monthly.revenue.tolist()}
    if identity == "fill-missing":
        return df.assign(value=df.value.fillna(df.value.median()))
    if identity == "sort-orders":
        return df.sort_values(["price", "city"], ascending=[False, True]).reset_index(drop=True)
    if identity == "select-columns":
        return df[["city", "price"]].copy()
    if identity == "aov":
        return float((df.quantity * df.price).sum() / len(df))
    if identity == "customer-summary":
        return (
            df.assign(revenue=df.quantity * df.price)
            .groupby("customer_id", as_index=False)
            .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"))
            .sort_values("customer_id")
            .reset_index(drop=True)
        )
    if identity == "junior-audit":
        clean = df.drop_duplicates("order_id").dropna(subset=["city", "price", "quantity"])
        clean = clean.loc[(clean.price >= 0) & (clean.quantity > 0) & (clean.status == "paid")]
        return (
            clean.assign(
                city=clean.city.str.strip().str.title(), revenue=clean.quantity * clean.price
            )
            .groupby("city", as_index=False)
            .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
            .sort_values(["revenue", "city"], ascending=[False, True])
            .reset_index(drop=True)
        )
    raise ValueError(f"No reference for {identity}")


FEEDBACK = {
    "unseen-categories": "Решение не работает с новыми городами. Используйте все категории входной таблицы.",
    "shuffled": "Результат зависит от исходного порядка строк. Проверьте сортировку по контракту.",
    "one-group": "Решение должно работать и для одной строки / одного города.",
    "decimals": "Проверьте вычисления с дробными значениями и не округляйте раньше времени.",
    "duplicates": "Проверьте правило обработки повторяющихся значений из условия.",
    "missing": "Обработайте пропуски согласно контракту: NaN нельзя сравнивать через ==.",
    "different-months": "Количество месяцев изменилось. Подписи и точки должны следовать данным.",
    "larger": "Решение должно обрабатывать произвольное количество входных строк.",
}


def compare(challenge: dict, response: dict, expected: Any) -> tuple[bool, str]:
    if response.get("error"):
        return False, response["error"]
    if challenge["immutable"] and response.get("mutated") is not False:
        return (
            False,
            "Unexpected mutation: не изменяйте входной DataFrame; используйте copy или assign.",
        )
    output = response.get("result", {})
    try:
        if challenge["kind"] in {"dataframe", "sql"}:
            if output.get("type") != "dataframe":
                return False, "Wrong type: верните pandas DataFrame."
            actual = pd.DataFrame(output["data"], columns=output["columns"])
            if actual.columns.tolist() != expected.columns.tolist():
                return (
                    False,
                    f"Expected columns: {list(expected.columns)}; your columns: {list(actual.columns)}",
                )
            # Contracts ignore index and allow equivalent numeric dtypes, but check column order.
            pd.testing.assert_frame_equal(
                actual.reset_index(drop=True),
                expected.reset_index(drop=True),
                check_dtype=False,
                check_exact=False,
                rtol=challenge["rtol"],
                atol=challenge["atol"],
            )
        elif challenge["kind"] == "array":
            if output.get("type") != "array":
                return False, "Wrong type: верните numpy.ndarray."
            np.testing.assert_allclose(
                output["data"], expected, rtol=challenge["rtol"], atol=challenge["atol"]
            )
        elif challenge["kind"] == "scalar":
            if (
                output.get("type") != "scalar"
                or output.get("data") is None
                or not math.isclose(
                    output["data"], expected, rel_tol=challenge["rtol"], abs_tol=challenge["atol"]
                )
            ):
                return False, "Incorrect result: верните вычисленное число."
        elif challenge["kind"] == "plot":
            if output.get("type") != "plot" or len(output.get("lines", [])) != 1:
                return False, "Верните Figure с одной линией на одной области axes."
            if not all(output.get(k, "").strip() for k in ["title", "xlabel", "ylabel"]):
                return False, "Добавьте заголовок и подписи обеих осей."
            line = output["lines"][0]
            if line["x"] != expected["x"]:
                return False, "Подписи месяцев должны соответствовать данным и идти по возрастанию."
            np.testing.assert_allclose(
                line["y"], expected["y"], rtol=challenge["rtol"], atol=challenge["atol"]
            )
        return True, "Проверка пройдена"
    except (AssertionError, TypeError, ValueError, KeyError, AttributeError):
        return (
            False,
            "Incorrect result: проверьте значения, количество строк и порядок по контракту.",
        )


def execute_case(challenge: dict, code: str, case: dict, index: int) -> dict:
    broker = os.getenv("RUNNER_URL")
    if broker:
        try:
            response = httpx.post(
                f"{broker}/execute",
                headers={"X-Runner-Token": os.getenv("RUNNER_TOKEN", "")},
                json={"challengeId": challenge["id"], "code": code, "caseIndex": index},
                timeout=challenge["timeLimit"] + 25,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise RunnerUnavailable(
                "Сервис исполнения недоступен. Проверьте Docker runner."
            ) from exc
    from runner.docker_executor import execute

    return execute(
        {
            "kind": challenge["kind"],
            "function": challenge["function"],
            "code": code,
            "data": case["data"],
            "columns": list(challenge["inputSchema"]),
        },
        challenge["timeLimit"],
        challenge["memoryLimit"],
    )


def grade(challenge: dict, code: str, submit: bool = True) -> dict:
    results = []
    visible = None
    duration = 0.0
    preview = None
    for i, case in enumerate(cases(challenge) if submit else cases(challenge)[:1]):
        response = execute_case(challenge, code, case, i)
        duration += response.get("duration", 0)
        expected = reference(challenge["id"], frame(case["data"], list(challenge["inputSchema"])))
        passed, detail = compare(challenge, response, expected)
        if i == 0:
            visible = response
            if isinstance(expected, pd.DataFrame):
                preview = json.loads(expected.head(100).to_json(orient="split"))
        results.append(
            {
                "hidden": i > 0,
                "passed": passed,
                "category": case["category"],
                "feedback": "Проверка пройдена"
                if passed
                else (
                    detail
                    if i == 0
                    else FEEDBACK.get(case["category"], "Проверьте контракт задачи.")
                ),
            }
        )
    assert visible is not None
    return {
        "status": "passed" if all(x["passed"] for x in results) else "failed",
        "submitted": submit,
        "tests": results,
        "visibleTestsPassed": int(results[0]["passed"]),
        "hiddenTestsPassed": sum(x["passed"] for x in results[1:]),
        "failedTestCategory": next((x["category"] for x in results if not x["passed"]), None),
        "duration": round(duration, 3),
        "timeout": visible.get("error") == "Timeout",
        "resourceLimitExceeded": visible.get("error") in {"MemoryLimit", "OutputLimit"},
        "stdout": visible.get("stdout", ""),
        "stderr": visible.get("message", visible.get("stderr", "")),
        "output": visible.get("result"),
        "expected": preview,
    }
