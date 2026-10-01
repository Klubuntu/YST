# Installation

Back to the [README](../README.md).

## ⚙️ Requirements

- **Python 3.8+** – [download](https://www.python.org/downloads/release/python-3810/)
  — or use a compiled build and skip Python entirely.
- **`requests`** – YouTube Data API calls.
- **`colorama`** – ANSI colors, including native support in the classic Windows Command Prompt.
- **A YouTube Data API key** – read from `YOUTUBE_API_KEY`, falling back to the
  key in `src/YST_lib/required.py`. Create one in the Google Cloud console and
  enable the *YouTube Data API v3*.

## 📥 Option A — Windows executable

- [Download `YST.exe` from the repository](https://github.com/Klubuntu/YST/raw/main/dist/YST.exe)
- or grab it from the [v0.8 release page](https://github.com/Klubuntu/YST/releases/download/v0.8/YST.exe)

Double-click the file and follow the prompts. No Python required.

Releases also ship a self-contained `yst` binary for Linux and macOS:

```bash
chmod +x yst
./yst monitor UCifZaTQPiHE2QRgEwDNfhug -dashboard=True
```

## 📥 Option B — Run from source

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

Colors work out of the box once `colorama` is installed. Run the tool with
`python src\YST.py` on Windows, `python src/YST.py` elsewhere, or
`./scripts/yst` for the wrapper that resolves the path for you.

## ⚙️ Configuration

The API key is read from the `YOUTUBE_API_KEY` environment variable, falling
back to the built-in key. Copy `.env.example` to `.env` next to the working
directory to set it there instead of exporting it for every run:

```
# .env
YOUTUBE_API_KEY=your-key-here
```

An environment variable always wins over `.env`. Invalid keys, exhausted quota,
a disabled API and rate limiting are reported with a message explaining what to
do, rather than an HTTP error.

## 🪟 Windows launcher

`scripts/run.bat` runs the tool with a preset channel and video:

```bat
scripts\run.bat
```

## 🐧 Linux and macOS

There is no separate Python dependency story: the tool is pure Python, so the
source install is all that is needed. The release binaries are built with
PyInstaller as single files.

## 🔨 Rebuilding the executables

A `.spec` build is already a onefile build, so PyInstaller rejects `--onefile`
and `--name` when a spec file is given — the name comes from the
`YST_BINARY_NAME` environment variable instead.

```bash
./scripts/build.sh          # current platform -> dist/YST.exe or dist/yst
./scripts/build-linux.sh    # dist/yst.linux, in a Linux container
./scripts/build-macos.sh    # dist/yst.macos, in a macOS container
scripts\build.bat           # Windows -> dist\YST.exe
```

Or by hand:

```bash
pip install -r requirements.txt pyinstaller

YST_BINARY_NAME=yst pyinstaller build/YST.spec --distpath dist --workpath build/yst
```

Publishing a release, checksums and signing are covered in
[development](development.md#-releases).