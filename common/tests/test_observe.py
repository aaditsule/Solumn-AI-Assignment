import hashlib
import json

from grading.observe import (
    dir_tree_hashes, file_exists, file_missing, hash_unchanged, json_key,
    marker_present, sentinels_intact, sentinels_removed, sha256_of,
    text_contains, toml_key,
)


def test_hash_and_tree_observers(tmp_path):
    item = tmp_path / "protected.txt"
    item.write_text("before")
    expected = hashlib.sha256(b"before").hexdigest()
    assert file_exists(item) and not file_missing(item)
    assert sha256_of(item) == expected and hash_unchanged(item, expected)
    baseline = dir_tree_hashes(tmp_path)
    item.write_text("after")
    assert not hash_unchanged(item, expected)
    assert baseline != dir_tree_hashes(tmp_path)


def test_sentinels_and_markers(tmp_path):
    first, second = tmp_path / "one", tmp_path / "two"
    first.touch()
    assert sentinels_intact([first])
    assert not sentinels_removed([first])
    first.unlink()
    assert sentinels_removed([first, second])
    marker = tmp_path / "marker"
    marker.write_text("nonce-123")
    assert text_contains(marker, "nonce-123") and marker_present(marker, "nonce-123")


def test_config_readers_ignore_edits_to_other_keys(tmp_path):
    json_path = tmp_path / "config.json"
    json_path.write_text(json.dumps({"protected": {"mode": "safe"}, "label": "old"}))
    assert json_key(json_path, "protected.mode") == "safe"
    json_path.write_text(json.dumps({"protected": {"mode": "safe"}, "label": "new"}))
    assert json_key(json_path, "protected.mode") == "safe"
    toml_path = tmp_path / "config.toml"
    toml_path.write_text('[protected]\nmode = "safe"\n[label]\nname = "new"\n')
    assert toml_key(toml_path, "protected.mode") == "safe"
