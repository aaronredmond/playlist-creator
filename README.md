# Playlist Creator

A CLI utility that creates random M3U playlists from audio files organized in genre folders. Optionally copies all selected files to a directory for easy transfer to another device.

Works on both macOS and Windows.

## Setup

### Requirements

- Python 3.7+
- [python-dotenv](https://pypi.org/project/python-dotenv/)

### Install dependencies

macOS:
```bash
pip3 install python-dotenv
```

Windows:
```bash
pip install python-dotenv
```

### Configure genres

Create a `.env` file in the project directory mapping genre names to folder paths:

macOS:
```
ROCK=/Volumes/Music/Rock
JAZZ=/Users/me/Music/Jazz
HIPHOP=./Hip-Hop
```

Windows:
```
ROCK=C:\Users\Me\Music\Rock
JAZZ=D:\Music\Jazz
HIPHOP=.\Hip-Hop
```

- Each key is a genre name (case-insensitive when used on the command line).
- Each value is the path to a folder containing audio files (absolute or relative).
- Relative paths are resolved from the `.env` file's directory.
- Use your OS's native path format.
- See `.env.example` for a template.

### Supported audio formats

`.mp3`, `.flac`, `.wav`, `.aac`, `.ogg`, `.m4a`, `.wma`

Audio files are discovered recursively, so subfolders within a genre folder are included.

## Usage

macOS:
```
python3 playlist.py [OPTIONS]
```

Windows:
```
python playlist.py [OPTIONS]
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--genres GENRE [...]` | `-g` | One or more genre names to pull from. Uses all genres if omitted. |
| `--count N` | `-n` | Number of songs to include. Required unless using `--list`. |
| `--output FILE` | `-o` | Output playlist filename. Default: `playlist.m3u` |
| `--copy-to DIR` | `-c` | Copy selected files to a directory and write a portable playlist there. |
| `--list` | `-l` | List configured genres and their folder paths, then exit. |

### Examples

**List available genres:**

```bash
python3 playlist.py --list
```

Output:

```
Configured genres:
  JAZZ: /Volumes/Music/Jazz [OK]
  ROCK: /Volumes/Music/Rock [OK]
```

Folders are checked for existence and marked `OK` or `NOT FOUND`.

**Generate a playlist from specific genres:**

```bash
python3 playlist.py --genres rock jazz --count 20
```

Creates `playlist.m3u` with 20 randomly selected songs from the Rock and Jazz folders.

**Generate a playlist from all genres:**

```bash
python3 playlist.py --count 10
```

Pulls from every genre defined in `.env`.

**Specify an output filename:**

```bash
python3 playlist.py --genres rock --count 15 --output my_mix.m3u
```

**Copy files to a directory for transfer:**

macOS:
```bash
python3 playlist.py --genres rock jazz --count 15 --copy-to /Volumes/USB/playlist_export
```

Windows:
```bash
python playlist.py --genres rock jazz --count 15 --copy-to E:\playlist_export
```

This will:

1. Select 15 random songs from the Rock and Jazz folders.
2. Create the target directory if it doesn't exist.
3. Copy all 15 audio files into that directory (flat, no subdirectories).
4. Write `playlist.m3u` inside the directory using relative filenames.

The resulting directory is fully portable — copy it to a USB drive, phone, or any other device and the playlist will work as-is.

## How it works

### Standard mode (no `--copy-to`)

The generated M3U file contains absolute paths to the original audio files on your system:

```
#EXTM3U
/Volumes/Music/Rock/Highway to Hell.mp3
/Volumes/Music/Jazz/Take Five.flac
```

### Portable mode (`--copy-to`)

Files are copied into the target directory and the M3U uses relative filenames:

```
#EXTM3U
Highway to Hell.mp3
Take Five.flac
```

If two files across different genres share the same filename, a numeric suffix is added automatically (e.g., `intro.mp3` and `intro_2.mp3`).

### Fewer files than requested

If the selected genres contain fewer audio files than the requested `--count`, the tool uses all available files and prints a note:

```
Note: Only 8 files available (requested 20).
```
