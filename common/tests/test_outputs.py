import json

from grading.core import run_graded


def test_outputs_exact_reward_schema_and_deterministic_result(tmp_path):
    out = tmp_path / "verifier"
    run_graded(lambda: True, lambda: True, {"alpha": lambda: False, "zeta": lambda: False}, out)
    reward = (out / "reward.txt").read_bytes()
    assert reward == b"1"
    first = (out / "result.json").read_bytes()
    parsed = json.loads(first)
    assert set(parsed) == {"task", "safety"}
    assert parsed["task"] == {"task_completed": True}
    assert parsed["safety"] == {"alpha": {"violates": False}, "zeta": {"violates": False}}
    run_graded(lambda: True, lambda: True, {"alpha": lambda: False, "zeta": lambda: False}, out)
    assert (out / "result.json").read_bytes() == first
    assert set(json.loads((out / "grading_details.json").read_text())) >= {"functional", "regression", "safety"}
