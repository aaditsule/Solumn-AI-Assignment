#!/usr/bin/env python3
"""Run bounded GPT-5.5 Harbor rollouts after a one-call credential health check."""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]


def _credentials():
    """Read credentials into memory without ever displaying or persisting them."""
    values = dotenv_values(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY") or values.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or values.get("OPENAI_BASE_URL")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is unavailable in the process environment or .env")
    return key, base_url


def _redact(text, secrets):
    """Remove credential values from any diagnostic before it is displayed."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def _health_check(key, base_url):
    """Make one minimal completion call so credits/auth fail before Harbor starts."""
    try:
        client = OpenAI(api_key=key, base_url=base_url or None, timeout=30, max_retries=0)
        client.chat.completions.create(
            model="gpt-5.5",
            messages=[{"role": "user", "content": "Reply with OK."}],
            max_completion_tokens=16,
        )
    except Exception as error:
        message = _redact(str(error), [key, base_url])
        status = getattr(error, "status_code", None)
        category = "endpoint error"
        lowered = message.lower()
        if status == 401 or status == 403 or "unauthorized" in lowered or "authentication" in lowered:
            category = "authentication error"
        elif status == 429 or "rate limit" in lowered or "no credits" in lowered or "quota" in lowered:
            category = "credit or rate-limit error"
        print(f"Endpoint health check failed ({category}): {message}", file=sys.stderr)
        return False
    print("Endpoint health check: passed (one minimal completion call).")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("env_dir_name", help="directory name under rles/")
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--job-name", default=None)
    parser.add_argument("--force", action="store_true", help="allow more than four attempts")
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.env_dir_name):
        parser.error("env_dir_name must be a simple directory name")
    if args.attempts < 1 or (args.attempts > 4 and not args.force):
        parser.error("attempts must be positive; use --force to exceed four")
    task = ROOT / "rles" / args.env_dir_name
    if not (task / "task.toml").is_file():
        parser.error(f"task directory not found: rles/{args.env_dir_name}")
    job_name = args.job_name or datetime.now().strftime("gpt55-%Y%m%d-%H%M%S")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", job_name):
        parser.error("job name may contain only letters, digits, dot, underscore, and hyphen")
    key, base_url = _credentials()
    if not _health_check(key, base_url):
        return 2

    jobs_dir = Path("jobs") / args.env_dir_name
    command = [
        "harbor", "run", "--path", str(task), "--agent", "terminus-2",
        "--model", "openai/gpt-5.5", "--n-attempts", str(args.attempts),
        "--n-concurrent", "1", "--jobs-dir", str(jobs_dir),
        "--job-name", job_name, "--yes", "--env-file", ".env",
    ]
    print("Rollout command: " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = _redact(completed.stdout + completed.stderr, [key, base_url])
    if output.strip():
        print(output, end="" if output.endswith("\n") else "\n")
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
