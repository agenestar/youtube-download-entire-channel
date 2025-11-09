# YouTube Channel Downloader

A CLI tool to download all videos from a YouTube channel in maximum quality using YouTube Premium credentials.

## Current Status

**Phase 2 Complete:** ✅ Download videos in maximum quality

The tool can now:
- ✅ List all videos from a YouTube channel
- ✅ Validate YouTube Premium cookie files
- ✅ **Download videos in maximum quality (bestvideo+bestaudio)**
- ✅ **Progress tracking with speed and ETA**
- ✅ **Dry-run mode to preview downloads**
- ✅ Display video metadata in formatted tables
- ✅ Handle private/removed videos gracefully
- ✅ Provide detailed error messages and download summaries

## Features

- 📋 List all videos from a channel
- 🔐 YouTube Premium cookie authentication
- ⬇️ Download videos in maximum quality (bestvideo+bestaudio merged to MP4)
- 📊 Progress bars with download speed and ETA
- ✨ Rich terminal output with progress tables
- 🎯 Automatic video quality selection (highest available)
- 📁 Clean file naming: Videos saved as `{video_id}.mp4`
- 📄 **CSV metadata export** with complete video information (title, description, date, views, likes, resolution, etc.)
- 🔄 Dry-run mode to preview downloads
- ⚡ **Smart resume**: Automatically skips already-downloaded videos
- 🛑 **Fail-safe**: Stops on errors (rate limiting, network issues) to preserve progress
- 🎬 Handles private/removed videos gracefully

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install in development mode
pip install -e ".[dev]"
```

## Usage

### List Videos

List all videos from a channel:

```bash
download-channel list "https://www.youtube.com/@channelname/videos"
```

With YouTube Premium cookie for accessing member-only content:

```bash
download-channel list "https://www.youtube.com/@channelname/videos" --cookie-file cookies.txt
```

List options:
- `--cookie-file, -c`: Path to Netscape format cookie file
- `--max-display, -n`: Maximum videos to display (default: 20, use 0 for all)
- `--verbose, -v`: Show detailed output

### Download Videos

Download all videos from a channel in maximum quality:

```bash
download-channel download "https://www.youtube.com/@channelname/videos" --cookie-file cookies.txt
```

**What gets created:**
- Videos saved as `{video_id}.mp4` (e.g., `VxzXfjskKH4.mp4`)
- `videos_metadata.csv` with complete metadata for all downloaded videos

**CSV Metadata includes:**
- Video ID, title, description
- Upload date, duration, views, likes
- Channel name and ID
- Resolution, FPS, codecs
- File size and download timestamp

Download to a specific directory:

```bash
download-channel download "https://www.youtube.com/@channelname/videos" \
  --cookie-file cookies.txt \
  --output-dir ~/Videos/MyChannel
```

Dry-run (preview what would be downloaded):

```bash
download-channel download "https://www.youtube.com/@channelname/videos" \
  --cookie-file cookies.txt \
  --dry-run
```

Download options:
- `--cookie-file, -c`: Path to Netscape format cookie file (recommended)
- `--output-dir, -o`: Directory to save videos (default: `downloads`)
- `--dry-run`: Simulate downloads without actually downloading
- `--skip-existing/--no-skip-existing`: Skip already downloaded videos (default: enabled)
- `--verbose, -v`: Show detailed yt-dlp output

## Exporting YouTube Cookies

To download premium content or member-only videos, you need to export your YouTube cookies:

1. Install a browser extension:
   - **Chrome/Edge**: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - **Firefox**: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. Visit [youtube.com](https://youtube.com) and log in with your Premium account

3. Click the extension icon and export cookies for `youtube.com`

4. Save the file (e.g., `cookies.txt`) and use it with `--cookie-file`

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

## Project Structure

```
youtube-download-entire-channel/
├── src/youtube_channel_downloader/
│   ├── __init__.py
│   ├── cli.py                 # CLI interface
│   ├── cookie_validator.py    # Cookie file validation
│   └── channel_lister.py      # Video listing logic
├── tests/
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.11+
- yt-dlp
- typer
- rich

## License

MIT
