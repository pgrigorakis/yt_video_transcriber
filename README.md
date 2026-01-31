# YouTube Transcriber

Downloads audio from YouTube videos and transcribes them using OpenAI Whisper.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- FFmpeg
- Deno (recommended) or Node.js 20+

## Installation

```bash
# Install Deno (macOS)
brew install deno

# Install Python dependencies
uv add "yt-dlp[default]" openai-whisper
```

## Usage

```bash
# Basic usage
uv run main.py 'https://www.youtube.com/watch?v=VIDEO_ID'

# Use a larger Whisper model for better accuracy
uv run main.py -m medium 'https://www.youtube.com/watch?v=VIDEO_ID'

# Keep the downloaded audio file
uv run main.py --keep-audio 'https://www.youtube.com/watch?v=VIDEO_ID'

# Specify output directory
uv run main.py -d ./transcripts 'https://www.youtube.com/watch?v=VIDEO_ID'
```

Output: `transcribed_audio_{VIDEO_ID}.txt`

## Options

| Flag           | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| `-m, --model`  | Whisper model: tiny, base, small, medium, large (default: base) |
| `-o, --output` | Custom output filename                                          |
| `-d, --dir`    | Output directory (default: current)                             |
| `--keep-audio` | Keep the downloaded MP3 file                                    |
