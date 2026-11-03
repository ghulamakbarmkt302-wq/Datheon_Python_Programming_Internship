# University Help Desk Chatbot (Python)

A rule-based chatbot for a university help desk. Type a question in the terminal, and the bot answers from a FAQ file. There is no AI: the bot finds keywords in your message and gives the matching answer.

## Features

- Answers questions about office hours, admission, fees, library and contact
- Handles several topics in one message ("fees and library")
- Ignores case, extra spaces and punctuation
- Matches whole words only, so "hi" does not match "this"
- Polite fallback for questions it does not understand
- Exit with `bye`, `exit` or `quit` (or Ctrl+C)
- Clear error message if the FAQ file is missing or broken
- Uses only the standard library (no installs needed)

## Requirements

- Python 3.8 or newer

## How to run

```bash
python3 chatbot.py
```

On Windows, use `py chatbot.py`, or `python chatbot.py`.

Example:

```
Help Desk Bot: Hello! I can help with: hours, admission, fees, library, contact. Type 'bye' to exit.
You: what are your timings?
Help Desk Bot: The help desk is open Monday to Saturday, 9:00 AM to 5:00 PM. ...
You: bye
Help Desk Bot: Goodbye! Have a nice day.
```

## Editing the answers

All answers are in `faq.json`, so you can change them without touching the Python code.

- Each **intent** has a `name`, a list of `keywords` and an `answer`.
- If a message contains keywords from several intents, the bot gives the answers for up to 3 of them.
- `fallback` is the reply for unknown questions.
- `exit_words` are the words that end the chat.

The file included here uses **sample information**. Replace the hours, contact details and fee text with the real ones before using it.

## Tests

```bash
python3 test_chatbot.py
```

## Files

| File | Purpose |
|---|---|
| `chatbot.py` | The chatbot program |
| `faq.json` | Questions, keywords and answers (sample data) |
| `test_chatbot.py` | Unit tests |
| `README.md` | This file |
