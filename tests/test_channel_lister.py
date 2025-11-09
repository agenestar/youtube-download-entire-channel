"""Tests for channel listing functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from youtube_channel_downloader.channel_lister import (
    list_channel_videos,
    display_video_table,
    ChannelListingError,
)


@pytest.fixture
def mock_channel_info():
    """Mock channel information from yt-dlp."""
    return {
        "title": "Test Channel",
        "id": "UC1234567890",
        "channel_id": "UC1234567890",
        "entries": [
            {
                "id": "video1",
                "title": "Test Video 1",
                "duration": 180,
            },
            {
                "id": "video2",
                "title": "Test Video 2",
                "duration": 3600,
            },
            {
                "id": "video3",
                "title": "Test Video 3",
                "duration": 90,
            },
        ],
    }


@patch("youtube_channel_downloader.channel_lister.yt_dlp.YoutubeDL")
def test_list_channel_videos_success(mock_ydl_class, mock_channel_info):
    """Test successful channel video listing."""
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value=mock_channel_info)
    mock_ydl_class.return_value = mock_ydl

    videos = list_channel_videos("https://youtube.com/@testchannel")

    assert len(videos) == 3
    assert videos[0]["id"] == "video1"
    assert videos[0]["title"] == "Test Video 1"
    assert videos[1]["duration"] == 3600


@patch("youtube_channel_downloader.channel_lister.yt_dlp.YoutubeDL")
def test_list_channel_videos_with_cookie(mock_ydl_class, mock_channel_info):
    """Test channel listing with cookie file."""
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value=mock_channel_info)
    mock_ydl_class.return_value = mock_ydl

    cookie_path = Path("/fake/cookies.txt")
    videos = list_channel_videos("https://youtube.com/@testchannel", cookie_file=cookie_path)

    # Verify cookie file was passed to yt-dlp
    call_args = mock_ydl_class.call_args[0][0]
    assert "cookiefile" in call_args
    assert call_args["cookiefile"] == str(cookie_path)
    assert len(videos) == 3


@patch("youtube_channel_downloader.channel_lister.yt_dlp.YoutubeDL")
def test_list_channel_videos_filters_none_entries(mock_ydl_class):
    """Test that None entries (private/removed videos) are filtered out."""
    mock_info = {
        "title": "Test Channel",
        "id": "UC1234567890",
        "entries": [
            {"id": "video1", "title": "Video 1", "duration": 100},
            None,  # Removed/private video
            {"id": "video2", "title": "Video 2", "duration": 200},
            None,
        ],
    }

    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value=mock_info)
    mock_ydl_class.return_value = mock_ydl

    videos = list_channel_videos("https://youtube.com/@testchannel")

    assert len(videos) == 2
    assert all(v is not None for v in videos)


@patch("youtube_channel_downloader.channel_lister.yt_dlp.YoutubeDL")
def test_list_channel_videos_authentication_error(mock_ydl_class):
    """Test handling of authentication errors."""
    import yt_dlp.utils

    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(
        side_effect=yt_dlp.utils.DownloadError("Sign in to confirm your age")
    )
    mock_ydl_class.return_value = mock_ydl

    with pytest.raises(ChannelListingError, match="Authentication required"):
        list_channel_videos("https://youtube.com/@testchannel")


@patch("youtube_channel_downloader.channel_lister.yt_dlp.YoutubeDL")
def test_list_channel_videos_generic_error(mock_ydl_class):
    """Test handling of generic yt-dlp errors."""
    import yt_dlp.utils

    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(side_effect=yt_dlp.utils.DownloadError("Channel not found"))
    mock_ydl_class.return_value = mock_ydl

    with pytest.raises(ChannelListingError, match="Failed to list channel videos"):
        list_channel_videos("https://youtube.com/@testchannel")


@patch("youtube_channel_downloader.channel_lister.console")
def test_display_video_table(mock_console):
    """Test video table display."""
    videos = [
        {"id": "vid1", "title": "Video 1", "duration": 180},
        {"id": "vid2", "title": "Video 2", "duration": 3665},  # 1:01:05
        {"id": "vid3", "title": "Video 3", "duration": 0},
    ]

    display_video_table(videos)

    # Verify console.print was called with a Table
    assert mock_console.print.called


@patch("youtube_channel_downloader.channel_lister.console")
def test_display_video_table_max_rows(mock_console):
    """Test video table display with max rows limit."""
    videos = [{"id": f"vid{i}", "title": f"Video {i}", "duration": 100} for i in range(50)]

    display_video_table(videos, max_rows=10)

    assert mock_console.print.called
