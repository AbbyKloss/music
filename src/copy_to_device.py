import logging
import os
from pathlib import Path
from shutil import copy2
from sys import argv

import yaml
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__file__)


def main(src: os.PathLike, dst: os.PathLike, allowed_filetypes: list[str]):
    src_path = Path(src)
    dst_path = Path(dst)
    files: list[tuple[Path, Path]] = []

    logger.info("Getting all files...")
    for filetype in allowed_filetypes:
        pattern = f"*.{filetype}"
        files.extend(
            [
                (x, dst_path / x.relative_to(src_path))
                for x in src_path.rglob(pattern)
                if not (dst_path / x.relative_to(src_path)).exists()
            ]
        )

    files.sort()

    logger.info(f"Got [{len(files)}] file(s). Beginning copy process...")
    for s, d in tqdm(files, total=len(files)):
        logger.debug(d)
        if d.exists():
            continue
        d.parent.mkdir(parents=True, exist_ok=True)
        try:
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
