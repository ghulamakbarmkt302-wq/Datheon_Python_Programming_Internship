import builtins
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chatbot as bot

FAQ = bot.load_faq(Path(__file__).with_name("faq.json"))


class ChatbotTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(bot.normalize("  What's the FEE?? "), "what s the fee")
        self.assertEqual(bot.normalize(""), "")

    def test_greeting(self):
        answer, done = bot.reply("Hello there", FAQ)
        self.assertIn("Welcome", answer)
        self.assertFalse(done)

    def test_hours_question(self):
        answer, _ = bot.reply("What are your timings?", FAQ)
        self.assertIn("9:00 AM", answer)

    def test_admission_question(self):
        answer, _ = bot.reply("I want to apply for admission", FAQ)
        self.assertIn("Admissions Office", answer)

    def test_keyword_is_whole_word_only(self):
        # 'hi' must not match inside 'this' or 'within'
        self.assertNotIn("Welcome", bot.reply("this is within reach", FAQ)[0])

    def test_multi_intent_answers_both(self):
        answer, _ = bot.reply("fees and library", FAQ)
        self.assertIn("Fee details", answer)
        self.assertIn("library is open", answer.lower())
        self.assertEqual(answer.count("\n"), 1)

    def test_multi_intent_three_topics(self):
        answer, _ = bot.reply("fees, library and timings", FAQ)
        self.assertEqual(answer.count("\n"), 2)

    def test_fallback_for_unknown(self):
        answer, done = bot.reply("tell me a joke", FAQ)
        self.assertEqual(answer, FAQ["fallback"])
        self.assertFalse(done)

    def test_empty_message_asks_again(self):
        answer, done = bot.reply("   ", FAQ)
        self.assertIn("Please type a question", answer)
        self.assertFalse(done)

    def test_exit_words_stop_chat(self):
        for word in ["bye", "EXIT", " quit "]:
            answer, done = bot.reply(word, FAQ)
            self.assertTrue(done, word)
            self.assertIn("Goodbye", answer)

    def test_load_faq_rejects_bad_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad.json"
            path.write_text(json.dumps({"intents": [{"name": "x"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                bot.load_faq(path)
            path.write_text("{ not json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                bot.load_faq(path)

    def test_chat_loop_runs_until_bye(self):
        inputs = iter(["hours", "", "bye"])
        lines = []
        bot.chat(FAQ, input_fn=lambda prompt="": next(inputs), output=lines.append)
        text = "\n".join(lines)
        self.assertIn("9:00 AM", text)
        self.assertIn("Please type a question", text)
        self.assertIn("Goodbye", text)

    def test_chat_loop_handles_ctrl_c(self):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt
        lines = []
        bot.chat(FAQ, input_fn=raise_interrupt, output=lines.append)  # must not raise
        self.assertTrue(lines)

    def test_main_missing_file(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = bot.main(["--faq", "/nonexistent/faq.json"])
        self.assertEqual(code, 1)
        self.assertIn("not found", buf.getvalue())

    def test_main_runs_chat(self):
        orig = builtins.input
        builtins.input = lambda prompt="": "bye"
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = bot.main([])
        finally:
            builtins.input = orig
        self.assertEqual(code, 0)
        self.assertIn("Goodbye", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=1)
