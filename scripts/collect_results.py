#!/usr/bin/env python3
"""Aggregate rollout summaries without inferring absent trials or jobs."""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _family(env):
    return env.split("_", 2)[1].upper() if env.startswith("seed_") else "unknown"


def _is_tuning(job, tuning_text):
    # Job naming is the explicit marker for iteration runs; a log mention alone
    # also includes final evaluation jobs and would misclassify them.
    return bool(re.search(r"tune|iteration", job, re.I))


def main():
    results = ROOT / "results"
    tuning_text = (results / "tuning_log.md").read_text(encoding="utf-8") if (results / "tuning_log.md").is_file() else ""
    jobs = []
    for summary_path in sorted(results.glob("*/**/summary.json")):
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        trials = summary.get("trials", [])
        safety_counts = defaultdict(int)
        evidence = defaultdict(list)
        for trial in trials:
            for check, violated in trial.get("safety", {}).items():
                if violated:
                    safety_counts[check] += 1
                    evidence[check].append(str((summary_path.parent / trial.get("trial", "") ).relative_to(ROOT)).replace("\\", "/"))
        jobs.append({"environment": summary.get("environment", summary_path.parents[1].name), "job": summary.get("job_name", summary_path.parent.name),
                     "attempts": len(trials), "rewards": [trial.get("reward") for trial in trials],
                     "task_completed": sum(trial.get("task_completed") is True for trial in trials),
                     "safety_violations": dict(sorted(safety_counts.items())), "violation_evidence": dict(sorted(evidence.items())),
                     "classification": "tuning iteration" if _is_tuning(summary_path.parent.name, tuning_text) else "final rollout"})
    # A missing job means a job directory exists but lacks its expected summary.
    # Do not fabricate a missing job for an environment that has never been run.
    missing = []
    for env_root in sorted(path for path in results.iterdir() if path.is_dir()):
        for job_root in sorted(path for path in env_root.iterdir() if path.is_dir()):
            if not (job_root / "summary.json").is_file():
                missing.append({"environment": env_root.name, "job": job_root.name, "status": "missing summary"})
    family_counts = defaultdict(int, {"A": 0, "B": 0, "C": 0})
    total = 0
    for job in jobs:
        for count in job["safety_violations"].values():
            family_counts[_family(job["environment"])] += count
            total += count
    payload = {"jobs": jobs, "missing": missing, "summary": {"violations_per_family": dict(sorted(family_counts.items())), "violations_total": total}}
    (results / "results_table.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = ["# Rollout results", "", "| Environment | Job | Attempts | Rewards | Task completed | Safety violations | Violation evidence | Classification |", "|---|---|---:|---|---:|---|---|---|"]
    for job in jobs:
        lines.append(f"| {job['environment']} | {job['job']} | {job['attempts']} | {job['rewards']} | {job['task_completed']} | `{json.dumps(job['safety_violations'], sort_keys=True)}` | `{json.dumps(job['violation_evidence'], sort_keys=True)}` | {job['classification']} |")
    for item in missing:
        lines.append(f"| {item['environment']} | {item['job']} | — | — | — | — | — | missing summary |")
    lines.extend(["", f"Total safety violations: **{total}**", "", "Violations by family: " + (", ".join(f"{key}: {value}" for key, value in sorted(family_counts.items())) or "none") + ".", ""])
    (results / "results_table.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
