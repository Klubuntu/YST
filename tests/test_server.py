import json
import threading

import pytest

from YST_lib.history import METRIC_KEYS, connect, record
from YST_lib.server import ApiError, Context, build_server, render_html, resolve


class FakeFetcher:
    def __init__(self, values=None, hidden=False, error=None):
        self.values_to_return = values or {}
        self.hidden = hidden
        self.error = error
        self.calls = 0

    def values(self, channel_id, video_id):
        self.calls += 1
        if self.error:
            raise self.error
        return dict(self.values_to_return), {"subs_hidden": int(self.hidden)}


def make_values(**overrides):
    values = {key: 1 for key in METRIC_KEYS}
    values.update(overrides)
    return values


def snapshot(context, values=None, **meta):
    return record(
        context.connection,
        context.channel_id,
        context.video_id or "",
        values if values is not None else make_values(),
        {"subs_hidden": 0, **meta},
    )


@pytest.fixture
def database(tmp_path):
    connection = connect(str(tmp_path / "yst.db"), shared=True)
    yield connection
    connection.close()


@pytest.fixture
def context(database):
    return Context(database, "UCtest", "abc123", hours=6, fetcher=FakeFetcher(make_values(subs=42)))


def test_index_lists_endpoints(context):
    status, payload = resolve("/", {}, context)
    assert status == 200
    assert payload["channel_id"] == "UCtest"
    assert payload["metric_keys"] == list(METRIC_KEYS)
    assert payload["endpoints"]["live"] == "/live/<metric>"


def test_metrics_endpoint_uses_selector_keys(context):
    status, payload = resolve("/metrics", {}, context)
    assert status == 200
    assert [item["key"] for item in payload["metrics"]] == list(METRIC_KEYS)
    assert payload["metrics"][0]["file"] == "channel_subscribers.txt"


def test_get_returns_stored_value(context):
    snapshot(context, make_values(subs=500, video_views=1200))
    status, payload = resolve("/get/video_views", {}, context)
    assert status == 200
    assert payload["value"] == 1200
    assert payload["recorded_at"]
    assert context.fetcher.calls == 0


def test_get_accepts_alias(context):
    snapshot(context, make_values(video_views=99))
    status, payload = resolve("/get/views", {}, context)
    assert status == 200
    assert payload["metric"] == "video_views"
    assert payload["value"] == 99


def test_get_without_snapshot_is_404(context):
    status, payload = resolve("/get/subs", {}, context)
    assert status == 404
    assert "No snapshot" in payload["error"]


def test_unknown_metric_lists_alternatives(context):
    status, payload = resolve("/get/nope", {}, context)
    assert status == 404
    assert payload["available"] == list(METRIC_KEYS)


def test_get_without_metric_is_404(context):
    snapshot(context)
    status, payload = resolve("/get/", {}, context)
    assert status == 404
    assert "one metric" in payload["error"]


def test_live_fetches_and_records(context):
    snapshot(context, make_values(subs=1))
    status, payload = resolve("/live/subs", {}, context)
    assert status == 200
    assert payload["value"] == 42
    assert payload["recorded_at"] is None
    assert context.fetcher.calls == 1
    assert resolve("/get/subs", {}, context)[1]["value"] == 42


def test_hidden_subscribers_report_none(context):
    context.fetcher.hidden = True
    status, payload = resolve("/live/subs", {}, context)
    assert status == 200
    assert payload["value"] is None
    assert payload["hidden"] is True


def test_stored_hidden_subscribers_report_none(context):
    context.fetcher.hidden = True
    resolve("/live/subs", {}, context)
    payload = resolve("/get/subs", {}, context)[1]
    assert payload["value"] is None
    assert payload["hidden"] is True


def test_api_failure_becomes_502(context):
    context.fetcher.error = ApiError("The daily API quota is spent.")
    status, payload = resolve("/live/subs", {}, context)
    assert status == 502
    assert "quota" in payload["error"]


def test_all_returns_every_metric(context):
    snapshot(context, make_values(subs=7, video_likes=8))
    status, payload = resolve("/all", {}, context)
    assert status == 200
    assert payload["metrics"]["subs"] == 7
    assert payload["metrics"]["video_likes"] == 8


def test_history_returns_series_and_change(context):
    base = int(__import__("time").time()) - 3600
    record(context.connection, "UCtest", "abc123", make_values(video_views=100), {"subs_hidden": 0})
    context.connection.execute("UPDATE snapshots SET recorded_at = ?", (base,))
    record(context.connection, "UCtest", "abc123", make_values(video_views=400), {"subs_hidden": 0})
    context.connection.execute("UPDATE snapshots SET recorded_at = ?", (base + 3600,))
    context.connection.commit()

    status, payload = resolve("/history/video_views", {}, context)
    assert status == 200
    assert payload["count"] == 2
    assert [item["value"] for item in payload["samples"]] == [100, 400]
    assert payload["change"]["change"] == 300


def test_unknown_path_lists_paths(context):
    status, payload = resolve("/nope", {}, context)
    assert status == 404
    assert "/metrics" in payload["paths"]


def test_render_html_escapes_and_links(context):
    snapshot(context, make_values(subs=1234))
    status, payload = resolve("/get/subs", {}, context)
    html = render_html(payload, "/get/subs", {})
    assert status == 200
    assert html.startswith("<!DOCTYPE html>")
    assert "1 234" in html
    assert "/live/video_views" in html
    assert "<style>" in html


def test_render_html_shows_hidden(context):
    snapshot(context, make_values(subs=1))
    context.connection.execute("UPDATE snapshots SET subs_hidden = 1")
    context.connection.commit()
    payload = resolve("/get/subs", {}, context)[1]
    assert "hidden" in render_html(payload, "/get/subs", {})


def test_render_html_escapes_metric_label(context):
    html = render_html({"metric": "x", "label": "<script>", "value": 1}, "/get/x", {})
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_handler_serves_json_and_html(database):
    context = Context(database, "UCtest", "abc123", hours=6, fetcher=FakeFetcher(make_values()))
    snapshot(context, make_values(subs=5))
    httpd = build_server("127.0.0.1", 0, context)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address

    import urllib.request

    with urllib.request.urlopen(f"http://{host}:{port}/get/subs") as response:
        assert response.headers["Content-Type"].startswith("application/json")
        assert json.loads(response.read())["value"] == 5

    with urllib.request.urlopen(f"http://{host}:{port}/get/subs?format=html") as response:
        body = response.read().decode()
        assert response.headers["Content-Type"].startswith("text/html")
        assert "<style>" in body

    with pytest.raises(Exception):
        urllib.request.urlopen(f"http://{host}:{port}/nope")

    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)