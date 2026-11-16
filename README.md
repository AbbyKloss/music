# music
my scripts i use to keep my music straight on my DAPs

## [copy_to_itunes.py](./src/copy_to_itunes.py)
Copies all song files from a `src` directory to a `dst` directory, with a `chk` directory, which it uses to see if the files already existed based on track artist and track title.

## Usage
```shell
python copy_to_itunes.py [config.py]
```

filetypes:
- `flac`
- `ogg`
- `m4a`

Note: An example config file is located at [itunes_example_config.yaml](./configs/itunes_example_config.yaml)

## [convert_to_alac.py](./src/convert_to_alac.py)
Converts a song from all considered filetypes to `.m4a`.

## Usage
```shell
python convert_to_alac.py [config.py]
```

filetypes:
- `flac`
- `ogg`
- `m4a`

Note: An example config file is located at [config.yaml](./configs/config.yaml)

## [copy_to_device.py](./src/copy_to_device.py)
Copies all files from the given filetype to another path, checking first to see if the exact path relative to the `dst` path already exists.

## Usage
```shell
python copy_to_device.py [config.py]
```

filetypes:
- dealer's choice

Note: An example config file is located at [copy_config.yaml](./configs/copy_config.yaml)


## Install
requires conda. 
```shell
conda env create -f env.yaml
```
