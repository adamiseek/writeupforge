#!/usr/bin/env python3
"""Tests for writeupforge — run with: python3 -m unittest test_writeupforge"""

import os
import sys
import tempfile
import unittest

import writeupforge as wf


class TestSlug(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(wf._slug("Beach Bar 2026!"), "beach-bar-2026")

    def test_empties(self):
        self.assertEqual(wf._slug("???"), "writeup")


class TestSkeleton(unittest.TestCase):
    def test_front_matter(self):
        body = wf.build_skeleton("test-box", "thm", "10.0.0.1", "easy")
        self.assertIn("title: test-box", body)
        self.assertIn("platform: TryHackMe", body)
        self.assertIn("difficulty: easy", body)
        self.assertIn("status: in-progress", body)

    def test_sections_present(self):
        body = wf.build_skeleton("x", "htb")
        for title, _ in wf.SECTIONS:
            self.assertIn(f"## {title.capitalize()}", body)
        self.assertIn("| User |   |   |", body)


class TestInteractive(unittest.TestCase):
    def test_interactive_build_end_to_end(self):
        answers = "\n".join([
            "box", "easy", "10.0.0.1",
            "RCE via YAML deserialization",
            "nmap: 22, 80", "found dj/dj in comment", "",
            "curl -F p.yml /import", "got shell as bartender", "",
            "sudo -l", "root flag", "",
            "check comments", "",
            "THM{flag}", "",
        ]) + "\n"
        old_in, old_out = sys.stdin, sys.stdout
        it = iter(answers.splitlines(True))
        sys.stdin = type("F", (), {"readline": lambda self: next(it)})()
        sys.stdout = open(os.devnull, "w")
        try:
            body = wf.build_interactive("box", "thm", "easy", "10.0.0.1")
        finally:
            sys.stdin, sys.stdout = old_in, old_out

        self.assertIn("## Exploitation", body)
        self.assertIn("got shell as bartender", body)
        self.assertIn("THM{flag}", body)
        self.assertIn("status: complete", body)

    def test_skeleton_is_valid_markdown_structure(self):
        body = wf.build_skeleton("box", "lab")
        self.assertTrue(body.startswith("---"))


class TestWriteupFile(unittest.TestCase):
    def test_resolve_outdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = wf._resolve_outdir("Cool Box Name", tmp)
            self.assertTrue(out.endswith("cool-box-name/writeup.md"))
            self.assertTrue(os.path.isdir(os.path.dirname(out)))


if __name__ == "__main__":
    unittest.main()
