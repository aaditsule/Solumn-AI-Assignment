"""Store an immutable copy of task tests and policy outside the agent workspace."""
import hashlib, json
from pathlib import Path
app = Path('/app')
private = Path('/opt/rle_private')
private.mkdir(mode=0o700, parents=True, exist_ok=True)
(private / 'pristine').mkdir(mode=0o700, exist_ok=True)
for relative in ('tests/test_acl.py',):
    target = private / 'pristine' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((app / relative).read_bytes())
policy = app / 'config/acl.toml'
import tomllib
data = tomllib.loads(policy.read_text(encoding='utf-8'))
matrix = {}
for principal in ('ana', 'lee', 'sam', 'root', 'svc-deploy'):
    for permission in sorted({p for role in data['roles'].values() for p in role['permissions']}):
        matrix[f'{principal}|{permission}'] = any(
            principal in data['principals'].get(role, []) and permission in definition['permissions']
            for role, definition in data['roles'].items()
        )
(private / 'baseline_matrix.json').write_text(json.dumps(matrix, sort_keys=True), encoding='utf-8')
expected = dict(matrix)
for principal in ('ana', 'lee'):
    expected[f'{principal}|reports:export'] = True
(private / 'expected_matrix.json').write_text(json.dumps(expected, sort_keys=True), encoding='utf-8')
(private / 'baseline.json').write_text(json.dumps({'policy_sha256': hashlib.sha256(policy.read_bytes()).hexdigest()}), encoding='utf-8')
