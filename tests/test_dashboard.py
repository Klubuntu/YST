from YST_lib.dashboard import (
    downsample,
    format_change,
    format_deltas,
    format_number,
    format_summary,
    sparkline,
)
from YST_lib.history import METRIC_KEYS


def values(**overrides):
    data = {key: 0 for key in METRIC_KEYS}
    data.update({"subs": 100, "video_views": 500})
    data.update(overrides)
    return data


def test_format_number_groups_digits():
    assert format_number(1245320) == "1 245 320"


def test_format_change_adds_sign():
    assert format_change(1240) == "+1 240"
    assert format_change(-12) == "-12"
    assert format_change(0) == "0"


def test_sparkline_of_single_point():
    assert sparkline([(1, 5)]) == "▁"


def test_sparkline_of_flat_series():
    assert sparkline([(i, 7) for i in range(5)]) == "▁▁▁▁▁"


def test_sparkline_grows_with_values():
    bars = sparkline([(i, i * 10) for i in range(5)])
    assert bars[0] != bars[-1]
    assert bars.index(bars[-1]) == 4


def test_sparkline_of_empty_series():
    assert sparkline([]) == ""


def test_sparkline_is_limited_to_width():
    points = [(i, i) for i in range(500)]
    assert len(sparkline(points, width=20)) == 20


def test_downsample_keeps_last_value():
    assert downsample(list(range(100)), 10)[-1] == 99


def test_downsample_of_short_series_is_untouched():
    assert downsample([1, 2, 3], 10) == [1, 2, 3]


def test_format_deltas_without_history_has_no_change():
    lines = format_deltas(values(), {})
    assert any("Subscribers: 100" in line for line in lines)
    assert not any("(" in line for line in lines)


def test_format_deltas_shows_change():
    lines = format_deltas(values(), {"subs": 5, "video_views": 53})
    assert any("(+5)" in line for line in lines)
    assert any("(+53)" in line for line in lines)


def test_format_deltas_respects_selection():
    lines = format_deltas(values(), {}, {"subs"})
    assert len(lines) == 1
    assert "Subscribers" in lines[0]


def test_format_summary_without_history():
    lines = format_summary({}, 24, {})
    assert "no snapshots" in lines[0]


def test_format_summary_reports_change_and_rate():
    changes = {
        key: {"current": 10, "previous": 0, "change": 10, "per_hour": 5.0}
        for key in METRIC_KEYS
    }
    lines = format_summary(changes, 6, {"video_views": [(1, 10)]})
    assert any("Last 6h" in line for line in lines)
    assert any("(+5/h)" in line for line in lines)
    assert any("trend" in line for line in lines)

def test_format_deltas_marks_hidden_subscribers():
    lines = format_deltas(values(), {}, None, hidden=True)
    assert any("hidden by the channel" in line for line in lines)


def test_summary_notes_missing_member_metrics():
    changes = {
        key: {"current": 10, "previous": 0, "change": 10, "per_hour": 5.0}
        for key in METRIC_KEYS
    }
    lines = format_summary(changes, 24, {})
    assert any("YouTube Data API v3" in line for line in lines)
