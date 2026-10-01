import json
import threading
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from YST_lib.cli import STAT_FILES, api_error_message, normalize_stat
from YST_lib.dashboard import METRIC_LABELS, format_number
from YST_lib.history import METRIC_KEYS, changes, latest, record, series
from YST_lib.required import API_KEY, API_URL, REQUEST_TIMEOUT

CHANNEL_METRICS = ("subs", "channel_views", "channel_videos")
VIDEO_METRICS = ("video_views", "video_likes", "video_comments")

STYLE = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 2rem 1rem;
  font: 16px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  background: #0f1115;
  color: #e6e6e6;
}
main { max-width: 46rem; margin: 0 auto; }
h1 { font-size: 1.5rem; margin: 0 0 .25rem; }
h2 { font-size: 1.1rem; margin: 2rem 0 .5rem; color: #d7a800; }
p.lede { margin: 0 0 1.5rem; color: #9aa0a6; }
table { width: 100%; border-collapse: collapse; margin: .5rem 0 1rem; }
th, td { text-align: left; padding: .5rem .6rem; border-bottom: 1px solid #2a2e35; }
th { font-weight: 600; color: #9aa0a6; font-size: .8rem; text-transform: uppercase; }
td.value { font-variant-numeric: tabular-nums; font-weight: 600; }
code { background: #1a1d23; padding: .1rem .35rem; border-radius: 3px; font-size: .9em; }
a { color: #7fb5ff; }
.hidden { color: #9aa0a6; font-style: italic; }
footer { margin-top: 2.5rem; color: #6b7076; font-size: .8rem; }
"""


def _escape(value):
    return escape(str(value), quote=True)


class ApiError(Exception):
    """Raised instead of exiting, so a request failure becomes a 502."""


class LiveFetcher:
    """Reads the channel and video statistics straight from the API."""

    def __init__(self, timeout=REQUEST_TIMEOUT):
        self.timeout = timeout

    def _get(self, path):
        import requests

        url = f"{API_URL}/{path}"
        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.RequestException as e:
            raise ApiError(f"Network error: {e}") from e
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if not response.ok:
            raise ApiError(api_error_message(response, payload))
        return payload

    def channel(self, channel_id):
        try:
            statistics = self._get(f"channels?part=statistics&id={channel_id}&key={API_KEY}")["items"][0][
                "statistics"
            ]
        except (KeyError, IndexError, TypeError) as e:
            raise ApiError("Invalid Channel ID") from e
        hidden = bool(statistics.get("hiddenSubscriberCount", False))
        return {
            "subs": 0 if hidden else int(statistics.get("subscriberCount", 0) or 0),
            "channel_views": int(statistics.get("viewCount", 0) or 0),
            "channel_videos": int(statistics.get("videoCount", 0) or 0),
        }, {"subs_hidden": int(hidden)}

    def video(self, video_id):
        query = f"videos?part=snippet,contentDetails,statistics&id={video_id}&key={API_KEY}"
        try:
            item = self._get(query)["items"][0]
        except (KeyError, IndexError, TypeError) as e:
            raise ApiError("Invalid Video ID") from e
        statistics = item.get("statistics", {})
        snippet = item.get("snippet", {})
        details = item.get("contentDetails", {})
        return {
            "video_views": int(statistics.get("viewCount", 0) or 0),
            "video_likes": int(statistics.get("likeCount", 0) or 0),
            "video_comments": int(statistics.get("commentCount", 0) or 0),
        }, {
            "video_title": snippet.get("title"),
            "video_duration": details.get("duration"),
            "video_published_at": snippet.get("publishedAt"),
        }

    def values(self, channel_id, video_id):
        metrics, meta = self.channel(channel_id)
        if video_id:
            video_metrics, video_meta = self.video(video_id)
            metrics.update(video_metrics)
            meta.update(video_meta)
        return metrics, meta


class Context:
    """Everything a request needs, shared by the threaded handlers."""

    def __init__(self, connection, channel_id, video_id, hours=24, fetcher=None):
        self.connection = connection
        self.channel_id = channel_id
        self.video_id = video_id
        self.hours = hours
        self.fetcher = fetcher or LiveFetcher()
        self.lock = threading.Lock()

    def snapshot(self, video_id=None):
        with self.lock:
            return latest(self.connection, self.channel_id, self.video_id if video_id is None else video_id)

    def record_live(self, values, meta):
        with self.lock:
            return record(
                self.connection,
                self.channel_id,
                self.video_id or "",
                values,
                {**meta, "subs_hidden": int(meta.get("subs_hidden", False))},
            )

    def series(self, key, hours=None):
        with self.lock:
            return series(self.connection, self.channel_id, key, self.video_id, hours or self.hours)

    def changes(self, hours=None):
        with self.lock:
            return changes(self.connection, self.channel_id, self.video_id, hours or self.hours)


def _metric_value(row, key):
    if key == "subs" and row.get("subs_hidden"):
        return None
    value = row.get(key)
    return int(value) if isinstance(value, (int, float)) else value


def _payload(key, value, context, recorded_at, hidden=False):
    return {
        "metric": key,
        "label": METRIC_LABELS.get(key, key),
        "value": value,
        "hidden": hidden,
        "channel_id": context.channel_id,
        "video_id": context.video_id or None,
        "recorded_at": recorded_at,
        "window_hours": context.hours,
    }


def stored(key, context):
    row = context.snapshot()
    if not row:
        raise LookupError(f"No snapshot stored for {context.channel_id} yet. Run the monitor first.")
    hidden = key == "subs" and bool(row.get("subs_hidden"))
    return _payload(key, _metric_value(row, key), context, row["recorded_at"], hidden)


def live(key, context):
    values, meta = context.fetcher.values(context.channel_id, context.video_id)
    context.record_live(values, meta)
    hidden = key == "subs" and bool(meta.get("subs_hidden"))
    return _payload(key, None if hidden else _metric_value(values, key), context, None, hidden)


def resolve(path, query, context):
    """Map a request path to (status, payload). Pure, apart from the API read."""
    segments = [part for part in path.split("/") if part]

    if not segments:
        return 200, index(context)
    head, rest = segments[0], segments[1:]

    if head == "health":
        return 200, {"status": "ok", "channel_id": context.channel_id, "video_id": context.video_id}

    if head in ("get", "live"):
        if len(rest) != 1:
            return 404, {"error": f"Use /{head}/<metric>, one metric at a time."}
        key = normalize_stat(rest[0])
        if key is None:
            return 404, {"error": f"Unknown metric '{rest[0]}'", "available": list(METRIC_KEYS)}
        try:
            payload = live(key, context) if head == "live" else stored(key, context)
        except LookupError as e:
            return 404, {"error": str(e)}
        except ApiError as e:
            return 502, {"error": str(e)}
        return 200, payload

    if head == "history":
        if len(rest) != 1:
            return 404, {"error": "Use /history/<metric>"}
        key = normalize_stat(rest[0])
        if key is None:
            return 404, {"error": f"Unknown metric '{rest[0]}'", "available": list(METRIC_KEYS)}
        samples = context.series(key)
        delta = context.changes().get(key)
        return 200, {
            "metric": key,
            "label": METRIC_LABELS.get(key, key),
            "channel_id": context.channel_id,
            "video_id": context.video_id or None,
            "window_hours": context.hours,
            "count": len(samples),
            "samples": [{"recorded_at": at, "value": value} for at, value in samples],
            "change": delta,
        }

    if head == "metrics":
        return 200, {
            "metrics": [
                {"key": key, "label": METRIC_LABELS.get(key, key), "file": STAT_FILES[key]}
                for key in METRIC_KEYS
            ]
        }

    if head == "all":
        row = context.snapshot()
        if not row:
            return 404, {"error": f"No snapshot stored for {context.channel_id} yet."}
        hidden = bool(row.get("subs_hidden"))
        return 200, {
            "channel_id": context.channel_id,
            "video_id": context.video_id or None,
            "recorded_at": row["recorded_at"],
            "metrics": {
                key: (None if key == "subs" and hidden else int(row.get(key, 0) or 0))
                for key in METRIC_KEYS
            },
        }

    return 404, {"error": "Not found", "paths": ["/", "/metrics", "/get/<metric>", "/live/<metric>", "/history/<metric>"]}


def render_html(payload, path="", query=None):
    """One small template for every successful response."""
    query = query or {}
    if isinstance(payload, dict) and "error" in payload:
        return _page(f"<h1>404</h1><p>{_escape(payload['error'])}</p>", query)

    parts = []
    if "metrics" in payload and isinstance(payload["metrics"], dict):
        rows = "".join(
            f"<tr><td>{_escape(METRIC_LABELS.get(key, key))}</td>"
            f"<td class='value'>{_escape('hidden' if value is None else format_number(value))}</td></tr>"
            for key, value in payload["metrics"].items()
        )
        parts.append(f"<h2>Stored snapshot</h2><table>{rows}</table>")
    elif "metrics" in payload and isinstance(payload["metrics"], list):
        rows = "".join(
            f"<tr><td><code>{_escape(item['key'])}</code></td><td>{_escape(item['label'])}</td>"
            f"<td>{_escape(item['file'])}</td></tr>"
            for item in payload["metrics"]
        )
        parts.append(f"<h2>Metrics</h2><table><tr><th>Key</th><th>Label</th><th>File</th></tr>{rows}</table>")
    elif "samples" in payload:
        rows = "".join(
            f"<tr><td>{_escape(at)}</td><td class='value'>{_escape(format_number(value))}</td></tr>"
            for at, value in ((item["recorded_at"], item["value"]) for item in payload["samples"][-200:])
        )
        change = payload.get("change") or {}
        summary = ""
        if change:
            summary = (
                f"<p class='lede'>change {_escape(format_number(change['change']))}, "
                f"{_escape(format_number(change['per_hour']))}/h</p>"
            )
        parts.append(
            f"<h2>{_escape(payload.get('label', payload['metric']))} over {_escape(payload['window_hours'])}h</h2>"
            f"{summary}<table><tr><th>Recorded at</th><th>Value</th></tr>{rows}</table>"
        )
    elif "value" in payload:
        shown = "hidden" if payload["value"] is None else format_number(payload["value"])
        stamp = payload.get("recorded_at")
        note = "live" if stamp is None else f"recorded at {stamp}"
        parts.append(
            f"<h2>{_escape(payload.get('label', payload['metric']))}</h2>"
            f"<p class='value'>{_escape(shown)}</p><p class='lede'>{_escape(note)}</p>"
        )

    suffix = "?format=html" if query.get("format", [""])[0].lower() == "html" else ""
    links = "".join(
        f"<tr><td><a href='/{head}/{_escape(key)}{suffix}'><code>/{head}/{_escape(key)}</code></a></td></tr>"
        for key in METRIC_KEYS
        for head in ("get", "live")
    )
    parts.append(
        "<h2>Endpoints</h2><table>"
        "<tr><th>Path</th></tr>"
        f"<tr><td><a href='/?format=html'><code>/</code></a></td></tr>"
        f"<tr><td><a href='/metrics{suffix}'><code>/metrics</code></a></td></tr>"
        "<tr><td><code>/all</code></td></tr>"
        "<tr><td><code>/history/&lt;metric&gt;</code></td></tr>"
        f"{links}</table>"
    )
    return _page("".join(parts), query)


def index(context):
    return {
        "service": "YST",
        "channel_id": context.channel_id,
        "video_id": context.video_id or None,
        "window_hours": context.hours,
        "endpoints": {
            "metrics": "/metrics",
            "all": "/all",
            "get": "/get/<metric>",
            "live": "/live/<metric>",
            "history": "/history/<metric>",
            "health": "/health",
        },
        "metric_keys": list(METRIC_KEYS),
    }


def _page(body, query):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YST</title>
<style>{STYLE}</style>
</head>
<body><main>{body}
<footer>Generated by YouTube Stats Tool (YST)</footer>
</main></body>
</html>"""


def make_handler(context):
    class Handler(BaseHTTPRequestHandler):
        server_version = "YST"

        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            wants = query.get("format", [""])[0].lower() == "html" or "text/html" in (
                self.headers.get("Accept") or ""
            )
            try:
                status, payload = resolve(parsed.path, query, context)
            except Exception as e:  # a bad request must not kill the server
                status, payload = 500, {"error": str(e)}
            if wants and status == 200:
                body = render_html(payload, parsed.path, query)
                content_type = "text/html; charset=utf-8"
            elif wants:
                body = _page(f"<h1>{status}</h1><p>{_escape(payload.get('error', ''))}</p>", query)
                content_type = "text/html; charset=utf-8"
            else:
                body = json.dumps(payload, indent=2)
                content_type = "application/json; charset=utf-8"
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    return Handler


def build_server(host, port, context):
    return ThreadingHTTPServer((host, port), make_handler(context))