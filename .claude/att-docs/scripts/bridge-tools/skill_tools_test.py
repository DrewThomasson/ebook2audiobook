#!/usr/bin/env python3
"""Cases for skill_tools.py, which compares the tool and argument names the skills use with
the bridge's tool list. Each case writes a small tool list and the scanned Markdown files
into a scratch folder and runs the script on them; the real skills are not read.

usage: python3 scripts/bridge-tools/skill_tools_test.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "skill_tools.py")
README = "README.md"
VOICE = "plugins/voice/skills/voice-request/SKILL.md"
HOOKS = "plugins/voice/skills/voice-bridge-hooks/SKILL.md"

TOOLS = {
    "send": ["anyway", "session", "text"],
    "read_issue": ["number", "repo"],
    "rename_session": ["name", "session"],
    "summary": [],
}


class Scratch:
    """A scratch root holding a tool list and Markdown files, and a way to run the check."""

    def __init__(self, tools=None):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        self.snapshot = os.path.join(self.root, "tools.json")
        self.write_snapshot({"source": "abc", "tools": TOOLS if tools is None else tools})
        for rel in (README, VOICE, HOOKS):
            self.write(rel, "")

    def write_snapshot(self, data):
        with open(self.snapshot, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def run(self):
        return subprocess.run(
            [sys.executable, "-I", SCRIPT, "--snapshot", self.snapshot, "--root", self.root],
            capture_output=True, text=True)


class SkillToolsTest(unittest.TestCase):
    def setUp(self):
        self.scratch = Scratch()
        self.addCleanup(self.scratch.dir.cleanup)

    def check(self, voice="", hooks="", readme="", files=None):
        self.scratch.write(VOICE, voice)
        self.scratch.write(HOOKS, hooks)
        self.scratch.write(README, readme)
        for rel, text in (files or {}).items():
            self.scratch.write(rel, text)
        return self.scratch.run()

    def test_known_tools_and_arguments_pass_without_noise(self):
        r = self.check(voice="Use `send(anyway, session, text)` and `read_issue(number, repo)`.")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(r.stdout.strip(), "0 errors, 0 warnings")

    def test_a_tool_named_in_prose_alone_passes(self):
        r = self.check(voice="Call `read_issue` and `rename_session` when the user asks.")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("0 warnings", r.stdout)

    def test_an_unknown_tool_fails_with_its_file_and_line(self):
        r = self.check(hooks="One line.\nThen `read_pull_request` is named.\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"ERROR  {HOOKS}:2: `read_pull_request` is not a bridge tool", r.stdout)

    def test_an_unknown_tool_in_call_form_fails(self):
        r = self.check(readme="`merge_pull_request(confirm)` merges.")
        self.assertEqual(r.returncode, 1)
        self.assertIn("merge_pull_request is not a bridge tool", r.stdout)

    def test_an_argument_the_tool_does_not_take_fails_and_lists_the_real_ones(self):
        r = self.check(voice="`read_issue(number, branch)`")
        self.assertEqual(r.returncode, 1)
        self.assertIn("read_issue takes no argument branch (it takes number, repo)", r.stdout)

    def test_every_bad_argument_in_one_call_is_reported(self):
        r = self.check(voice="`send(first, session, second)`")
        self.assertEqual(r.stdout.count("takes no argument"), 2, r.stdout)

    def test_an_argument_that_is_not_a_name_fails(self):
        r = self.check(voice="`send(session=1)`")
        self.assertEqual(r.returncode, 1)
        self.assertIn("is not an argument name", r.stdout)

    def test_names_that_are_not_tools_are_ignored(self):
        r = self.check(
            hooks="`session_title.py`, `hook_pid`, `ast_edit`, `read_ledger(path)`, "
                  "`register(core)`, `call(args, context)`, `now.json`, `en_US-amy-medium`.")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_bare_one_word_tool_name_is_not_checked(self):
        # `follow` is a plain word that is a tool in the real list and code elsewhere.
        r = self.check(voice="The `follow` option and `summary` are words.")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_fenced_block_is_not_scanned(self):
        r = self.check(voice="```sh\nrun `old_tool(x)` here\n```\nAfter the fence `read_issue(number)`.")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("old_tool", r.stdout)

    def test_a_span_after_a_fence_is_scanned_again(self):
        r = self.check(voice="```\ncode\n```\n`old_tool`")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"{VOICE}:4", r.stdout)

    def test_a_span_that_wraps_a_line_does_not_hide_the_ones_after_it(self):
        r = self.check(voice="Title `<base> - <task>\n(<state>)` then `old_tool(x)` and `send(bogus)`.")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"{VOICE}:2: `old_tool(x)`: old_tool is not a bridge tool", r.stdout)
        self.assertIn("send takes no argument bogus", r.stdout)

    def test_a_call_form_wrapped_over_two_lines_is_read_whole(self):
        r = self.check(voice="Use `send(anyway,\nsession, text)` here.")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("anyway,", r.stdout)

    def test_a_stray_backtick_does_not_pair_with_the_next_list_item(self):
        r = self.check(voice="- a lone ` tick\n- `old_tool` in the next item\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"{VOICE}:2:", r.stdout)

    def test_a_fence_closes_only_on_its_own_marker(self):
        text = "```\ncode\n~~~\n`inside_one`\n```\n`after_one`\n"
        r = self.check(voice=text)
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("inside_one", r.stdout)
        self.assertIn("`after_one` is not a bridge tool", r.stdout)

    def test_a_longer_fence_is_not_closed_by_a_shorter_one(self):
        r = self.check(voice="````\n```\n`inside_one`\n```\n````\n`after_one`\n")
        self.assertNotIn("inside_one", r.stdout)
        self.assertIn("`after_one` is not a bridge tool", r.stdout)

    def test_a_fence_marker_inside_a_line_of_text_does_not_open_a_fence(self):
        r = self.check(voice="```inline``` and `old_tool`\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("`old_tool` is not a bridge tool", r.stdout)

    def test_a_stray_backtick_in_a_heading_does_not_pair_with_the_next_line(self):
        r = self.check(voice="# Title with ` tick\nnext `old_tool` here\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"{VOICE}:2:", r.stdout)

    def test_a_stray_backtick_does_not_pair_across_a_blank_line(self):
        r = self.check(voice="a lone ` tick\n\nthen `old_tool` here\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"{VOICE}:3:", r.stdout)

    def test_an_indented_fence_inside_a_list_item_is_a_fence(self):
        r = self.check(voice="- item\n\n    ~~~\n    `inside_one` and `send(bogus)`\n    ~~~\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_call_wrapped_inside_a_block_quote_is_read_whole(self):
        r = self.check(voice="> Use `send(anyway,\n> session)` here.\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_span_closes_on_a_backtick_run_of_its_own_length(self):
        r = self.check(voice="``a`b`` and `old_tool`")
        self.assertEqual(r.returncode, 1)
        self.assertIn("`old_tool` is not a bridge tool", r.stdout)
        self.assertEqual(r.stdout.count("ERROR"), 1)

    def test_an_argument_no_call_form_names_warns_and_leaves_the_exit_status(self):
        r = self.check(voice="`read_issue(repo)`", hooks="`send(anyway)`")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("WARN   read_issue: the bridge takes number,", r.stdout)
        self.assertIn("WARN   send: the bridge takes session, text,", r.stdout)
        self.assertNotIn("rename_session", r.stdout)
        self.assertIn("0 errors, 2 warnings", r.stdout)

    def test_arguments_named_in_different_files_cover_the_tool_together(self):
        r = self.check(voice="`read_issue(repo)`", hooks="`read_issue(number)`")
        self.assertEqual(r.stdout.strip(), "0 errors, 0 warnings")

    def test_an_empty_call_form_covers_a_tool_with_no_arguments(self):
        r = self.check(voice="`summary()`")
        self.assertEqual(r.stdout.strip(), "0 errors, 0 warnings")

    def test_an_error_and_a_warning_together_exit_one(self):
        r = self.check(voice="`read_issue(repo)` and `old_tool`")
        self.assertEqual(r.returncode, 1)
        self.assertIn("1 errors, 1 warnings", r.stdout)

    def test_another_markdown_file_naming_a_tool_fails_until_it_is_scanned(self):
        r = self.check(files={"docs/guide.md": "Ask for `rename_session` and `send(anyway)`.\n"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("docs/guide.md:1: `rename_session` names the bridge tool rename_session", r.stdout)
        self.assertIn("docs/guide.md:1: `send(anyway)` names the bridge tool send", r.stdout)

    def test_another_markdown_file_with_a_plain_word_or_other_snake_case_name_passes(self):
        r = self.check(files={"docs/guide.md": "Use `send` the word, `foo_bar` and `summary`.\n"})
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_the_changelog_and_other_worktrees_are_not_read(self):
        r = self.check(files={
            "CHANGELOG.md": "`rename_session` was added.\n",
            ".claude/worktrees/x/docs/a.md": "`rename_session`\n",
            "node_modules/pkg/README.md": "`rename_session`\n",
        })
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_scanned_file_that_is_missing_fails(self):
        self.check()
        os.remove(os.path.join(self.scratch.root, HOOKS))
        r = self.scratch.run()
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"ERROR  {HOOKS}: is listed in SCANNED but does not exist", r.stdout)

    def test_a_missing_tool_list_fails_with_the_fix(self):
        os.remove(self.scratch.snapshot)
        r = self.scratch.run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("run refresh.sh", r.stderr + r.stdout)

    def test_a_malformed_tool_list_fails(self):
        for bad in ({}, {"tools": {}}, {"tools": {"send": "text"}}, {"tools": {"send": [1]}}, []):
            self.scratch.write_snapshot(bad)
            r = self.scratch.run()
            self.assertEqual(r.returncode, 1, bad)
            self.assertIn("expected a non-empty", r.stderr + r.stdout, bad)


if __name__ == "__main__":
    unittest.main()
