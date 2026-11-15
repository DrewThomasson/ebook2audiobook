#!/usr/bin/env python3
"""Checks stray_files_gate.py: which git calls it refuses and which it lets through.

usage: python3 stray_files_gate_test.py

The decisions run against scratch git repositories, with the global and system git
configuration switched off. The end-to-end cases run the hook as a process.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, 'stray_files_gate.py')
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import stray_files_gate as gate  # noqa: E402

ENV = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null',
           GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t',
           GIT_COMMITTER_EMAIL='t@t')


def payload(command, cwd, tool='Bash'):
    return {'tool_name': tool, 'tool_input': {'command': command}, 'cwd': cwd}


class Gate(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = os.path.join(tmp.name, 'repo')
        os.makedirs(self.repo)
        self.git('init', '-q', '-b', 'main')
        self.write('src/a.py', 'print(1)\n')
        self.git('add', 'src/a.py')
        self.git('commit', '-q', '-m', 'init')

    def git(self, *args, cwd=None):
        return subprocess.run(['git', *args], cwd=cwd or self.repo, env=ENV, check=True,
                              capture_output=True, text=True).stdout

    def write(self, rel, text='x\n'):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(text)

    def decide(self, command, config=None, cwd=None):
        return gate.decide(payload(command, cwd or self.repo), config or {})

    def reason(self, command, config=None, cwd=None):
        out = self.decide(command, config, cwd)
        self.assertIsNotNone(out, f'{command!r} should be refused')
        body = out['hookSpecificOutput']
        self.assertEqual(body['permissionDecision'], 'deny')
        return body['permissionDecisionReason']

    def allowed(self, command, config=None, cwd=None):
        self.assertIsNone(self.decide(command, config, cwd), f'{command!r} should pass')

    # -- staging the whole tree

    def test_bulk_adds_are_refused(self):
        for command in ('git add -A', 'git add --all', 'git add .', 'git add -Av',
                        'git add -- .', 'git add ./', 'cd x && git add .',
                        'GIT_TRACE=0 git add -A', 'git -C . add -A'):
            self.assertIn('by name', self.reason(command), command)

    def test_named_adds_and_tracked_only_adds_pass(self):
        for command in ('git add src/a.py', 'git add src', 'git add -u', 'git add -p src/a.py',
                        'git status', 'ls .', 'echo git add -A'):
            self.allowed(command)

    def test_bulk_add_can_be_allowed_but_junk_checks_stay(self):
        self.allowed('git add .', {'allowBulkAdd': True})
        self.assertIn('__pycache__', self.reason('git add pkg/__pycache__/x.pyc',
                                                 {'allowBulkAdd': True}))

    # -- naming a junk path

    def test_named_junk_is_refused_even_forced(self):
        for command, pattern in (('git add pkg/__pycache__/x.cpython-312.pyc', '__pycache__/'),
                                 ('git add -f mod.pyc', '*.pyc'),
                                 ('git add node_modules', 'node_modules/'),
                                 ('git add web/node_modules/left-pad/index.js', 'node_modules/'),
                                 ('git add coverage/lcov.info', 'coverage/'),
                                 ('git add test-results/out.xml', 'test-results/'),
                                 ('git add docs/.DS_Store', '.DS_Store'),
                                 ('git add notes.txt.swp', '*.swp'),
                                 ('git add old.py~', '*~'),
                                 ('git add build.log', '*.log'),
                                 ('git add scratch.tmp', '*.tmp')):
            self.assertIn(pattern, self.reason(command), command)

    def test_a_junk_add_is_refused_in_a_chain(self):
        self.assertIn('*.pyc', self.reason('git add src/a.py mod.pyc && git commit -m x'))

    def test_ordinary_names_are_not_junk(self):
        for path in ('src/a.py', 'coverage.md', 'docs/logging.md', 'src/cache.py',
                     'my_node_modules_notes.md', 'catalog.py'):
            self.allowed(f'git add {path}')

    def test_allow_lets_a_fixture_through(self):
        config = {'allow': ['tests/fixtures/*.log']}
        self.allowed('git add tests/fixtures/run.log', config)
        self.assertIn('*.log', self.reason('git add logs/run.log', config))

    def test_patterns_add_folders_paths_and_file_names(self):
        config = {'patterns': ['build-output/', 'gen/*.out', '*.bak']}
        self.assertIn('build-output/', self.reason('git add a/build-output/x', config))
        self.assertIn('gen/*.out', self.reason('git add gen/x.out', config))
        self.assertIn('*.bak', self.reason('git add x.bak', config))
        self.allowed('git add other/x.out', config)

    # -- committing with junk in the index

    def test_commit_with_a_staged_pyc_is_refused_and_names_the_fix(self):
        self.write('pkg/__pycache__/m.cpython-312.pyc')
        self.write('src/b.py')
        self.git('add', '-f', 'pkg/__pycache__/m.cpython-312.pyc', 'src/b.py')
        reason = self.reason('git commit -m "add b"')
        self.assertIn('pkg/__pycache__/m.cpython-312.pyc', reason)
        self.assertNotIn('src/b.py', reason)
        self.assertIn('git restore --staged', reason)
        self.assertIn('.gitignore', reason)

    def test_commit_after_unstaging_passes(self):
        self.write('pkg/__pycache__/m.pyc')
        self.write('src/b.py')
        self.git('add', '-f', 'pkg/__pycache__/m.pyc', 'src/b.py')
        self.reason('git commit -m x')
        self.git('restore', '--staged', 'pkg/__pycache__/m.pyc')
        self.allowed('git commit -m x')

    def test_every_commit_form_is_checked(self):
        self.write('x.pyc')
        self.git('add', '-f', 'x.pyc')
        for command in ('git commit -m x', 'git commit --amend --no-edit', 'git commit -am x',
                        'git add src && git commit -m x', 'git -C . commit -m x'):
            self.assertIn('x.pyc', self.reason(command), command)

    def test_deleting_tracked_junk_is_not_refused(self):
        self.write('old.pyc')
        self.git('add', '-f', 'old.pyc')
        self.git('commit', '-q', '-m', 'oops')
        self.git('rm', '-q', '--cached', 'old.pyc')
        self.allowed('git commit -m "remove the cache file"')

    def test_a_renamed_in_junk_is_refused(self):
        self.write('src/c.py', 'print(2)\n')
        self.git('add', 'src/c.py')
        self.git('commit', '-q', '-m', 'c')
        self.git('mv', 'src/c.py', 'c.pyc')
        self.assertIn('c.pyc', self.reason('git commit -m x'))

    def test_a_folder_add_in_the_same_command_as_the_commit_is_checked(self):
        self.write('src/__pycache__/a.cpython-312.pyc')
        self.write('src/b.py')
        reason = self.reason('git add src && git commit -m "add b"')
        self.assertIn('src/__pycache__/a.cpython-312.pyc', reason)
        self.allowed('git add src/b.py && git commit -m "add b"')

    def test_a_folder_add_skips_ignored_junk_unless_forced(self):
        self.write('.gitignore', '__pycache__/\n')
        self.write('src/__pycache__/a.pyc')
        self.write('src/b.py')
        self.allowed('git add src')
        self.assertIn('a.pyc', self.reason('git add -f src'))

    def test_a_bulk_add_that_is_allowed_still_checks_what_it_would_stage(self):
        self.write('pkg/__pycache__/m.pyc')
        self.assertIn('m.pyc', self.reason('git add .', {'allowBulkAdd': True}))

    def test_junk_the_repository_already_tracks_is_left_alone(self):
        self.write('fixtures/run.log', 'one\n')
        self.git('add', '-f', 'fixtures/run.log')
        self.git('commit', '-q', '-m', 'fixture')
        self.write('fixtures/run.log', 'two\n')
        self.allowed('git add fixtures/run.log')
        self.git('add', 'fixtures/run.log')
        self.allowed('git commit -m "update the fixture"')

    def test_a_cd_earlier_in_the_command_moves_the_repository(self):
        self.write('x.pyc')
        self.git('add', '-f', 'x.pyc')
        elsewhere = os.path.dirname(self.repo)
        self.assertIn('x.pyc', self.reason(f'cd {self.repo} && git commit -m x', cwd=elsewhere))
        self.assertIn('x.pyc', self.reason(f'cd {os.path.basename(self.repo)} && git commit -m x',
                                           cwd=elsewhere))
        self.allowed(f'cd {elsewhere} && git status', cwd=self.repo)

    def test_paths_typed_in_a_subdirectory_are_checked_from_the_repository_top(self):
        self.write('sub/data/f.log', 'one\n')
        self.git('add', '-f', 'sub/data/f.log')
        self.git('commit', '-q', '-m', 'fixture')
        self.write('sub/data/f.log', 'two\n')
        sub = os.path.join(self.repo, 'sub')
        self.allowed('git add data', cwd=sub)
        self.allowed('git add data/f.log', cwd=sub)
        self.write('sub/data/new.log')
        self.assertIn('sub/data/new.log', self.reason('git add data', cwd=sub))
        self.assertIn('sub/data/new.log', self.reason('git add data/new.log', cwd=sub))

    def test_allow_globs_match_from_the_repository_top_in_a_subdirectory(self):
        self.write('sub/fixtures/run.log')
        sub = os.path.join(self.repo, 'sub')
        config = {'allow': ['sub/fixtures/*.log']}
        self.allowed('git add fixtures/run.log', config, cwd=sub)
        self.allowed('git add fixtures', config, cwd=sub)
        self.assertIn('run.log', self.reason('git add fixtures/run.log', cwd=sub))

    def test_a_tracked_file_named_by_a_top_pathspec_from_a_subdirectory_passes(self):
        self.write('keep.log', 'one\n')
        self.git('add', '-f', 'keep.log')
        self.git('commit', '-q', '-m', 'fixture')
        self.write('keep.log', 'two\n')
        self.write('sub/x.txt')
        sub = os.path.join(self.repo, 'sub')
        self.allowed('git add :/keep.log', cwd=sub)
        self.allowed("git add ':(top)keep.log'", cwd=sub)

    def test_updating_tracked_files_is_not_a_bulk_add(self):
        self.write('fresh.pyc')
        for command in ('git add -u .', 'git add --update .', 'git add -p .', 'git add -u'):
            self.allowed(command)
        self.assertIn('by name', self.reason('git add -A .'))

    def test_finishing_a_merge_that_brings_in_tracked_junk_is_not_refused(self):
        self.git('checkout', '-q', '-b', 'other')
        self.write('fix.log', 'from other\n')
        self.git('add', '-f', 'fix.log')
        self.git('commit', '-q', '-m', 'other adds a fixture')
        self.git('checkout', '-q', 'main')
        self.write('src/b.py')
        self.git('add', 'src/b.py')
        self.git('commit', '-q', '-m', 'main moves on')
        self.git('merge', '-q', '--no-commit', '--no-ff', 'other')
        self.allowed('git commit --no-edit')
        self.write('mine.log')
        self.git('add', '-f', 'mine.log')
        self.assertIn('mine.log', self.reason('git commit --no-edit'))

    def test_a_heredoc_with_an_apostrophe_does_not_hide_the_commit(self):
        self.write('x.pyc')
        self.git('add', '-f', 'x.pyc')
        command = "git commit -F - <<'EOF'\ndon't add junk\nEOF"
        self.assertIn('x.pyc', self.reason(command))
        self.git('restore', '--staged', 'x.pyc')
        self.allowed(command)

    def test_a_tool_input_that_is_not_an_object_passes(self):
        self.assertIsNone(gate.decide({'tool_name': 'Bash', 'tool_input': 'x'}, {}))

    def test_commit_reads_the_repository_named_by_dash_c(self):
        self.write('x.pyc')
        self.git('add', '-f', 'x.pyc')
        elsewhere = os.path.dirname(self.repo)
        self.assertIn('x.pyc', self.reason(f'git -C {self.repo} commit -m x', cwd=elsewhere))

    def test_a_clean_index_commits(self):
        self.write('src/b.py')
        self.git('add', 'src/b.py')
        self.allowed('git commit -m "add b"')

    def test_a_directory_that_is_not_a_repository_passes(self):
        with tempfile.TemporaryDirectory() as plain:
            self.allowed('git commit -m x', cwd=plain)

    # -- calls that are not for this hook

    def test_other_tools_and_commands_pass(self):
        self.write('x.pyc')
        self.git('add', '-f', 'x.pyc')
        self.assertIsNone(gate.decide(payload('git commit -m x', self.repo, tool='Edit'), {}))
        self.assertIsNone(gate.decide({'tool_name': 'Bash', 'tool_input': {}}, {}))
        self.assertIsNone(gate.decide({'tool_name': 'Bash', 'tool_input': {'command': 7}}, {}))
        for command in ('git status', 'git log --oneline', 'git push origin main',
                        'echo "git commit" > note.txt', 'make commit'):
            self.allowed(command)


class Process(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.config = os.path.join(self.tmp, 'extension.json')

    def run_hook(self, config, command='git add .', *extra):
        if config is not None:
            with open(self.config, 'w') as f:
                f.write(config)
        args = [sys.executable, '-B', HOOK, '--config', self.config, *extra]
        return subprocess.run(args, input=json.dumps(payload(command, self.tmp)),
                              capture_output=True, text=True, timeout=60)

    def test_a_refusal_is_one_json_object_on_stdout(self):
        done = self.run_hook('{"strayFiles": {}}')
        self.assertEqual(done.returncode, 0)
        out = json.loads(done.stdout)
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_a_call_that_passes_prints_nothing(self):
        done = self.run_hook('{"strayFiles": {}}', 'git add src/a.py')
        self.assertEqual((done.returncode, done.stdout), (0, ''))

    def test_unreadable_input_passes(self):
        with open(self.config, 'w') as f:
            f.write('{"strayFiles": {}}')
        done = subprocess.run([sys.executable, '-B', HOOK, '--config', self.config],
                              input='not json', capture_output=True, text=True, timeout=60)
        self.assertEqual((done.returncode, done.stdout), (0, ''))

    def test_no_file_no_section_or_true_means_every_default(self):
        absent = os.path.join(self.tmp, 'absent.json')
        for args in ([], ['--config', absent]):
            done = subprocess.run([sys.executable, '-B', HOOK, *args],
                                  input=json.dumps(payload('git add .', self.tmp)),
                                  capture_output=True, text=True, timeout=60)
            self.assertEqual(done.returncode, 0)
            self.assertEqual(json.loads(done.stdout)['hookSpecificOutput']['permissionDecision'],
                             'deny')
        for config in ('{}', '{"other": {}}', '{"strayFiles": true}'):
            self.assertEqual(json.loads(self.run_hook(config).stdout)
                             ['hookSpecificOutput']['permissionDecision'], 'deny', config)

    def test_a_false_section_turns_the_hook_off(self):
        done = self.run_hook('{"strayFiles": false}')
        self.assertEqual((done.returncode, done.stdout), (0, ''))

    def test_usage_and_config_errors_exit_64(self):
        stray_flag = subprocess.run([sys.executable, '-B', HOOK, '--nope'], input='{}',
                                    capture_output=True, text=True, timeout=60)
        self.assertEqual(stray_flag.returncode, 64)
        self.assertIn('usage', stray_flag.stderr)
        for config in ('[]', 'not json', '{"strayFiles": "yes"}',
                       '{"strayFiles": {"patterns": "x"}}',
                       '{"strayFiles": {"allow": [1]}}'):
            done = self.run_hook(config)
            self.assertEqual(done.returncode, 64, config)


if __name__ == '__main__':
    unittest.main()
