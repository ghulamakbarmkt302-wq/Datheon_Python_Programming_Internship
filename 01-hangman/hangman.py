"""Hangman: a console word guessing game.

The player guesses a hidden word one letter at a time. Each wrong guess adds
a part to the ASCII gallows. Repeating a letter costs nothing.

Optional: save an English word list as 'words.txt' next to this file (one
word per line). If the file is missing, a built-in list is used.
"""
import random
import string
from pathlib import Path

MAX_MISTAKES = 6
WORD_FILE = Path(__file__).with_name("words.txt")
DEFAULT_WORDS = [
    "python", "variable", "function", "computer", "program", "keyboard",
    "algorithm", "developer", "university", "console", "string", "library",
    "network", "database", "history", "science", "pakistan", "lahore",
    "elephant", "mountain", "rainbow", "treasure", "guitar", "sunshine",
]

# Gallows drawing for 0 to 6 mistakes. Index = number of mistakes so far.
STAGES = [
    """
  +---+
  |   |
      |
      |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========""",
]


def load_words(path=WORD_FILE):
    """Return the words from the word file, or the built-in list if unusable."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return DEFAULT_WORDS
    words = [line.strip().lower() for line in lines]
    words = [w for w in words if w.isalpha()]
    return words or DEFAULT_WORDS


def masked(word, guessed):
    """Show guessed letters and '_' for the rest, e.g. '_ A _ H E O N'."""
    return " ".join(c.upper() if c in guessed else "_" for c in word)


def print_banner(lines):
    width = max(len(line) for line in lines) + 4
    print("+" + "-" * width + "+")
    for line in lines:
        print("|  " + line.ljust(width - 2) + "|")
    print("+" + "-" * width + "+")


def print_board(word, guessed, mistakes):
    print()
    print(STAGES[mistakes])
    print()
    print("Word:     ", masked(word, guessed))
    print("Guessed:  ", " ".join(sorted(g.upper() for g in guessed)) or "-")
    print(f"Mistakes: {mistakes}/{MAX_MISTAKES} (wrong guesses left: {MAX_MISTAKES - mistakes})")


def ask_letter(guessed):
    """Ask until the player gives a new single letter a-z."""
    while True:
        raw = input("Guess a letter: ").strip().lower()
        if len(raw) != 1 or raw not in string.ascii_lowercase:
            print("Please enter a single letter from a to z.")
        elif raw in guessed:
            print(f"You already guessed '{raw.upper()}'. No penalty, try another letter.")
        else:
            return raw


def play_round(word):
    """Play one game. Return True if the player wins, False if they lose."""
    guessed = set()
    mistakes = 0
    while True:
        print_board(word, guessed, mistakes)
        letter = ask_letter(guessed)
        guessed.add(letter)
        if letter in word:
            print(f"Good guess! '{letter.upper()}' is in the word.")
        else:
            mistakes += 1
            print(f"Sorry, '{letter.upper()}' is not in the word.")

        if all(c in guessed for c in word):
            print_board(word, guessed, mistakes)
            print()
            print_banner(["YOU WIN!", f"You guessed the word: {word.upper()}"])
            return True
        if mistakes == MAX_MISTAKES:
            print_board(word, guessed, mistakes)
            print()
            print_banner(["GAME OVER", f"The word was: {word.upper()}"])
            return False


def main():
    words = load_words()
    print_banner(["HANGMAN", "Guess the hidden word, one letter at a time."])
    try:
        while True:
            play_round(random.choice(words))
            again = input("\nPlay again? (y/n): ").strip().lower()
            if again not in ("y", "yes"):
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("Thanks for playing Hangman!")


if __name__ == "__main__":
    main()
