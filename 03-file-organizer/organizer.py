"""Automated file organizer and cleanup utility.

Sorts the files in a folder (for example Downloads) into category subfolders
based on their extension: Documents, Images, Videos, Archives and Code.

Safe by default: without --run, nothing is moved. The program only shows what
it would do. Files with an unknown extension are left where they are.
Name clashes are handled by renaming the new file, for example
'report (1).pdf', so an existing file is never overwritten.
"""
import argparse
import logging
import os
import shutil
from collections import Counter
from pathlib import Path

DEFAULT_LOG = Path(__file__).with_name("organizer.log")

CATEGORIES = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".xlsx": "Documents", ".pptx": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".html": "Code", ".css": "Code",
    ".cpp": "Code", ".java": "Code", ".c": "Code",
}


def category_for(path):
    """Return the category name for a file, or None if the extension is unknown."""
    return CATEGORIES.get(Path(path).suffix.lower())


def unique_destination(folder, name):
    """Return a path in folder that does not exist yet: 'a.pdf', 'a (1).pdf', ..."""
    dest = Path(folder) / name
    stem, suffix = Path(name).stem, Path(name).suffix
    counter = 1
    while dest.exists():
        dest = Path(folder) / f"{stem} ({counter}){suffix}"
        counter += 1
    return dest


def plan_moves(source):
    """Look at the top level of source only (no subfolders, no hidden files).

    Returns (moves, unknown): moves is a sorted list of (file_path, category),
    unknown is a list of files whose extension has no category.
    """
    moves, unknown = [], []
    with os.scandir(source) as entries:
        for entry in entries:
            if entry.name.startswith("."):
                continue
            if not entry.is_file(follow_symlinks=False):
                continue
            path = Path(entry.path)
            category = category_for(path)
            if category is None:
                unknown.append(path)
            else:
                moves.append((path, category))
    return sorted(moves), sorted(unknown)


def organize(source, dry_run=True, logger=None):
    """Move files from source into category folders. Return a summary dict."""
    logger = logger or logging.getLogger("organizer")
    source = Path(source)
    if not source.is_dir():
        raise NotADirectoryError(f"'{source}' is not a folder")

    moves, unknown = plan_moves(source)
    result = {
        "moved": 0,       # files actually moved (run mode)
        "planned": 0,     # files that would be moved (dry run)
        "failed": 0,      # files skipped because of an error
        "unknown": len(unknown),
        "by_category": Counter(),
    }

    for path, category in moves:
        folder = source / category
        if dry_run:
            dest = unique_destination(folder, path.name)
            result["planned"] += 1
            result["by_category"][category] += 1
            logger.info("[dry run] %s -> %s", path.name, dest.relative_to(source))
            continue

        try:
            folder.mkdir(exist_ok=True)
            dest = unique_destination(folder, path.name)
            shutil.move(str(path), str(dest))
        except PermissionError:
            result["failed"] += 1
            logger.warning("SKIPPED %s: permission denied", path.name)
        except FileExistsError:
            result["failed"] += 1
            logger.warning("SKIPPED %s: a file with this name already exists", path.name)
        except OSError as err:
            result["failed"] += 1
            logger.warning("SKIPPED %s: %s", path.name, err)
        else:
            result["moved"] += 1
            result["by_category"][category] += 1
            logger.info("MOVED %s -> %s", path.name, dest.relative_to(source))

    return result


def print_summary(result, source, dry_run):
    mode = "DRY RUN (nothing was moved)" if dry_run else "MOVED"
    count = result["planned"] if dry_run else result["moved"]
    print()
    print("=== Summary ===")
    print(f"Folder:          {source}")
    print(f"Mode:            {mode}")
    print(f"Files {'to move' if dry_run else 'moved'}:  {count}")
    print(f"Left alone (unknown type): {result['unknown']}")
    print(f"Skipped (errors):          {result['failed']}")
    if result["by_category"]:
        print("By category:")
        for name, n in sorted(result["by_category"].items()):
            print(f"  {name:<10} {n}")
    if dry_run:
        print("\nRun again with --run to move the files.")


def setup_logging(log_path):
    logger = logging.getLogger("organizer")
    for old in logger.handlers[:]:
        old.close()
        logger.removeHandler(old)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sort files into category folders by extension.")
    parser.add_argument("folder", help="folder to organize, for example ~/Downloads")
    parser.add_argument("--run", action="store_true", help="actually move files (default is a dry run)")
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation when using --run")
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="log file path")
    args = parser.parse_args(argv)

    source = Path(args.folder).expanduser()
    if not source.is_dir():
        print(f"Error: '{source}' is not a folder.")
        return 1

    dry_run = not args.run
    if not dry_run and not args.yes:
        answer = input(f"This will move files inside {source}. Type 'yes' to continue: ").strip().lower()
        if answer != "yes":
            print("Cancelled. Nothing was moved.")
            return 0

    logger = setup_logging(args.log)
    result = organize(source, dry_run=dry_run, logger=logger)
    print_summary(result, source, dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
