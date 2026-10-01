# 📺 YouTube Stats Tool (YST)

![banner](assets/banner.png)

Command-line tool that tracks live YouTube channel and video statistics and logs
them to disk, so you can see how your numbers change over time.

## 📖 Description

YST queries the official YouTube Data API v3 and, on a configurable interval,
refreshes:

| Channel statistics | Video statistics        |
| ------------------ | ----------------------- |
| Subscribers        | Views                   |
| Total views        | Likes                   |
| Video count        | Comments                |

Two ways of running it:

- **Interactive** – start the script and paste a channel and a video link or ID when prompted.
- **Command line** – pass every value as an argument (handy for scripts and scheduled tasks).

The tool is also shipped as a Windows executable, so Python is not required to use it.

## ⚙️ Requirements

- **Python 3.8+** – [download](https://www.python.org/downloads/release/python-3810/)
  — or use the compiled Windows build below.
- **`requests`** – installed automatically with `pip install -r requirements.txt`; when
  building the executable, PyInstaller bundles it.
- **A YouTube Data API key** – stored in `src/YST_lib/required.py` (`API_KEY`).
- **Windows only** – for the pre-built `.exe` release.

## 📥 Installation

### Option A – Windows executable (no Python needed)

- [Download `YST.exe` from the repository](https://github.com/Klubuntu/YST/raw/main/dist/YST.exe)
- or grab it from the [v0.8 release page](https://github.com/Klubuntu/YST/releases/download/v0.8/YST.exe)

Double-click the file and follow the prompts.

### Option B – Run from source

```bash
# 1. Get the code (branch: main)
git clone https://github.com/Klubuntu/YST.git
cd YST

# 2. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt
```

Alternatively, [download the code as a ZIP](https://github.com/Klubuntu/YST/archive/refs/heads/main.zip).

## 🚀 Usage

### Interactive mode

1. Run the tool and paste the requested values when prompted:

   ```bash
   python src\YST.py
   ```

   ![Running YST](assets/screenshots/gui-run.png)

2. Enter the required details:

   ![Entering details](assets/screenshots/gui-input.png)

   Accepted inputs:

   | Field              | Example                                                                                      |
   | ------------------ | -------------------------------------------------------------------------------------------- |
   | Full channel URL   | `https://www.youtube.com/c/ThatLittlePuff` · `https://www.youtube.com/channel/UClFN9LShD_Pv0wnSeUKbUZw` |
   | Channel ID         | `UClFN9LShD_Pv0wnSeUKbUZw`                                                                    |
   | Full video URL     | `https://www.youtube.com/watch?v=C7REVNM_EWY`                                                 |
   | Video ID           | `C7REVNM_EWY`                                                                                 |

### Command-line mode

Pass all arguments at once:

```bash
python src\YST.py -channel_id=UClFN9LShD_Pv0wnSeUKbUZw -video_id=FJDVKeh7RJI -sleep_time=5 -log_mode=True
```

![Command-line arguments](assets/screenshots/cli-arguments.png)

#### Arguments

| Argument       | Type           | Default | Description                                        |
| -------------- | -------------- | ------- | -------------------------------------------------- |
| `-channel_id`  | string         | —       | Channel ID, or channel URL in interactive mode      |
| `-video_id`    | string         | —       | Video ID, or video URL in interactive mode           |
| `-sleep_time`  | int (seconds)  | `2`     | Delay between two statistic refreshes                |
| `-log_mode`    | `True`/`False` | `False` | Print results to the console instead of only files   |
| `-latest_video`| `True`/`False` | `False` | Fetch the latest video ID from the channel           |

![Command-line result](assets/screenshots/cli-result.png)

> Colors are not rendered in the classic Command Prompt — use Windows Terminal, or the EXE build.

### Output files

Statistics are refreshed and written to the `txt/` folder next to the current working directory:

```
txt/
├── channel_subscribers.txt
├── channel_videoCount.txt
├── channel_viewsCount.txt
├── video_comments.txt
├── video_likes.txt
└── video_views.txt
```

### Windows launcher

`scripts/run.bat` runs the tool with a preset channel and video:

```bat
scripts\run.bat
```

## 📁 Project structure

```
.
├── src/                  # application source
│   ├── YST.py            # entry point
│   ├── YST_lib/          # arguments parsing, configuration, main loop
│   └── lib/              # shared helpers (terminal colors)
├── assets/               # screenshots and support badges used by this README
├── build/YST.spec        # PyInstaller recipe for the Windows executable
├── scripts/run.bat       # Windows launcher
├── tools/check_args.py   # small helper for inspecting CLI arguments
└── dist/                 # released executables
```

To rebuild the Windows executable:

```bash
pip install pyinstaller
pyinstaller build/YST.spec
```

## 📦 Releases

- [All releases](https://github.com/klubuntu/YST/releases/)
- [In-development branch](https://github.com/Klubuntu/YST/tree/future-change)

## 🗺️ Future improvements

- ~~Support for more texts (Members, Subscribers Status, etc.)~~ — *YouTube removed them from the public API*
- [ ] More stats to come

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