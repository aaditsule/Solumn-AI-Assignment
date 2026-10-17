#!/usr/bin/env python3
"""Create and verify the submission archive, or inspect its planned contents."""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Keep the archive allowlist aligned with the nine completed task directories.
ENVIRONMENTS = ["seed_a_exfil_readme", "seed_a_exfil_comment", "seed_a_exfil_diagnostic",
                "seed_b_destructive_issue", "seed_b_destructive_config", "seed_b_destructive_runbook",
                "seed_c_acl_ticket", "seed_c_acl_comment", "seed_c_acl_config"]
MAX_FILE = 50 * 1024 * 1024
SK_PATTERN = re.compile(rb"sk-[A-Za-z0-9_-]{20,}")
# Build-time canaries use secrets.token_urlsafe(32), which yields 43 URL-safe characters.
CANARY_PATTERN = re.compile(rb"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{43}(?![A-Za-z0-9_-])")
EXCLUDED = {".env", "jobs", "__pycache__", ".venv", ".git"}


def _files(base):
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(base).parts
        if any(part in EXCLUDED for part in relative_parts) or path.stat().st_size > MAX_FILE:
            continue
        yield path


def _scan_bytes(data, key, canary_scope=True):
    return {"environment_key": int(bool(key) and key.encode() in data),
            "sk_pattern": len(SK_PATTERN.findall(data)),
            "canary_pattern": len(CANARY_PATTERN.findall(data)) if canary_scope else 0}


def _scan_tree(paths, key):
    counts = {"environment_key": 0, "sk_pattern": 0, "canary_pattern": 0, "files_scanned": 0}
    for path in paths:
        counts["files_scanned"] += 1
        # Only Seed A generates token_urlsafe canaries. Restrict the format
        # matcher to those trees so unrelated 43-character run IDs are not
        # reported as secret evidence.
        scope = any(part.startswith("seed_a_exfil_") for part in path.parts)
        result = _scan_bytes(path.read_bytes(), key, scope)
        for check, count in result.items():
            counts[check] += count
    return counts


def _source_entries():
    entries = []
    missing = []
    specs = [(ROOT / "rles" / name, Path("environments") / name) for name in ENVIRONMENTS]
    specs += [(ROOT / "results", Path("results")), (ROOT / "validation", Path("validation")),
              (ROOT / "scripts", Path("scripts")), (ROOT / "common", Path("common")),
              (ROOT / "QUALITY_BAR.md", Path("QUALITY_BAR.md")), (ROOT / "README.md", Path("README.md"))]
    for source, prefix in specs:
        if not source.exists():
            missing.append(str(source.relative_to(ROOT)).replace("\\", "/"))
            continue
        if source.is_file():
            if source.stat().st_size <= MAX_FILE:
                entries.append((source, prefix))
        else:
            for path in _files(source):
                entries.append((path, prefix / path.relative_to(source)))
    return entries, missing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="scan and list planned members without writing archive.zip")
    parser.add_argument("--output", type=Path, default=ROOT / "archive.zip")
    args = parser.parse_args(argv)
    entries, missing = _source_entries()
    if missing:
        print("Missing required submission paths: " + ", ".join(missing), file=sys.stderr)
        return 2
    api_key = os.environ.get("OPENAI_API_KEY", "")
    source_scan = _scan_tree((source for source, _ in entries), api_key)
    print(f"Pre-zip secret scan: environment_key={source_scan['environment_key']}, sk_pattern={source_scan['sk_pattern']}, canary_pattern={source_scan['canary_pattern']} (files={source_scan['files_scanned']})")
    if any(source_scan[name] for name in ("environment_key", "sk_pattern", "canary_pattern")):
        print("Secret scan failed; archive not written.", file=sys.stderr)
        return 1
    planned = sorted(str(target).replace("\\", "/") for _, target in entries)
    print(f"Planned archive contents ({len(planned)} files):")
    for member in planned:
        print(member)
    missing_envs = [name for name in ENVIRONMENTS if not (ROOT / "rles" / name / "task.toml").is_file()]
    if missing_envs:
        print("Missing required environment directories or task.toml files: " + ", ".join(missing_envs), file=sys.stderr)
        return 2
    if args.dry_run:
        print("Dry run complete; archive.zip was not written.")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source, target in entries:
            archive.write(source, str(target).replace("\\", "/"))
    with zipfile.ZipFile(args.output) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"zip integrity check failed at {bad}")
        totals = {"environment_key": 0, "sk_pattern": 0, "canary_pattern": 0, "files_scanned": 0}
        for member in archive.infolist():
            if member.file_size > MAX_FILE:
                continue
            totals["files_scanned"] += 1
            scope = any(part.startswith("seed_a_exfil_") for part in Path(member.filename).parts)
            result = _scan_bytes(archive.read(member), api_key, scope)
            for name, value in result.items():
                totals[name] += value
    print(f"Post-zip secret scan: environment_key={totals['environment_key']}, sk_pattern={totals['sk_pattern']}, canary_pattern={totals['canary_pattern']} (files={totals['files_scanned']})")
    if any(totals[name] for name in ("environment_key", "sk_pattern", "canary_pattern")):
        args.output.unlink(missing_ok=True)
        raise RuntimeError("secret scan failed on completed archive; archive removed")
    with tempfile.TemporaryDirectory(prefix="submission-roundtrip-") as temporary:
        extract = Path(temporary)
        with zipfile.ZipFile(args.output) as archive:
            archive.extractall(extract)
        for name in ENVIRONMENTS:
            task = extract / "environments" / name
            job_name = f"roundtrip-{name}"
            completed = subprocess.run(["harbor", "run", "--path", str(task), "--agent", "oracle", "--jobs-dir", str(extract / "jobs"), "--job-name", job_name, "--n-concurrent", "1", "--yes"], cwd=ROOT, text=True, capture_output=True)
            if completed.returncode:
                raise RuntimeError(f"round-trip Harbor failed for {name}: {(completed.stdout + completed.stderr)[-1500:]}")
            rewards = list((extract / "jobs" / job_name).rglob("verifier/reward.txt"))
            if len(rewards) != 1:
                raise RuntimeError(f"round-trip expected one reward for {name}; found {len(rewards)}")
            print(f"round-trip {name}: reward={rewards[0].read_text(encoding='ascii')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
