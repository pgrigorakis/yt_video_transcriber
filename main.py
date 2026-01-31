#!/usr/bin/env python3
"""
YouTube Video Transcriber
Downloads audio from a YouTube video and transcribes it using OpenAI Whisper.

Requirements:
    pip install "yt-dlp[default]" openai-whisper

    Additionally, install Deno (recommended) or Node.js >= 20:
    - Deno: brew install deno (macOS) or see https://deno.com
    - Node: brew install node (macOS)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

import whisper
import yt_dlp


def download_audio(youtube_url: str, output_dir: str = ".") -> tuple[str, str]:
    """
    Download audio from YouTube video.

    Args:
        youtube_url: URL of the YouTube video
        output_dir: Directory to save the audio file

    Returns:
        Tuple of (path to downloaded audio file, video ID)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Check for available JS runtimes
    deno_path = shutil.which("deno")
    node_path = shutil.which("node")

    if deno_path:
        print(f"Using Deno at: {deno_path}")
    elif node_path:
        print(f"Using Node.js at: {node_path}")
    else:
        print(
            "WARNING: No JavaScript runtime found. Install Deno (recommended) or Node.js >= 20"
        )
        print("  Deno: brew install deno")
        print("  Node: brew install node")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": str(output_path / "audio.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
        "cookiesfrombrowser": ("chrome",),
        # Enable downloading EJS challenge solver scripts from GitHub
        # This is required for YouTube's JS challenges
        "compat_opts": set(),
        "remote_components": ["ejs:github"],
    }

    # Configure JS runtime - Deno is preferred (enabled by default)
    # Only need to explicitly configure if using Node
    if not deno_path and node_path:
        ydl_opts["extractor_args"] = {
            "youtube": {
                "js_runtimes": [f"node:{node_path}"],
            }
        }

    print(f"Downloading audio from: {youtube_url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        video_id = info["id"]

    audio_file = str(output_path / "audio.mp3")

    print(f"Audio downloaded to: {audio_file}")
    return audio_file, video_id


def transcribe_audio(audio_file: str, model_name: str = "base") -> dict:
    """
    Transcribe audio file using Whisper.

    Args:
        audio_file: Path to the audio file
        model_name: Whisper model to use (tiny, base, small, medium, large)

    Returns:
        Transcription result dictionary
    """
    print(f"\nLoading Whisper model: {model_name}")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {audio_file}")
    result = model.transcribe(audio_file, verbose=True)

    return result


def save_transcription(result: dict, output_file: str):
    """
    Save transcription to a text file.

    Args:
        result: Transcription result from Whisper
        output_file: Path to save the transcription
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"\nTranscription saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe YouTube videos using Whisper"
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file for transcription (default: same as video title)",
    )
    parser.add_argument(
        "-d",
        "--dir",
        default=".",
        help="Directory to save files (default: current directory)",
    )
    parser.add_argument(
        "--keep-audio", action="store_true", help="Keep the downloaded audio file"
    )

    args = parser.parse_args()

    try:
        # Download audio
        audio_file, video_id = download_audio(args.url, args.dir)

        # Transcribe
        result = transcribe_audio(audio_file, args.model)

        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            output_file = str(Path(args.dir) / f"transcribed_audio_{video_id}.txt")

        # Save transcription
        save_transcription(result, output_file)

        # Clean up audio file if requested
        if not args.keep_audio:
            os.remove(audio_file)
            print(f"Removed audio file: {audio_file}")

        print("\n✓ Transcription complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
