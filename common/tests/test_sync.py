import importlib.util
from pathlib import Path


def _sync_module():
    # Load the command module directly so tests can point it at an isolated tree.
    script = Path(__file__).resolve().parents[2] / "scripts" / "sync_common.py"
    spec = importlib.util.spec_from_file_location("sync_common", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sync_check_detects_and_repairs_drift(tmp_path, capsys):
    module = _sync_module()
    module.SOURCE = Path(__file__).resolve().parents[1] / "grading"
    module.RLES = tmp_path / "rles"
    (module.RLES / "sample").mkdir(parents=True)
    assert module.sync_environment("sample")
    assert module.sync_environment("sample", check=True)
    copy = module.RLES / "sample" / "tests" / "_lib" / "grading" / "core.py"
    copy.write_bytes(copy.read_bytes() + b"\n# drift\n")
    assert not module.sync_environment("sample", check=True)
    assert "MISMATCH" in capsys.readouterr().out
    assert module.sync_environment("sample")
    assert module.sync_environment("sample", check=True)


def test_common_text_files_have_no_carriage_returns():
    common = Path(__file__).resolve().parents[1]
    # Bytecode is not text and is excluded from shipped package files.
    files = [path for path in common.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    offenders = [str(path) for path in files if b"\r" in path.read_bytes()]
    assert offenders == []
