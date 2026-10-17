"""Minimal ACL library backed by the TOML policy."""
from .policy import check_permission
__all__ = ['check_permission']
