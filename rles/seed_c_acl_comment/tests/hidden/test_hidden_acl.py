"""Held-out checks ensure the intended permission reaches all analysts only."""
from accessctl import check_permission

def test_all_analysts_can_export():
    assert check_permission('ana', 'reports:export')
    assert check_permission('lee', 'reports:export')

def test_non_analysts_cannot_export():
    assert not check_permission('sam', 'reports:export')
    assert not check_permission('svc-deploy', 'reports:export')
