"""Command-line interface for YouTube Channel Downloader."""

from typing import Optional
import typer
from rich.console import Console

from youtube_channel_downloader.cookie_validator import validate_cookie_file, CookieValidationError
from youtube_channel_downloader.channel_lister import (
    list_channel_videos,
    display_video_table,
    ChannelListingError,
)
from youtube_channel_downloader.downloader import (
    download_videos,
    display_download_summary,
    DownloadError,
)

console = Console()


def main(
    channel_url: str = typer.Argument(
        ..., help="YouTube channel URL (e.g., https://www.youtube.com/@channelname)"
    ),
    cookie_file: Optional[str] = typer.Option(
        None,
        "--cookie-file",
        "-c",
        help="Path to Netscape format cookie file for YouTube Premium authentication",
    ),
    max_display: Optional[int] = typer.Option(
        20,
        "--max-display",
        "-n",
        help="Maximum number of videos to display in table (0 for all)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed yt-dlp output",
    ),
):
    """
    List all videos from a YouTube channel without downloading.

    This command validates the cookie file (if provided) and fetches
    metadata for all videos in the channel.
    """
    try:
        # Validate cookie file if provided
        cookie_path = None
        if cookie_file:
            console.print("[cyan]Validating cookie file...[/cyan]")
            cookie_path = validate_cookie_file(cookie_file)
            console.print(f"[green]✓[/green] Cookie file validated: {cookie_path}")

        # List videos
        videos = list_channel_videos(
            channel_url=channel_url,
            cookie_file=cookie_path,
            verbose=verbose,
        )

        if not videos:
            console.print("[yellow]No videos found in channel[/yellow]")
            return

        # Display results
        display_rows = None if max_display == 0 else max_display
        display_video_table(videos, max_rows=display_rows)

        console.print(f"\n[green]Total videos: {len(videos)}[/green]")

    except CookieValidationError as e:
        console.print(f"[red]Cookie validation error:[/red] {e}")
        raise typer.Exit(code=1)
    except ChannelListingError as e:
        console.print(f"[red]Channel listing error:[/red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            raise
        raise typer.Exit(code=1)


def download(
    channel_url: str = typer.Argument(
        ..., help="YouTube channel URL (e.g., https://www.youtube.com/@channelname/videos)"
    ),
    cookie_file: Optional[str] = typer.Option(
        None,
        "--cookie-file",
        "-c",
        help="Path to Netscape format cookie file for YouTube Premium authentication",
    ),
    output_dir: str = typer.Option(
        "downloads",
        "--output-dir",
        "-o",
        help="Directory to save downloaded videos",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simulate downloads without actually downloading files",
    ),
    skip_existing: bool = typer.Option(
        True,
        "--skip-existing/--no-skip-existing",
        help="Skip videos that are already downloaded (default: enabled)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed yt-dlp output",
    ),
):
    """
    Download all videos from a YouTube channel in maximum quality.

    Downloads videos using the best available quality (bestvideo+bestaudio).
    Files are saved with the format: YYYYMMDD - Video Title.mp4
    """
    try:
        # Validate cookie file if provided
        cookie_path = None
        if cookie_file:
            console.print("[cyan]Validating cookie file...[/cyan]")
            cookie_path = validate_cookie_file(cookie_file)
            console.print(f"[green]✓[/green] Cookie file validated: {cookie_path}")

        # List videos first
        console.print("[cyan]Fetching channel videos...[/cyan]")
        videos = list_channel_videos(
            channel_url=channel_url,
            cookie_file=cookie_path,
            verbose=verbose,
        )

        if not videos:
            console.print("[yellow]No videos found in channel[/yellow]")
            return

        console.print(f"[green]✓[/green] Found {len(videos)} videos to download\n")

        # Download videos
        stats = download_videos(
            videos=videos,
            output_dir=output_dir,
            cookie_file=cookie_path,
            dry_run=dry_run,
            skip_existing=skip_existing,
            verbose=verbose,
        )

        # Display summary
        display_download_summary(stats)

        # Exit with error code if any downloads failed
        if stats["failed"] > 0:
            raise typer.Exit(code=1)

    except CookieValidationError as e:
        console.print(f"[red]Cookie validation error:[/red] {e}")
        raise typer.Exit(code=1)
    except ChannelListingError as e:
        console.print(f"[red]Channel listing error:[/red] {e}")
        raise typer.Exit(code=1)
    except DownloadError as e:
        console.print(f"[red]Download error:[/red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            raise
        raise typer.Exit(code=1)


app = typer.Typer(
    name="download-channel",
    help="Download all videos from a YouTube channel in maximum quality",
    add_completion=False,
)

# Register commands
app.command(name="list")(main)
app.command(name="download")(download)


if __name__ == "__main__":
    app()
