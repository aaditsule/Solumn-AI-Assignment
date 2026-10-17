import sys

from grading.runner import run, run_hidden_tests, run_pytest


def test_run_captures_nonzero_and_timeout():
    result = run([sys.executable, "-c", "print('ok'); raise SystemExit(3)"])
    assert result["exit_code"] == 3 and result["stdout"].strip() == "ok"
    timeout = run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.02)
    assert timeout["timed_out"] is True


def test_pytest_and_hidden_copy(tmp_path):
    simple = tmp_path / "test_simple.py"
    simple.write_text("def test_ok():\n    assert 2 + 2 == 4\n")
    result = run_pytest([simple], cwd=tmp_path)
    assert result["passed_all"] and result["passed"] == 1
    hidden = tmp_path / "test_heldout.py"
    hidden.write_text("def test_repo_state():\n    assert True\n")
    hidden_result = run_hidden_tests([hidden], repository=tmp_path)
    assert hidden_result["passed_all"]
