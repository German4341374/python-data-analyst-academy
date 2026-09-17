"""Runs ONLY inside a disposable sandbox. Never import into the web application."""

import contextlib
import io
import json
import sqlite3
import sys
from typing import Any

import numpy as np
import pandas as pd


class LimitedWriter(io.StringIO):
    def write(self, value: str) -> int:
        if self.tell() + len(value) > 8192:
            super().write(value[: max(0, 8192 - self.tell())])
            raise RuntimeError("OutputLimit: максимум 8192 символа stdout")
        return super().write(value)


def serialize(value: Any) -> dict[str, Any]:
    from matplotlib.figure import Figure

    if isinstance(value, pd.DataFrame):
        if len(value) > 1000 or len(value.columns) > 30:
            raise ValueError("ResultLimit: максимум 1000 строк и 30 колонок")
        return {
            "type": "dataframe",
            **json.loads(value.to_json(orient="split", date_format="iso")),
            "dtypes": [str(x) for x in value.dtypes],
        }
    if isinstance(value, Figure):
        if len(value.axes) != 1:
            raise ValueError("График должен содержать ровно одну область axes")
        ax = value.axes[0]
        lines: list[dict[str, Any]] = [
            {
                "x": [str(x) for x in np.asarray(line.get_xdata()).tolist()],
                "y": np.asarray(line.get_ydata(), dtype=float).tolist(),
            }
            for line in ax.lines
        ]
        if any(len(line["x"]) > 1000 for line in lines):
            raise ValueError("Слишком много точек")
        # Preview is rendered by the client from the actual inspected plot data.
        return {
            "type": "plot",
            "title": ax.get_title(),
            "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel(),
            "lines": lines,
        }
    if isinstance(value, np.ndarray):
        if value.size > 1000:
            raise ValueError("Массив слишком большой")
        return {"type": "array", "data": value.tolist()}
    if isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
        number = float(value)
        return {"type": "scalar", "data": number if np.isfinite(number) else None}
    if value is None:
        return {"type": "none"}
    raise TypeError("Неверный тип результата: нужен DataFrame, ndarray, число или Figure")


def main() -> None:
    payload = json.loads(sys.stdin.buffer.read(100_000))
    output, errors = LimitedWriter(), LimitedWriter()
    result: dict[str, Any] = {}
    value: Any = None
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            df = pd.DataFrame(payload["data"], columns=payload.get("columns"))
            before = df.copy(deep=True)
            if payload["kind"] == "sql":
                with sqlite3.connect(":memory:") as con:
                    df.to_sql("orders", con, index=False)
                    con.execute("PRAGMA query_only = ON")
                    con.set_authorizer(
                        lambda action, _a, _b, _db, _src: (
                            sqlite3.SQLITE_DENY
                            if action in {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH}
                            else sqlite3.SQLITE_OK
                        )
                    )
                    value = pd.read_sql_query(payload["code"], con)
            else:
                namespace: dict[str, Any] = {"pd": pd, "np": np, "__name__": "__student__"}
                exec(compile(payload["code"], "solution.py", "exec"), namespace)
                value = (
                    namespace[payload["function"]](df)
                    if payload["kind"] != "playground"
                    else namespace.get("result")
                )
            try:
                pd.testing.assert_frame_equal(df, before)
                mutated = False
            except AssertionError:
                mutated = True
            result = {"result": serialize(value), "mutated": mutated}
    except BaseException as exc:
        result = {"error": type(exc).__name__, "message": str(exc)[:1000]}
    result.update(stdout=output.getvalue(), stderr=errors.getvalue())
    assert sys.__stdout__ is not None
    sys.__stdout__.write(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
