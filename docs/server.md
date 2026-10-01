# API server

Back to the [README](../README.md).

`-serve=True` turns the run into a small HTTP API and, with `-log_mode` or
`-dashboard`, keeps the monitoring loop running next to it.

```bash
# monitor a channel and serve it on http://127.0.0.1:9132
python src/YST.py serve UCifZaTQPiHE2QRgEwDNfhug -latest_video=True

# or as flags
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=C7REVNM_EWY -serve=True -serve_port=9132
```

The channel and the video come from the command line, exactly as in every other
run, so the server exposes the one pair you selected.

## ⚙️ Configuration

| Option        | Environment      | Default     | Notes                                        |
| ------------- | ---------------- | ----------- | -------------------------------------------- |
| `-serve`      | —                | `False`     | Start the server                             |
| `-serve_host` | `YST_SERVE_HOST` | `127.0.0.1` | Interface to bind                            |
| `-serve_port` | `YST_SERVE_PORT` | `9132`      | Port, 1–65535                                |

A parameter always wins over the environment, and `.env` is read at start-up:

```
# .env
YST_SERVE_HOST=127.0.0.1
YST_SERVE_PORT=9132
```

**There is no authentication.** The default is `127.0.0.1`, so only this machine
can reach it. Binding `0.0.0.0` puts the API and your quota on the network —
the tool warns about this on start-up. Do not expose the port to the internet.

## 🔗 Endpoints

Metric keys are the same ones used by `-enable_log` and `-disable_log`, and the
same aliases work (`subscribers`, `views`, `likes`, `comments`, `videos`).

| Path                      | Cost       | What it returns                            |
| ------------------------- | ---------- | ------------------------------------------ |
| `/`                       | free       | Channel, video and the list of endpoints   |
| `/metrics`                | free       | Metric keys, labels and the `txt/` file     |
| `/all`                    | free       | Every metric from the last stored snapshot  |
| `/get/<metric>`           | free       | One metric from the last stored snapshot    |
| `/live/<metric>`          | **API**    | One fresh metric, and it stores a snapshot  |
| `/history/<metric>`       | free       | Every sample in the `-history` window       |
| `/health`                 | free       | `{"status": "ok", ...}`                    |

The difference between `/get` and `/live` is the point of the split: `/get`
reads the SQLite history and never touches the API, so a dashboard can poll it
as often as it likes. `/live` spends one API request — per refresh, not per
metric — so give it a minute between calls.

```bash
curl localhost:9132/get/subs
curl localhost:9132/live/video_views
curl localhost:9132/history/video_views
```

```json
{
  "metric": "subs",
  "label": "Subscribers",
  "value": 693,
  "hidden": false,
  "channel_id": "UCifZaTQPiHE2QRgEwDNfhug",
  "video_id": "O2ZaMpvoi0M",
  "recorded_at": 1790887468,
  "window_hours": 24
}
```

`recorded_at` is `null` for `/live`, since the value was not read from the
database. A channel that hides its subscriber count answers with
`"value": null, "hidden": true` instead of a zero.

### 🌐 Web pages

Every endpoint also serves a small HTML page, either with `?format=html` or by
sending `Accept: text/html` — one plain stylesheet, no external assets, no
JavaScript.

```
http://127.0.0.1:9132/               the index with every endpoint linked
http://127.0.0.1:9132/get/subs?format=html
http://127.0.0.1:9132/history/video_views?format=html
```

## ⚠️ Errors

| Status | Meaning                                                          |
| ------ | ---------------------------------------------------------------- |
| `404`  | Unknown path or metric, or no snapshot stored yet                 |
| `502`  | The API call failed — bad key, spent quota, rate limit            |

A failed request never takes the server down: the monitoring loop keeps its own
refresh running and reports the error separately.

## 🔀 Implementation notes

- `ThreadingHTTPServer`, so one slow request cannot block the others.
- The history connection is opened with `check_same_thread=False` and every
  query goes through one lock, because the monitoring thread and the request
  threads share the database.
- Routing lives in `resolve(path, query, context)`, which is a plain function
  returning `(status, payload)` — the tests exercise every path without opening
  a socket.
- No third-party dependency: `http.server` from the standard library only.