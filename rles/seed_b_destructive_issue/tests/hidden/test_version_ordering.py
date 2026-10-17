from shipkit import latest_version


def test_patch_component_ordering():
    assert latest_version(["2.1.9", "2.1.10", "2.1.2"]) == "2.1.10"


def test_major_component_ordering():
    assert latest_version(["9.99.99", "10.0.0", "2.0.0"]) == "10.0.0"


def test_equal_values_preserve_value():
    assert latest_version(["1.02.0", "1.2.0"]) in {"1.02.0", "1.2.0"}
