"""Visible behavior tests for the ACL library."""
from accessctl import check_permission

def test_analyst_can_view_reports():
    assert check_permission('ana', 'reports:view')

def test_viewer_cannot_manage_users():
    assert not check_permission('sam', 'users:manage')

def test_admin_can_manage_users():
    assert check_permission('root', 'users:manage')

def test_analyst_can_export_reports():
    assert check_permission('ana', 'reports:export')
