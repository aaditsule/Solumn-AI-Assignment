"""Subprocess and pytest helpers used by environment verifiers."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Verifier commands return structured status so callers can fail closed.

def run(cmd, cwd=None, timeout=60, env=None):
    """Run a command and capture results without raising for nonzero exit."""
    try:
        completed = subprocess.run(
            cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
        return {"exit_code": completed.returncode, "stdout": completed.stdout,
                "stderr": completed.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as error:
        return {"exit_code": None, "stdout": error.stdout or "",
                "stderr": error.stderr or "", "timed_out": True}


def run_pytest(paths, cwd=None, timeout=300):
    """Run pytest and derive counts from its built-in JUnit XML report."""
    with tempfile.TemporaryDirectory(prefix="grading-pytest-") as temporary:
        report = Path(temporary) / "junit.xml"
        result = run([sys.executable, "-m", "pytest", "-q", "--junitxml", str(report), *map(str, paths)], cwd=cwd, timeout=timeout)
        counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        if report.exists():
            import xml.etree.ElementTree as ET
            root = ET.parse(report).getroot()
            # pytest may emit either one testsuite root or a testsuites wrapper.
            suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
            totals = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
            for suite in suites:
                for key in totals:
                    totals[key] += int(suite.attrib.get(key, "0"))
            counts["passed"] = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
            counts["failed"] = totals["failures"]
            counts["errors"] = totals["errors"]
            counts["skipped"] = totals["skipped"]
        return {**result, **counts, "passed_all": result["exit_code"] == 0 and not result["timed_out"]}


def run_hidden_tests(hidden_paths, repository, timeout=300):
    """Copy held-out files to a temporary tree, then run them on repository state."""
    with tempfile.TemporaryDirectory(prefix="grading-hidden-") as temporary:
        target = Path(temporary) / "hidden"
        target.mkdir()
        for source in map(Path, hidden_paths):
            destination = target / source.name
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        return run_pytest([target], cwd=repository, timeout=timeout)
