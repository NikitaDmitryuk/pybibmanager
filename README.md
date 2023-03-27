# PyBibManager

PyBibManager is a command-line tool for processing `.bib` files to remove unused and/or duplicate entries.
The tool helps researchers to keep their bibliography files clean and organized.
It is particularly useful when working with large `.bib` files containing numerous sources.

## Features

- Remove unused entries from the `.bib` file based on citations in the LaTeX project files
- Detect duplicate entries in the `.bib` file and let the user decide which entries to keep
- Handle partial duplicates and differences in entry fields
- Accept BibTeX file and LaTeX directory as command-line arguments

## Usage

1. Install Python 3.6 or higher if you haven't already.
2. Download the script `pybibmanager.py` and save it to a convenient location.
3. Open a terminal (command prompt) and navigate to the location of the script.
4. Run the script with appropriate command-line options.

```sh
python pybibmanager.py --bib-file [BIB_FILE_PATH] --tex-dir [TEX_DIRECTORY_PATH] [--remove-unused] [--remove-duplicates]
```

## Arguments

- `--bib-file`: The path to the `.bib` file that needs to be processed.
- `--tex-dir`: The directory containing the LaTeX project files. The script will search for citations in all `.tex` files within this directory.
- `--remove-unused`: Remove entries in the `.bib` file that are not cited in the LaTeX project files.
- `--remove-duplicates`: Remove duplicate entries in the `.bib` file. The tool will display the detected duplicates and let the user decide which entries to keep.

## Example

```sh
python pybibmanager.py --bib-file bibliography.bib --tex-dir ./chapters --remove-unused --remove-duplicates
```

This command will process the `bibliography.bib` file, removing unused entries based on the citations found in the LaTeX project files within the `./chapters` directory.
It will also detect duplicate entries and prompt the user to decide which ones to keep.
