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

See `docs/runbooks/release-verification.md` for how verification is run.
