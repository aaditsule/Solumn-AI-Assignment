# Harbor Recon Notes

Recon completed against the locally installed Harbor 0.24.0 package on 2026-10-10. “Verified” means directly observed by a command or probe run here; “Read-only” means established from the installed schema/source or Harbor documentation. The local installed package takes precedence when it differs from current online documentation.

## Version and commands

**VERIFIED.** `harbor --version` prints `0.24.0`. `harbor --help` lists these top-level commands: `check`, `analyze`, `init`, `run`, `exec`, `publish`, `upload`, `download`, `sync`, `view`, `adapter`, `agent`, `task`, `dataset`, `job`, `hub`, `trial`, `cache`, `plugins`, `auth`, and `version`. `harbor run` aliases `harbor job start`.

The locally installed CLI exposes the following commands used by this assignment:

```text
harbor --version
harbor --help
harbor task schema
harbor agent list
harbor agent schema terminus-2
harbor run --help
harbor run --path <task-or-dataset> --agent oracle --jobs-dir jobs --job-name <name> --n-concurrent 1 --yes
harbor run --path <task-or-dataset> --agent nop --jobs-dir jobs --job-name <name> --n-concurrent 1 --yes
harbor run --path <task-or-dataset> --agent terminus-2 --model openai/gpt-5.5 --n-concurrent 1 --jobs-dir jobs --job-name <name> --yes --env-file .env
```

`-p` is `--path`, a local task or dataset directory. `-i` is `--include-task-name`, a task-name filter for a dataset (it is not an instruction flag). `-o` is `--jobs-dir`, the output directory. `--job-name` names the job subdirectory. `--yes` auto-confirms prompts. `-n` is `--n-concurrent` (simultaneous trials), not the attempt count; `-k` is `--n-attempts`. Example parallel invocation: `harbor run -p <dataset> -a nop -n 4 -o jobs --job-name parallel-check --yes`.

**VERIFIED from `harbor run --help` on 2026-10-10.** `--n-attempts` (alias `-k`) is the number of attempts per trial; `--n-concurrent` (alias `-n`) controls simultaneous trials. A two-attempt single-task rollout uses `--n-attempts 2 --n-concurrent 1`.

The exact oracle, no-op, and terminus commands and their outcomes from this recon are recorded in `PROGRESS.md`. Oracle and no-op are installed agents. `harbor agent list` also lists `terminus-2`.

## Task layout

**VERIFIED by the probe and READ-ONLY from `TaskPaths` source.** A single-step task uses:

```text
task/
├── task.toml
├── instruction.md
├── environment/
│   ├── Dockerfile                 # or docker-compose.yaml for a compose environment
│   └── files copied/built into the environment
├── tests/
│   └── test.sh                    # or test.bat for a Windows task
└── solution/
    └── solve.sh                  # or solve.bat; required by the oracle agent
```

`task.toml` configures metadata and runtime. `instruction.md` is supplied as the instruction string to the selected agent. `environment/` defines the environment image and build context. `tests/` contains the verifier entrypoint and supporting test files. `solution/` is uploaded to `/solution` and executed by the `oracle` agent. The instruction and verifier script are required for a runnable single-step task; solution files are needed when using `oracle`. `README.md` and `trajectory.json` are optional. Multi-step tasks use `steps/<name>/` with per-step instruction, solution, and tests.

## `task.toml` schema

**READ-ONLY.** `harbor task schema` prints the installed JSON Schema. Every root key below is optional in the Pydantic schema; defaults apply when omitted. A runnable task still needs the relevant files listed above. Unknown fields should not be added.

| Section | Fields (required fields marked `*`) |
|---|---|
| Root | `schema_version` (default `1.4`), `source`, `multi_step_reward_strategy` (`mean` or `final`), `metadata` (free-form object), `steps`, `artifacts` |
| `[task]` | `name*` (package name, normally `org/name`), `version`, `description`, `authors` (each author has `name*`, optional `email`), `keywords` |
| `[environment]` | `network_mode` (`no-network`, `public`, `allowlist`; default `public`), `allowed_hosts`, `build_timeout_sec` (seconds; default 600), `docker_image`, `os` (`linux` default or `windows`), `cpus`, `memory_mb`, `storage_mb`, `gpus`, `gpu_types`, `tpu` (`type*`, `topology*`), `mcp_servers`, `env`, `skills_dir`, `healthcheck`, `workdir`, deprecated `allow_internet` |
| `[[environment.mcp_servers]]` | `name*`, `transport` (`stdio`, `sse`, `streamable-http`; default `sse`), `url`, `command`, `args`; `url` is needed for HTTP transports and `command` for `stdio` |
| `[environment.healthcheck]` | `command*`, `interval_sec` (5), `timeout_sec` (30), `start_period_sec` (0), `start_interval_sec` (5), `retries` (3); time values are seconds |
| `[agent]` | `network_mode`, `allowed_hosts`, `timeout_sec` (seconds), `user` |
| `[verifier]` | `network_mode`, `allowed_hosts`, `timeout_sec` (seconds; default 600), `env`, `user`, `environment_mode` (`shared` or `separate`), `environment` (same schema as `[environment]`), `collect` |
| `[[verifier.collect]]` | `command*`, `service` (default `main`), `timeout_sec` (seconds; default 60), `user` |
| `[solution]` | `env` |
| `[[steps]]` | `name*`, `agent`, `verifier`, `min_reward`, `healthcheck`, `artifacts` |
| Artifact object | `source*`, `destination`, `exclude`, `service` |

Resource units: `cpus`, `gpus`, and `memory_mb`/`storage_mb` are integer counts; memory and storage are megabytes. `build_timeout_sec`, `timeout_sec`, and healthcheck intervals are seconds. Environment resource values default to unset, so Harbor/provider defaults apply. Environment `env` values can interpolate host variables by name (for example `${NAME}`); never place credential values in task metadata or files.

An explicit `[environment].docker_image` selects a prebuilt image; supported providers may then omit a Dockerfile. Otherwise Harbor uses the task environment definition. For this local Docker run, `environment/Dockerfile` was built with `environment/` as the Docker build context. The probe Dockerfile pins Python 3.12.4 slim Bookworm by digest.

## Test and verifier behavior

**VERIFIED by the oracle probe; implementation details are also READ-ONLY in `harbor/verifier/verifier.py`.** Harbor starts the agent before uploading `tests/`. The oracle recorded `TESTS_VISIBLE_DURING_AGENT=false`; when verification began, Harbor copied the task `tests/` tree to `/tests` and executed `/tests/test.sh`. Therefore hidden tests placed in `tests/` are not visible in the agent phase for this provider/mode.

The tested probe used `[verifier].environment_mode = "shared"`. The verifier ran in the same still-running task container, from working directory `/app`, as UID 0 (root). The probe saw `OPENAI_API_KEY` absent from the verifier process environment. Model API credentials are used by Harbor on the host for model calls; do not pass them into task containers. With no explicit verifier environment, Harbor defaults to a shared environment; adding a verifier environment selects a separate environment unless overridden.

Harbor's verifier entrypoint is the task's `tests/test.sh` (or `test.bat` for Windows). It executes through the environment command bridge; in the probe it ran under Bash and wrote its own logs under the verifier output directory. The verifier's exit status alone is not the reward: Harbor parses a numeric reward file. A verifier crash is recorded as an error; the task's own safety-check fail-closed behavior must still be implemented by its test script.

## Output file locations

**VERIFIED.** In the container, Harbor expects verifier output in `/logs/verifier/`. The probe wrote `/logs/verifier/reward.txt` as exactly one byte (`1`, no newline) and Harbor accepted it. The installed parser recognizes `/logs/verifier/reward.json` and `/logs/verifier/reward.txt`; if both exist, `reward.json` takes precedence. Harbor expects numeric reward data, not the assignment-specific `result.json` structure.

Harbor downloads the verifier output directory to `jobs/<job>/<trial>/verifier/`. The probe's extra `/logs/verifier/result.json` was preserved there alongside `reward.txt` and `test-stdout.txt`. This is a Harbor output copy; the `result.json` schema is owned by the task verifier, not interpreted by Harbor.

## Background-service recipe that works

**VERIFIED.** The probe's Dockerfile uses an `ENTRYPOINT` startup script. The script starts the Python standard-library HTTP listener in the background, writes its PID and persistent JSONL log under `/var/log/probe/`, then `exec`s `sleep infinity`. This kept the listener alive from container start through agent execution and shared-container verification. A simulated POST reached it; the verifier subsequently read its log and detected the canary.

Use this pattern when the verifier must inspect the service's state: keep the service and verifier in the same shared environment, write logs to a persistent container path, and ensure the foreground entrypoint process remains alive. `CMD`-only and a Compose sidecar were not separately tested. A separate verifier container cannot see the agent container's filesystem automatically; use a shared volume, a Compose service/collect hook, or explicit artifact collection for cross-container state. Those alternatives remain unverified here.

## Hostname mapping recipe

**VERIFIED for local Docker runtime.** Appending `127.0.0.1 probe.local` to `/etc/hosts` when the container is running succeeded, and `getent hosts probe.local` resolved it to loopback. For a Harbor Compose environment, use Compose `extra_hosts` (for example `probe.local:127.0.0.1`) or add the entry from a root startup script. The startup-time method is preferable because Docker manages `/etc/hosts` when it creates the container. Build-time `/etc/hosts` edits and mappings in non-Docker providers were not tested. For Compose sidecars, use the Compose service name to reach the sidecar over the Compose network rather than mapping it to loopback.

## Result/log directory structure

**VERIFIED from actual job output.** A local job is written as:

```text
jobs/<job-name>/
├── config.json
├── lock.json
├── job.log
├── result.json                       # job summary and aggregate metrics
└── <trial-name>/
    ├── config.json
    ├── lock.json
    ├── trial.log
    ├── result.json                   # per-trial metadata and verifier reward
    ├── agent/                        # oracle.txt or agent transcript/trajectory files
    ├── verifier/                     # reward.txt, result.json, test-stdout.txt
    └── artifacts/
```

The terminus attempt created `agent/recording.cast` and `agent/terminus_2.pane` before its model call failed, demonstrating that terminal trajectory recording starts during setup. Exact files under `agent/` depend on the selected agent and options. Job folders are excluded from Git by `.gitignore`.

## Windows notes

**VERIFIED.** The host shell is native Windows PowerShell. WSL reports default version 2; Ubuntu is installed but stopped, and Docker Desktop is running its `desktop-linux` context. Docker reports `Docker Desktop`. The task ran in Linux containers. Docker access was initially denied by the sandbox and worked after an approved Docker access request. Git required `-c safe.directory='D:/Solumn AI Assignment'` because the sandbox identity differs from the workspace owner; no global Git ownership setting was changed.

Files added in this stage use LF. `.gitignore` already covered `.env`, `jobs/`, `__pycache__/`, `*.pyc`, and `.venv/`; `git check-ignore` confirmed `.env` and `jobs/` are ignored. `.gitattributes` already forces LF for `*.sh`, `*.py`, `*.toml`, `*.md`, and `Dockerfile`. Avoid PowerShell `Set-Content` defaults that could introduce CRLF; patch-created files here are LF.

## Unknowns and risks

- The requested `terminus-2` run reached an endpoint response reporting no credits, and Harbor recorded `RateLimitError`. The endpoint request path was exercised, but no successful model response was obtained, so a completed inference and fully valid credential status are not established. The model call trajectory consequently contains no response turn.
- The Harbor package and Docker image are installed/cached locally. A clean machine needs the pinned base image available locally or network access to fetch it during image build. The probe itself installs no packages and makes no network requests during verification.
- The container's outbound access to `https://example.com` was verified. The local Docker environment used `network_mode = "public"`; a separate verifier's effective outbound access and non-Docker providers may differ. Use explicit network policies when authoring later tasks.
- `/etc/hosts` runtime mutation was verified only on Docker Desktop Linux. Build-time host-file edits, Compose `extra_hosts`, sidecar persistence, and remote-provider hostname behavior were not exercised.
- Harbor 0.24.0 accepts `reward.json` and `reward.txt`, preferring JSON when both exist. It does not require or preserve a specially shaped task `result.json` unless the verifier writes it in `/logs/verifier/`; the probe verified that an extra file there is returned.
- The probe is disposable and is not a real assignment environment. No files under `rles/` were created or changed.

## Copy-paste cheatsheet

```powershell
harbor --version
harbor --help
harbor task schema
harbor agent list
harbor agent schema terminus-2

# Oracle/reference solution
harbor run --path scripts/probe_task --agent oracle --jobs-dir jobs --job-name stage0-final-oracle --n-concurrent 1 --yes

# No-op agent
harbor run --path scripts/probe_task --agent nop --jobs-dir jobs --job-name stage0-nop --n-concurrent 1 --yes

# Model-backed attempt; .env values are not printed by this command
harbor run --path scripts/probe_task --agent terminus-2 --model openai/gpt-5.5 --n-concurrent 1 --jobs-dir jobs --job-name stage0-terminus --yes --env-file .env

# Run four dataset trials concurrently; -i filters task names and -o sets output directory
harbor run -p <dataset-path> -i '<task-name-pattern>' -a nop -n 4 -o jobs --job-name parallel-check --yes
```
