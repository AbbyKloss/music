import logging
import os
from json import dumps
from pathlib import Path
from shutil import copy2
from sys import argv

import yaml
from tinytag import TinyTag
from tqdm import tqdm

from convert_to_alac import convert_song_to_alac, song_file_extensions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__file__)


def get_track_artist_title_from_path(track_path: Path) -> str:
    tags = TinyTag.get(track_path)
    return f"{tags.artist}_{tags.title}"


def main(
    src: os.PathLike, chk: os.PathLike, dst: os.PathLike, allowed_filetypes: list[str]
):
    src_path = Path(src)
    chk_path = Path(chk)
    dst_path = Path(dst)
    files: list[tuple[Path, Path]] = []

    skip_suffixes = [".m4a", ".mp3"]

    logger.info("Getting all files...")
    itunes_titles = [
        get_track_artist_title_from_path(x)
        for x in chk_path.rglob("*")
        if x.suffix in skip_suffixes
    ]

    for filetype in allowed_filetypes:
        pattern = f"*.{filetype}"

        files.extend(
            [
                [
                    x,
                    (dst_path / x.relative_to(src_path)),
                ]
                for x in src_path.rglob(pattern)
                if get_track_artist_title_from_path(x) not in itunes_titles
            ]
        )

    files.sort()

    for s, d in tqdm(files, total=len(files)):
        d.parent.mkdir(parents=True, exist_ok=True)
        try:
            if s.suffix in song_file_extensions.keys():
                convert_song_to_alac(s, d.parent)
            else:
                copy2(s, d)
        except OSError as e:
            logger.error(f"Failed at '{d}'")
            raise e


if __name__ == "__main__":
    if len(argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} [config yaml]")

    config_file = argv[1]

    data = None
    with open(config_file, "r") as infile:
        data = yaml.safe_load(infile)

    main(**data)
