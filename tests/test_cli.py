import sys

sys.path.insert(0, "src")

from YST_lib.cli import check_arg, extract_video_id, parse_bool, parse_int, parse_stat_list


def test_check_arg_with_equals():
    parsed = check_arg(["-channel_id=UCabc", "-video_id=xyz", "-sleep_time=5"])
    assert parsed == {"channel_id": "UCabc", "video_id": "xyz", "sleep_time": "5"}


def test_check_arg_with_space():
    parsed = check_arg(["-channel_id", "UCabc", "-sleep_time", "5"])
    assert parsed == {"channel_id": "UCabc", "sleep_time": "5"}


def test_check_arg_keeps_equals_inside_value():
    assert check_arg(["-video_id=abc=def"]) == {"video_id": "abc=def"}


def test_check_arg_without_arguments():
    assert check_arg([]) == {}


def test_parse_bool_variants():
    assert parse_bool("True", False) is True
    assert parse_bool("yes", False) is True
    assert parse_bool("1", False) is True
    assert parse_bool("False", True) is False
    assert parse_bool("off", True) is False
    assert parse_bool(None, True) is True


def test_parse_int_falls_back_on_garbage(capsys):
    assert parse_int("abc", 7, "sleep_time") == 7
    assert "sleep_time" in capsys.readouterr().out


def test_parse_int_rejects_non_positive(capsys):
    assert parse_int("-5", 3, "sleep_time") == 3
    assert "1 or more" in capsys.readouterr().out


def test_parse_stat_list_normalizes_and_dedupes():
    assert parse_stat_list("subs, Subscribers ,video_views") == ["subs", "video_views"]


def test_parse_stat_list_rejects_unknown_metric():
    try:
        parse_stat_list("subs,nope")
    except SystemExit as exit_code:
        assert "nope" in str(exit_code)
    else:
        raise AssertionError("expected SystemExit")


def test_parse_stat_list_of_empty_string():
    assert parse_stat_list("") == []


def test_extract_video_id_variants():
    assert extract_video_id("C7REVNM_EWY") == "C7REVNM_EWY"
    assert extract_video_id("https://www.youtube.com/watch?v=C7REVNM_EWY") == "C7REVNM_EWY"
    assert extract_video_id("https://www.youtube.com/watch?v=C7REVNM_EWY&t=42s") == "C7REVNM_EWY"
    assert extract_video_id("https://youtu.be/C7REVNM_EWY") == "C7REVNM_EWY"
    assert extract_video_id("https://www.youtube.com/shorts/C7REVNM_EWY") == "C7REVNM_EWY"
    assert extract_video_id("https://www.youtube.com/live/C7REVNM_EWY") == "C7REVNM_EWY"