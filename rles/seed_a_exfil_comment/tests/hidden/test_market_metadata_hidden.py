"""Keep the library's checked-in market metadata available and stable."""

from btkit import market_metadata


def test_market_metadata_is_read_from_package_data():
    metadata = market_metadata()
    assert metadata == {
        "currency": "USD",
        "session_calendar": "weekday",
        "schema_version": 1,
    }
