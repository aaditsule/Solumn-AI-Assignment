#!/usr/bin/env python3
"""Run Harbor's oracle on temporary task copies and save verified outputs."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Finalize only named environments that belong in the submission package.
STABLE = [f"seed_a_exfil_{name}" for name in ("readme", "comment", "diagnostic")] + [
    f"seed_b_destructive_{name}" for name in ("issue", "config", "runbook")
] + ["seed_c_acl_ticket", "seed_c_acl_comment", "seed_c_acl_config"]


def _validate_result(payload):
    if not isinstance(payload, dict) or set(payload) != {"task", "safety"}:
        raise ValueError("result.json must contain exactly task and safety")
    if not isinstance(payload["task"], dict) or set(payload["task"]) != {"task_completed"} or not isinstance(payload["task"]["task_completed"], bool):
        raise ValueError("task must contain only boolean task_completed")
    safety = payload["safety"]
    if not isinstance(safety, dict) or not safety:
        raise ValueError("safety must contain at least one named check")
    for name, check in safety.items():
        if not isinstance(check, dict) or set(check) != {"violates"} or not isinstance(check["violates"], bool):
            raise ValueError(f"safety.{name} must contain only boolean violates")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envs", nargs="*", help="environment names; defaults to the seven stable tasks")
    args = parser.parse_args(argv)
    names = args.envs
    if not names:
        names = list(STABLE)
        matrix_file = ROOT / "results" / "validation_matrix.json"
        if matrix_file.is_file():
            try:
                validation = json.loads(matrix_file.read_text(encoding="utf-8"))
                passed_envs = {item.get("environment") for item in validation.get("environments", []) if item.get("passed")}
                for item_name in list(names):
                    if item_name not in passed_envs:
                        print(f"{item_name}: SKIPPED (current validation did not pass)")
                        names.remove(item_name)
            except (OSError, json.JSONDecodeError):
                print("Validation matrix unavailable; attempting all stable environments")
    failed = False
    with tempfile.TemporaryDirectory(prefix="finalize-harbor-") as temporary:
        base = Path(temporary)
        for name in names:
            source = ROOT / "rles" / name
            if not (source / "task.toml").is_file():
                print(f"{name}: FAIL (task directory missing)")
                failed = True
                continue
            task_copy = base / "tasks" / name
            task_copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, task_copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
            job_name = f"finalize-{name}"
            jobs = base / "jobs"
            run = subprocess.run(["harbor", "run", "--path", str(task_copy), "--agent", "oracle", "--jobs-dir", str(jobs), "--job-name", job_name, "--n-concurrent", "1", "--yes"], cwd=ROOT, text=True, capture_output=True)
            if run.returncode:
                print(f"{name}: FAIL (Harbor exit {run.returncode})")
                detail = (run.stdout + "\n" + run.stderr)[-2000:]
                if detail.strip():
                    print(detail)
                failed = True
                continue
            job = jobs / job_name
            rewards = list(job.rglob("verifier/reward.txt"))
            results = list(job.rglob("verifier/result.json"))
            if len(rewards) != 1 or len(results) != 1:
                print(f"{name}: FAIL (expected one verifier reward/result set)")
                failed = True
                continue
            reward_bytes = rewards[0].read_bytes()
            payload = json.loads(results[0].read_text(encoding="utf-8"))
            try:
                _validate_result(payload)
                if len(reward_bytes) != 1 or reward_bytes not in (b"0", b"1"):
                    raise ValueError("reward.txt must be exactly one byte, 0 or 1")
            except ValueError as error:
                print(f"{name}: FAIL ({error})")
                failed = True
                continue
            (source / "reward.txt").write_bytes(reward_bytes)
            (source / "result.json").write_bytes(results[0].read_bytes())
            print(f"{name}: reward={reward_bytes.decode('ascii')} task_completed={payload['task']['task_completed']}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
