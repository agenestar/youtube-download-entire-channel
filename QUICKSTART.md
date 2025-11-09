# Quick Start Guide

## Installation

```bash
# The tool is already installed in the virtual environment
source .venv/bin/activate  # Activate venv (macOS/Linux)

# Or use the full path
.venv/bin/download-channel --help
```

## Usage

### 1. List Videos Without Authentication

For public channels:

```bash
download-channel "https://www.youtube.com/@channelname"
```

### 2. Export YouTube Cookies (for Premium/Member Content)

**Chrome/Edge:**
1. Install [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Visit youtube.com and log in
3. Click the extension icon
4. Click "Export" for youtube.com
5. Save as `cookies.txt`

**Firefox:**
1. Install [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Visit youtube.com and log in
3. Click the extension icon
4. Export cookies
5. Save as `cookies.txt`

### 3. List Videos With Authentication

```bash
download-channel "https://www.youtube.com/@channelname" --cookie-file cookies.txt
```

### 4. Common Options

```bash
# Show more videos (default is 20)
download-channel "https://www.youtube.com/@channelname" --max-display 50

# Show ALL videos
download-channel "https://www.youtube.com/@channelname" --max-display 0

# Verbose output (see yt-dlp details)
download-channel "https://www.youtube.com/@channelname" --verbose

# Combine options
download-channel "https://www.youtube.com/@channelname" \
  --cookie-file cookies.txt \
  --max-display 0 \
  --verbose
```

## Example Output

```
Validating cookie file...
✓ Cookie file validated: /path/to/cookies.txt
Fetching channel information...
✓ Cookie file loaded successfully
✓ Found 245 videos in 'Example Channel'

                                    Channel Videos                                    
┏━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃    # ┃ Video ID      ┃ Title                             ┃ Duration ┃
┡━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│    1 │ dQw4w9WgXcQ   │ Never Gonna Give You Up           │ 3:32     │
│    2 │ abc123def456  │ Example Video Title               │ 12:45    │
│    3 │ xyz789abc012  │ Another Great Video               │ 1:23:45  │
└──────┴───────────────┴───────────────────────────────────┴──────────┘

Total videos: 245
```

## Troubleshooting

### "Cookie file not found"
- Check the path to your cookies.txt file
- Use absolute path or relative to current directory

### "Cookie file does not appear to be in Netscape format"
- Make sure you exported in Netscape/cookies.txt format
- The file should start with `# Netscape HTTP Cookie File`

### "Authentication required"
- Some channels require YouTube Premium or membership
- Export cookies while logged in to your Premium account
- Make sure cookies haven't expired (they usually last 1-2 years)

### "Channel not found"
- Check the URL is correct
- Try the channel's videos tab: `https://www.youtube.com/@channelname/videos`
- Some URLs might work better: `/c/channelname`, `/channel/UC...`, etc.

## Development

Run tests:
```bash
pytest -v
```

Format code:
```bash
black src/ tests/
ruff check src/ tests/
```

## What's Next?

Phase 1 (Current): ✅ List videos and validate cookies
Phase 2 (Coming): 🔄 Download videos in maximum quality

See `PHASE1_SUMMARY.md` for implementation details.
