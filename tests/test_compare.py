from YST_lib.compare import (
    build_rows,
    format_compact,
    format_legend,
    format_table,
    ratio,
    views_per_hour,
)


def video(**overrides):
    data = {
        "video_id": "C7REVNM_EWY",
        "video_title": "Meow Chef",
        "video_duration": 12,
        "video_views": 2827211,
        "video_likes": 157438,
        "video_comments": 428,
    }
    data.update(overrides)
    return data


def test_ratio_in_percent():
    assert ratio(50, 1000) == 5.0


def test_ratio_of_zero_views_is_none():
    assert ratio(0, 0) is None


def test_views_per_hour():
    assert views_per_hour(3600, 3600) == 3600
    assert views_per_hour(1000, 7200) == 500


def test_views_per_hour_without_duration_is_none():
    assert views_per_hour(1000, None) is None
    assert views_per_hour(1000, 0) is None


def test_format_compact():
    assert format_compact(999) == "999"
    assert format_compact(1500) == "1.5k"
    assert format_compact(2_500_000) == "2.5M"
    assert format_compact(3_000_000_000) == "3.0B"


def test_build_rows_contains_ratios():
    rows = build_rows([video()])
    assert rows[0]["like_ratio"] == 100 * 157438 / 2827211
    assert rows[0]["views_per_hour"] == 2827211 / (12 / 3600)


def test_build_rows_without_likes():
    rows = build_rows([video(video_likes=0, video_views=0)])
    assert rows[0]["like_ratio"] is None
    assert rows[0]["comment_ratio"] is None


def test_format_table_has_header_and_one_row_per_video():
    lines = format_table(build_rows([video(), video(video_id="OTHER")]))
    assert lines[0].strip().startswith("Video")
    assert set(lines[1]) == {"-"}
    assert len(lines) == 4


def test_format_table_marks_missing_rate():
    lines = format_table(build_rows([video(video_duration=None)]))
    assert "n/a" in lines[2]


def test_format_table_shows_compact_rate():
    lines = format_table(build_rows([video()]))
    assert "848.2M/h" in lines[2]


def test_format_legend_maps_ids_to_titles():
    legend = format_legend(build_rows([video()]))
    assert legend == ["C7REVNM_EWY = Meow Chef (0:12)"]


def test_format_legend_skips_missing_titles():
    assert format_legend(build_rows([video(video_title=None)])) == []