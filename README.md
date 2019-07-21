# video-metadata-parser README

This contains a script to add the source file's _'DateTimeOriginal'_ to the file's filename as:

> {FILENAME}.YYYYMMDD_HHMM.{ORIIGNAL EXT}


## Usage

To update filenames in a given directory to include the _'DateTimeOriginal'_ in the filename use the command below:

```
python update_filenames.py --directory tmp/
```