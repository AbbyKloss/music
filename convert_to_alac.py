import json
import os
from glob import glob
from subprocess import Popen, run
from sys import argv
from shutil import copy2

import yaml
from tqdm import tqdm

# old bash ver. :
# #! /bin/bash

# OUTPUT_DIR="m4a_tests"

# mkdir ${OUTPUT_DIR};
# for i in *.flac; do
#         echo $i;
#         ffmpeg -i "$i" -y -v 0 -vcodec copy -ar 48000 -sample_fmt s16 "${OUTPUT_DIR}/${i%.flac}".flac;
#         ffmpeg -i "${OUTPUT_DIR}/$i" -y -v 0 -vcodec copy -acodec alac "${OUTPUT_DIR}/${i%.flac}".m4a;
#         rm "${OUTPUT_DIR}/$i";
# done


def convert_flac_to_alac(
    input_file: os.PathLike, output_dir: os.PathLike
) -> os.PathLike:
    """
    Function that converts a song from a .flac format to ALAC

    Parameters
    ----------
    input_file : os.PathLike
        Path to desired track
    output_dir : os.PathLike
        Path to put the new ALAC file

    Returns
    -------
    os.PathLike
        The new file's location
    """
    basename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{basename}.m4a")
    if os.path.exists(output_file):
        return output_file

    command = [
        "ffmpeg",
        "-i",
        f"{input_file}",
        "-y",
        "-v",
        "0",
        "-vcodec",
        "copy",
        "-acodec",
        "alac",
        f"{output_file}",
    ]
    res = Popen(command)
    res.wait()

    return output_file


def convert_opus_to_alac(input_file: os.PathLike, output_dir: os.PathLike):
    """
    Function that converts a song from a .opus format to ALAC. probably not good.

    Parameters
    ----------
    input_file : os.PathLike
        Path to desired track
    output_dir : os.PathLike
        Path to put the new ALAC file

    Returns
    -------
    os.PathLike
        The new file's location
    """
    """
    Function that converts a song from its current file format to ALAC

    Parameters
    ----------
    input_file : os.PathLike
        Path to desired track
    output_dir : os.PathLike
        Path to put the new ALAC file

    Returns
    -------
    os.PathLike
        The new file's location
    """
    basename, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.join(output_dir, f"{basename}.m4a")

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
        f'{output_file}',
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


def convert_song_to_alac(
    input_file: os.PathLike, output_dir: os.PathLike
) -> os.PathLike:
    """
    Function that converts a song from its current file format to ALAC

    Parameters
    ----------
    input_file : os.PathLike
        Path to desired track
    output_dir : os.PathLike
        Path to put the new ALAC file

    Returns
    -------
    os.PathLike
        The new file's location
    """
    filetype = os.path.splitext(input_file)[1]

    return song_file_extensions[filetype](input_file, output_dir)


def convert_album_to_alac(
    album_dir: os.PathLike, output_dir: os.PathLike
) -> os.PathLike:
    """Function that runs `convert_song_to_alac` on a whole directory of songs

    Parameters
    ----------
    album_dir : os.PathLike
        Directory of songs to convert to ALAC
    output_dir : os.PathLike
        Directory to place new files

    Returns
    -------
    os.PathLike
        `output_dir`
    """
    songs = [
        os.path.join(album_dir, x)
        for x in os.listdir(album_dir)
        if os.path.splitext(x)[-1] in song_file_extensions.keys()
    ]
    album_name = os.path.basename(album_dir)
    out_songs = [
        convert_song_to_alac(song, output_dir)
        for song in tqdm(
            songs, total=len(songs), position=1, leave=False, desc=album_name
        )
    ]

    return output_dir


def convert_albums_to_alac(input_dirs: list[os.PathLike], output_dir: os.PathLike):
    """
    i'm not going as hard on this one. sanitizes input and does a loop to run `convert_album_to_alac` on all albums input
    """

    # try to figure out how to not do this first pass, this sucks
    glob_dirs = []
    rm_dirs = []

    # get the directories that need to be globbed
    for input_dir in input_dirs:
        if "*" not in input_dir:
            continue
        new_dirs = [x for x in glob(input_dir) if os.path.isdir(os.path.join(input_dir, x))]
        glob_dirs.extend(new_dirs)
        rm_dirs.append(input_dir)

    # remove the directories that were globbed
    for rm_dir in rm_dirs:
        input_dirs.remove(rm_dir)

    # extend the input_dirs list with the new album dirs
    input_dirs.extend(glob_dirs)
    input_dirs.sort()

    for input_dir in tqdm(input_dirs, total=len(input_dirs), position=0):
        album_dir = os.path.normpath(input_dir)
        convert_album_to_alac(album_dir, os.path.normpath(output_dir))


if __name__ == "__main__":
    if len(argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} [config yaml]")

    config_file = argv[1]

    data = None
    with open(config_file, "r") as infile:
        data = yaml.safe_load(infile)

    convert_albums_to_alac(**data)
