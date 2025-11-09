# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2025-11-08

### Added
- **Smart resume capability**: Automatically skips already-downloaded videos by checking CSV and existing files
- `--skip-existing/--no-skip-existing` option (enabled by default)
- Script now stops on download errors instead of continuing, preserving progress

### Changed
- Downloads stop immediately on any error (rate limiting, network issues, etc.)
- Better handling of interrupted downloads - just re-run the same command to resume

## [0.3.0] - 2025-11-08

### Changed
- **Videos now saved with video ID as filename** (`{video_id}.mp4` instead of date-title format)
- **CSV metadata export**: All video metadata automatically saved to `videos_metadata.csv`

### Added
- Comprehensive metadata capture: title, description, upload date, duration, views, likes, channel info, resolution, codecs, file size
- CSV file updated with each download for easy tracking
- Download timestamp for each video

## [0.2.0] - 2025-11-08

### Added
- **Video downloading in maximum quality** (bestvideo+bestaudio merged to MP4)
- Progress bars with download speed, ETA, and file size
- `download` command with options for output directory and dry-run mode
- Download summary with success/failure statistics
- Automatic output directory creation
- File naming format: `YYYYMMDD - Video Title.mp4`
- Support for dry-run mode to preview downloads
- 7 new tests for downloader module (27 total tests)

### Changed
- CLI now uses subcommands: `list` and `download`
- Updated all documentation with download examples

### Fixed
- Duration formatting now handles float and None values
- SSL certificate verification issues on macOS

## [0.1.0] - 2025-11-08

### Added
- Initial release
- Cookie validation for YouTube Premium authentication
- Channel video listing functionality
- CLI interface with Typer
- Rich terminal output with formatted tables
- Comprehensive test suite
- Support for handling private/removed videos gracefully
