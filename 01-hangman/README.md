# Hangman Word Guessing Game (Console, Python)

A terminal Hangman game written in Python 3. Guess the hidden word one letter at a time. Each wrong guess adds a part to the ASCII gallows. You get 6 wrong guesses.

## Features

- ASCII gallows that updates with every wrong guess
- Masked word display, for example `_ A _ H E O N`
- Tracks guessed letters; repeating a letter is not penalised
- Input validation (only single letters a to z)
- Random word from a built-in list, or from your own `words.txt`
- Victory and defeat screens, and a play-again option

## Requirements

- Python 3.8 or newer (standard library only, no installs needed)

## How to run

```bash
python3 hangman.py
```

On Windows:

```bash
python hangman.py
```

### Word list

`words.txt` is included. It has 8,794 English words of 4 or more letters, one per line, taken from a common-English frequency list. Offensive or unsuitable words were removed. To use your own list, replace `words.txt` with another one-word-per-line file. If the file is missing or empty, the built-in list is used.

## Project structure

| File | Purpose |
|---|---|
| `hangman.py` | The whole game |
| `words.txt` | Word list used for random words |
| `README.md` | This file |

## How the code is organised

| Function | What it does |
|---|---|
| `load_words()` | Reads `words.txt` or falls back to the built-in list |
| `masked()` | Builds the `_ A _ H E O N` display |
| `print_board()` | Shows the gallows, masked word, guessed letters and mistakes |
| `ask_letter()` | Asks for a new valid letter |
| `play_round()` | Runs one game and returns win or loss |
| `main()` | Starts the game and handles play-again and Ctrl+C |

## Rules

- You have 6 wrong guesses. On the 6th, the game is over.
- A correct letter reveals every matching position in the word.
- Guessing a letter you already tried does not count as a mistake.
