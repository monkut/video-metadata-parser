"""
Convert filenames, for supported files, in a given directory to include the 'DateTimeOriginal' value as:

    {FILENAME}.YYYYMMDD_HHMM.{ORIIGNAL EXT}

"""
import sys
import logging
import datetime
from pathlib import Path
from functools import lru_cache
import pprint
import exiftool


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (%(name)s) %(funcName)s: %(message)s'
)

logger = logging.getLogger()


class ExifInfo:

    def __init__(self, exif_info: dict):
        self._info = exif_info

        self._info['SourceFile'] = Path(exif_info['SourceFile'])

        # update datetime strings to datetime objects
        datetime_string_suffixes = (
            'Date',
            'DateTimeOriginal'
        )
        for key in self._info.keys():
            if key.endswith(datetime_string_suffixes):
                self._info[key] = self._parse_datetime_string(self._info[key])

    def _parse_datetime_string(self, datetime_string: str) -> datetime.datetime:
        datetime_obj = datetime.datetime.strptime(datetime_string, '%Y:%m:%d %H:%M:%S%z')
        return datetime_obj

    @property
    def filepath(self) -> Path:
        return self._info['SourceFile']

    @property
    @lru_cache(maxsize=1)
    def datetime_original(self):
        for key in self._info.keys():
            if key.endswith('DateTimeOriginal'):
                return self._info[key]
        else:
            raise KeyError('Could not find Key ending with: DateTimeOriginal')

    def __str__(self):
        return pprint.pformat(self._info, indent=4)

    def __repr__(self):
        return self.__str__()


def process_directory(directory: Path, extensions_to_process=('.mts', )):
    target_filepaths = []
    for item in directory.glob('*'):
        if item.is_file() and item.name.lower().endswith(extensions_to_process):
            target_filepaths.append(item)

    assert target_filepaths
    with exiftool.ExifTool() as et:
        filepaths = [str(p) for p in target_filepaths]
        files_metadata = et.get_metadata_batch(filepaths)

    for data in files_metadata:
        file_metadata = ExifInfo(data)
        yyyymmdd_hhmm = file_metadata.datetime_original.strftime('%Y%m%d_%H%M')
        if not file_metadata.filepath.name.endswith(f'{yyyymmdd_hhmm}{file_metadata.filepath.suffix}'):
            updated_ext_filename = file_metadata.filepath.with_suffix(f'.{yyyymmdd_hhmm}{file_metadata.filepath.suffix}')
            logger.info(f'changing filename: {file_metadata.filepath} -> {updated_ext_filename}')
            file_metadata.filepath.replace(updated_ext_filename)
        else:
            logger.info(f'SKIPPING - (filename already contains original_datetime) - {file_metadata.filepath}')


def directory_path_type(obj: str):
    p = Path(obj)
    assert p.exists(), f'Not Found: {obj}'
    assert p.is_dir(), f'Not a directory: {obj}'
    return p


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-d', '--directory',
        type=directory_path_type,
    )
    args = parser.parse_args()
    process_directory(args.directory)

