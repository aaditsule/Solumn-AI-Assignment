from shipkit import latest_version


def test_public_api_is_importable():
    assert callable(latest_version)
