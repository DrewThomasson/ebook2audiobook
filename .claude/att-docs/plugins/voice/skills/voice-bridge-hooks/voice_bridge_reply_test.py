#!/usr/bin/env python3
"""Tests for voice_bridge_reply.py. Run with: python3 voice_bridge_reply_test.py"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402
hook_config.use(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test-config.json'))
import voice_bridge_reply as hook  # noqa: E402


class VoiceBridgeReplyTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        os.makedirs(os.path.join(self.root, 'pending'))
        self.socket = '/run/user/1000/cc-socks/4242.sock'

    def mark_pending(self, key='4242'):
        open(os.path.join(self.root, 'pending', key), 'w').close()

    def test_pending_request_gets_the_reply(self):
        self.mark_pending()
        path = hook.handle({'last_assistant_message': ' Done. '}, self.socket, self.root)
        with open(path) as reply:
            self.assertEqual(json.load(reply)['text'], 'Done.')
        self.assertEqual(os.path.basename(path), '4242.json')

    def test_no_marker_writes_nothing(self):
        self.assertIsNone(hook.handle({'last_assistant_message': 'x'}, self.socket, self.root))
        self.assertFalse(os.path.exists(os.path.join(self.root, 'replies')))

    def test_marker_for_another_session_writes_nothing(self):
        self.mark_pending('9999')
        self.assertIsNone(hook.handle({'last_assistant_message': 'x'}, self.socket, self.root))

    def test_session_without_socket_or_text(self):
        self.mark_pending()
        self.assertIsNone(hook.handle({'last_assistant_message': 'x'}, None, self.root))
        self.assertIsNone(hook.handle({'last_assistant_message': '  '}, self.socket, self.root))
        self.assertIsNone(hook.handle({}, self.socket, self.root))

    def follow(self, age=0):
        folder = os.path.join(self.root, 'follow')
        os.makedirs(folder, exist_ok=True)
        marker = os.path.join(folder, '4242')
        open(marker, 'w').close()
        then = time.time() - age
        os.utime(marker, (then, then))

    def feed(self):
        with open(os.path.join(self.root, 'feed', '4242.json')) as entries:
            return json.load(entries)

    def test_followed_session_feeds_every_reply(self):
        self.follow()
        hook.handle({'last_assistant_message': 'one'}, self.socket, self.root)
        hook.handle({'last_assistant_message': 'two'}, self.socket, self.root)
        self.assertEqual([(e['seq'], e['text']) for e in self.feed()], [(1, 'one'), (2, 'two')])
        self.assertFalse(os.path.exists(os.path.join(self.root, 'replies')))

    def test_feed_keeps_the_latest_entries(self):
        self.follow()
        for i in range(hook.FEED_KEEP + 5):
            hook.handle({'last_assistant_message': str(i)}, self.socket, self.root)
        entries = self.feed()
        self.assertEqual(len(entries), hook.FEED_KEEP)
        self.assertEqual(entries[-1]['seq'], hook.FEED_KEEP + 5)

    def test_stale_follow_feeds_nothing(self):
        self.follow(age=hook.FOLLOW_IDLE_SECONDS + 60)
        hook.handle({'last_assistant_message': 'x'}, self.socket, self.root)
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def speech_on(self, session='abc'):
        folder = os.path.join(self.root, 'speak-attention')
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, session + '.replies'), 'w').close()
        return folder

    def test_push_feeds_without_a_follow(self):
        hook.push(' Question: go on? ', self.socket, self.root)
        hook.push('Done.', self.socket, self.root)
        self.assertEqual([e['text'] for e in self.feed()], ['Question: go on?', 'Done.'])

    def test_followed_needs_a_recent_follow_marker(self):
        self.assertFalse(hook.followed('4242', self.root))
        self.follow()
        self.assertTrue(hook.followed('4242', self.root))
        self.follow(age=hook.FOLLOW_IDLE_SECONDS + 60)
        self.assertFalse(hook.followed('4242', self.root))
        self.assertFalse(hook.followed('', self.root))

    def test_concurrent_adds_all_land_with_distinct_seqs(self):
        threads = [threading.Thread(target=hook.push, args=(f'note {n}', self.socket, self.root))
                   for n in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sorted(e['seq'] for e in self.feed()), list(range(1, 9)))

    def test_push_needs_a_socket_and_text(self):
        self.assertIsNone(hook.push('x', None, self.root))
        self.assertIsNone(hook.push('  ', self.socket, self.root))
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_speech_mode_stop_leaves_the_feed_to_pushes(self):
        self.follow()
        self.mark_pending()
        speech = self.speech_on()
        payload = {'session_id': 'abc', 'last_assistant_message': 'Done.'}
        path = hook.handle(payload, self.socket, self.root, speech=speech)
        self.assertEqual(os.path.basename(path), '4242.json')
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_speech_mode_for_another_session_still_feeds(self):
        self.follow()
        speech = self.speech_on('other')
        payload = {'session_id': 'abc', 'last_assistant_message': 'Done.'}
        hook.handle(payload, self.socket, self.root, speech=speech)
        self.assertEqual([e['text'] for e in self.feed()], ['Done.'])

    def waiting(self, key='4242'):
        try:
            with open(os.path.join(self.root, 'attention', key + '.json')) as entry:
                return json.load(entry)['reason']
        except FileNotFoundError:
            return None

    def prompt(self, tool='Bash', tool_input=None):
        return {'hook_event_name': 'PermissionRequest', 'tool_name': tool,
                'tool_input': tool_input or {}}

    def test_permission_prompt_marks_the_session_waiting(self):
        payload = self.prompt(tool_input={'command': 'git push', 'description': 'Push it'})
        self.assertEqual(hook.attention(payload, self.socket, self.root),
                         'a permission prompt for Bash, Push it')
        self.assertEqual(self.waiting(), 'a permission prompt for Bash, Push it')

    def run_main(self, form, payload):
        argv = ['voice_bridge_reply.py'] + ([form] if form else [])
        stdin = tempfile.TemporaryFile('w+')
        stdin.write(json.dumps(payload))
        stdin.seek(0)
        saved = (sys.argv, sys.stdin, os.environ.get('XDG_RUNTIME_DIR'),
                 os.environ.get('CLAUDE_CODE_MESSAGING_SOCKET'))
        sys.argv, sys.stdin = argv, stdin
        os.environ['XDG_RUNTIME_DIR'] = self.runtime
        os.environ['CLAUDE_CODE_MESSAGING_SOCKET'] = self.socket
        try:
            return hook.main()
        finally:
            sys.argv, sys.stdin = saved[0], saved[1]
            for name, value in zip(('XDG_RUNTIME_DIR', 'CLAUDE_CODE_MESSAGING_SOCKET'), saved[2:]):
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            stdin.close()

    def prepare_mark(self):
        self.runtime = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.runtime, ignore_errors=True)
        self.root = os.path.join(self.runtime, 'voice-bridge')
        os.makedirs(os.path.join(self.root, 'pending'))
        hook.attention(self.prompt(), self.socket, self.root)
        self.assertIsNotNone(self.waiting())

    def test_a_removed_form_still_passed_by_an_old_hook_entry_does_nothing(self):
        self.prepare_mark()
        done = {'hook_event_name': 'PostToolUse', 'tool_name': 'Bash', 'session_id': 'abc'}
        self.assertEqual(self.run_main('spoken', done), 0)
        self.assertIsNotNone(self.waiting())

    def test_an_unknown_form_does_nothing(self):
        self.prepare_mark()
        self.assertEqual(self.run_main('bogus', {'hook_event_name': 'Stop',
                                                 'last_assistant_message': 'Done.'}), 0)
        self.assertIsNotNone(self.waiting())

    def test_a_session_with_no_prompt_is_not_waiting(self):
        self.assertIsNone(self.waiting())
        hook.attention({'hook_event_name': 'PostToolUse', 'tool_name': 'Bash'},
                       self.socket, self.root)
        self.assertIsNone(self.waiting())

    def test_the_call_finishing_and_a_prompt_submit_clear_the_mark(self):
        done = {**self.prompt(), 'hook_event_name': 'PostToolUse'}
        for finished in (done, {'hook_event_name': 'UserPromptSubmit'}):
            hook.attention(self.prompt(), self.socket, self.root)
            hook.attention(finished, self.socket, self.root)
            self.assertIsNone(self.waiting(), finished['hook_event_name'])
        self.assertFalse(os.path.exists(os.path.join(self.root, 'attention', '4242.json')))

    def test_a_parallel_call_finishing_leaves_the_open_prompt(self):
        push = self.prompt(tool_input={'command': 'git push'})
        hook.attention(push, self.socket, self.root)
        read = {'hook_event_name': 'PostToolUse', 'tool_name': 'Read',
                'tool_input': {'file_path': '/x'}}
        hook.attention(read, self.socket, self.root)
        self.assertEqual(self.waiting(), 'a permission prompt for Bash')
        hook.attention({**push, 'hook_event_name': 'PostToolUse'}, self.socket, self.root)
        self.assertIsNone(self.waiting())

    def test_the_newest_open_prompt_is_the_one_read(self):
        hook.attention(self.prompt(), self.socket, self.root, now=1)
        edit = self.prompt('Edit', {'file_path': '/y'})
        hook.attention(edit, self.socket, self.root, now=2)
        self.assertEqual(self.waiting(), 'a permission prompt for Edit')
        hook.attention({**edit, 'hook_event_name': 'PostToolUse'}, self.socket, self.root)
        self.assertEqual(self.waiting(), 'a permission prompt for Bash')

    def test_mcp_tool_reads_by_its_own_name_and_long_detail_is_cut(self):
        hook.attention(self.prompt('mcp__ccd_host__sync_with_base_branch'), self.socket,
                       self.root)
        self.assertEqual(self.waiting(), 'a permission prompt for sync with base branch')
        hook.attention(self.prompt(tool_input={'description': 'word ' * 40}), self.socket,
                       self.root)
        reason = self.waiting()
        self.assertTrue(reason.endswith('word...'), reason)
        self.assertLessEqual(len(reason), len('a permission prompt for Bash, ') + 83)

    def test_followed_prompt_adds_one_note_to_the_feed(self):
        self.follow()
        hook.attention(self.prompt(), self.socket, self.root)
        self.assertEqual([e['text'] for e in self.feed()], [
            'Waiting on you: a permission prompt for Bash. It can be answered with '
            'answer_prompt, or in the app.'])

    def test_unfollowed_prompt_feeds_nothing(self):
        hook.attention(self.prompt(), self.socket, self.root)
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_a_question_marks_waiting_without_a_feed_note(self):
        self.follow()
        for event in ('PreToolUse', 'PermissionRequest'):
            payload = {'hook_event_name': event, 'tool_name': 'AskUserQuestion'}
            self.assertEqual(hook.attention(payload, self.socket, self.root), 'a question')
        self.assertEqual(self.waiting(), 'a question')
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_other_pre_tool_use_leaves_the_mark(self):
        hook.attention(self.prompt(), self.socket, self.root)
        hook.attention({'hook_event_name': 'PreToolUse', 'tool_name': 'Read'}, self.socket,
                       self.root)
        self.assertEqual(self.waiting(), 'a permission prompt for Bash')

    def test_attention_needs_a_socket_and_a_tool(self):
        self.assertIsNone(hook.attention(self.prompt(), None, self.root))
        self.assertIsNone(hook.attention(self.prompt(''), self.socket, self.root))
        self.assertIsNone(self.waiting())

    def test_stop_that_asks_marks_a_question_and_any_other_stop_clears(self):
        hook.attention(self.prompt(), self.socket, self.root)
        asks = {'last_assistant_message': 'Merge it?'}
        self.assertEqual(hook.stop_waiting(asks, self.socket, self.root), 'a question')
        self.assertEqual(self.waiting(), 'a question')
        self.assertIsNone(hook.stop_waiting({'last_assistant_message': 'Done.'}, self.socket,
                                            self.root))
        self.assertIsNone(self.waiting())

    def transcript(self, *rows):
        path = os.path.join(self.root, 'transcript.jsonl')
        with open(path, 'w') as out:
            out.write('\n'.join(json.dumps(row) for row in rows) + '\n')
        return path

    @staticmethod
    def use(use_id, tool_input, stamp):
        return {'type': 'assistant', 'timestamp': stamp, 'message': {'content': [
            {'type': 'tool_use', 'id': use_id, 'name': 'Bash', 'input': tool_input}]}}

    @staticmethod
    def result(use_id, stamp):
        return {'type': 'user', 'timestamp': stamp, 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': use_id, 'is_error': True}]}}

    def test_a_denied_prompt_is_dropped_by_the_next_finished_call(self):
        push = self.prompt(tool_input={'command': 'git push'})
        hook.attention(push, self.socket, self.root, now=100)
        path = self.transcript(self.use('a', {'command': 'git push'}, '1970-01-01T00:01:39Z'),
                               self.result('a', '1970-01-01T00:01:41Z'))
        read = {'hook_event_name': 'PostToolUse', 'tool_name': 'Read', 'tool_input': {},
                'transcript_path': path}
        hook.attention(read, self.socket, self.root)
        self.assertIsNone(self.waiting())

    def test_an_earlier_run_of_the_same_command_leaves_the_open_prompt(self):
        path = self.transcript(self.use('a', {'command': 'git push'}, '1970-01-01T00:00:10Z'),
                               self.result('a', '1970-01-01T00:00:11Z'))
        push = {**self.prompt(tool_input={'command': 'git push'}), 'transcript_path': path}
        hook.attention(push, self.socket, self.root, now=100)
        read = {'hook_event_name': 'PostToolUse', 'tool_name': 'Read', 'tool_input': {},
                'transcript_path': path}
        hook.attention(read, self.socket, self.root)
        self.assertEqual(self.waiting(), 'a permission prompt for Bash')

    def test_a_stop_reads_a_wrap_up_question_from_the_transcript_tail(self):
        ask = {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 'w', 'name': 'mcp__ccd_turn__wrap_up',
             'input': {'recap': 'r', 'ask': 'Merge?'}}]}}
        path = self.transcript({'type': 'user', 'message': {'content': 'go'}}, ask)
        stop = {'last_assistant_message': 'Done.', 'transcript_path': path}
        self.assertEqual(hook.stop_waiting(stop, self.socket, self.root), 'a question')

    def test_tail_rows_skips_the_cut_line(self):
        path = self.transcript(*[{'type': 'user', 'n': n, 'pad': 'x' * 100} for n in range(50)])
        old, hook.TAIL_BYTES = hook.TAIL_BYTES, 1000
        try:
            rows = hook.tail_rows(path)
        finally:
            hook.TAIL_BYTES = old
        self.assertTrue(rows and rows[-1]['n'] == 49 and len(rows) < 10)
        self.assertEqual(hook.tail_rows(None), [])

    def test_a_finished_call_drops_the_last_stops_question(self):
        hook.stop_waiting({'last_assistant_message': 'Merge it?'}, self.socket, self.root)
        hook.attention({'hook_event_name': 'PostToolUse', 'tool_name': 'Read', 'tool_input': {}},
                       self.socket, self.root)
        self.assertIsNone(self.waiting())

    def follow_milestones(self):
        self.follow()
        with open(os.path.join(self.root, 'follow', '4242.mode'), 'w') as mode:
            mode.write('milestones')

    def test_all_mode_feeds_the_reply_unmarked_and_adds_no_milestone(self):
        self.follow()

        def never_asked(payload):
            raise AssertionError('all mode never asks whether a stop is a milestone')
        payload = {'last_assistant_message': 'Pass 2 clean.'}
        hook.handle(payload, self.socket, self.root)
        self.assertIsNone(hook.milestone_stop(payload, self.socket, self.root,
                                              check=never_asked))
        self.assertEqual([sorted(e) for e in self.feed()], [['at', 'reply', 'seq', 'text']])

    def test_milestones_mode_copies_only_a_milestone_stop(self):
        self.follow_milestones()
        for text, major in (('Pass 1 fixed two.', False), ('Done.', True)):
            payload = {'last_assistant_message': text}
            hook.handle(payload, self.socket, self.root)
            hook.milestone_stop(payload, self.socket, self.root, check=lambda p, m=major: m)
        self.assertEqual([(e['text'], e.get('kind')) for e in self.feed()],
                         [('Pass 1 fixed two.', None), ('Done.', None),
                          ('Done.', hook.MILESTONE)])

    def test_speech_mode_milestone_stop_adds_its_copy(self):
        self.follow_milestones()
        speech = self.speech_on()
        payload = {'last_assistant_message': 'Ready.', 'session_id': 'abc'}
        hook.handle(payload, self.socket, self.root, speech=speech)
        hook.milestone_stop(payload, self.socket, self.root, check=lambda p: True)
        self.assertEqual([(e['text'], e.get('kind')) for e in self.feed()],
                         [('Ready.', hook.MILESTONE)])

    def opened_payload(self, command, stdout):
        return {'tool_name': 'Bash', 'tool_input': {'command': command},
                'tool_response': {'stdout': stdout, 'stderr': ''}}

    def test_opened_pull_request_is_a_milestone(self):
        self.follow_milestones()
        command = 'gh pr create --title "feat: quieter follow (#5189)" --body-file b.md'
        url = 'https://github.com/o/r/pull/5250\n'
        self.assertIsNotNone(hook.opened(self.opened_payload(command, url), self.socket,
                                         self.root))
        entry = self.feed()[0]
        self.assertEqual(entry['text'], 'Opened pull request 5250: feat: quieter follow (#5189).')
        self.assertEqual(entry['kind'], hook.MILESTONE)

    def test_opened_needs_a_create_that_printed_a_url_and_a_milestones_follow(self):
        self.follow_milestones()
        url = 'https://github.com/o/r/pull/5250'
        self.assertIsNone(hook.opened(self.opened_payload('gh pr create -t x', 'failed'),
                                      self.socket, self.root))
        self.assertIsNone(hook.opened(self.opened_payload('gh pr view 5250', url),
                                      self.socket, self.root))
        os.remove(os.path.join(self.root, 'follow', '4242.mode'))
        self.assertIsNone(hook.opened(self.opened_payload('gh pr create -t x', url),
                                      self.socket, self.root))
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_opened_skips_a_create_refused_for_an_existing_pull_request(self):
        self.follow_milestones()
        refused = ('a pull request for branch "x" into branch "main" already exists:\n'
                   'https://github.com/o/r/pull/5100\n')
        self.assertIsNone(hook.opened(self.opened_payload('gh pr create -t x 2>&1', refused),
                                      self.socket, self.root))
        other = 'see https://github.com/o/r/pull/5100 for it\n'
        self.assertIsNone(hook.opened(self.opened_payload('gh pr create -t x; echo', other),
                                      self.socket, self.root))

    def test_a_question_adds_one_milestone_across_its_two_hooks(self):
        self.follow_milestones()
        hook.attention(self.ask(), self.socket, self.root)
        hook.attention({**self.ask(), 'hook_event_name': 'PermissionRequest'}, self.socket,
                       self.root)
        self.assertEqual(len(self.feed()), 1)

    def test_opened_counts_a_create_beside_another_commands_already_exists(self):
        self.follow_milestones()
        output = ('https://github.com/o/r/pull/5252\n'
                  'tag v1 already exists, skipping\n')
        hook.opened(self.opened_payload('gh pr create -t x && tagger', output), self.socket,
                    self.root)
        self.assertEqual(self.feed()[0]['text'], 'Opened pull request 5252: x.')

    def test_opened_counts_a_create_beside_a_git_already_exists(self):
        self.follow_milestones()
        payload = self.opened_payload('git worktree add ../w b; gh pr create -t x',
                                      'https://github.com/o/r/pull/5300\n')
        payload['tool_response']['stderr'] = "fatal: '../w' already exists"
        hook.opened(payload, self.socket, self.root)
        entry = self.feed()[0]
        self.assertEqual(entry['text'], 'Opened pull request 5300: x.')
        self.assertNotIn('copy', entry)

    def test_stop_and_question_milestones_are_marked_as_copies(self):
        self.follow_milestones()
        hook.attention(self.ask(), self.socket, self.root)
        hook.milestone_stop({'last_assistant_message': 'Done.'}, self.socket, self.root,
                            check=lambda p: True)
        self.assertEqual([e.get('copy') for e in self.feed()], [True, True])
        # Only the stop's copy is a reply, which the bridge reads as a summary when long.
        self.assertEqual([e.get('reply') for e in self.feed()], [None, True])

    def test_opened_skips_a_refusal_on_standard_error(self):
        self.follow_milestones()
        payload = self.opened_payload('gh pr create --fill || gh pr view --json url -q .url',
                                      'https://github.com/a/b/pull/7\n')
        payload['tool_response']['stderr'] = ('a pull request for branch "x" into branch '
                                              '"main" already exists:')
        self.assertIsNone(hook.opened(payload, self.socket, self.root))

    def test_milestone_stop_adds_nothing_once_the_follow_stops_during_the_check(self):
        self.follow_milestones()

        def stops_following(payload):
            os.remove(os.path.join(self.root, 'follow', '4242'))
            return True
        self.assertIsNone(hook.milestone_stop({'last_assistant_message': 'Done.'},
                                              self.socket, self.root, check=stops_following))
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_opened_reads_the_url_on_its_own_line_in_a_chain(self):
        self.follow_milestones()
        chained = ('https://github.com/o/r/pull/5251\n'
                   'waiting for merge: x - https://github.com/o/r/pull/5251\n')
        hook.opened(self.opened_payload('gh pr create -t x && catchup add-pr', chained),
                    self.socket, self.root)
        self.assertEqual(self.feed()[0]['text'], 'Opened pull request 5251: x.')

    def test_pr_title_reads_each_spelling(self):
        self.assertEqual(hook.pr_title('gh pr create -t "A b" --body-file f'), 'A b')
        self.assertEqual(hook.pr_title("gh pr create --title='A b'"), 'A b')
        self.assertEqual(hook.pr_title('gh pr create --body-file f'), '')
        self.assertEqual(hook.pr_title('gh pr create --title "unclosed'), '')
        self.assertEqual(hook.pr_title("git log -t foo && gh pr create --title 'Real'"), 'Real')
        self.assertEqual(hook.pr_title('gh pr create --body-file f && echo -t no'), '')
        self.assertEqual(hook.pr_title('gh pr create --fill\ngh pr edit 5 -t Other'), '')
        self.assertEqual(hook.pr_title('gh pr create \\\n  -t "Wrapped"'), 'Wrapped')
        self.assertEqual(hook.pr_title('gh pr create --title "$(cat t)" -F b'), '')
        self.assertEqual(hook.pr_title("gh pr create -t 'Fix $HOME path' -F b"),
                         'Fix $HOME path')

    def ask(self):
        return {'hook_event_name': 'PreToolUse', 'tool_name': 'AskUserQuestion',
                'tool_input': {'questions': [{'question': 'Which runner?'},
                                             {'question': 'Retry it?'}]}}

    def test_question_is_a_milestone_entry_in_milestones_mode(self):
        self.follow_milestones()
        hook.attention(self.ask(), self.socket, self.root)
        entry = self.feed()[0]
        self.assertEqual(entry['text'], 'Waiting on you: a question. Which runner? Retry it? '
                         'It can be answered with answer_prompt, or in the app.')
        self.assertEqual(entry['kind'], hook.MILESTONE)

    def test_question_adds_nothing_in_all_mode(self):
        self.follow()
        hook.attention(self.ask(), self.socket, self.root)
        self.assertFalse(os.path.exists(os.path.join(self.root, 'feed')))

    def test_prompt_note_is_a_milestone(self):
        self.follow()
        hook.attention({'hook_event_name': 'PermissionRequest', 'tool_name': 'Bash',
                        'tool_input': {}}, self.socket, self.root)
        self.assertIs(self.feed()[0]['milestone'], True)

    def stop_with(self, reply, rows):
        path = os.path.join(self.root, 'transcript.jsonl')
        with open(path, 'w') as out:
            out.write(''.join(json.dumps(row) + '\n' for row in rows))
        return {'last_assistant_message': reply, 'transcript_path': path}

    def test_stop_milestone_holds_a_stop_with_background_work_due(self):
        prompt = {'type': 'user', 'timestamp': '2026-10-24T10:00:00Z',
                  'message': {'role': 'user', 'content': 'implement 5189'}}
        waiting = {'type': 'user', 'timestamp': '2026-10-24T10:01:00Z',
                   'toolUseResult': {'backgroundTaskId': 'b1', 'stdout': ''},
                   'message': {'role': 'user',
                               'content': [{'type': 'tool_result', 'content': 'x'}]}}
        self.assertFalse(hook.stop_milestone(self.stop_with('Pass 2 fixed one.',
                                                            [prompt, waiting])))
        self.assertTrue(hook.stop_milestone(self.stop_with('Merge it?', [prompt, waiting])))
        self.assertTrue(hook.stop_milestone(self.stop_with('All done.', [prompt])))

    def ready_record(self, number):
        with open(os.path.join(self.root, 'ready', f'4242-{number}.json')) as record:
            return json.load(record)

    def test_ready_form_records_each_pull_request_the_check_lets_through(self):
        payload = {'last_assistant_message': 'Done.\n\nPULL REQUEST 5250 IS READY FOR YOUR '
                   'REVIEW\nPULL REQUEST 5251 IS READY FOR\nYOUR REVIEW', 'session_id': 'abc',
                   'cwd': '/repo/x'}
        written = hook.ready(payload, self.socket, self.root, now=50,
                             check=lambda p: ['5250'])
        self.assertEqual(len(written), 1)
        self.assertEqual(self.ready_record(5250), {'number': 5250, 'at': 50, 'session': 'abc',
                                                'cwd': '/repo/x'})
        self.assertFalse(os.path.exists(os.path.join(self.root, 'ready', '4242-5251.json')))

    def test_ready_form_runs_unfollowed_and_skips_a_reply_with_no_ready_line(self):
        self.assertFalse(os.path.exists(os.path.join(self.root, 'follow')))
        checked = []
        self.assertEqual(hook.ready({'last_assistant_message': 'Pass 2 fixed one.'},
                                    self.socket, self.root, check=checked.append), [])
        self.assertEqual(checked, [])
        self.assertEqual(len(hook.ready({'last_assistant_message': 'PULL REQUEST 9 IS READY '
                                         'FOR YOUR REVIEW'}, self.socket, self.root,
                                        check=lambda p: ['9'])), 1)

    def test_ready_numbers_lists_each_pull_request_the_ready_lines_name(self):
        payload = self.stop_with('PULL REQUEST 5251 IS READY FOR YOUR REVIEW\n'
                                 'PULL REQUEST 5250 IS READY FOR YOUR REVIEW', [])
        self.assertEqual(hook.ready_numbers(payload), ['5250', '5251'])

    def test_stop_starts_the_ready_form_only_for_a_ready_line(self):
        spawned = []
        self.assertFalse(hook.start_ready({'last_assistant_message': 'Done.'},
                                          spawn=spawned.append))
        ready = {'last_assistant_message': 'pull request 7 is ready for your review'}
        self.assertTrue(hook.start_ready(ready, spawn=spawned.append))
        self.assertEqual(spawned, [ready])
        # The ready line in the turn's closing transcript text counts, as ready_numbers
        # reads it, and words that only resemble it do not.
        closing = {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
            {'type': 'text', 'text': 'PULL REQUEST **#8** IS READY FOR YOUR REVIEW'}]}}
        self.assertTrue(hook.start_ready(self.stop_with('Done.', [closing]),
                                         spawn=spawned.append))
        self.assertFalse(hook.start_ready({'last_assistant_message': 'Is it ready for your '
                                           'review?'}, spawn=spawned.append))

    def test_socket_key(self):
        self.assertEqual(hook.socket_key('/tmp/cc-socks-1000/77.sock'), '77')
        self.assertEqual(hook.socket_key('/tmp/other'), '')
        self.assertEqual(hook.socket_key(''), '')


class AnswerFormTest(unittest.TestCase):
    """The answer form, run with a clock the test moves and a sleep that stands in for the
    bridge writing its answer."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.socket = '/run/user/1000/cc-socks/4242.sock'
        self.clock = [1000.0]

    def prompt(self, tool='Bash', tool_input=None):
        return {'hook_event_name': 'PermissionRequest', 'tool_name': tool,
                'tool_input': tool_input or {'command': 'git push', 'description': 'Push it'}}

    def prompts(self):
        folder = os.path.join(self.root, 'prompts', '4242')
        return [json.load(open(os.path.join(folder, name))) for name in os.listdir(folder)]

    def run_with(self, payload, answer=None, wait=30, on_sleep=None):
        """Runs await_answer; on its first sleep, answer(prompt) gives the answer file's
        fields, written as the bridge writes them."""
        seen = []

        def sleep(_seconds):
            if not seen:
                [prompt] = self.prompts()
                seen.append(prompt)
                if answer:
                    hook.write_json(os.path.join(self.root, 'answers', '4242'),
                                    prompt['id'] + '.json', answer(prompt))
            if on_sleep:
                on_sleep(len(seen))
            self.clock[0] += hook.ANSWER_POLL_SECONDS
            seen.append(None)

        decision = hook.await_answer(payload, self.socket, self.root,
                                     clock=lambda: self.clock[0], sleep=sleep, wait=wait)
        return decision, seen[0] if seen else None

    def bound(self, behavior, **fields):
        return lambda prompt: {'id': prompt['id'], 'behavior': behavior, **fields}

    def test_bound_allow_becomes_the_decision_and_nothing_is_left_behind(self):
        decision, prompt = self.run_with(self.prompt(), self.bound('allow'))
        self.assertEqual(decision, {'behavior': 'allow'})
        self.assertEqual(prompt['tool'], 'Bash')
        self.assertEqual(prompt['input'], {'command': 'git push', 'description': 'Push it'})
        self.assertEqual(prompt['pid'], os.getpid())
        self.assertRegex(prompt['id'], r'^[0-9a-f]{32}$')
        self.assertEqual(self.prompts(), [])
        # The answer file is gone, and the acknowledgement for the bridge is left.
        self.assertEqual(os.listdir(os.path.join(self.root, 'answers', '4242')),
                         [prompt['id'] + '.took'])
        self.assertNotIn('digest', prompt)

    def test_deny_says_the_voice_chat_denied_it(self):
        decision, _ = self.run_with(self.prompt(), self.bound('deny'))
        self.assertEqual(decision, {'behavior': 'deny', 'message': hook.DENIED})

    def test_each_request_gets_its_own_id(self):
        _, first = self.run_with(self.prompt(), self.bound('deny'))
        _, second = self.run_with(self.prompt(), self.bound('deny'))
        self.assertNotEqual(first['id'], second['id'])

    def test_an_answer_naming_another_prompt_is_refused(self):
        replayed = lambda prompt: {'id': 'f' * 32, 'behavior': 'allow'}
        decision, prompt = self.run_with(self.prompt(), replayed, wait=3)
        self.assertIsNone(decision)
        self.assertEqual(self.prompts(), [])
        self.assertEqual(os.listdir(os.path.join(self.root, 'answers', '4242')),
                         [prompt['id'] + '.refused'])

    def test_an_answer_the_bridge_cancelled_first_is_never_read(self):
        answers = os.path.join(self.root, 'answers', '4242')

        def cancel(prompt):
            # The bridge timed out and renamed the answer before the hook claimed it.
            return {'id': prompt['id'], 'behavior': 'allow'}

        def cancelled(count):
            if count == 1:
                [name] = [n for n in os.listdir(answers) if n.endswith('.json')]
                os.rename(os.path.join(answers, name),
                          os.path.join(answers, name[:-5] + '.cancelled'))

        self.assertEqual(self.run_with(self.prompt(), cancel, wait=3,
                                       on_sleep=cancelled)[0], None)
        self.assertTrue(all(n.endswith('.cancelled') for n in os.listdir(answers)))

    def test_an_answer_written_under_an_old_id_is_never_read(self):
        _, old = self.run_with(self.prompt(), self.bound('deny'))
        # An answer the bridge wrote for the old request, after that hook returned.
        hook.write_json(os.path.join(self.root, 'answers', '4242'), old['id'] + '.json',
                        {'id': old['id'], 'behavior': 'allow'})
        self.assertEqual(self.run_with(self.prompt(), wait=3)[0], None)

    def test_a_question_is_allowed_with_its_questions_and_answers(self):
        asks = {'questions': [{'question': 'Which runner?',
                               'options': [{'label': 'Linux'}, {'label': 'Windows'}]}]}
        decision, _ = self.run_with(
            self.prompt('AskUserQuestion', asks),
            self.bound('allow', answers={'Which runner?': 'Windows'}))
        self.assertEqual(decision, {'behavior': 'allow', 'updatedInput': {
            **asks, 'answers': {'Which runner?': 'Windows'}}})

    def test_a_question_allowed_without_answers_never_decides(self):
        asks = {'questions': [{'question': 'Which runner?', 'options': [{'label': 'Linux'}]}]}
        self.assertEqual(self.run_with(self.prompt('AskUserQuestion', asks),
                                       self.bound('allow'), wait=3)[0], None)
        # The answer it could not take is refused, so the bridge says to answer again.
        [left] = os.listdir(os.path.join(self.root, 'answers', '4242'))
        self.assertTrue(left.endswith('.refused'), left)

    def test_mode_changes_settings_paths_and_long_input_stay_in_the_app(self):
        for payload in (
                self.prompt('ExitPlanMode', {'plan': 'Do it'}),
                self.prompt('Edit', {'file_path': '/repo/.claude/settings.json'}),
                self.prompt('Bash', {'command': "sed -i 's/a/b/' .claude/settings.json"}),
                self.prompt('Bash', {'command': 'cp x.sh ~/.claude/hooks/x.sh'}),
                self.prompt('Write', {'file_path': '/repo/a.txt', 'content': 'x' * 2000})):
            self.assertEqual(self.run_with(payload, self.bound('allow')), (None, None))
        self.assertFalse(os.path.exists(os.path.join(self.root, 'prompts')))

    def test_a_name_that_only_holds_claude_is_not_a_settings_path(self):
        for value in ('notes.claude.md', '/repo/claude/x', 'my.claude', '/repo/src/a.ts'):
            self.assertFalse(hook.app_only(self.prompt('Edit', {'file_path': value})), value)
        for value in ('.claude', '/repo/.claude/a', r'C:\r\.claude\x'):
            self.assertTrue(hook.app_only(self.prompt('Edit', {'file_path': value})), value)

    def test_a_command_that_can_reach_settings_stays_in_the_app(self):
        tree = '.claude/worktrees/x'
        for value in (f'cd {tree} && cd ../.. && sed -i s/a/b/ settings.json',
                      f'cd {tree} && cd ../.. && cat hooks/h.sh',
                      f'cd /repo/{tree}/src/.. && ls', 'ls .claude', 'cat notes.claude.md',
                      'cp a src/settings.json', f'ls {tree} .claude/hooks',
                      'ls .claude/worktrees/../hooks', 'ls .claude/worktrees/./x'):
            self.assertTrue(hook.app_only(self.prompt('Bash', {'command': value})), value)
        for value in ('git log --oneline', f'cd /repo/{tree} && npm test',
                      f"cd '/repo/{tree}' && git status", f'ls /repo/{tree}'):
            self.assertFalse(hook.app_only(self.prompt('Bash', {'command': value})), value)
        # Every field that runs as a command counts, whatever the tool.
        for tool_input in ({'cmd': f'cd {tree} && cd ../.. && cat hooks/h.sh'},
                           {'shell': {'line': 'cp a settings.json'}},
                           {'code': "open('../.claude/x')"},
                           {'script': ['ls', 'notes.claude.md']}):
            self.assertTrue(hook.app_only(self.prompt('mcp__x__run', tool_input)),
                            tool_input)

    def test_file_content_that_mentions_settings_stays_answerable(self):
        for tool_input in (
                {'file_path': '/repo/docs/a.md', 'content': 'Edit settings.json, then ..'},
                {'file_path': '/repo/notes.claude.md', 'content': 'x'},
                {'file_path': '/repo/src/a.ts', 'old_string': 'settings.json',
                 'new_string': '../settings.json'}):
            self.assertFalse(hook.app_only(self.prompt('Edit', tool_input)), tool_input)
        # A .claude path in the content still keeps it in the app, as a target there does.
        for tool_input in ({'file_path': '/repo/.claude/settings.json', 'content': 'x'},
                           {'file_path': '/repo/a.sh', 'content': 'cp x .claude/hooks/'}):
            self.assertTrue(hook.app_only(self.prompt('Write', tool_input)), tool_input)

    def test_a_worktree_checkout_is_source_but_its_own_claude_folder_is_not(self):
        tree = '/repo/.claude/worktrees/issue-1'
        for value in (f'{tree}/src/a.ts', f'cd {tree} && ls', f'ls {tree}'):
            self.assertFalse(hook.app_only(self.prompt('Edit', {'file_path': value})), value)
        for value in (f'{tree}/.claude/settings.json', '/repo/.claude/worktrees',
                      '/repo/.claude/settings.json', '/repo/.claude/worktrees/../settings.json',
                      f'{tree}/../../hooks/h.sh', '/repo/.claude/worktrees/./x'):
            self.assertTrue(hook.app_only(self.prompt('Edit', {'file_path': value})), value)

    def test_a_settings_path_nested_in_the_input_stays_in_the_app(self):
        for tool_input in ({'edits': [{'file_path': '/repo/.claude/settings.json'}]},
                           {'args': {'path': '~/.claude/hooks/h.sh'}}):
            self.assertTrue(hook.app_only(self.prompt('mcp__x__write', tool_input)))
        self.assertFalse(hook.app_only(self.prompt('mcp__x__write', {'args': ['/repo/a']})))

    def test_a_session_without_a_socket_offers_nothing(self):
        self.assertIsNone(hook.await_answer(self.prompt(), None, self.root))
        self.assertFalse(os.path.exists(os.path.join(self.root, 'prompts')))

    def test_the_wait_ends_once_the_app_answers(self):
        call = hook.call_of(self.prompt())

        def app(count):
            # The attention form marks the call, then its PostToolUse clears the mark.
            if count == 1:
                hook.mark_waiting(self.root, '4242', call, 'a permission prompt', 1)
            elif count == 3:
                hook.clear_waiting(self.root, '4242')

        decision, _ = self.run_with(self.prompt(), wait=hook.ANSWER_WAIT_SECONDS, on_sleep=app)
        self.assertIsNone(decision)
        self.assertLess(self.clock[0] - 1000.0, 5)
        self.assertEqual(self.prompts(), [])

    def transcript_rows(self, payload, rows):
        transcript = os.path.join(self.root, 'transcript.jsonl')
        with open(transcript, 'w') as out:
            out.write('\n'.join(json.dumps(row) for row in rows) + '\n')
        return {**payload, 'transcript_path': transcript}

    def test_the_wait_ends_on_a_subagent_refusal_or_a_running_call(self):
        payload = self.prompt()
        use = {'timestamp': '2100-01-01T00:00:00+00:00', 'isSidechain': True,
               'message': {'content': [{'type': 'tool_use', 'id': 'u2', 'name': 'Bash',
                                        'input': payload['tool_input']}]}}
        for after in (
                {'timestamp': '2100-01-01T00:00:01+00:00', 'isSidechain': True,
                 'message': {'content': [
                     {'type': 'tool_result', 'tool_use_id': 'u2', 'content': 'denied'}]}},
                {'timestamp': '2100-01-01T00:00:01+00:00', 'type': 'progress',
                 'toolUseID': 'bash-progress-1', 'parentToolUseID': 'u2'}):
            self.clock[0] = 1000.0
            with_rows = self.transcript_rows(payload, [use])

            def lands(count, after=after, with_rows=with_rows):
                # The row is written after the hook started.
                if count == 1:
                    with open(with_rows['transcript_path'], 'a') as out:
                        out.write(json.dumps(after) + '\n')

            decision, _ = self.run_with(with_rows, wait=hook.ANSWER_WAIT_SECONDS,
                                        on_sleep=lands)
            self.assertIsNone(decision)
            self.assertLessEqual(self.clock[0] - 1000.0, hook.ANSWER_RESULT_SECONDS + 1)

    def test_the_prompt_is_offered_before_the_old_progress_rows_are_read(self):
        order = []
        real_tail, real_write = hook.tail_rows, hook.write_json
        hook.tail_rows = lambda *a, **k: order.append('tail') or real_tail(*a, **k)
        hook.write_json = lambda *a: order.append('write') or real_write(*a)
        try:
            self.run_with(self.prompt(), self.bound('deny'))
        finally:
            hook.tail_rows, hook.write_json = real_tail, real_write
        self.assertEqual(order[:2], ['write', 'tail'])

    def test_a_progress_row_already_there_when_the_hook_starts_does_not_end_the_wait(self):
        payload = self.prompt()
        rows = [{'timestamp': '2100-01-01T00:00:00+00:00', 'message': {'content': [
            {'type': 'tool_use', 'id': 'u1', 'name': 'Bash',
             'input': payload['tool_input']}]}},
            {'timestamp': '2100-01-01T00:00:01+00:00', 'type': 'progress',
             'toolUseID': 'bash-progress-0', 'parentToolUseID': 'u1'}]
        decision, _ = self.run_with(self.transcript_rows(payload, rows), wait=30)
        self.assertIsNone(decision)
        self.assertGreaterEqual(self.clock[0] - 1000.0, 30)

    def test_the_wait_ends_on_a_result_the_transcript_gives_the_call(self):
        transcript = os.path.join(self.root, 'transcript.jsonl')
        payload = {**self.prompt(), 'transcript_path': transcript}
        rows = [{'timestamp': '2100-01-01T00:00:00+00:00', 'message': {'content': [
            {'type': 'tool_use', 'id': 'u1', 'name': 'Bash', 'input': payload['tool_input']}]}},
            {'timestamp': '2100-01-01T00:00:01+00:00', 'message': {'content': [
                {'type': 'tool_result', 'tool_use_id': 'u1', 'content': 'denied'}]}}]
        with open(transcript, 'w') as out:
            out.write('\n'.join(json.dumps(row) for row in rows) + '\n')
        decision, _ = self.run_with(payload, wait=hook.ANSWER_WAIT_SECONDS)
        self.assertIsNone(decision)
        self.assertLessEqual(self.clock[0] - 1000.0, hook.ANSWER_RESULT_SECONDS + 1)


if __name__ == '__main__':
    unittest.main()
