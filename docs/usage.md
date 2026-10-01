# Usage

Back to the [README](../README.md). See also
[metrics and history](metrics.md), [comparison and watchlists](comparison.md)
and the [API server](server.md).

## Interactive mode

1. Run the tool and paste the requested values when prompted:

   ```bash
   python src\YST.py
   ```

   On start-up the tool prints its ASCII banner:

   ```text
    __  _____________
    \ \/ / ___/_  __/
     \  /\__ \ / /
     / /___/ // /
    /_//____//_/
   ```

   ![Running YST](../assets/screenshots/gui-run.png)

2. Enter the required details:

   ![Entering details](../assets/screenshots/gui-input.png)

   Accepted inputs:

   | Field            | Example                                                                                      |
   | ---------------- | -------------------------------------------------------------------------------------------- |
   | Full channel URL | `https://www.youtube.com/c/ThatLittlePuff` · `https://www.youtube.com/channel/UClFN9LShD_Pv0wnSeUKbUZw` |
   | Channel ID       | `UClFN9LShD_Pv0wnSeUKbUZw`                                                                    |
   | Channel handle   | `@ThatLittlePuff`                                                                             |
   | Full video URL   | `https://www.youtube.com/watch?v=C7REVNM_EWY` · `https://youtu.be/C7REVNM_EWY`                |
   | Video ID         | `C7REVNM_EWY`                                                                                 |

Anything the command line does not provide is asked for, so `-channel_id` with
a missing video still works interactively.

## Sub-commands

Shortcuts for the frequent runs. Each one expands to the flags shown, and every
option still works afterwards:

| Command           | Equivalent to                                           |
| ----------------- | ------------------------------------------------------- |
| `video <ID>`      | `-video_id=<ID>` (channel is asked for)                 |
| `channel <ID>`    | `-channel_id=<ID> -latest_video=True`                   |
| `latest <ID>`     | `-channel_id=<ID> -latest_video=True`                   |
| `monitor <ID>`    | `-channel_id=<ID> -latest_video=True -log_mode=True`    |
| `compare <ID...>` | `-compare=<ID1,ID2,...>`                                |
| `export <ID>`     | `-channel_id=<ID> -export=csv`                          |
| `serve <ID>`      | `-channel_id=<ID> -serve=True -latest_video=True -log_mode=True` |

```bash
python src/YST.py --help
python src/YST.py monitor UCifZaTQPiHE2QRgEwDNfhug -sleep_time=60 -dashboard=True
python src/YST.py compare C7REVNM_EWY Xknt3_QJY7o
```

## Command-line mode

Pass all arguments at once:

```bash
python src\YST.py -channel_id=UClFN9LShD_Pv0wnSeUKbUZw -video_id=FJDVKeh7RJI -sleep_time=5 -log_mode=True
```

![Command-line arguments](../assets/screenshots/cli-arguments.png)

Values can be attached with `=` or passed as the next token, so
`-sleep_time=5` and `-sleep_time 5` are the same. Boolean flags accept
`true`/`false`, `1`/`0`, `yes`/`no` and `on`/`off`, in any case.

### Options

| Argument             | Type           | Default       | Description                                     |
| -------------------- | -------------- | ------------- | ----------------------------------------------- |
| `-channel_id`        | string         | —             | Channel ID, `@handle`, or channel URL            |
| `-video_id`          | string         | —             | Video ID or video URL                            |
| `-sleep_time`        | int (seconds)  | `2`           | Delay between two statistic refreshes            |
| `-log_mode`          | `True`/`False` | `False`       | Print results to the console instead of files    |
| `-latest_video`      | `True`/`False` | `False`       | Fetch the latest video ID from the channel       |
| `-enable_log`        | metric list    | all           | Log only the listed metrics                      |
| `-disable_log`       | metric list    | —             | Log everything except the listed metrics         |
| `-list_logs`         | `True`/`False` | `False`       | Print the available metric keys and exit         |
| `-snapshot_time`     | int (sec)      | `60`          | How often a snapshot is written to the history   |
| `-history`           | int (hours)    | `24`          | Window used by the dashboard and the export      |
| `-dashboard`         | `True`/`False` | `False`       | Add the history summary and sparkline            |
| `-chart`             | `True`/`False` | `False`       | Draw block charts of the history window          |
| `-report`            | `True`/`False` | `False`       | Write an HTML report with SVG charts and exit    |
| `-db`                | path           | `data/yst.db` | Location of the history database                 |
| `-export`            | `csv`/`json`   | —             | Export the stored history and exit               |
| `-export_path`       | path           | `exports`     | Folder for exported files                        |
| `-compare`           | video list     | —             | Compare videos side by side and exit             |
| `-compare_channels`  | channel list   | —             | Compare channels side by side and exit           |
| `-watchlist`         | path           | —             | Monitor every channel listed in a text file      |
| `-serve`             | `True`/`False` | `False`       | Serve the numbers over HTTP                      |
| `-serve_host`        | host           | `127.0.0.1`   | Interface the API server binds to                |
| `-serve_port`        | int (port)     | `9132`        | Port for the API server, 1–65535                |

![Command-line result](../assets/screenshots/cli-result.png)

> Output is colored through `colorama`, so colors render in the classic Command Prompt too.
> When stdout is not a terminal (e.g. piped to a file), escape codes are stripped automatically.

## Output files

Statistics are refreshed and written to the `txt/` folder next to the current
working directory:

```
txt/
├── channel_subscribers.txt
├── channel_videoCount.txt
├── channel_viewsCount.txt
├── video_comments.txt
├── video_likes.txt
└── video_views.txt
```

Only the metrics selected with `-enable_log` / `-disable_log` are written, see
[metrics and history](metrics.md#choosing-which-metrics-to-log).

## Examples

```bash
# all metrics on the console every 5s
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=Xknt3_QJY7o -sleep_time=5 -log_mode=True

# quiet: only write txt/ files, no console output
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=Xknt3_QJY7o -sleep_time=10

# track the newest video of the channel automatically
python src/YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -latest_video=True -sleep_time=30

# only two metrics
python src/YST.py -channel_id=UC... -video_id=... -enable_log subs, video_views

# everything except two metrics
python src/YST.py -channel_id=UC... -video_id=... -disable_log subs, video_views

# fast refresh (minimum is 1s)
python src/YST.py -channel_id=UC... -video_id=... -sleep_time=1 -log_mode=True

# handles and URLs instead of IDs
python src/YST.py -channel_id=@ThatLittlePuff -video_id=https://youtu.be/C7REVNM_EWY

# list the metric keys and exit
python src/YST.py -list_logs=True

# serve the same numbers over HTTP
python src/YST.py serve UCifZaTQPiHE2QRgEwDNfhug -serve_port=9132

# interactive, everything is asked
python src/YST.py
```

## Scheduled runs

The tool is built to be left running in the background:

```bash
# hourly, quiet, only the newest video
0 * * * * cd /workspaces/YST && ./scripts/yst -channel_id=UC... -latest_video=True -sleep_time=3600 -disable_log subs >> yst.log 2>&1
```

Snapshot interval (`-snapshot_time`) is independent of the refresh interval, so
polling the API slowly while keeping a dense history is fine — though every
refresh costs API quota, so `-sleep_time` should stay well above 60s for long
runs.