import builtins
import contextlib
import io
import logging
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import organizer as org


def make_files(folder, names):
    for name in names:
        (Path(folder) / name).write_text("x", encoding="utf-8")


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.log = logging.getLogger("test-organizer")
        self.log.handlers.clear()
        self.log.addHandler(logging.NullHandler())

    def sample_folder(self):
        folder = self.tmp / "Downloads"
        folder.mkdir()
        make_files(folder, ["a.pdf", "b.jpg", "c.zip", "d.xyz", "PHOTO.JPG", "notes.TXT", ".hidden.pdf"])
        (folder / "SubDir").mkdir()
        make_files(folder / "SubDir", ["inside.pdf"])
        return folder

    def test_category_for(self):
        self.assertEqual(org.category_for("x.pdf"), "Documents")
        self.assertEqual(org.category_for("PHOTO.JPG"), "Images")
        self.assertEqual(org.category_for("clip.mp4"), "Videos")
        self.assertEqual(org.category_for("bundle.zip"), "Archives")
        self.assertEqual(org.category_for("main.py"), "Code")
        self.assertIsNone(org.category_for("mystery.xyz"))
        self.assertIsNone(org.category_for("noext"))

    def test_unique_destination_adds_counter(self):
        folder = self.tmp / "F"
        folder.mkdir()
        make_files(folder, ["a.pdf", "a (1).pdf"])
        self.assertEqual(org.unique_destination(folder, "a.pdf").name, "a (2).pdf")
        self.assertEqual(org.unique_destination(folder, "new.pdf").name, "new.pdf")

    def test_plan_moves_skips_subfolders_hidden_and_sorts(self):
        folder = self.sample_folder()
        moves, unknown = org.plan_moves(folder)
        names = [p.name for p, _ in moves]
        self.assertEqual(names, ["PHOTO.JPG", "a.pdf", "b.jpg", "c.zip", "notes.TXT"])
        self.assertEqual([p.name for p in unknown], ["d.xyz"])
        self.assertNotIn(".hidden.pdf", names)
        self.assertNotIn("inside.pdf", names)

    def test_dry_run_moves_nothing(self):
        folder = self.sample_folder()
        result = org.organize(folder, dry_run=True, logger=self.log)
        self.assertEqual(result["planned"], 5)
        self.assertEqual(result["moved"], 0)
        self.assertEqual(result["unknown"], 1)
        self.assertTrue((folder / "a.pdf").exists())
        self.assertFalse((folder / "Documents").exists())

    def test_run_moves_files_into_categories(self):
        folder = self.sample_folder()
        result = org.organize(folder, dry_run=False, logger=self.log)
        self.assertEqual(result["moved"], 5)
        self.assertEqual(result["failed"], 0)
        self.assertTrue((folder / "Documents" / "a.pdf").exists())
        self.assertTrue((folder / "Documents" / "notes.TXT").exists())
        self.assertTrue((folder / "Images" / "b.jpg").exists())
        self.assertTrue((folder / "Images" / "PHOTO.JPG").exists())
        self.assertTrue((folder / "Archives" / "c.zip").exists())
        self.assertTrue((folder / "d.xyz").exists())            # unknown type stays put
        self.assertTrue((folder / "SubDir" / "inside.pdf").exists())  # subfolder untouched
        self.assertTrue((folder / ".hidden.pdf").exists())            # hidden file untouched
        self.assertEqual(result["by_category"]["Documents"], 2)

    def test_name_clash_does_not_overwrite(self):
        folder = self.tmp / "Downloads"
        folder.mkdir()
        make_files(folder, ["report.pdf"])
        (folder / "Documents").mkdir()
        (folder / "Documents" / "report.pdf").write_text("OLD", encoding="utf-8")
        org.organize(folder, dry_run=False, logger=self.log)
        self.assertEqual((folder / "Documents" / "report.pdf").read_text(encoding="utf-8"), "OLD")
        self.assertTrue((folder / "Documents" / "report (1).pdf").exists())

    def test_permission_error_is_counted_and_others_still_move(self):
        folder = self.tmp / "Downloads"
        folder.mkdir()
        make_files(folder, ["locked.pdf", "free.pdf"])
        real_move = shutil.move

        def fake_move(src, dst):
            if src.endswith("locked.pdf"):
                raise PermissionError("denied")
            return real_move(src, dst)

        with mock.patch.object(org.shutil, "move", side_effect=fake_move):
            result = org.organize(folder, dry_run=False, logger=self.log)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["moved"], 1)
        self.assertTrue((folder / "locked.pdf").exists())
        self.assertTrue((folder / "Documents" / "free.pdf").exists())

    def test_missing_folder_raises(self):
        with self.assertRaises(NotADirectoryError):
            org.organize(self.tmp / "nope", dry_run=True, logger=self.log)

    def test_cli_dry_run_default_and_confirmation(self):
        folder = self.sample_folder()
        log_file = self.tmp / "t.log"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = org.main([str(folder), "--log", str(log_file)])
        self.assertEqual(code, 0)
        self.assertIn("DRY RUN", buf.getvalue())
        self.assertTrue((folder / "a.pdf").exists())

        # --run asks for confirmation; 'no' cancels
        answers = iter(["no"])
        orig = builtins.input
        builtins.input = lambda p="": next(answers)
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                org.main([str(folder), "--run", "--log", str(log_file)])
        finally:
            builtins.input = orig
        self.assertIn("Cancelled", out.getvalue())
        self.assertTrue((folder / "a.pdf").exists())

    def test_cli_run_with_yes_moves_and_logs(self):
        folder = self.sample_folder()
        log_file = self.tmp / "t.log"
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = org.main([str(folder), "--run", "--yes", "--log", str(log_file)])
        self.assertEqual(code, 0)
        self.assertIn("MOVED", out.getvalue())
        self.assertTrue((folder / "Documents" / "a.pdf").exists())
        self.assertIn("MOVED a.pdf", log_file.read_text(encoding="utf-8"))

    def test_cli_bad_folder_returns_error(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = org.main([str(self.tmp / "missing")])
        self.assertEqual(code, 1)
        self.assertIn("is not a folder", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=1)
