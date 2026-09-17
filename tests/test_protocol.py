import pytest
from pydantic import ValidationError

from runner.protocol import WorkerResponse


@pytest.mark.parametrize(
    "payload",
    [
        {"mutated": "false"},
        {"result": "not-an-object"},
        {"result": {"type": "html", "data": "<script>bad</script>"}},
        {"result": {"type": "dataframe", "columns": ["a"], "data": [[1, 2]]}},
        {"result": {"type": "plot", "image": "PHN2Zz48L3N2Zz4="}},
        {"stdout": "x" * 8193},
    ],
)
def test_untrusted_protocol_rejects_malformed_data(payload):
    with pytest.raises(ValidationError):
        WorkerResponse.model_validate(payload)


def test_worker_cannot_supply_pass_verdict_or_duration():
    result = WorkerResponse.model_validate(
        {"status": "passed", "duration": 0, "mutated": False}
    ).model_dump()
    assert "status" not in result and "duration" not in result
