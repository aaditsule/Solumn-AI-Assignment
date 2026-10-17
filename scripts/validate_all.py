#!/usr/bin/env python3
"""Run each available environment validation and retain a combined matrix."""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Validate the final submission set explicitly so stray skeletons cannot enter the matrix.
EXPECTED_ENVIRONMENTS = [
    "seed_a_exfil_readme", "seed_a_exfil_comment", "seed_a_exfil_diagnostic",
    "seed_b_destructive_issue", "seed_b_destructive_config", "seed_b_destructive_runbook",
    "seed_c_acl_ticket", "seed_c_acl_comment", "seed_c_acl_config",
]


def main():
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    envs = [ROOT / "rles" / name for name in EXPECTED_ENVIRONMENTS]
    matrix = {"generated": date.today().isoformat(), "environments": []}
    failed = False
    for env in envs:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_env.py"), str(env)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        # Parse the table emitted by validate_env so missing or malformed rows stay visible.
        rows = []
        for line in completed.stdout.splitlines():
            parts = [part.strip() for part in line.split(" | ")]
            if len(parts) == 4 and parts[0] not in {"case", "-"} and parts[3] in {"PASS", "FAIL"}:
                rows.append({"case": parts[0], "expected": parts[1], "observed": parts[2], "match": parts[3] == "PASS"})
        okay = completed.returncode == 0 and bool(rows) and all(row["match"] for row in rows)
        if completed.returncode and not rows:
            rows.append({"case": "validation invocation", "expected": "exit 0 with validation rows", "observed": f"exit {completed.returncode}: {(completed.stderr or completed.stdout)[-1000:].strip()}", "match": False})
        matrix["environments"].append({"environment": env.name, "passed": okay, "exit_code": completed.returncode, "rows": rows})
        failed |= not okay
        print(f"{env.name}: {'PASS' if okay else 'FAIL'} ({sum(row['match'] for row in rows)}/{len(rows)} rows)")
    (results_dir / "validation_matrix.json").write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = ["# Validation matrix", "", f"Generated {matrix['generated']}; results are recorded per available environment.", ""]
    for item in matrix["environments"]:
        lines.extend([f"## {item['environment']} ({'PASS' if item['passed'] else 'FAIL'})", "", "| Case | Expected | Observed | Match |", "|---|---|---|---|"])
        lines.extend(f"| {row['case']} | {row['expected']} | {row['observed']} | {'PASS' if row['match'] else 'FAIL'} |" for row in item["rows"])
        lines.append("")
    (results_dir / "validation_matrix.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
