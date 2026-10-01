# 📺 YouTube Stats Tool (YST)

![banner](assets/banner.png)

Command-line tool that tracks YouTube channel and video statistics over time.
It refreshes the numbers on an interval, writes them to disk, keeps a local
history so growth is measurable, exports the result as CSV, JSON or an HTML
report, and can serve the same numbers over a small HTTP API.

| Channel statistics | Video statistics |
| ------------------ | ---------------- |
| Subscribers        | Views            |
| Total views        | Likes            |
| Video count        | Comments         |

Plus video length, publication date, hidden subscriber counts, comparisons
between videos or channels, and terminal charts.

## 🚀 Quick start

```bash
# Windows executable: double-click it and paste the requested values

# from source
git clone https://github.com/Klubuntu/YST.git
cd YST
pip install -r requirements.txt

# monitor a channel with console output, deltas and a summary
python src/YST.py monitor UCifZaTQPiHE2QRgEwDNfhug -dashboard=True

# compare two videos
python src/YST.py compare C7REVNM_EWY Xknt3_QJY7o

# export the stored history
python src/YST.py export UCifZaTQPiHE2QRgEwDNfhug

# serve the numbers over HTTP on http://127.0.0.1:9132
python src/YST.py serve UCifZaTQPiHE2QRgEwDNfhug
```

On Linux and macOS use `./scripts/yst` in place of `python src/YST.py`.
Stop a run with `Ctrl+C`; results land in `txt/`, history in `data/`.

## 📖 Documentation

| Document                                     | What it covers                                        |
| -------------------------------------------- | ----------------------------------------------------- |
| [Installation](docs/installation.md)         | Requirements, executables, source install, `.env` keys |
| [Usage](docs/usage.md)                       | Interactive mode, sub-commands, every option           |
| [Metrics and history](docs/metrics.md)       | Logged values, selection, deltas, dashboard, export   |
| [Comparison and watchlists](docs/comparison.md) | Comparing videos and channels, monitoring a watchlist |
| [API server](docs/server.md)           | HTTP endpoints, configuration, web pages              |
| [Development](docs/development.md)     | Layout, tests, CI, releases and signing, roadmap      |

Start with [usage](docs/usage.md) for the full option reference.

## 📦 Releases

- [All releases](https://github.com/klubuntu/YST/releases/) — `YST.exe` for
  Windows and `yst` for Linux and macOS, each with a checksum
- [In-development branch](https://github.com/Klubuntu/YST/tree/future-change)

## 🗺️ Roadmap

Planned: documented scheduled runs (cron, systemd, Task Scheduler),
channel-level trends in the report, and threshold alerts. Member counts and
subscriber status are unavailable — YouTube removed them from the public API.
The [full roadmap](docs/development.md#roadmap) has the details.

## 💖 Support this project

All pull requests, translations, and corrections are welcome — see [open an issue or a PR](https://github.com/Klubuntu/YST/pulls).

If the tool is useful to you, you can support its development:

[![Pull Request](assets/support/pull-request.png)](https://github.com/Klubuntu/YST/pulls)
[![Buy Me A Coffee](assets/support/buy-me-a-coffee.png)](https://www.buymeacoffee.com/klubuntu)
[![Support on Patreon](assets/support/patreon.png)](https://patreon.com/klubuntu)
[![Support with PayPal](assets/support/paypal.png)](https://www.paypal.com/biz/profile/OnerOSTeam)

## 📄 License

No license file has been added to this repository yet. Until one is added, the
code is not granted any usage rights — please open an issue if you want to
reuse it.