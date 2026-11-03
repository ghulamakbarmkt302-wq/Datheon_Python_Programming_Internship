# Datheon Python Programming Internship: Projects

This repository contains my four Python projects for the Datheon Python Programming Internship. Each project is in its own folder, with its own README explaining how to run it and how to test it.

| # | Folder | Project | What it does |
|---|---|---|---|
| 1 | `01-hangman` | Hangman word guessing game | Console game: guess a hidden word letter by letter in 6 attempts, with ASCII gallows art. |
| 2 | `02-stock-portfolio` | Stock portfolio performance tracker | Tracks stock positions, calculates value and gain/loss, and saves summaries to CSV. |
| 3 | `03-file-organizer` | Automated file organizer and cleanup utility | Sorts files in a folder into Documents, Images, Videos, Archives and Code folders. Dry run by default. |
| 4 | `04-chatbot` | Rule-based help desk chatbot | Answers FAQs from a JSON file using keyword matching, with fallback replies and exit commands. |

## Requirements

- Python 3.8 or newer. No third-party packages are needed.

## How to run

Open a terminal in the project folder and run:

```bash
python hangman.py
python portfolio.py --prices sample_prices.csv
python organizer.py "path/to/a/test/folder"
python chatbot.py
```

On Windows, use `py` instead of `python` if `python` is not recognised.

## Tests

Each project has a test file. Run it from its folder:

```bash
python test_portfolio.py
python test_organizer.py
python test_chatbot.py
```

## License

Each project folder contains an MIT license.
