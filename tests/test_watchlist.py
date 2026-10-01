import pytest

from YST_lib.watchlist import (
    build_rows,
    format_table,
    parse_watchlist,
    render_watchlist,
    views_per_video,
)


def channel(**overrides):
    data = {
        "channel_id": "UClFN9LShD_Pv0wnSeUKbUZw",
        "channel_title": "That Little Puff",
        "subs_hidden": False,
        "subs": 38600000,
        "channel_views": 37278025432,
        "channel_videos": 1290,
    }
    data.update(overrides)
    return data


def test_views_per_video():
    assert views_per_video(1000, 10) == 100


def test_views_per_video_without_videos_is_none():
    assert views_per_video(1000, 0) is None


def test_build_rows_calculates_ratio():
    rows = build_rows([channel()])
    assert rows[0]["views_per_video"] == 37278025432 / 1290


def test_build_rows_hides_subscribers_when_hidden():
    rows = build_rows([channel(subs_hidden=True, subs=0)])
    assert rows[0]["subs"] == 0


def test_format_table_keeps_full_channel_id():
    lines = format_table(build_rows([channel()]))
    assert lines[2].startswith("UClFN9LShD_Pv0wnSeUKbUZw")


def test_format_table_marks_missing_ratio():
    lines = format_table(build_rows([channel(channel_videos=0)]))
    assert "n/a" in lines[2]


def test_render_watchlist_shows_hidden_counts():
    lines = render_watchlist([channel(subs_hidden=True)])
    assert "hidden" in lines[0]
    assert "UClFN9LShD_Pv0wnSeUKbUZw" in lines[0]


def test_parse_watchlist_skips_comments_and_blanks(tmp_path):
    path = tmp_path / "watchlist.txt"
    path.write_text("# header\n\nUCone\nUCtwo  # trailing comment\nUCone\n")
    assert parse_watchlist(str(path)) == ["UCone", "UCtwo"]


def test_parse_watchlist_without_path():
    assert parse_watchlist(None) == []


def test_parse_watchlist_missing_file_exits():
    with pytest.raises(SystemExit):
        parse_watchlist("/tmp/does-not-exist-yst.txt")