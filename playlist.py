#!/usr/bin/env python3
"""Create random M3U playlists from audio files organized in genre folders."""

from __future__ import annotations

import argparse
import random
import shutil
import sys
from pathlib import Path

from dotenv import dotenv_values

AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma"}
SCRIPT_DIR = Path(__file__).resolve().parent


def load_genres() -> dict[str, Path]:
    """Load genre-to-folder mappings from .env file."""
    env_path = SCRIPT_DIR / ".env"
    if not env_path.exists():
        print(f"Error: No .env file found at {env_path}", file=sys.stderr)
        print("Create one with genre=folder mappings. See .env.example.", file=sys.stderr)
        sys.exit(1)

    values = dotenv_values(env_path)
    genres = {}
    for key, value in values.items():
        if value:
            path = Path(value)
            if not path.is_absolute():
                path = (SCRIPT_DIR / path).resolve()
            genres[key.upper()] = path
    if not genres:
        print("Error: No genre mappings found in .env file.", file=sys.stderr)
        sys.exit(1)
    return genres


def list_genres(genres: dict[str, Path]) -> None:
    """Print configured genres and their folder paths."""
    print("Configured genres:")
    for name, path in sorted(genres.items()):
        exists = "OK" if path.exists() else "NOT FOUND"
        print(f"  {name}: {path} [{exists}]")


def scan_audio_files(folder: Path) -> list[Path]:
    """Recursively scan a folder for audio files."""
    files = []
    for f in folder.rglob("*"):
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(f)
    return files


def collect_songs(genres: dict[str, Path], requested: list[str] | None) -> list[Path]:
    """Collect audio files from requested genres (or all if none specified)."""
    if requested:
        selected = {g.upper() for g in requested}
        unknown = selected - genres.keys()
        if unknown:
            print(f"Error: Unknown genre(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(genres.keys()))}", file=sys.stderr)
            sys.exit(1)
    else:
        selected = set(genres.keys())

    songs = []
    for name in sorted(selected):
        folder = genres[name]
        if not folder.exists():
            print(f"Warning: Folder for {name} does not exist: {folder}", file=sys.stderr)
            continue
        found = scan_audio_files(folder)
        print(f"  {name}: {len(found)} files found")
        songs.extend(found)
    return songs


def write_m3u(filepath: Path, entries: list[str]) -> None:
    """Write an M3U playlist file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for entry in entries:
            f.write(f"{entry}\n")


def unique_filename(target_dir: Path, name: str) -> str:
    """Return a unique filename within target_dir, appending _N if needed."""
    stem = Path(name).stem
    suffix = Path(name).suffix
    candidate = name
    counter = 2
    while (target_dir / candidate).exists():
        candidate = f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def copy_to_directory(songs: list[Path], target_dir: Path, output_name: str) -> None:
    """Copy selected songs to target directory and write a portable M3U there."""
    target_dir.mkdir(parents=True, exist_ok=True)
    copied_names = []
    for i, song in enumerate(songs, 1):
        dest_name = unique_filename(target_dir, song.name)
        dest = target_dir / dest_name
        print(f"  [{i}/{len(songs)}] Copying {song.name} -> {dest_name}")
        shutil.copy2(song, dest)
        copied_names.append(dest_name)

    m3u_path = target_dir / output_name
    write_m3u(m3u_path, copied_names)
    print(f"\nPortable playlist written to {m3u_path}")
    print(f"  {len(copied_names)} files copied to {target_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create random M3U playlists from genre folders."
    )
    parser.add_argument(
        "--genres", "-g", nargs="+", metavar="GENRE",
        help="One or more genre names (uses all if omitted)",
    )
    parser.add_argument(
        "--count", "-n", type=int,
        help="Number of songs to include",
    )
    parser.add_argument(
        "--output", "-o", default="playlist.m3u", metavar="FILE",
        help="Output playlist filename (default: playlist.m3u)",
    )
    parser.add_argument(
        "--copy-to", "-c", metavar="DIR",
        help="Copy playlist files to this directory for portable transfer",
    )
    parser.add_argument(
        "--list", "-l", action="store_true",
        help="List configured genres and exit",
    )
    args = parser.parse_args()

    genres = load_genres()

    if args.list:
        list_genres(genres)
        return

    if args.count is None:
        parser.error("--count / -n is required when not using --list")

    if args.count < 1:
        parser.error("--count must be at least 1")

    print("Scanning folders...")
    songs = collect_songs(genres, args.genres)

    if not songs:
        print("Error: No audio files found in the selected genre folders.", file=sys.stderr)
        sys.exit(1)

    count = min(args.count, len(songs))
    if count < args.count:
        print(f"Note: Only {count} files available (requested {args.count}).")

    selected = random.sample(songs, count)
    print(f"\nSelected {count} songs.")

    if args.copy_to:
        target_dir = Path(args.copy_to)
        print(f"\nCopying files to {target_dir}...")
        copy_to_directory(selected, target_dir, args.output)
    else:
        entries = [str(song) for song in selected]
        output_path = Path(args.output)
        write_m3u(output_path, entries)
        print(f"Playlist written to {output_path}")


if __name__ == "__main__":
    main()
