from YST_lib.cli import format_duration, parse_duration, parse_published_at


def test_parse_duration_variants():
    assert parse_duration("PT1H2M3S") == 3723
    assert parse_duration("PT45S") == 45
    assert parse_duration("PT2M") == 120
    assert parse_duration("PT0S") == 0


def test_parse_duration_rejects_garbage():
    assert parse_duration("1:23") is None
    assert parse_duration("") is None
    assert parse_duration(None) is None


def test_format_duration_short_and_long():
    assert format_duration(83) == "1:23"
    assert format_duration(3723) == "1:02:03"
    assert format_duration(None) == "unknown"


def test_parse_published_at_returns_epoch():
    assert parse_published_at("2023-01-29T12:00:00Z") == 1674993600


def test_parse_published_at_with_offset():
    assert parse_published_at("2023-01-29T13:00:00+01:00") == 1674993600


def test_parse_published_at_rejects_garbage():
    assert parse_published_at("yesterday") is None
    assert parse_published_at(None) is None