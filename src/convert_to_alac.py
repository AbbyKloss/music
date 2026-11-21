import os
from glob import glob
from pathlib import Path
from shutil import copy2
from subprocess import Popen
from sys import argv

import yaml
from tqdm import tqdm


def convert_flac_to_alac(input_file: Path, output_dir: Path) -> Path:
    """
    Function that converts a song from a .flac format to ALAC

    Parameters
    ----------
    input_file : Path
        Path to desired track
    output_dir : Path
        Path to put the new ALAC file

    Returns
    -------
    Path
        The new file's location
    """
    basename = input_file.stem
    output_file = (output_dir / basename).with_suffix(".m4a")
    if os.path.exists(output_file):
        return output_file

    command = [
        "ffmpeg",
        "-i",
        f"{str(input_file)}",
        "-y",
        "-v",
        "0",
        "-vcodec",
        "copy",
        "-acodec",
        "alac",
        f"{str(output_file)}",
    ]
    res = Popen(command)
    res.wait()

    return output_file


def convert_opus_to_alac(input_file: Path, output_dir: Path) -> Path:
    """
    Function that converts a song from a .opus format to ALAC. probably not good.

    Parameters
    ----------
    input_file : Path
        Path to desired track
    output_dir : Path
        Path to put the new ALAC file

    Returns
    -------
    Path
        The new file's location
    """
    """
    Function that converts a song from its current file format to ALAC

    Parameters
    ----------
    input_file : Path
        Path to desired track
    output_dir : Path
        Path to put the new ALAC file

    Returns
    -------
    Path
        The new file's location
    """
    basename = input_file.stem
    output_file = (output_dir / basename).with_suffix(".m4a")
    if os.path.exists(output_file):
        return output_file

    command = [
        "ffmpeg",
        "-i",
        f"{input_file}",
        "-y",
        "-v",
        "0",
        "-map_metadata",
        "0:s:a:0",
        "-c:a",
        "alac",
        f"{output_file}",
    ]

    res = Popen(command)
    res.wait()

    return output_file


song_file_extensions = {
    ".flac": convert_flac_to_alac,
    ".opus": convert_opus_to_alac,
    ".m4a": copy2,
    # add more as they are found
}


def convert_song_to_alac(input_file: Path, output_dir: Path) -> Path:
    """
    Function that converts a song from its current file format to ALAC

    Parameters
    ----------
    input_file : Path
        Path to desired track
    output_dir : Path
        Path to put the new ALAC file

    Returns
    -------
    Path
        The new file's location
    """
    filetype = input_file.suffix

    out_file: Path = song_file_extensions[filetype](input_file, output_dir)
    return out_file


def convert_album_to_alac(album_dir: Path, output_dir: Path) -> Path:
    """Function that runs `convert_song_to_alac` on a whole directory of songs

    Parameters
    ----------
    album_dir : Path
        Directory of songs to convert to ALAC
    output_dir : Path
        Directory to place new files

    Returns
    -------
    Path
        `output_dir`
    """
    songs = [
        album_dir / x
        for x in album_dir.iterdir()
        if x.suffix in song_file_extensions.keys()
    ]
    album_name = os.path.basename(album_dir)
    out_songs = [
        convert_song_to_alac(song, output_dir)
        for song in tqdm(
            songs, total=len(songs), position=1, leave=False, desc=album_name
        )
    ]

    return output_dir


def convert_albums_to_alac(input_dirs: list[Path], output_dir: Path) -> None:
    """
    i'm not going as hard on this one. sanitizes input and does a loop to run `convert_album_to_alac` on all albums input
    """
    input_dirs: list[Path] = [Path(x) for x in input_dirs]
    output_dir: Path = Path(output_dir)

    # try to figure out how to not do this first pass, this sucks
    glob_dirs = []
    rm_dirs = []

    # get the directories that need to be globbed
    for input_dir in input_dirs:
        if "*" not in str(input_dir):
            continue
        new_dirs = [
            x for x in glob(str(input_dir), recursive=True) if (input_dir / x).is_dir()
        ]
        glob_dirs.extend(new_dirs)
        rm_dirs.append(input_dir)

    # remove the directories that were globbed
    for rm_dir in rm_dirs:
        input_dirs.remove(rm_dir)

    # extend the input_dirs list with the new album dirs
    input_dirs.extend(glob_dirs)
    input_dirs.sort()

    for input_dir in tqdm(input_dirs, total=len(input_dirs), position=0):
        convert_album_to_alac(input_dir, output_dir)


if __name__ == "__main__":
    if len(argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} [config yaml]")

    config_file = argv[1]

    data = None
    with open(config_file, "r") as infile:
        data = yaml.safe_load(infile)

    convert_albums_to_alac(**data)
