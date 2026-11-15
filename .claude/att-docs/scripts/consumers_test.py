#!/usr/bin/env python3
"""Checks .github/consumers.json, the list of repositories that pin Overmind.

The names are repositories owned by merph518, written without the owner, in plain
(case-sensitive) sort order.

usage: python3 scripts/consumers_test.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, ".github", "consumers.json")


class Consumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(PATH, encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_the_only_key_is_consumers(self):
        self.assertIsInstance(self.data, dict)
        self.assertEqual(list(self.data), ["consumers"])

    def test_consumers_is_a_non_empty_list_of_strings(self):
        names = self.data["consumers"]
        self.assertIsInstance(names, list)
        self.assertTrue(names)
        for name in names:
            self.assertIsInstance(name, str)
            self.assertTrue(name.strip(), "a name is empty")

    def test_names_are_unique(self):
        names = self.data["consumers"]
        self.assertEqual(len(names), len(set(names)))

    def test_names_are_sorted(self):
        names = self.data["consumers"]
        self.assertEqual(names, sorted(names))

    def test_names_are_repository_names_without_an_owner(self):
        for name in self.data["consumers"]:
            self.assertTrue(re.fullmatch(r"[A-Za-z0-9._-]+", name),
                            f"{name} is not a bare repository name")


if __name__ == "__main__":
    unittest.main()
