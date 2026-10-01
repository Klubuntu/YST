# Development

Back to the [README](../README.md).

## 📁 Project structure

```
.
├── src/                  # application source
│   ├── YST.py            # entry point
│   └── YST_lib/          # required, cli, arguments, banner, history,
│                         # dashboard, compare, watchlist, exporter, report,
│                         # server, main
├── assets/               # screenshots and support badges used by the README
├── build/YST.spec        # PyInstaller recipe for the executables
├── docs/                 # this documentation set
├── scripts/              # run.bat for Windows, yst wrapper, build scripts
├── tests/                # pytest suite
├── tools/check_args.py   # small helper for inspecting CLI arguments
└── dist/                 # released executables
```

Module map inside `src/YST_lib/`:

| Module      | Responsibility                                             |
| ----------- | ---------------------------------------------------------- |
| `required`  | Configuration, `.env` loading, output folder, colorama init |
| `cli`       | Argument, ID, duration, metric and API error parsing        |
| `arguments` | Resolves flags into the `options` dict, prompts when needed  |
| `banner`    | ASCII banner                                               |
| `main`      | API calls, refresh loop, file writing, wiring               |
| `history`   | SQLite snapshots, deltas, window queries                    |
| `dashboard` | Delta lines, sparkline, block charts, details               |
| `compare`   | Video comparison table                                      |
| `watchlist` | Channel comparison table and watchlist rendering            |
| `exporter`  | CSV and JSON output                                         |
| `report`    | Self-contained HTML report with SVG charts                  |
| `server`    | HTTP API and its HTML pages, see [server](server.md)        |

Generated at runtime and ignored by git: `txt/` (latest values), `data/`
(history database), `exports/` (CSV, JSON and HTML output). `.env.example`
shows the recognised settings.

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

`pytest.ini` puts `src/` on the path, so the tests import the same modules the
tool runs. The suite covers argument parsing (both value forms, boolean and
integer validation, metric lists, sub-commands), the snapshot store against a
temporary SQLite file, dashboard and chart formatting, the comparison tables,
the watchlist parser, both export formats, the HTML report and the API server —
its routing, HTML pages and error paths are tested as plain functions, and one
test binds port `0` to check the handler itself.

Lint with pyflakes, the same check CI runs:

```bash
python -m pyflakes src tests
```

## 🔄 CI

`.github/workflows/ci.yml` runs on pushes to `main` and on pull requests:

- **test** – the pytest suite on Linux, Windows and macOS
- **lint** – pyflakes over `src` and `tests`
- **build** – PyInstaller on all three platforms from `build/YST.spec`, each
  uploaded as an artifact

To build the same binaries locally, `scripts/build.sh` does the current host
and `scripts/build-linux.sh` and `scripts/build-macos.sh` do the other one:

```bash
./scripts/build.sh          # current platform, outputs dist/
./scripts/build-linux.sh    # Linux binary, needs Docker
./scripts/build-macos.sh    # macOS binary, needs Docker
```

Both cross scripts build in a container, because PyInstaller cannot produce a
macOS binary on Linux or the other way round. `scripts/build.bat` is the
Windows equivalent.

## 📦 Releases

- [All releases](https://github.com/klubuntu/YST/releases/)
- [In-development branch](https://github.com/Klubuntu/YST/tree/future-change)

Publishing a release: tag the repository with `v*` and push.
`.github/workflows/release.yml` then runs the tests and lint, builds
`YST.exe`, `yst` (Linux) and `yst` (macOS), writes a SHA-256 checksum for each
and attaches everything to a GitHub release.

Signing is optional. Adding a `GPG_PRIVATE_KEY` secret (and optionally
`GPG_PASSPHRASE`) makes the workflow sign the combined checksum file and attach
`checksums.txt.asc` as well; without a key the signing steps are skipped and the
release publishes unsigned. GitHub does not expose secrets in a job-level `if`,
so the check happens in a step and gates the rest.

To verify a download:

```bash
sha256sum -c yst.sha256
gpg --verify checksums.txt.asc   # only for signed releases
```

## 🗺️ Roadmap

Done in this repository:

- [x] Automatic URL parsing — channel URLs, `@handle`, `youtu.be`, `/shorts/`, `/live/`
- [x] Local history of every snapshot with growth deltas
- [x] Dashboard with 24h summary, per-hour rates and sparkline
- [x] CSV and JSON export
- [x] Video comparison with like, comment and views-per-hour ratios
- [x] Channel comparison and a watchlist of several channels
- [x] Publication date and video length, and hidden subscriber counts
- [x] Terminal block charts over a longer window and a self-contained HTML report
- [x] Releases with Linux and macOS binaries, checksums and optional GPG signature
- [x] Sub-commands (`video`, `channel`, `latest`, `monitor`, `compare`, `export`, `serve`) next to the flags
- [x] `.env` configuration and messages for invalid keys, spent quota and rate limits
- [x] pytest suite and a CI workflow building the executables
- [x] Linux and macOS support through the source install and the releases
- [x] HTTP API server with JSON and small HTML pages, see [server](server.md)
- [ ] Authentication for the API server when it is not localhost-only
- [ ] Serving several channels over the API at once

Planned:

- [ ] Scheduled runs documented for cron, systemd and Task Scheduler
- [ ] Channel-level trends in the report, not only per video
- [ ] Alerting, for example when a video passes a views threshold
- ~~Support for more texts (Members, Subscribers Status, etc.)~~ — *YouTube removed them from the public API*

## 🤝 Contributing

Pull requests, translations and corrections are welcome. Keep changes focused,
add tests for new behaviour, run `python -m pytest` and `python -m pyflakes src tests`
before pushing, and match the commit style: a lowercase conventional prefix, an
imperative summary and, when the reason is not obvious, a short body after a
blank line.

```text
feat: draw terminal charts over the history window

`-chart=True` adds a block chart of video views, channel views and subscribers
next to the dashboard, scaled to the `-history` window and labelled with its
range.
```