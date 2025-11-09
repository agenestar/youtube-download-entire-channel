"""Channel video listing functionality using yt-dlp."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import yt_dlp
from rich.console import Console
from rich.table import Table


console = Console()


class ChannelListingError(Exception):
    """Raised when channel listing fails."""

    pass


def list_channel_videos(
    channel_url: str, cookie_file: Optional[Path] = None, verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    List all videos from a YouTube channel without downloading them.

    Args:
        channel_url: URL of the YouTube channel or playlist
        cookie_file: Optional path to Netscape format cookie file for authentication
        verbose: Whether to show detailed yt-dlp output

    Returns:
        List of video metadata dictionaries

    Raises:
        ChannelListingError: If listing fails
    """
    ydl_opts = {
        "extract_flat": "in_playlist",  # Don't download, just extract metadata
        "quiet": not verbose,
        "no_warnings": not verbose,
        "ignoreerrors": True,  # Continue on errors (e.g., private videos)
    }

    if cookie_file:
        ydl_opts["cookiefile"] = str(cookie_file)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            console.print("[cyan]Fetching channel information...[/cyan]")

            # Extract channel/playlist info
            info = ydl.extract_info(channel_url, download=False)

            if not info:
                raise ChannelListingError("Could not extract channel information")

            # Check if authentication worked by looking for premium indicators
            if cookie_file:
                console.print("[green]✓[/green] Cookie file loaded successfully")

            # Handle both channel pages and playlists
            if "entries" in info:
                videos = list(info["entries"])
                channel_title = info.get("title", "Unknown Channel")
            else:
                # Single video
                videos = [info]
                channel_title = info.get("channel", "Unknown Channel")

            # Filter out None entries (removed/private videos)
            videos = [v for v in videos if v is not None]

            console.print(f"[green]✓[/green] Found {len(videos)} videos in '{channel_title}'")

            return videos

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Sign in" in error_msg or "login" in error_msg.lower():
            raise ChannelListingError(
                "Authentication required. Please provide a valid YouTube Premium cookie file."
            )
        raise ChannelListingError(f"Failed to list channel videos: {error_msg}")
    except Exception as e:
        raise ChannelListingError(f"Unexpected error listing channel: {str(e)}")


def display_video_table(videos: List[Dict[str, Any]], max_rows: Optional[int] = None) -> None:
    """
    Display videos in a formatted table.

    Args:
        videos: List of video metadata dictionaries
        max_rows: Maximum number of rows to display (None for all)
    """
    table = Table(title="Channel Videos")
    table.add_column("#", style="cyan", width=6)
    table.add_column("Video ID", style="yellow", width=15)
    table.add_column("Title", style="green")
    table.add_column("Duration", style="blue", width=10)

    display_videos = videos[:max_rows] if max_rows else videos

    for idx, video in enumerate(display_videos, 1):
        video_id = video.get("id", "N/A")
        title = video.get("title", "Unknown Title")
        duration = video.get("duration")

        # Format duration as MM:SS or HH:MM:SS
        if duration is not None and duration > 0:
            # Convert to int to handle float values
            duration = int(duration)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "N/A"

        table.add_row(str(idx), video_id, title, duration_str)

    if max_rows and len(videos) > max_rows:
        table.caption = f"Showing {max_rows} of {len(videos)} videos"

    console.print(table)
