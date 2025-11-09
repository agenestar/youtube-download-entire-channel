"""Video downloading functionality using yt-dlp."""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yt_dlp
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)


console = Console()


class DownloadError(Exception):
    """Raised when video download fails."""

    pass


def download_videos(
    videos: List[Dict[str, Any]],
    output_dir: str = "downloads",
    cookie_file: Optional[Path] = None,
    dry_run: bool = False,
    max_concurrent: int = 1,
    verbose: bool = False,
    skip_existing: bool = True,
) -> Dict[str, Any]:
    """
    Download videos from a list of video metadata.

    Args:
        videos: List of video metadata dictionaries from channel_lister
        output_dir: Directory to save downloaded videos
        cookie_file: Optional path to cookie file for authentication
        dry_run: If True, only simulate downloads without actually downloading
        max_concurrent: Number of concurrent downloads (currently supports 1)
        verbose: Whether to show detailed yt-dlp output
        skip_existing: If True, skip videos that are already downloaded

    Returns:
        Dictionary with download statistics (success, failed, skipped counts)

    Raises:
        DownloadError: If download fails
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    stats = {"total": len(videos), "success": 0, "failed": 0, "skipped": 0, "failed_videos": []}

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be downloaded[/yellow]")

    console.print(f"[cyan]Downloading {len(videos)} videos to: {output_path.absolute()}[/cyan]\n")

    # Configure yt-dlp options for maximum quality
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(output_path / "%(id)s.%(ext)s"),  # Use video ID as filename
        "quiet": not verbose,
        "no_warnings": not verbose,
        "ignoreerrors": False,
        "writesubtitles": False,
        "writeautomaticsub": False,
        "noplaylist": True,  # We're processing videos individually
        "writethumbnail": False,
        "writeinfojson": False,
    }

    if cookie_file:
        ydl_opts["cookiefile"] = str(cookie_file)

    if dry_run:
        ydl_opts["simulate"] = True

    # Prepare CSV file for metadata
    csv_path = output_path / "videos_metadata.csv"
    csv_exists = csv_path.exists()

    # Load already downloaded video IDs from CSV if skip_existing is enabled
    downloaded_ids = set()
    if skip_existing and csv_exists:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    downloaded_ids.add(row["video_id"])
            if downloaded_ids:
                console.print(
                    f"[cyan]Found {len(downloaded_ids)} already downloaded videos - will skip them[/cyan]"
                )
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read existing CSV: {e}[/yellow]")

    # CSV headers
    csv_headers = [
        "video_id",
        "title",
        "description",
        "upload_date",
        "duration",
        "view_count",
        "like_count",
        "channel",
        "channel_id",
        "uploader",
        "thumbnail",
        "width",
        "height",
        "fps",
        "video_codec",
        "audio_codec",
        "filesize",
        "download_timestamp",
    ]

    # Open CSV file for appending
    csv_file = open(csv_path, "a", newline="", encoding="utf-8")
    csv_writer = csv.DictWriter(csv_file, fieldnames=csv_headers, extrasaction="ignore")

    # Write header if new file
    if not csv_exists or csv_path.stat().st_size == 0:
        csv_writer.writeheader()

    try:
        # Download each video
        for idx, video in enumerate(videos, 1):
            video_id = video.get("id", "unknown")
            video_title = video.get("title", "Unknown Title")
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # Check if video is already downloaded
            if skip_existing and video_id in downloaded_ids:
                console.print(f"[yellow][{idx}/{len(videos)}][/yellow] {video_title}")
                console.print("[yellow]⊘ Already downloaded - skipping[/yellow]\n")
                stats["skipped"] += 1
                continue

            # Check if video file already exists
            if skip_existing:
                video_file = output_path / f"{video_id}.mp4"
                if video_file.exists():
                    console.print(f"[yellow][{idx}/{len(videos)}][/yellow] {video_title}")
                    console.print("[yellow]⊘ File already exists - skipping[/yellow]\n")
                    stats["skipped"] += 1
                    # Add to downloaded_ids to track it
                    downloaded_ids.add(video_id)
                    continue

            console.print(f"[cyan][{idx}/{len(videos)}][/cyan] {video_title}")

            try:
                # Create progress tracking
                video_info = None
                with Progress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:

                    task_id = progress.add_task("Downloading...", total=100)

                    def progress_hook(d):
                        if d["status"] == "downloading":
                            if "total_bytes" in d:
                                downloaded = d.get("downloaded_bytes", 0)
                                total = d["total_bytes"]
                                percent = (downloaded / total) * 100
                                progress.update(task_id, completed=percent)
                            elif "total_bytes_estimate" in d:
                                downloaded = d.get("downloaded_bytes", 0)
                                total = d["total_bytes_estimate"]
                                percent = (downloaded / total) * 100
                                progress.update(task_id, completed=percent)
                        elif d["status"] == "finished":
                            progress.update(task_id, completed=100)

                    ydl_opts["progress_hooks"] = [progress_hook]

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Extract full video info for metadata
                        video_info = ydl.extract_info(video_url, download=not dry_run)

                # Write metadata to CSV
                if video_info:
                    metadata = {
                        "video_id": video_info.get("id", video_id),
                        "title": video_info.get("title", ""),
                        "description": video_info.get("description", ""),
                        "upload_date": video_info.get("upload_date", ""),
                        "duration": video_info.get("duration", ""),
                        "view_count": video_info.get("view_count", ""),
                        "like_count": video_info.get("like_count", ""),
                        "channel": video_info.get("channel", ""),
                        "channel_id": video_info.get("channel_id", ""),
                        "uploader": video_info.get("uploader", ""),
                        "thumbnail": video_info.get("thumbnail", ""),
                        "width": video_info.get("width", ""),
                        "height": video_info.get("height", ""),
                        "fps": video_info.get("fps", ""),
                        "video_codec": video_info.get("vcodec", ""),
                        "audio_codec": video_info.get("acodec", ""),
                        "filesize": video_info.get(
                            "filesize", video_info.get("filesize_approx", "")
                        ),
                        "download_timestamp": datetime.now().isoformat(),
                    }
                    csv_writer.writerow(metadata)
                    csv_file.flush()  # Ensure data is written immediately

                stats["success"] += 1
                console.print("[green]✓[/green] Downloaded successfully\n")

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                stats["failed"] += 1
                stats["failed_videos"].append(
                    {"id": video_id, "title": video_title, "error": error_msg}
                )
                console.print(f"[red]✗[/red] Failed: {error_msg}\n")
                console.print("[red]Stopping due to download error[/red]")
                break  # Stop on download error

            except KeyboardInterrupt:
                console.print("\n[yellow]Download cancelled by user[/yellow]")
                raise

            except Exception as e:
                stats["failed"] += 1
                stats["failed_videos"].append(
                    {"id": video_id, "title": video_title, "error": str(e)}
                )
                console.print(f"[red]✗[/red] Unexpected error: {e}\n")
                console.print("[red]Stopping due to unexpected error[/red]")
                break  # Stop on unexpected error

    finally:
        csv_file.close()

    return stats


def display_download_summary(stats: Dict[str, Any]) -> None:
    """
    Display a summary of download results.

    Args:
        stats: Download statistics dictionary
    """
    console.print("\n" + "=" * 60)
    console.print("[bold]Download Summary[/bold]")
    console.print("=" * 60)
    console.print(f"Total videos:    {stats['total']}")
    console.print(f"[green]✓ Successful:    {stats['success']}[/green]")
    console.print(f"[red]✗ Failed:        {stats['failed']}[/red]")
    console.print(f"[yellow]⊘ Skipped:       {stats['skipped']}[/yellow]")

    if stats["failed_videos"]:
        console.print("\n[red]Failed videos:[/red]")
        for video in stats["failed_videos"]:
            console.print(f"  • {video['title']} ({video['id']})")
            console.print(f"    Error: {video['error']}")
