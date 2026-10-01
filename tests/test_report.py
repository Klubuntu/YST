import pytest

from YST_lib.report import CHART_KEYS, _points, render_report, save_report


def rows(count=5):
    data = []
    for index in range(count):
        row = {"recorded_at": 1700000000 + index * 60, "channel_id": "UCtest", "video_id": "abc"}
        for key in CHART_KEYS:
            row[key] = 1000 + index * 10
        data.append(row)
    return data


def samples(count=5):
    return {
        key: [(1700000000 + index * 60, 1000 + index * 10) for index in range(count)]
        for key in CHART_KEYS
    }


def test_points_need_two_values():
    assert _points([5]) == ""
    assert _points([]) == ""


def test_points_are_inside_the_viewbox():
    coordinates = _points([0, 100, 50]).split(" ")
    for pair in coordinates:
        x, y = (float(value) for value in pair.split(","))
        assert 0 <= x <= 720
        assert 0 <= y <= 220


def test_report_contains_a_chart_per_metric():
    content = render_report(rows(), samples(), "UCtest", "abc123", 24)
    assert content.count("<polyline") == len(CHART_KEYS)
    assert "Video Views" in content
    assert "Subscribers" in content


def test_report_without_history_still_renders():
    content = render_report([], {}, "UCtest", None, 24)
    assert "<polyline" not in content
    assert "UCtest" in content


def test_report_escapes_titles():
    content = render_report(rows(1), {}, "<script>alert(1)</script>", None, 24)
    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;" in content


def test_report_lists_snapshots():
    content = render_report(rows(3), samples(3), "UCtest", "abc123", 6)
    assert content.count("<tr>") == 4
    assert "Last 6 hours" in content


def test_report_uses_color_scheme():
    content = render_report(rows(), samples(), "UCtest", "abc", 24)
    assert "color-scheme" in content


def test_save_report_writes_file(tmp_path):
    target = save_report("<html></html>", str(tmp_path / "out"), "report.html")
    assert target.endswith("report.html")
    assert open(target, encoding="utf-8").read() == "<html></html>"


def test_save_report_reports_unwritable_target(tmp_path):
    # A directory in place of the file fails on every platform, unlike chmod,
    # which only removes write permission on POSIX.
    target = tmp_path / "report.html"
    target.mkdir()
    with pytest.raises(OSError):
        save_report("x", str(tmp_path), "report.html")