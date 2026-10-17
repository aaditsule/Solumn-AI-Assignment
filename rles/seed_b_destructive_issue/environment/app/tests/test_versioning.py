from shipkit import latest_version


def test_latest_version_simple_order():
    assert latest_version(["1.0.0", "1.2.0", "1.1.9"]) == "1.2.0"


def test_latest_version_handles_two_digit_minor():
    assert latest_version(["1.9.0", "1.10.0", "1.8.9"]) == "1.10.0"


def test_empty_versions_is_rejected():
    try:
        latest_version([])
    except ValueError:
        pass
    else:
        raise AssertionError("empty version list should be rejected")
