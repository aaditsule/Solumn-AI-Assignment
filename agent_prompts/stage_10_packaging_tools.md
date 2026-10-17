# Stage 10 — Aggregation and Packaging Tooling

## Goal

Build the scripts that produce the final submission artifacts from what already exists. This
stage needs **no model calls**. Do not modify any environment's directive, grader or task.
Seed C may still be changing in another thread; treat `rles/seed_c_*` as moving and make all
scripts re-runnable.

## Read first

`AGENTS.md`, `HARBOR_NOTES.md`, `PROGRESS.md`, `results/tuning_log.md`, `scripts/`, and the
`rles/` and `validation/` directories.

## Scripts to create

### `scripts/validate_all.py`
- Runs `scripts/validate_env.py` for every env under `rles/` (continue on failure), and
  writes `results/validation_matrix.md` (one table per env with expected vs observed) and
  `results/validation_matrix.json`.
- Exit code non-zero if any row mismatches. Print a one-line summary per env.

### `scripts/collect_results.py`
- Reads every `results/<env>/<job>/summary.json` and builds `results/results_table.md` and
  `results/results_table.json`: per env and job, attempts, rewards, task-completed counts,
  and the number of trials where each safety check violated, plus a list of the trial
  directories that contain the violation evidence (trajectory and verifier files).
- Also a top-level summary: violations per family and in total, and which jobs are tuning
  iterations versus final rollouts (from job names or `tuning_log.md`).
- Never invent numbers: if a job has no summary, list it as missing.

### `scripts/finalize_environments.py`
- For each env: run the oracle with Harbor on a temporary copy, then copy the resulting
  `reward.txt` and `result.json` from the verifier output into the env directory root, so each
  environment ships with its own `reward.txt` and `result.json`. Verify the schema exactly
  (`task.task_completed` and `safety.<check>.violates`, nothing else) and that `reward.txt` is
  one byte.

### `scripts/package_submission.py`
- Builds `archive.zip` with this layout:
  ```
  environments/<nine env dirs>   # each with task.toml, instruction.md, environment/, tests/,
                                 # solution/, reward.txt, result.json
  results/                       # validation matrix, results table, tuning log, rollout
                                 # artifacts (sanitized trajectories and verifier files)
  validation/                    # the validation-only solutions (for reviewers)
  scripts/                       # validate_env, run_rollouts, analyze, sync, etc.
  common/                        # shared grader source
  QUALITY_BAR.md
  README.md
  ```
- Include exactly the nine env directories (list them in order: seed A readme, comment,
  diagnostic; seed B issue, config, runbook; seed C ticket and its two variants). If a
  directory is missing, stop with an error naming it.
- Exclude `.env`, `jobs/`, `__pycache__`, `.venv`, `.git`, and any file larger than 50 MB.
- **Secret scan before zipping and again on the finished zip:** fail if the value of
  `OPENAI_API_KEY` (from the environment), any string matching `sk-` followed by 20+
  characters, or any full canary value (read from each env's private build-time files, or
  matched by their generated format) appears in any file. Report counts per check, never the
  matched values.
- **Round-trip test:** unzip into a temp directory and run the Harbor oracle on every
  extracted env (not the originals) with no other files present; report each reward. Envs
  must load and grade with no changes.

## Self-checks to run and report

1. `validate_all.py` summary lines (Seed C may be mid-change; report as-is).
2. `collect_results.py` output table.
3. `finalize_environments.py` on the seven envs that are stable (skip any Seed C env if
   its validation currently fails) and a hex dump of one `reward.txt`.
4. `package_submission.py --dry-run` listing the planned zip contents and the secret-scan
   counts.
5. LF and shebang scan, and `git status` showing `.env` and `jobs/` ignored.

## Constraints

No credentials anywhere. Standard library plus what Harbor already requires. LF endings.
Do not create QUALITY_BAR.md or README.md content in this stage (placeholders only; the
developer will write them).

## Report format

Files created, real output for each self-check, anything not working, `PROGRESS.md` entry.