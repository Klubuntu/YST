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

def test_expand_subcommand_monitor():
    parsed = check_arg(["monitor", "UCabc", "-sleep_time", "60"])
    assert parsed == {
        "channel_id": "UCabc",
        "sleep_time": "60",
        "latest_video": "True",
        "log_mode": "True",
    }


def test_expand_subcommand_video():
    assert check_arg(["video", "abc123"]) == {"video_id": "abc123"}


def test_expand_subcommand_compare_joins_ids():
    assert check_arg(["compare", "a", "b", "c"]) == {"compare": "a,b,c"}


def test_expand_subcommand_export_defaults_to_csv():
    assert check_arg(["export", "UCabc"]) == {"channel_id": "UCabc", "export": "csv"}


def test_expand_subcommand_channel_uses_latest_video():
    assert check_arg(["channel", "UCabc"]) == {
        "channel_id": "UCabc",
        "latest_video": "True",
    }


def test_subcommand_requires_an_id():
    try:
        check_arg(["monitor", "-log_mode=True"])
    except SystemExit as exit_code:
        assert "needs an ID" in str(exit_code)
    else:
        raise AssertionError("expected SystemExit")


def test_flags_still_work_without_subcommand():
    assert check_arg(["-channel_id=UCabc", "-video_id=abc"]) == {
        "channel_id": "UCabc",
        "video_id": "abc",
    }


def test_load_env_file_reads_pairs(tmp_path):
    from YST_lib.required import load_env_file

    env = tmp_path / ".env"
    env.write_text("# comment\nYOUTUBE_API_KEY=abc123\nOTHER='quoted'\nbroken\n\nEMPTY=\n")
    loaded = load_env_file(str(env))
    assert loaded == {"YOUTUBE_API_KEY": "abc123", "OTHER": "quoted", "EMPTY": ""}


def test_load_env_file_without_file(tmp_path):
    from YST_lib.required import load_env_file

    assert load_env_file(str(tmp_path / "missing.env")) == {}


def test_api_error_message_for_known_reason():
    from YST_lib.cli import api_error_message

    class Response:
        status_code = 403
        ok = False

    payload = {"error": {"errors": [{"reason": "quotaExceeded"}]}}
    assert "quota" in api_error_message(Response(), payload).lower()


def test_api_error_message_for_unknown_status():
    from YST_lib.cli import api_error_message

    class Response:
        status_code = 500
        ok = False

    assert "500" in api_error_message(Response(), {})


def test_api_error_message_detects_invalid_key_by_message():
    from YST_lib.cli import api_error_message

    class Response:
        status_code = 400
        ok = False

    payload = {
        "error": {
            "code": 400,
            "message": "API key not valid. Please pass a valid API key.",
            "errors": [{"reason": "badRequest", "domain": "global"}],
            "status": "INVALID_ARGUMENT",
        }
    }
    assert "API key is invalid" in api_error_message(Response(), payload)


def test_api_error_message_reads_error_info_details():
    from YST_lib.cli import api_error_message

    class Response:
        status_code = 400
        ok = False

    payload = {
        "error": {
            "errors": [{"reason": "badRequest"}],
            "details": [{"@type": "ErrorInfo", "reason": "API_KEY_INVALID"}],
        }
    }
    assert "API key is invalid" in api_error_message(Response(), payload)


def test_api_error_message_falls_back_to_api_message():
    from YST_lib.cli import api_error_message

    class Response:
        status_code = 418
        ok = False

    payload = {"error": {"errors": [{"reason": "teapot"}], "message": "I am a teapot"}}
    assert api_error_message(Response(), payload) == "I am a teapot"
