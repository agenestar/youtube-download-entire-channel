# YouTube Channel Downloader

Download all videos from a YouTube channel in maximum quality with YouTube Premium authentication.

## Quick Start

```bash
# Install
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# List videos
download-channel list "https://www.youtube.com/@channelname/videos"

# Download with cookies
download-channel download "https://www.youtube.com/@channelname/videos" --cookie-file cookies.txt
```

## Features

- Download videos in maximum quality (bestvideo+bestaudio merged to MP4)
- YouTube Premium cookie authentication for member-only content
- Progress tracking with download speed and ETA
- CSV metadata export (title, views, resolution, etc.)
- Smart resume - skips already-downloaded videos
- Dry-run mode to preview downloads

## Usage

### List Videos

```bash
# Basic listing
download-channel list "https://www.youtube.com/@channelname/videos"

# With authentication
download-channel list "https://www.youtube.com/@channelname/videos" --cookie-file cookies.txt

# Show all videos (default shows 20)
download-channel list "https://www.youtube.com/@channelname/videos" --max-display 0
```

### Download Videos

```bash
# Download all videos
download-channel download "https://www.youtube.com/@channelname/videos" --cookie-file cookies.txt

# Custom output directory
download-channel download "https://www.youtube.com/@channelname/videos" \
  --cookie-file cookies.txt \
  --output-dir ~/Videos/MyChannel

# Preview without downloading
download-channel download "https://www.youtube.com/@channelname/videos" \
  --cookie-file cookies.txt \
  --dry-run
```

**Output:**
- Videos: `{video_id}.mp4` (e.g., `VxzXfjskKH4.mp4`)
- Metadata: `videos_metadata.csv` with complete video information

## Getting YouTube Cookies

Required for Premium/member-only content:

1. Install browser extension:
   - **Chrome/Edge**: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - **Firefox**: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. Visit [youtube.com](https://youtube.com) and log in

3. Click extension icon and export cookies for `youtube.com`

4. Save as `cookies.txt` (Netscape format)

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

## Requirements

Python 3.11+ • yt-dlp • typer • rich

## License

MIT
