# Automated File Organizer & Cleanup Utility (Python)

A console script that tidies a cluttered folder such as Downloads. It looks at each file's extension and moves it into a category folder: Documents, Images, Videos, Archives or Code.

## Features

- Sorts files by extension into category folders, created automatically
- **Dry run by default:** shows what would happen and moves nothing
- Asks for confirmation before moving, unless you pass `--yes`
- Never overwrites a file: a clash becomes `report (1).pdf`
- Leaves subfolders, hidden files and unknown file types alone
- Skips files it cannot move (for example, permission denied) and keeps going
- Writes every action to `organizer.log` and prints a summary

## Requirements

- Python 3.8 or newer (standard library only)

## How to use

Preview first (nothing is moved):

```bash
python3 organizer.py ~/Downloads
```

Move the files, with a confirmation prompt:

```bash
python3 organizer.py ~/Downloads --run
```

Move the files without the prompt:

```bash
python3 organizer.py ~/Downloads --run --yes
```

On Windows, use `python` instead of `python3`, and a path such as `C:\Users\you\Downloads`.

Options:

| Option | Meaning |
|---|---|
| `folder` | The folder to organize (required) |
| `--run` | Actually move files. Without it, only a preview is shown |
| `--yes` | Skip the confirmation question when using `--run` |
| `--log FILE` | Where to write the log (default: `organizer.log` next to the script) |

## Categories

| Category | Extensions |
|---|---|
| Documents | .pdf, .doc, .docx, .txt, .xlsx, .pptx |
| Images | .jpg, .jpeg, .png, .gif, .bmp |
| Videos | .mp4, .mkv, .avi, .mov |
| Archives | .zip, .rar, .7z |
| Code | .py, .js, .html, .css, .cpp, .java, .c |

To add an extension, add a line to the `CATEGORIES` dictionary in `organizer.py`.

## Tests

```bash
python3 test_organizer.py
```

The tests use temporary folders, so your files are never touched.

## Files

| File | Purpose |
|---|---|
| `organizer.py` | The program |
| `test_organizer.py` | Unit tests |
| `README.md` | This file |

## Notes

- Only the top level of the folder is sorted. Subfolders are not changed.
- Use a test folder first, and keep a backup of anything important.
