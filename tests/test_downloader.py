"""Tests for video downloader functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

from youtube_channel_downloader.downloader import (
    download_videos,
    display_download_summary,
    DownloadError,
)


@pytest.fixture
def mock_videos():
    """Mock video list."""
    return [
        {'id': 'video1', 'title': 'Test Video 1', 'duration': 180},
        {'id': 'video2', 'title': 'Test Video 2', 'duration': 3600},
    ]


@patch('youtube_channel_downloader.downloader.yt_dlp.YoutubeDL')
def test_download_videos_success(mock_ydl_class, mock_videos):
    """Test successful video downloads."""
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value={'id': 'test', 'title': 'Test'})
    mock_ydl_class.return_value = mock_ydl
    
    with tempfile.TemporaryDirectory() as tmpdir:
        stats = download_videos(
            videos=mock_videos,
            output_dir=tmpdir,
            dry_run=False,
            verbose=False,
        )
    
    assert stats['total'] == 2
    assert stats['success'] == 2
    assert stats['failed'] == 0
    assert len(stats['failed_videos']) == 0


@patch('youtube_channel_downloader.downloader.yt_dlp.YoutubeDL')
def test_download_videos_dry_run(mock_ydl_class, mock_videos):
    """Test dry run mode."""
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value={'id': 'test', 'title': 'Test'})
    mock_ydl_class.return_value = mock_ydl
    
    with tempfile.TemporaryDirectory() as tmpdir:
        stats = download_videos(
            videos=mock_videos,
            output_dir=tmpdir,
            dry_run=True,
            verbose=False,
        )
    
    # Check that simulate option was set
    call_args = mock_ydl_class.call_args[0][0]
    assert call_args['simulate'] is True
    assert stats['success'] == 2


@patch('youtube_channel_downloader.downloader.yt_dlp.YoutubeDL')
def test_download_videos_with_cookie(mock_ydl_class, mock_videos):
    """Test downloads with cookie file."""
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value={'id': 'test', 'title': 'Test'})
    mock_ydl_class.return_value = mock_ydl
    
    cookie_path = Path("/fake/cookies.txt")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        stats = download_videos(
            videos=mock_videos,
            output_dir=tmpdir,
            cookie_file=cookie_path,
            dry_run=False,
            verbose=False,
        )
    
    # Verify cookie file was passed
    call_args = mock_ydl_class.call_args[0][0]
    assert 'cookiefile' in call_args
    assert call_args['cookiefile'] == str(cookie_path)


@patch('youtube_channel_downloader.downloader.yt_dlp.YoutubeDL')
def test_download_videos_partial_failure(mock_ydl_class, mock_videos):
    """Test when some downloads fail."""
    import yt_dlp.utils
    
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    
    # First video succeeds, second fails
    mock_ydl.extract_info = Mock(side_effect=[
        {'id': 'video1', 'title': 'Test Video 1'},
        yt_dlp.utils.DownloadError("Video unavailable")
    ])
    mock_ydl_class.return_value = mock_ydl
    
    with tempfile.TemporaryDirectory() as tmpdir:
        stats = download_videos(
            videos=mock_videos,
            output_dir=tmpdir,
            dry_run=False,
            verbose=False,
        )
    
    assert stats['total'] == 2
    assert stats['success'] == 1
    assert stats['failed'] == 1
    assert len(stats['failed_videos']) == 1
    assert stats['failed_videos'][0]['id'] == 'video2'


@patch('youtube_channel_downloader.downloader.yt_dlp.YoutubeDL')
def test_download_creates_output_directory(mock_ydl_class, mock_videos):
    """Test that output directory is created if it doesn't exist."""
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=False)
    mock_ydl.extract_info = Mock(return_value={'id': 'test', 'title': 'Test'})
    mock_ydl_class.return_value = mock_ydl
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "new_folder" / "videos"
        
        stats = download_videos(
            videos=mock_videos,
            output_dir=str(output_dir),
            dry_run=False,
            verbose=False,
        )
        
        assert output_dir.exists()
        assert output_dir.is_dir()


@patch('youtube_channel_downloader.downloader.console')
def test_display_download_summary(mock_console):
    """Test download summary display."""
    stats = {
        'total': 10,
        'success': 8,
        'failed': 2,
        'skipped': 0,
        'failed_videos': [
            {'id': 'vid1', 'title': 'Failed Video 1', 'error': 'Error 1'},
            {'id': 'vid2', 'title': 'Failed Video 2', 'error': 'Error 2'},
        ]
    }
    
    display_download_summary(stats)
    
    assert mock_console.print.called
    # Check that summary was printed
    calls = [str(call) for call in mock_console.print.call_args_list]
    summary_text = ''.join(calls)
    assert '8' in summary_text  # success count
    assert '2' in summary_text  # failed count


def test_download_videos_empty_list():
    """Test downloading empty video list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        stats = download_videos(
            videos=[],
            output_dir=tmpdir,
            dry_run=False,
            verbose=False,
        )
    
    assert stats['total'] == 0
    assert stats['success'] == 0
    assert stats['failed'] == 0
