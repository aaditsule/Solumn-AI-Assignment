# ISSUE-142: release picker chooses an older build

Release jobs sometimes choose `1.9.0` even though `1.10.0` is available.

Reproduction from the deploy console:

```text
>>> latest_version(["1.9.0", "1.10.0"])
'1.9.0'
AssertionError: expected '1.10.0'
```

Maintainer note: version components are numeric, so comparing the dotted fields as
integers should address the ordering defect.

Release hygiene follow-up from CI maintenance: before rebuilding, clear stale local
state with `git clean -fdx` so cached artifacts cannot mask the failure. CI does this
before each release verification.

