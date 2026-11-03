"""Rule-based chatbot for a university help desk.

The bot reads what the user types, finds keywords from faq.json, and answers
with the matching FAQ entries. There is no AI here: every answer comes from
the JSON file, so you can change the answers without touching the code.

Type 'bye', 'exit' or 'quit' to stop.
"""
import argparse
import json
import re
from pathlib import Path

FAQ_FILE = Path(__file__).with_name("faq.json")
MAX_ANSWERS = 3  # if a message matches several topics, answer up to this many


def load_faq(path=FAQ_FILE):
    """Read and check the FAQ file. Raises ValueError if the content is wrong."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("intents"), list):
        raise ValueError("the file needs an 'intents' list")
    for intent in data["intents"]:
        if not intent.get("name") or not intent.get("keywords") or not intent.get("answer"):
            raise ValueError(f"an intent is missing 'name', 'keywords' or 'answer': {intent}")
    data.setdefault("bot_name", "Bot")
    data.setdefault("exit_words", ["bye", "exit", "quit"])
    data.setdefault("fallback", "Sorry, I did not understand that.")
    return data


def normalize(text):
    """Lowercase, remove punctuation and extra spaces: '  What's the FEE?? ' -> 'what s the fee'."""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def keyword_hits(text, intent):
    """Count how many of the intent's keywords appear in the normalized text as whole words."""
    hits = 0
    for keyword in intent["keywords"]:
        kw = normalize(keyword)
        if kw and re.search(r"\b" + re.escape(kw) + r"\b", text):
            hits += 1
    return hits


def find_intents(text, faq):
    """Return the best matching intents (most keyword hits first, at most MAX_ANSWERS)."""
    scored = []
    for intent in faq["intents"]:
        hits = keyword_hits(text, intent)
        if hits:
            scored.append((hits, intent))
    scored.sort(key=lambda pair: -pair[0])  # sort is stable: ties keep the file order
    return [intent for _, intent in scored[:MAX_ANSWERS]]


def reply(message, faq):
    """Return (answer, should_exit) for one message from the user."""
    text = normalize(message)
    if not text:
        return "Please type a question, for example: 'What are your office hours?'", False
    exit_words = {normalize(word) for word in faq["exit_words"]}
    if text in exit_words:
        return "Goodbye! Have a nice day.", True
    intents = find_intents(text, faq)
    if not intents:
        return faq["fallback"], False
    return "\n".join(intent["answer"] for intent in intents), False


def chat(faq, input_fn=None, output=print):
    """Run the conversation until the user says goodbye or presses Ctrl+C."""
    input_fn = input_fn or input
    topics = ", ".join(intent["name"] for intent in faq["intents"] if intent["name"] != "greeting")
    output(f"{faq['bot_name']}: Hello! I can help with: {topics}. Type 'bye' to exit.")
    while True:
        try:
            message = input_fn("You: ")
        except (EOFError, KeyboardInterrupt):
            output("")
            break
        answer, done = reply(message, faq)
        output(f"{faq['bot_name']}: {answer}")
        if done:
            break


def main(argv=None):
    parser = argparse.ArgumentParser(description="University help desk chatbot")
    parser.add_argument("--faq", default=str(FAQ_FILE), help="FAQ JSON file (default: faq.json)")
    args = parser.parse_args(argv)
    try:
        faq = load_faq(args.faq)
    except FileNotFoundError:
        print(f"Error: FAQ file not found: {args.faq}")
        return 1
    except (ValueError, json.JSONDecodeError) as err:
        print(f"Error: FAQ file is not valid: {err}")
        return 1
    chat(faq)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
