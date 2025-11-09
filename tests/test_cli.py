"""Tests for CLI interface."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch
import tempfile
from pathlib import Path

from youtube_channel_downloader.cli import app


runner = CliRunner()


@pytest.fixture
def valid_cookie_file():
    """Create a valid cookie file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write(".youtube.com\tTRUE\t/\tTRUE\t0\tcookie_name\tcookie_value\n")
        cookie_path = f.name

    yield cookie_path

    Path(cookie_path).unlink()


@pytest.fixture
def mock_videos():
    """Mock video list."""
    return [
        {"id": "video1", "title": "Test Video 1", "duration": 180},
        {"id": "video2", "title": "Test Video 2", "duration": 3600},
    ]


@patch("youtube_channel_downloader.cli.list_channel_videos")
@patch("youtube_channel_downloader.cli.display_video_table")
def test_list_videos_basic(mock_display, mock_list, mock_videos):
    """Test basic list-videos command."""
    mock_list.return_value = mock_videos

    result = runner.invoke(app, ["list", "https://youtube.com/@testchannel"])

    assert result.exit_code == 0
    assert mock_list.called
    assert mock_display.called
    assert "Total videos: 2" in result.stdout


@patch("youtube_channel_downloader.cli.list_channel_videos")
@patch("youtube_channel_downloader.cli.display_video_table")
def test_list_videos_with_cookie(mock_display, mock_list, mock_videos, valid_cookie_file):
    """Test list-videos command with cookie file."""
    mock_list.return_value = mock_videos

    result = runner.invoke(
        app, ["list", "https://youtube.com/@testchannel", "--cookie-file", valid_cookie_file]
    )

    assert result.exit_code == 0
    assert "Cookie file validated" in result.stdout
    assert mock_list.called


@patch("youtube_channel_downloader.cli.list_channel_videos")
def test_list_videos_invalid_cookie(mock_list):
    """Test list-videos with invalid cookie file."""
    result = runner.invoke(
        app,
        ["list", "https://youtube.com/@testchannel", "--cookie-file", "/nonexistent/cookies.txt"],
    )

    assert result.exit_code == 1
    assert "Cookie validation error" in result.stdout


@patch("youtube_channel_downloader.cli.list_channel_videos")
@patch("youtube_channel_downloader.cli.display_video_table")
def test_list_videos_no_videos(mock_display, mock_list):
    """Test list-videos when channel has no videos."""
    mock_list.return_value = []

    result = runner.invoke(app, ["list", "https://youtube.com/@testchannel"])

    assert result.exit_code == 0
    assert "No videos found" in result.stdout
    assert not mock_display.called


@patch("youtube_channel_downloader.cli.list_channel_videos")
def test_list_videos_channel_error(mock_list):
    """Test list-videos with channel listing error."""
    from youtube_channel_downloader.channel_lister import ChannelListingError

    mock_list.side_effect = ChannelListingError("Channel not found")

    result = runner.invoke(app, ["list", "https://youtube.com/@testchannel"])

    assert result.exit_code == 1
    assert "Channel listing error" in result.stdout


@patch("youtube_channel_downloader.cli.list_channel_videos")
@patch("youtube_channel_downloader.cli.display_video_table")
def test_list_videos_max_display(mock_display, mock_list, mock_videos):
    """Test list-videos with max-display option."""
    mock_list.return_value = mock_videos

    result = runner.invoke(app, ["list", "https://youtube.com/@testchannel", "--max-display", "1"])

    assert result.exit_code == 0
    # Verify max_rows was passed to display function
    call_args = mock_display.call_args
    assert call_args[1]["max_rows"] == 1


@patch("youtube_channel_downloader.cli.list_channel_videos")
@patch("youtube_channel_downloader.cli.display_video_table")
def test_list_videos_verbose(mock_display, mock_list, mock_videos):
    """Test list-videos with verbose flag."""
    mock_list.return_value = mock_videos

    result = runner.invoke(app, ["list", "https://youtube.com/@testchannel", "--verbose"])

    assert result.exit_code == 0
    # Verify verbose was passed
    call_args = mock_list.call_args
    assert call_args[1]["verbose"] is True
