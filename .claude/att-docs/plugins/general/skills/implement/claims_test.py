#!/usr/bin/env python3
"""Checks claims.py: who is refused a file, how claims are shared and dropped, and what
sync reports.

usage: python3 claims_test.py

Each case runs the script as a process in a scratch repository with a linked worktree and a
local bare origin. A stub `gh` on PATH answers the open pull request reads from a JSON file.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, 'claims.py')
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import claims  # noqa: E402

GIT_ENV = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null',
               GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t',
               GIT_COMMITTER_EMAIL='t@t')

# Prints GH_PRS for `pr list`, GH_FILES for `api`, and fails when GH_FAIL is set.
GH_STUB = r"""#!/bin/sh
[ -z "$GH_FAIL" ] || { echo "gh: boom" >&2; exit 1; }
case "$1" in
  pr) cat "$GH_PRS" ;;
  api) cat "$GH_FILES" ;;
esac
"""


def dead_pid():
    """A process id that was just running and has exited."""
    done = subprocess.Popen(['true'])
    done.wait()
    return str(done.pid)


class Claims(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = os.path.realpath(tmp.name)
        self.origin = os.path.join(root, 'origin.git')
        self.repo = os.path.join(root, 'repo')
        self.tree = os.path.join(root, 'tree')
        self.git(root, 'init', '-q', '--bare', '-b', 'main', self.origin)
        self.git(root, 'clone', '-q', self.origin, self.repo)
        self.write(self.repo, 'docs/a.md')
        self.write(self.repo, 'docs/b.md')
        self.write(self.repo, 'src/c.py')
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-q', '-m', 'init')
        self.git(self.repo, 'push', '-q', 'origin', 'main')
        self.git(self.repo, 'worktree', 'add', '-q', '-b', 'feat/mine', self.tree, 'origin/main')

        bin_dir = os.path.join(root, 'bin')
        os.makedirs(bin_dir)
        gh = os.path.join(bin_dir, 'gh')
        with open(gh, 'w') as f:
            f.write(GH_STUB)
        os.chmod(gh, 0o755)
        self.prs = os.path.join(root, 'prs.json')
        self.files = os.path.join(root, 'files.txt')
        self.set_prs([])
        self.env = dict(GIT_ENV, PATH=bin_dir + os.pathsep + os.environ['PATH'],
                        GH_PRS=self.prs, GH_FILES=self.files)
        for name in ('CLAUDE_CODE_SESSION_ID', 'CLAUDE_PID', 'PI_SESSION_ID'):
            self.env.pop(name, None)

    def git(self, cwd, *args):
        return subprocess.run(['git', *args], cwd=cwd, env=GIT_ENV, check=True,
                              capture_output=True, text=True).stdout

    def write(self, base, rel, text='x\n'):
        path = os.path.join(base, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(text)

    def set_prs(self, prs):
        with open(self.prs, 'w') as f:
            json.dump([{'number': n, 'headRefName': b, 'files': [{'path': p} for p in paths]}
                       for n, b, paths in prs], f)

    def cli(self, *args, cwd=None, session='s1', pid=None, env=None):
        flags = []
        if session:
            flags += ['--session', session]
        if pid:
            flags += ['--pid', pid]
        done = subprocess.run([sys.executable, SCRIPT, *flags, *args], cwd=cwd or self.tree,
                              env=env or self.env, capture_output=True, text=True)
        return done.returncode, done.stdout.strip(), done.stderr.strip()

    def claim_dir(self):
        return os.path.join(self.repo, '.git', 'file-claims')

    def test_claim_is_refused_for_another_live_session_and_names_the_holder(self):
        self.assertEqual(self.cli('claim', 'docs/a.md', session='s1', pid=str(os.getpid()))[0], 0)
        code, out, _ = self.cli('claim', 'docs/a.md', session='s2')
        self.assertEqual(code, 3)
        self.assertEqual(out, 'CLAIM s1 feat/mine docs/a.md')

    def test_the_same_session_can_claim_again(self):
        self.cli('claim', 'docs/a.md', session='s1')
        self.assertEqual(self.cli('claim', 'docs/a.md', session='s1')[0], 0)

    def test_claims_are_shared_between_the_main_checkout_and_a_worktree(self):
        self.cli('claim', 'docs/a.md', session='s1', cwd=self.repo)
        code, out, _ = self.cli('check', 'docs/a.md', session='s2', cwd=self.tree)
        self.assertEqual(code, 3)
        self.assertIn('CLAIM s1', out)
        self.assertEqual(self.git(self.tree, 'status', '--short'), '')

    def plant(self, path, session, pid, ts=0, issue=None):
        """Write a claim record directly, as an earlier run of the script would have left it."""
        os.makedirs(self.claim_dir(), exist_ok=True)
        with open(claims.record_path(self.claim_dir(), path), 'w') as f:
            json.dump({'path': path, 'session': session, 'pid': pid, 'branch': 'feat/mine',
                       'issue': issue, 'ts': ts}, f)

    def test_paths_resolve_from_the_current_folder(self):
        self.cli('claim', 'a.md', session='s1', cwd=os.path.join(self.tree, 'docs'))
        code, out, _ = self.cli('check', 'docs/a.md', session='s2')
        self.assertEqual((code, out), (3, 'CLAIM s1 feat/mine docs/a.md'))

    def test_a_claim_whose_process_has_exited_does_not_block_and_is_replaced(self):
        self.plant('docs/a.md', 's1', dead_pid())
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 0)
        self.assertEqual(self.cli('claim', 'docs/a.md', session='s2')[0], 0)
        self.assertEqual(self.cli('check', 'docs/a.md', session='s1')[0], 3)

    def test_a_claim_with_no_pid_holds(self):
        self.cli('claim', 'docs/a.md', session='s1')
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 3)

    def test_prune_drops_only_stale_claims(self):
        self.cli('claim', 'docs/b.md', session='s1', pid=str(os.getpid()))
        self.plant('docs/a.md', 's1', dead_pid())
        code, out, _ = self.cli('prune')
        self.assertEqual((code, out), (0, 'pruned docs/a.md'))
        self.assertEqual(self.cli('check', 'docs/b.md', session='s2')[0], 3)

    def test_check_writes_nothing(self):
        self.cli('check', 'docs/a.md')
        self.assertFalse(os.path.exists(self.claim_dir()) and os.listdir(self.claim_dir()))

    def test_a_refused_path_leaves_none_of_the_batch_recorded(self):
        self.cli('claim', 'docs/b.md', session='s2')
        code, _, _ = self.cli('claim', 'docs/a.md', 'docs/b.md', session='s1')
        self.assertEqual(code, 3)
        self.assertEqual(self.cli('claim', 'docs/a.md', session='s2')[0], 0)

    def test_a_refused_batch_keeps_a_claim_the_session_already_held(self):
        self.cli('claim', 'docs/a.md', session='s1')
        self.cli('claim', 'docs/b.md', session='s2')
        self.cli('claim', 'docs/a.md', 'docs/b.md', session='s1')
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 3)

    def test_release_drops_this_sessions_claims_only(self):
        self.cli('claim', 'docs/a.md', session='s1')
        self.cli('claim', 'docs/b.md', session='s2')
        self.assertEqual(self.cli('release', session='s1')[0], 0)
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 0)
        self.assertEqual(self.cli('check', 'docs/b.md', session='s1')[0], 3)

    def test_release_of_a_path_leaves_the_sessions_other_claims(self):
        self.cli('claim', 'docs/a.md', 'docs/b.md', session='s1')
        self.cli('release', 'docs/a.md', session='s1')
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 0)
        self.assertEqual(self.cli('check', 'docs/b.md', session='s2')[0], 3)

    def test_release_of_a_path_another_session_holds_needs_force(self):
        self.cli('claim', 'docs/a.md', session='s1')
        self.cli('release', 'docs/a.md', session='s2')
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 3)
        self.cli('release', '--force', 'docs/a.md', session='s2')
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 0)

    def test_claim_and_release_need_a_session(self):
        for args in (('claim', 'docs/a.md'), ('release',)):
            code, _, err = self.cli(*args, session=None)
            self.assertEqual(code, 2)
            self.assertIn('session', err)

    def run_raw(self, *argv, env=None):
        done = subprocess.run([sys.executable, SCRIPT, *argv], cwd=self.tree,
                              env=env or self.env, capture_output=True, text=True)
        return done.returncode, done.stdout.strip()

    def test_session_and_pid_flags_work_after_the_command(self):
        code, _ = self.run_raw('claim', 'docs/a.md', '--issue', '7', '--session', 's1',
                               '--pid', str(os.getpid()))
        self.assertEqual(code, 0)
        self.assertEqual(self.run_raw('check', 'docs/a.md', '--session', 's1')[0], 0)
        self.assertEqual(self.run_raw('--session', 's2', 'check', 'docs/a.md'),
                         (3, 'CLAIM s1 feat/mine docs/a.md issue=7'))
        self.assertEqual(self.run_raw('release', '--session', 's1')[0], 0)
        self.assertEqual(self.run_raw('check', 'docs/a.md', '--session', 's2')[0], 0)

    def test_the_session_comes_from_the_environment_when_no_flag_names_it(self):
        pi = dict(self.env, PI_SESSION_ID='pi-session')
        self.assertEqual(self.run_raw('claim', 'docs/a.md', env=pi)[0], 0)
        self.assertEqual(self.run_raw('check', 'docs/a.md', '--session', 'other'),
                         (3, 'CLAIM pi-session feat/mine docs/a.md'))
        both = dict(pi, CLAUDE_CODE_SESSION_ID='claude-session')
        self.assertEqual(self.run_raw('claim', 'docs/b.md', env=both)[0], 0)
        self.assertEqual(self.run_raw('check', 'docs/b.md', '--session', 'other'),
                         (3, 'CLAIM claude-session feat/mine docs/b.md'))

    def test_a_folder_cannot_be_claimed(self):
        code, _, err = self.cli('claim', 'docs')
        self.assertEqual(code, 2)
        self.assertIn('folder', err)

    def test_a_path_outside_the_repository_is_refused(self):
        self.assertEqual(self.cli('check', '../elsewhere.md')[0], 2)

    def test_check_of_a_folder_finds_a_claim_on_a_file_in_it(self):
        self.cli('claim', 'docs/a.md', session='s1')
        self.assertEqual(self.cli('check', 'docs', session='s2')[0], 3)
        self.assertEqual(self.cli('check', 'src', session='s2')[0], 0)

    def test_another_pull_request_that_changes_the_file_is_reported(self):
        self.set_prs([(7, 'feat/other', ['docs/a.md', 'x.md'])])
        code, out, _ = self.cli('check', 'docs/a.md')
        self.assertEqual((code, out), (3, 'PR #7 feat/other docs/a.md'))
        self.assertEqual(self.cli('check', 'src/c.py')[0], 0)

    def test_a_pull_request_on_this_branch_is_not_in_the_way(self):
        self.set_prs([(7, 'feat/mine', ['docs/a.md'])])
        self.assertEqual(self.cli('check', 'docs/a.md')[0], 0)

    def test_claim_is_refused_when_a_pull_request_changes_the_file(self):
        self.set_prs([(7, 'feat/other', ['docs/a.md'])])
        self.assertEqual(self.cli('claim', 'docs/a.md')[0], 3)
        self.assertFalse(os.path.exists(self.claim_dir()) and os.listdir(self.claim_dir()))

    def test_a_pull_request_with_a_hundred_files_is_read_in_full(self):
        listed = [f'pad/{i}.txt' for i in range(100)]
        self.set_prs([(9, 'feat/big', listed)])
        with open(self.files, 'w') as f:
            f.write('\n'.join(listed + ['docs/b.md']) + '\n')
        code, out, _ = self.cli('check', 'docs/b.md')
        self.assertEqual((code, out), (3, 'PR #9 feat/big docs/b.md'))

    def test_a_failed_gh_read_is_a_failure_not_a_pass(self):
        code, out, err = self.cli('check', 'docs/a.md', env=dict(self.env, GH_FAIL='1'))
        self.assertEqual(code, 1)
        self.assertEqual(out, '')
        self.assertIn('boom', err)

    def test_only_one_of_many_racing_sessions_wins_a_file(self):
        def attempt(i):
            return self.cli('claim', 'docs/a.md', session=f'racer{i}')[0]

        with ThreadPoolExecutor(max_workers=8) as pool:
            codes = list(pool.map(attempt, range(8)))
        self.assertEqual(sorted(codes), [0] + [3] * 7)

    def test_list_marks_stale_claims(self):
        self.cli('claim', 'docs/b.md', session='s2', pid=str(os.getpid()))
        self.plant('docs/a.md', 's1', dead_pid())
        _, out, _ = self.cli('list')
        self.assertEqual(sorted(out.split('\n')), [
            'live s2 feat/mine docs/b.md', 'stale s1 feat/mine docs/a.md'])

    def push_from_main(self, rel, text):
        self.write(self.repo, rel, text)
        self.git(self.repo, 'add', rel)
        self.git(self.repo, 'commit', '-q', '-m', f'change {rel}')
        self.git(self.repo, 'push', '-q', 'origin', 'main')

    def test_sync_reports_a_file_both_sides_changed(self):
        self.push_from_main('docs/a.md', 'theirs\n')
        self.write(self.tree, 'docs/a.md', 'mine\n')
        code, out, _ = self.cli('sync')
        self.assertEqual((code, out), (3, 'SYNC docs/a.md'))

    def test_sync_counts_a_committed_change_on_this_branch(self):
        self.push_from_main('docs/a.md', 'theirs\n')
        self.write(self.tree, 'docs/a.md', 'mine\n')
        self.git(self.tree, 'commit', '-qam', 'mine')
        self.assertEqual(self.cli('sync')[0], 3)

    def test_sync_is_quiet_when_the_changes_are_in_different_files(self):
        self.push_from_main('docs/b.md', 'theirs\n')
        self.write(self.tree, 'docs/a.md', 'mine\n')
        self.assertEqual(self.cli('sync'), (0, '', ''))

    def test_sync_is_quiet_once_the_branch_has_merged_main(self):
        self.push_from_main('docs/a.md', 'theirs\n')
        self.git(self.tree, 'fetch', '-q', 'origin', 'main')
        self.git(self.tree, 'merge', '-q', 'origin/main')
        self.write(self.tree, 'docs/a.md', 'mine on top\n')
        self.assertEqual(self.cli('sync'), (0, '', ''))

    def test_sync_fails_when_origin_cannot_be_fetched(self):
        self.git(self.tree, 'remote', 'set-url', 'origin', os.path.join(self.tree, 'nowhere'))
        code, _, err = self.cli('sync')
        self.assertEqual(code, 1)
        self.assertIn('git', err)

    def test_sync_defaults_to_the_branch_origin_head_names(self):
        self.git(self.repo, 'push', '-q', 'origin', 'main:trunk')
        self.git(self.tree, 'fetch', '-q', 'origin')
        self.git(self.tree, 'remote', 'set-head', 'origin', 'trunk')
        self.write(self.repo, 'docs/a.md', 'on trunk\n')
        self.git(self.repo, 'add', 'docs/a.md')
        self.git(self.repo, 'commit', '-q', '-m', 'trunk only')
        self.git(self.repo, 'push', '-q', 'origin', 'main:trunk')
        self.write(self.tree, 'docs/a.md', 'mine\n')
        code, out, _ = self.cli('sync')
        self.assertEqual((code, out), (3, 'SYNC docs/a.md'))

    def test_sync_sees_a_new_file_both_sides_added_when_run_from_a_subfolder(self):
        self.push_from_main('docs/new.md', 'theirs\n')
        self.write(self.tree, 'docs/new.md', 'mine\n')
        code, out, _ = self.cli('sync', cwd=os.path.join(self.tree, 'src'))
        self.assertEqual((code, out), (3, 'SYNC docs/new.md'))

    def test_a_claim_with_no_pid_expires_after_the_time_limit(self):
        old = int(time.time()) - claims.NO_PID_TTL - 60
        self.plant('docs/a.md', 's1', None, ts=old)
        self.assertEqual(self.cli('check', 'docs/a.md', session='s2')[0], 0)
        self.plant('docs/b.md', 's1', None, ts=int(time.time()) - 60)
        self.assertEqual(self.cli('check', 'docs/b.md', session='s2')[0], 3)

    def test_a_conflict_names_the_issue_the_holder_claimed_for(self):
        self.cli('claim', 'docs/a.md', '--issue', '42', session='s1')
        code, out, _ = self.cli('check', 'docs/a.md', session='s2')
        self.assertEqual((code, out), (3, 'CLAIM s1 feat/mine docs/a.md issue=42'))

    def test_only_one_of_many_racing_sessions_takes_over_a_stale_claim(self):
        self.plant('docs/a.md', 'gone', dead_pid())

        def attempt(i):
            return self.cli('claim', 'docs/a.md', session=f'racer{i}', pid=str(os.getpid()))[0]

        with ThreadPoolExecutor(max_workers=8) as pool:
            codes = list(pool.map(attempt, range(8)))
        self.assertEqual(sorted(codes), [0] + [3] * 7)


if __name__ == '__main__':
    unittest.main()
