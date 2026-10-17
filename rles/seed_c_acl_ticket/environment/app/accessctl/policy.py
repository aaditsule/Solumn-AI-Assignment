"""Evaluate role permissions without exposing policy parsing to callers."""
from pathlib import Path
import tomllib

def check_permission(principal: str, permission: str) -> bool:
    """Return whether any role assigned to a principal grants a permission."""
    policy = tomllib.loads((Path(__file__).parents[1] / 'config/acl.toml').read_text(encoding='utf-8'))
    roles = policy['roles']
    memberships = policy['principals']
    return any(principal in members and permission in roles[role]['permissions']
               for role, members in memberships.items() if role in roles)
