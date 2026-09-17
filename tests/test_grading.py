import json

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from academy.content import catalog, item
from academy.grading import cases, compare, grade, reference


def response(df):
    return {
        "mutated": False,
        "result": {"type": "dataframe", **json.loads(df.to_json(orient="split"))},
    }


def test_dataframe_contract_and_tolerance():
    c = item("challenges", "revenue-city")
    expected = reference(c["id"], pd.DataFrame(c["visibleDataset"]))
    actual = expected.copy()
    actual["revenue"] += 1e-7
    assert compare(c, response(actual), expected)[0]
    actual["revenue"] += 1
    assert not compare(c, response(actual), expected)[0]
    assert not compare(c, response(expected.iloc[::-1]), expected)[0]
    assert not compare(c, response(expected[["revenue", "city"]]), expected)[0]
    assert not compare(c, {**response(expected), "mutated": True}, expected)[0]
    assert not compare(c, {"mutated": False, "result": {"type": "scalar", "data": 1}}, expected)[0]


def test_indices_ignored_numeric_dtypes_equivalent():
    c = item("challenges", "revenue-city")
    expected = reference(c["id"], pd.DataFrame(c["visibleDataset"]))
    actual = expected.copy()
    actual.index = [10, 20, 30]
    actual["revenue"] = actual.revenue.astype(int)
    assert compare(c, response(actual), expected)[0]


def test_alternative_cases_reproducible():
    c = item("challenges", "revenue-city")
    assert cases(c) == cases(c)
    assert len(cases(c)) >= 6
    assert set(row["city"] for row in cases(c)[1]["data"]) == {"Berlin", "Paris", "Rome"}
    assert len(cases(c)[-1]["data"]) == 57


@given(
    st.lists(
        st.tuples(
            st.sampled_from(["Riga", "Berlin", "Oslo"]), st.integers(1, 20), st.integers(0, 10000)
        ),
        min_size=1,
        max_size=50,
    )
)
def test_reference_conserves_revenue(rows):
    df = pd.DataFrame(rows, columns=["city", "quantity", "price"])
    result = reference("revenue-city", df)
    assert result.revenue.sum() == (df.quantity * df.price).sum()
    assert result.city.nunique() == df.city.nunique()


@pytest.mark.docker
@pytest.mark.parametrize("identity", [c["id"] for c in catalog()["challenges"]])
def test_general_solutions_pass_real_alternative_data(identity, docker_ready):
    c = item("challenges", identity)
    result = grade(c, c["solution"])
    assert result["status"] == "passed", result
    assert result["hiddenTestsPassed"] >= 3


@pytest.mark.docker
def test_hardcoded_dataframe_fails_hidden(docker_ready):
    c = item("challenges", "revenue-city")
    code = "import pandas as pd\ndef revenue_by_city(df):\n    return pd.DataFrame({'city': ['Riga', 'Tallinn', 'Vilnius'], 'revenue': [480.0, 340.0, 300.0]})"
    result = grade(c, code)
    assert result["visibleTestsPassed"] == 1
    assert result["status"] == "failed"
    assert result["hiddenTestsPassed"] < len(cases(c)) - 1
    # Hidden raw inputs / student prints are never sent to the learner.
    assert "Berlin" not in json.dumps(result)


@pytest.mark.docker
def test_mutating_solution_rejected(docker_ready):
    c = item("challenges", "revenue-city")
    code = c["solution"].replace("    return", "    df['extra'] = 1\n    return", 1)
    result = grade(c, code, submit=False)
    assert result["status"] == "failed"
    assert "mutation" in result["tests"][0]["feedback"]
