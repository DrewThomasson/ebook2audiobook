#!/usr/bin/env python3
"""Checks plugin_version_check.py: which plugins it calls behind, which version it measures
them against, and that it stays quiet when it cannot know.

usage: python3 plugin_version_check_test.py

Each case runs the hook as a process against a scratch plugins folder, with a stub `git` that
answers the tag lookup from a file, so nothing touches the network or the real installs.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "plugin_version_check.py")
PROJECT = "/work/demo"
OTHER = "/work/other"


class Scratch:
    """A ~/.claude with a plugins folder, a marketplace clone, and a stub git."""

    def __init__(self, root):
        self.config = os.path.join(root, "claude")
        self.plugins = os.path.join(self.config, "plugins")
        self.clone = os.path.join(self.plugins, "marketplaces", "att-docs")
        self.data = os.path.join(root, "data")
        self.bin = os.path.join(root, "bin")
        self.tags = os.path.join(root, "tags")
        self.git_calls = os.path.join(root, "git-calls")
        self.common = os.path.join(root, "common")
        os.makedirs(self.plugins)
        os.makedirs(self.bin)
        os.makedirs(self.data)
        with open(os.path.join(self.bin, "git"), "w") as f:
            f.write('#!/bin/sh\n'
                    'if [ "$3" = rev-parse ]; then [ -f "%s" ] || exit 128; cat "%s"; exit; fi\n'
                    'echo x >> "%s"\n[ -f "%s" ] || exit 128\ncat "%s"\n'
                    % (self.common, self.common, self.git_calls, self.tags, self.tags))
        os.chmod(os.path.join(self.bin, "git"), 0o755)

    def installed(self, **versions):
        """installed(general="0.3.0") installs each at user scope."""
        plugins = {"%s@att-docs" % n: [{"scope": "user", "version": v}]
                   for n, v in versions.items()}
        self.write(os.path.join(self.plugins, "installed_plugins.json"),
                   {"version": 2, "plugins": plugins})

    def scoped(self, name, entries):
        self.write(os.path.join(self.plugins, "installed_plugins.json"),
                   {"version": 2, "plugins": {"%s@att-docs" % name: entries}})

    def marketplace(self, source=None, **versions):
        self.write(os.path.join(self.plugins, "known_marketplaces.json"), {"att-docs": {
            "source": source or {"source": "github", "repo": "merph518/Overmind"},
            "installLocation": self.clone}})
        for name, version in versions.items():
            self.write(os.path.join(self.clone, "plugins", name, ".claude-plugin", "plugin.json"),
                       {"name": name, "version": version})

    def remote_tags(self, *tags):
        with open(self.tags, "w") as f:
            f.write("".join("%040d\trefs/tags/%s\n" % (i, t) for i, t in enumerate(tags)))

    def lookups(self):
        try:
            with open(self.git_calls) as f:
                return len(f.read().split())
        except OSError:
            return 0

    @staticmethod
    def write(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

    def run(self, project=PROJECT):
        env = dict(os.environ, CLAUDE_CONFIG_DIR=self.config, CLAUDE_PROJECT_DIR=project,
                   CLAUDE_PLUGIN_DATA=self.data, PATH=self.bin + os.pathsep + os.environ["PATH"])
        r = subprocess.run([sys.executable, HOOK], input="{}", capture_output=True, text=True,
                           env=env, timeout=30)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout) if r.stdout.strip() else None


class Check(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.s = Scratch(self.tmp.name)

    def text(self, project=PROJECT):
        out = self.s.run(project)
        self.assertIsNotNone(out, "a warning was expected")
        ctx = out["hookSpecificOutput"]
        self.assertEqual(ctx["hookEventName"], "SessionStart")
        self.assertEqual(out["systemMessage"], ctx["additionalContext"])
        return out["systemMessage"]

    def test_a_plugin_behind_the_marketplace_clone_is_reported_by_name(self):
        self.s.installed(general="0.3.0", voice="0.21.0", **{"att-docs": "0.21.0"})
        self.s.marketplace(general="0.21.0", voice="0.21.0", **{"att-docs": "0.21.0"})
        t = self.text()
        self.assertIn("general 0.3.0 (now 0.21.0)", t)
        self.assertNotIn("voice", t)
        self.assertNotIn("att-docs 0.21.0", t)

    def test_current_plugins_print_nothing(self):
        self.s.installed(general="0.21.0", voice="0.21.0")
        self.s.marketplace(general="0.21.0", voice="0.21.0")
        self.s.remote_tags("v0.20.0", "v0.21.0")
        self.assertIsNone(self.s.run())

    def test_the_newest_release_tag_counts_when_the_clone_is_older(self):
        self.s.installed(general="0.21.0", voice="0.21.0")
        self.s.marketplace(general="0.21.0", voice="0.21.0")
        self.s.remote_tags("v0.21.0", "v0.31.2", "v0.9.0")
        t = self.text()
        self.assertIn("general 0.21.0 (now 0.31.2)", t)
        self.assertIn("voice 0.21.0 (now 0.31.2)", t)

    def test_tags_compare_as_numbers_not_text(self):
        self.s.installed(general="0.9.0")
        self.s.marketplace(general="0.9.0")
        self.s.remote_tags("v0.9.0", "v0.10.0")
        self.assertIn("general 0.9.0 (now 0.10.0)", self.text())

    def test_a_lookup_that_fails_is_silent_and_not_retried_this_session_period(self):
        self.s.installed(general="0.21.0")
        self.s.marketplace(general="0.21.0")
        self.assertIsNone(self.s.run())
        self.assertIsNone(self.s.run())
        self.assertEqual(self.s.lookups(), 1)

    def test_a_fresh_cache_answers_without_asking_git(self):
        self.s.installed(general="0.21.0")
        self.s.marketplace(general="0.21.0")
        self.s.remote_tags("v0.31.2")
        self.text()
        self.text()
        self.assertEqual(self.s.lookups(), 1)

    def test_a_stale_cache_is_looked_up_again(self):
        self.s.installed(general="0.21.0")
        self.s.marketplace(general="0.21.0")
        self.s.remote_tags("v0.31.2")
        self.text()
        cache = os.path.join(self.s.data, "att-docs-latest-tag.json")
        self.s.write(cache, {"checked": 0, "tag": "v0.31.2"})
        self.s.remote_tags("v0.40.0")
        self.assertIn("(now 0.40.0)", self.text())

    def test_a_failed_lookup_keeps_the_tag_cached_before_it(self):
        self.s.installed(general="0.21.0")
        self.s.marketplace(general="0.21.0")
        cache = os.path.join(self.s.data, "att-docs-latest-tag.json")
        self.s.write(cache, {"checked": 0, "tag": "v0.31.2"})
        self.assertIn("(now 0.31.2)", self.text())

    def test_the_entry_for_this_project_wins_over_the_user_scope_one(self):
        self.s.scoped("general", [
            {"scope": "user", "version": "0.3.0"},
            {"scope": "local", "version": "0.21.0", "projectPath": PROJECT},
            {"scope": "local", "version": "0.1.0", "projectPath": OTHER}])
        self.s.marketplace(general="0.21.0")
        self.assertIsNone(self.s.run(PROJECT))
        self.assertIn("general 0.1.0", self.text(OTHER))
        self.assertIn("general 0.3.0", self.text("/work/third"))

    def test_a_pinned_marketplace_is_told_to_be_added_again_at_the_new_tag(self):
        self.s.installed(general="0.3.0")
        self.s.marketplace(source={"source": "github", "repo": "merph518/Overmind", "ref": "v0.3.0"},
                           general="0.3.0")
        self.s.remote_tags("v0.31.2")
        t = self.text()
        self.assertIn("claude plugin marketplace add merph518/Overmind#v0.31.2", t)
        self.assertIn("claude plugin install general@att-docs --scope user", t)
        self.assertNotIn("marketplace update", t)

    def test_an_unpinned_marketplace_is_told_to_update(self):
        self.s.installed(general="0.3.0")
        self.s.marketplace(general="0.3.0")
        self.s.remote_tags("v0.31.2")
        t = self.text()
        self.assertIn("claude plugin marketplace update att-docs", t)
        self.assertIn("claude plugin update general@att-docs --scope user", t)

    def test_the_commands_name_the_scope_the_project_runs_the_plugin_from(self):
        self.s.scoped("general", [{"scope": "user", "version": "0.21.0"},
                                  {"scope": "local", "version": "0.3.0", "projectPath": PROJECT}])
        self.s.marketplace(general="0.21.0")
        self.assertIn("claude plugin update general@att-docs --scope local", self.text())

    def test_a_worktree_with_no_entry_of_its_own_falls_back_to_the_main_checkouts(self):
        self.s.scoped("general", [
            {"scope": "user", "version": "0.3.0"},
            {"scope": "local", "version": "0.21.0", "projectPath": "/work/main"}])
        self.s.marketplace(general="0.21.0")
        with open(self.s.common, "w") as f:
            f.write("/work/main/.git\n")
        self.assertIsNone(self.s.run("/work/main/wt"))

    def test_a_worktree_with_an_entry_of_its_own_is_measured_by_it(self):
        self.s.scoped("general", [
            {"scope": "local", "version": "0.21.0", "projectPath": "/work/main"},
            {"scope": "local", "version": "0.1.0", "projectPath": "/work/main/wt"}])
        self.s.marketplace(general="0.21.0")
        with open(self.s.common, "w") as f:
            f.write("/work/main/.git\n")
        self.assertIn("general 0.1.0", self.text("/work/main/wt"))

    def test_a_plugin_the_project_turns_off_is_left_out(self):
        self.s.installed(general="0.3.0", voice="0.3.0")
        self.s.marketplace(general="0.21.0", voice="0.21.0")
        project = os.path.join(self.tmp.name, "proj")
        self.s.write(os.path.join(project, ".claude", "settings.json"),
                     {"enabledPlugins": {"general@att-docs": False}})
        t = self.s.run(project)["systemMessage"]
        self.assertIn("voice 0.3.0", t)
        self.assertNotIn("general 0.3.0", t)

    def test_a_local_setting_turning_a_plugin_back_on_beats_a_shared_one_turning_it_off(self):
        self.s.installed(general="0.3.0")
        self.s.marketplace(general="0.21.0")
        project = os.path.join(self.tmp.name, "proj")
        self.s.write(os.path.join(project, ".claude", "settings.json"),
                     {"enabledPlugins": {"general@att-docs": False}})
        self.s.write(os.path.join(project, ".claude", "settings.local.json"),
                     {"enabledPlugins": {"general@att-docs": True}})
        self.assertIn("general 0.3.0", self.s.run(project)["systemMessage"])

    def test_a_plugin_the_clone_no_longer_holds_is_not_reported(self):
        self.s.installed(general="0.3.0", gone="0.1.0")
        self.s.marketplace(general="0.21.0")
        self.s.remote_tags("v0.31.2")
        t = self.text()
        self.assertIn("general 0.3.0", t)
        self.assertNotIn("gone", t)

    def test_a_cache_dated_in_the_future_is_looked_up_again(self):
        self.s.installed(general="0.21.0")
        self.s.marketplace(general="0.21.0")
        self.s.write(os.path.join(self.s.data, "att-docs-latest-tag.json"),
                     {"checked": 9999999999, "tag": "v0.21.0"})
        self.s.remote_tags("v0.31.2")
        self.assertIn("(now 0.31.2)", self.text())

    def test_no_installed_plugins_and_unreadable_files_print_nothing(self):
        self.assertIsNone(self.s.run())
        with open(os.path.join(self.s.plugins, "installed_plugins.json"), "w") as f:
            f.write("not json")
        with open(os.path.join(self.s.plugins, "known_marketplaces.json"), "w") as f:
            f.write("[]")
        self.assertIsNone(self.s.run())

    def test_other_marketplaces_and_odd_versions_are_ignored(self):
        self.s.write(os.path.join(self.s.plugins, "installed_plugins.json"), {"plugins": {
            "x@elsewhere": [{"scope": "user", "version": "0.0.1"}],
            "general@att-docs": [{"scope": "user", "version": "main"}]}})
        self.s.marketplace(general="9.9.9")
        self.assertIsNone(self.s.run())


if __name__ == "__main__":
    unittest.main()
