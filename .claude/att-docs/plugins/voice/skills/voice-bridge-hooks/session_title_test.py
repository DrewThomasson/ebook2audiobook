#!/usr/bin/env python3
"""Checks session_title.py against fake session files, process folders and inbox sockets.

usage: python3 session_title_test.py
"""
import contextlib
import io
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_title as st  # noqa: E402


class Titles(unittest.TestCase):
    def test_split_takes_the_status_then_the_last_separator(self):
        self.assertEqual(st.split_title("Overmind 2"), ("Overmind 2", "", ""))
        self.assertEqual(st.split_title("Overmind 2 - read window"),
                         ("Overmind 2", "read window", ""))
        self.assertEqual(st.split_title("Overmind 2 - read window (waiting on CI)"),
                         ("Overmind 2", "read window", "waiting on CI"))
        self.assertEqual(st.split_title("Overmind 2 (idle)"), ("Overmind 2", "", "idle"))
        # The words the voice bridge writes for every session are statuses here too.
        self.assertEqual(st.split_title("Overmind 2 - PR #5 fix (needs you)"),
                         ("Overmind 2", "PR #5 fix", "needs you"))
        self.assertEqual(st.split_title("Overmind 2 (working)"), ("Overmind 2", "", "working"))
        self.assertEqual(st.split_title("Login - staging - one"),
                         ("Login - staging", "one", ""))
        # The number Claude Code adds after a status joins the base.
        self.assertEqual(st.split_title("Merge (idle) 2"), ("Merge 2", "", "idle"))
        self.assertEqual(st.split_title("Merge - fix (stuck) 3"), ("Merge 3", "fix", "stuck"))
        # Parentheses that are not one of the statuses stay part of the title.
        self.assertEqual(st.split_title("Overmind (draft)"), ("Overmind (draft)", "", ""))

    def test_a_partner_wait_splits_and_round_trips(self):
        self.assertEqual(st.split_title("Navi 2 - work (waiting on Data)"),
                         ("Navi 2", "work", "waiting on Data"))
        self.assertEqual(st.split_title("Navi (waiting on Data) 2"),
                         ("Navi 2", "", "waiting on Data"))
        self.assertEqual(st.split_title("Navi 2 (waiting on CI)"), ("Navi 2", "", "waiting on CI"))
        title = st.new_title("Navi 2 - work", "status", "waiting on Data")
        self.assertEqual(title, "Navi 2 - work (waiting on Data)")
        self.assertEqual(st.new_title(title, "status", ""), "Navi 2 - work")

    def test_a_partner_wait_needs_a_short_name_that_is_not_you_or_ci(self):
        for good in ("waiting on Data", "waiting on Data-2", "waiting on Ünï"):
            self.assertTrue(st.is_partner_wait(good), good)
        for bad in ("waiting on", "waiting on ", "waiting on (x)", "waiting on you",
                    "waiting on CI", "waiting on ci", "waiting on You", "waiting on  Data",
                    "waiting on " + "x" * 25, "idle", ""):
            self.assertFalse(st.is_partner_wait(bad), bad)
            if bad and bad not in st.STATUSES:
                with self.assertRaises(ValueError):
                    st.new_title("Navi 2", "status", bad)

    def test_work_replaces_the_work_name_and_takes_the_status_away(self):
        title = st.new_title("Overmind 2 - old work (stuck)", "work", "read   window")
        self.assertEqual(title, "Overmind 2 - read window")
        self.assertEqual(st.new_title("Overmind 2 - read window", "work", ""), "Overmind 2")
        self.assertEqual(st.new_title("Overmind 2", "work", "one - two"),
                         "Overmind 2 - one two")

    def test_status_keeps_the_base_and_the_work_name(self):
        self.assertEqual(st.new_title("Overmind 2 - read window", "status", "waiting on you"),
                         "Overmind 2 - read window (waiting on you)")
        self.assertEqual(st.new_title("Overmind 2 - read window (stuck)", "status", "idle"),
                         "Overmind 2 - read window (idle)")
        self.assertEqual(st.new_title("Overmind 2 - read window (idle)", "status", ""),
                         "Overmind 2 - read window")
        self.assertEqual(st.new_title("Overmind 2", "status", "stopped"), "Overmind 2 (stopped)")
        with self.assertRaises(ValueError):
            st.new_title("Overmind 2", "status", "napping")

    def test_a_new_status_replaces_a_numbered_one(self):
        self.assertEqual(st.new_title("Merge (idle) 2", "status", "stuck"), "Merge 2 (stuck)")
        self.assertEqual(st.new_title("Merge - fix (stuck) 2", "status", "idle"),
                         "Merge 2 - fix (idle)")
        self.assertEqual(st.new_title("Merge (idle) 2", "status", ""), "Merge 2")

    def test_a_long_work_name_is_cut_on_a_word_to_leave_room_for_the_status(self):
        title = st.new_title("Overmind 2", "work",
                             "a very long work name that would not fit in the sidebar at all")
        self.assertLessEqual(len(title), st.MAX_TITLE)
        self.assertEqual(title, "Overmind 2 - a very long work name that would not fit in the")
        # A status added later takes room from the work name.
        again = st.new_title(title, "status", "waiting on CI")
        self.assertLessEqual(len(again), st.MAX_TITLE)
        self.assertTrue(again.endswith(" (waiting on CI)"))
        self.assertEqual(st.split_title(again)[0], "Overmind 2")

    def test_a_base_with_no_room_is_refused(self):
        with self.assertRaises(ValueError):
            st.compose("x" * 59, "work", "")
        with self.assertRaises(ValueError):
            st.compose("x" * 58, "", "waiting on you")

    def test_a_long_base_keeps_the_status_and_drops_the_work_name(self):
        base = "x" * 40
        title = st.compose(base, "read window", "waiting on you")
        self.assertEqual(title, base + " (waiting on you)")
        self.assertLessEqual(len(title), st.MAX_TITLE)


class Sessions(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.sessions = os.path.join(self.dir, "sessions")
        self.proc = os.path.join(self.dir, "proc")
        os.makedirs(self.sessions)
        os.makedirs(self.proc)

    def proc_entry(self, pid, parent):
        os.makedirs(os.path.join(self.proc, str(pid)), exist_ok=True)
        fields = ["S", str(parent)] + ["0"] * 20
        with open(os.path.join(self.proc, str(pid), "stat"), "w") as f:
            f.write("%d (a name) with parens) %s" % (pid, " ".join(fields)))

    def session_file(self, pid, name, sock="/nowhere.sock"):
        with open(os.path.join(self.sessions, "%d.json" % pid), "w") as f:
            json.dump({"pid": pid, "name": name, "sessionId": "s-%d" % pid,
                       "messagingSocketPath": sock, "kind": "interactive"}, f)

    def test_the_nearest_ancestor_with_a_session_file_is_the_session(self):
        # shell 30 -> script's parent 20 -> claude 10 -> init 1; another session is elsewhere.
        self.proc_entry(30, 20)
        self.proc_entry(20, 10)
        self.proc_entry(10, 1)
        self.session_file(10, "Overmind 2")
        self.session_file(99, "Other")
        entry = st.find_own_session(self.sessions, self.proc, 30)
        self.assertEqual(entry["pid"], 10)
        self.assertIsNone(st.find_own_session(self.sessions, self.proc, 77))

    def test_a_file_without_a_pid_gets_the_process_id_it_is_named_for(self):
        with open(os.path.join(self.sessions, "40.json"), "w") as f:
            json.dump({"name": "No pid", "messagingSocketPath": "/x.sock"}, f)
        self.assertEqual(st.find_own_session(self.sessions, self.proc, 40)["pid"], 40)
        with open(os.path.join(self.sessions, "41.json"), "w") as f:
            json.dump({"pid": None, "messagingSocketPath": "/x.sock"}, f)
        self.assertEqual(st.find_own_session(self.sessions, self.proc, 41)["pid"], 41)

    def test_a_loop_in_the_process_tree_ends(self):
        self.proc_entry(5, 6)
        self.proc_entry(6, 5)
        self.assertIsNone(st.find_own_session(self.sessions, self.proc, 5))


class Fixture(unittest.TestCase):
    """A fake session with an inbox socket, which the tests below talk to."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(dir="/tmp")
        self.addCleanup(shutil.rmtree, self.dir)
        self.sessions = os.path.join(self.dir, "sessions")
        self.proc = os.path.join(self.dir, "proc")
        os.makedirs(self.sessions)
        os.makedirs(os.path.join(self.proc, "10"))
        with open(os.path.join(self.proc, "10", "stat"), "w") as f:
            f.write("10 (claude) S 1 " + " ".join(["0"] * 20))
        self.sock_path = os.path.join(self.dir, "inbox.sock")
        self.received = []
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.sock_path)
        self.server.listen(1)
        self.addCleanup(self.server.close)
        self.write_session("Overmind 2 - read window")
        self.env = mock.patch.dict(os.environ, {
            "SESSION_TITLE_SESSIONS_DIR": self.sessions, "SESSION_TITLE_PROC_DIR": self.proc,
            "SESSION_TITLE_PID": "10"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def write_session(self, name):
        with open(os.path.join(self.sessions, "10.json"), "w") as f:
            json.dump({"pid": 10, "name": name, "sessionId": "s-10",
                       "messagingSocketPath": self.sock_path, "kind": "interactive"}, f)

    def serve(self, apply=True):
        """Answers one rename the way the session does: it writes the new title to its file."""
        def run():
            conn, _ = self.server.accept()
            with conn:
                line = conn.makefile().readline()
            message = json.loads(line)
            self.received.append(message)
            if apply:
                self.write_session(message["name"])
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        code = st.main(["session_title.py", *args], out=out, err=err)
        return code, out.getvalue(), err.getvalue()


class Main(Fixture):

    def test_work_sends_the_rename_control_message_and_reads_the_title_back(self):
        thread = self.serve()
        code, out, _ = self.run_main("work", "main checkout guard")
        thread.join(5)
        self.assertEqual(code, 0)
        self.assertEqual(self.received, [{
            "type": "control", "action": "rename",
            "name": "Overmind 2 - main checkout guard", "session_id": "s-10"}])
        self.assertEqual(out.strip(),
                         "Renamed Overmind 2 - read window to Overmind 2 - main checkout guard.")

    def test_status_then_work_again_takes_the_status_off(self):
        thread = self.serve()
        self.assertEqual(self.run_main("status", "waiting on you")[0], 0)
        thread.join(5)
        self.assertEqual(self.received[-1]["name"],
                         "Overmind 2 - read window (waiting on you)")
        thread = self.serve()
        self.assertEqual(self.run_main("work", "read window")[0], 0)
        thread.join(5)
        self.assertEqual(self.received[-1]["name"], "Overmind 2 - read window")

    def test_a_title_that_is_already_right_sends_nothing(self):
        code, out, _ = self.run_main("work", "read window")
        self.assertEqual((code, self.received), (0, []))
        self.assertIn("already called", out)

    def test_show_prints_the_current_title(self):
        self.assertEqual(self.run_main("show")[1].strip(), "Overmind 2 - read window")

    def test_bad_input_and_a_missing_session_exit_1(self):
        self.assertEqual(self.run_main()[0], 1)
        self.assertEqual(self.run_main("status", "napping")[0], 1)
        self.assertEqual(self.run_main("work")[0], 1)
        with mock.patch.dict(os.environ, {"SESSION_TITLE_PID": "999"}):
            code, _, err = self.run_main("show")
        self.assertEqual(code, 1)
        self.assertIn("no Claude session", err)
        with mock.patch.dict(os.environ, {"SESSION_TITLE_PID": "abc"}):
            code, _, err = self.run_main("show")
        self.assertEqual(code, 1)
        self.assertIn("must be a process id", err)

    def test_a_title_that_does_not_change_is_said_so(self):
        self.serve(apply=False)
        with mock.patch.object(st, "WAIT_SECONDS", 0.3):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = st.main(["session_title.py", "work", "other"])
        self.assertEqual(code, 0)
        self.assertIn("did not change", out.getvalue())

    def test_an_unreachable_inbox_exits_1(self):
        self.server.close()
        os.remove(self.sock_path)
        code, _, err = self.run_main("work", "other")
        self.assertEqual(code, 1)
        self.assertIn("Could not reach", err)


CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults.json")


def human(text="go on"):
    return {"type": "user", "origin": {"kind": "human"},
            "message": {"role": "user", "content": text}}


def event(ident="b1", offset=30):
    """A task notification written offset seconds from now: after the stop when positive, the
    event that started the stopping turn when negative."""
    when = datetime.fromtimestamp(time.time() + offset, timezone.utc).isoformat()
    return {"type": "user", "timestamp": when, "message": {
        "role": "user", "content": "<task-notification>\n<task-id>%s</task-id>\n"
                                   "<status>completed</status>\n" % ident}}


def reply(text="Done."):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def tool(name, input_, ident="t1"):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": ident, "name": name, "input": input_}]}}


def bash(command, ident="t1"):
    return tool("Bash", {"command": command}, ident)


def output(ident, text):
    return {"type": "user", "toolUseResult": {"stdout": text}, "message": {
        "role": "user", "content": [{"type": "tool_result", "tool_use_id": ident,
                                     "content": text}]}}


def background():
    return {"type": "user", "timestamp": datetime.now(timezone.utc).isoformat(),
            "toolUseResult": {"backgroundTaskId": "b9"}, "message": {
                "role": "user", "content": [{"type": "tool_result", "content": "started"}]}}


class Hook(Fixture):
    """session_title.py hook prompt|stop, which sets the status without the session setting it."""

    def setUp(self):
        super().setUp()
        # A session that never shows the rename costs the hook this long, so keep it short.
        patch = mock.patch.object(st, "RENAME_WAIT_SECONDS", 0.3)
        patch.start()
        self.addCleanup(patch.stop)

    def run_hook(self, name, payload, rows=(), config=CONFIG, raw=None):
        path = os.path.join(self.dir, "transcript.jsonl")
        with open(path, "w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        full = {"hook_event_name": {"prompt": "UserPromptSubmit", "stop": "Stop"}[name],
                "session_id": "s-10", "transcript_path": path}
        full.update(payload)
        stdin = io.StringIO(json.dumps(full) if raw is None else raw)
        out, err = io.StringIO(), io.StringIO()
        args = ["session_title.py"] + (["--config", config] if config else []) + ["hook", name]
        code = st.main(args, out=out, err=err, stdin=stdin)
        self.assertEqual((code, out.getvalue(), err.getvalue()), (0, "", ""))

    def expect(self, status, name, payload=None, rows=(), **kw):
        """Runs the hook and checks the status the rename asked for, None for no rename."""
        if not status:
            # The hook is synchronous, so a rename it sent is already queued on the socket.
            self.run_hook(name, payload or {}, rows, **kw)
            self.server.setblocking(False)
            self.addCleanup(self.server.setblocking, True)
            with self.assertRaises(BlockingIOError):
                self.server.accept()
            self.server.setblocking(True)
            return
        thread = self.serve()
        self.run_hook(name, payload or {}, rows, **kw)
        thread.join(5)
        self.assertEqual([m["name"] for m in self.received],
                         ["Overmind 2 - read window (%s)" % status])
        self.assertEqual(self.received[0]["session_id"], "s-10")

    def test_a_prompt_sets_working_over_any_status(self):
        for old in ("needs you", "stuck", "idle"):
            self.received.clear()
            self.write_session("Overmind 2 - read window")
            self.write_session("Overmind 2 - read window (%s)" % old)
            self.expect("working", "prompt")

    def test_a_prompt_already_working_sends_nothing(self):
        self.write_session("Overmind 2 - read window (working)")
        self.expect(None, "prompt")

    def test_a_plain_stop_is_idle(self):
        self.expect("idle", "stop", rows=[human(), reply()])

    def test_a_question_in_the_reply_needs_you(self):
        rows = [human(), reply("Which one?")]
        self.expect("needs you", "stop", {"last_assistant_message": "Which one?"}, rows)

    def test_a_question_in_the_wrap_up_box_needs_you(self):
        rows = [human(), tool("mcp__ccd_turn__wrap_up", {"ask": "Merge it?"})]
        self.expect("needs you", "stop", rows=rows)

    def test_the_review_label_needs_you(self):
        command = 'gh pr edit 5 --add-label "Ready for Review"'
        rows = [human(), bash(command), output("t1", "https://github.com/o/r/pull/5\n")]
        self.expect("needs you", "stop", rows=rows)

    def test_the_review_label_is_skipped_without_a_config(self):
        command = 'gh pr edit 5 --add-label "Ready for Review"'
        rows = [human(), bash(command), output("t1", "https://github.com/o/r/pull/5\n")]
        # A label from an earlier read of a config must not carry over to a run with none.
        with mock.patch.dict(st.hook_config._state):
            st.hook_config.use(CONFIG)
            self.expect("idle", "stop", rows=rows, config=None)

    def test_a_config_that_does_not_read_skips_the_label_and_prints_nothing(self):
        command = 'gh pr edit 5 --add-label "Ready for Review"'
        rows = [human(), bash(command), output("t1", "https://github.com/o/r/pull/5\n")]
        self.assertTrue(st._load_config(CONFIG))
        for body in ("not json", "[]", "{}", '{"reviewLabel": "Ready"}'):
            path = os.path.join(self.dir, "bad.json")
            with open(path, "w") as f:
                f.write(body)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertFalse(st._load_config(path), body)
            self.received.clear()
            self.write_session("Overmind 2 - read window")
            written = io.StringIO()
            with contextlib.redirect_stderr(written):
                self.expect("idle", "stop", rows=rows, config=path)
            self.assertEqual(written.getvalue(), "")

    def test_a_session_with_no_title_is_left_alone(self):
        self.write_session("")
        self.expect(None, "prompt")
        self.expect(None, "stop", rows=[human(), reply()])

    def test_background_work_is_working(self):
        self.expect("working", "stop", rows=[human(), bash("sleep 60"), background(), reply()])

    def test_an_event_delivered_after_the_stop_is_working(self):
        self.expect("working", "stop", rows=[human(), reply(), event()])

    def test_a_question_beats_background_work(self):
        rows = [human(), background(), reply("Ready?")]
        self.expect("needs you", "stop", {"last_assistant_message": "Ready?"}, rows)

    def test_the_stop_time_is_the_hook_processs_start(self):
        # The hook "started" five seconds ago. An event delivered since then, within the
        # slack, started a turn after the stop; one delivered before it started this one.
        now = time.time() * 1000
        with mock.patch.object(st.background_pending, "started_ms", return_value=now - 5000):
            self.expect("idle", "stop", rows=[human(), event(offset=-5.5), reply()])
            self.received.clear()
            self.write_session("Overmind 2 - read window")
            self.expect("working", "stop", rows=[human(), reply(), event(offset=-4.9)])

    def test_a_later_hook_reads_the_title_the_earlier_one_set(self):
        self.write_session("Overmind 2 - read window (idle)")
        shown = "Overmind 2 - read window (working)"

        def run():
            conn, _ = self.server.accept()
            with conn:
                json.loads(conn.makefile().readline())
            time.sleep(0.15)
            self.write_session(shown)
        threading.Thread(target=run, daemon=True).start()
        self.run_hook("prompt", {})
        # The hook came back only once the session's file read the title it set, so the next
        # hook starts from it.
        with open(os.path.join(self.sessions, "10.json")) as f:
            self.assertEqual(json.load(f)["name"], shown)

    def test_a_title_that_differs_only_in_a_number_ends_the_wait_at_once(self):
        def run():
            conn, _ = self.server.accept()
            with conn:
                json.loads(conn.makefile().readline())
            self.write_session("Overmind 2 - read window (working) 2")
        threading.Thread(target=run, daemon=True).start()
        with mock.patch.object(st, "RENAME_WAIT_SECONDS", 5):
            started = time.monotonic()
            self.run_hook("prompt", {})
        self.assertLess(time.monotonic() - started, 2)

    def test_a_prompt_that_is_an_event_leaves_the_status_alone(self):
        notice = "<task-notification>\n<task-id>b1</task-id>\n<status>completed</status>\n"
        for word in st.KEPT_ACROSS_EVENTS:
            self.write_session("Overmind 2 - read window (%s)" % word)
            self.expect(None, "prompt", {"prompt": notice})
            self.expect(None, "prompt",
                        {"prompt": "<system-reminder>x</system-reminder>" + notice})
        self.received.clear()
        self.write_session("Overmind 2 - read window (waiting on CI)")
        self.expect("working", "prompt", {"prompt": "carry on"})

    def test_a_prompt_that_is_an_event_sets_working_over_the_other_statuses(self):
        notice = "<task-notification>\n<task-id>b1</task-id>\n<status>completed</status>\n"
        for word in ("idle", "needs you", "waiting on you"):
            self.received.clear()
            self.write_session("Overmind 2 - read window (%s)" % word)
            self.expect("working", "prompt", {"prompt": notice})
        self.received.clear()
        self.write_session("Overmind 2 - read window")
        self.expect("working", "prompt", {"prompt": notice})

    def title(self, status):
        self.write_session("Overmind 2 - read window (%s)" % status)

    def sets(self, status, ident="t1"):
        return [bash('python3 x/session_title.py status "%s"' % status, ident),
                output(ident, "Overmind 2 - read window (%s)\n" % status)]

    def test_a_needs_you_set_this_turn_is_kept_at_a_stop(self):
        self.title("needs you")
        rows = [human()] + self.sets("needs you") + [reply("Please review the pull request.")]
        self.expect(None, "stop", rows=rows)
        # Also when another Stop hook blocked and the turn went on.
        self.expect(None, "stop", {"stop_hook_active": True}, rows)

    def test_a_needs_you_left_from_an_earlier_turn_is_recomputed(self):
        # A relayed message starts a turn with no prompt hook, so nothing ended the old one.
        self.title("needs you")
        rows = self.sets("needs you") + [human("Voice request: x"), reply("All done.")]
        self.expect("idle", "stop", rows=rows)
        self.received.clear()
        self.title("needs you")
        self.expect("idle", "stop", {"stop_hook_active": True}, [human(), reply("All done.")])

    def test_a_needs_you_is_recomputed_to_a_real_question(self):
        self.write_session("Overmind 2 - read window")
        self.expect("needs you", "stop", {"last_assistant_message": "Which one?"},
                    [human(), reply("Which one?")])

    def test_the_latest_status_command_of_the_turn_decides(self):
        self.title("needs you")
        rows = [human()] + self.sets("needs you") + self.sets("stuck", "t2") + [reply()]
        self.expect("idle", "stop", rows=rows)

    def test_a_status_command_that_failed_or_is_written_another_way_is_read(self):
        failed = [bash('python3 session_title.py status "needs you"'),
                  {"type": "user", "message": {"role": "user", "content": [
                      {"type": "tool_result", "tool_use_id": "t1", "is_error": True,
                       "content": "no session"}]}}]
        self.title("needs you")
        self.expect("idle", "stop", rows=[human()] + failed + [reply()])
        for command in ("cd x && python3 /a/b/session_title.py status 'needs you' && ls",
                        'python3 session_title.py status -- "needs you"'):
            self.assertEqual(st.stop_attention.status_commands([bash(command)]), ["needs you"])

    def test_a_partner_wait_ignores_a_closing_question_and_the_review_label(self):
        self.title("waiting on Data")
        rows = [human()] + self.sets("waiting on Data")
        self.expect(None, "stop", {"last_assistant_message": "Anything else?"},
                    rows + [reply("Anything else?")])
        label = [bash('gh pr edit 5 --add-label "Ready for Review"', "t9"),
                 output("t9", "https://github.com/o/r/pull/5\n")]
        self.expect(None, "stop", rows=rows + label + [reply()])
        self.expect(None, "stop", {"stop_hook_active": True}, rows + [reply()])

    def test_a_partner_wait_keeps_over_background_work(self):
        self.title("waiting on Data")
        rows = [human()] + self.sets("waiting on Data") + [background(), reply()]
        self.expect(None, "stop", rows=rows)

    def test_a_wrap_up_question_beats_a_partner_wait(self):
        self.title("waiting on Data")
        rows = [human()] + self.sets("waiting on Data") + [
            tool("mcp__ccd_turn__wrap_up", {"ask": "Merge it?"}, "t7")]
        self.expect("needs you", "stop", rows=rows)

    def test_a_partner_wait_not_set_this_turn_is_recomputed(self):
        self.title("waiting on Data")
        self.expect("idle", "stop", rows=[human(), reply()])
        self.received.clear()
        self.title("waiting on Data")
        self.expect("needs you", "stop", {"last_assistant_message": "Which one?"},
                    [human(), reply("Which one?")])

    def test_a_prompt_ends_a_partner_wait(self):
        notice = "<task-notification>\n<task-id>b1</task-id>\n<status>completed</status>\n"
        for prompt in ("carry on", notice):
            self.received.clear()
            self.title("waiting on Data")
            self.expect("working", "prompt", {"prompt": prompt})

    def test_a_status_only_the_session_can_know_is_kept_at_a_stop(self):
        for word in st.KEPT_ACROSS_EVENTS:
            for title in ("Overmind 2 - read window (%s)", "Overmind 2 (%s)",
                          "Overmind 2 - read window (%s) 2"):
                self.write_session(title % word)
                self.expect(None, "stop", rows=[human(), reply()])
                self.expect(None, "stop", {"stop_hook_active": True}, [human(), reply()])

    def test_a_status_the_hook_writes_is_replaced_at_a_stop(self):
        for word in ("working", "idle", "waiting on you"):
            self.received.clear()
            self.write_session("Overmind 2 - read window (%s)" % word)
            if word == "idle":
                self.expect(None, "stop", rows=[human(), reply()])
            else:
                self.expect("idle", "stop", rows=[human(), reply()])

    def test_a_prompt_ends_a_kept_status(self):
        for word in st.KEPT_ACROSS_EVENTS + ("needs you",):
            self.received.clear()
            self.write_session("Overmind 2 - read window (%s)" % word)
            self.expect("working", "prompt", {"prompt": "carry on"})

    def test_a_title_changed_while_the_stop_ran_is_left_alone(self):
        real = st.read_transcript

        def renamed(path):
            # The next prompt's hook renamed the session while this one read the transcript.
            self.write_session("Overmind 2 - read window (working)")
            return real(path)
        self.write_session("Overmind 2 - read window (needs you)")
        with mock.patch.object(st, "read_transcript", renamed):
            self.expect(None, "stop", rows=[human(), reply()])

    def test_a_rename_shows_when_only_the_added_number_differs(self):
        wanted = "Overmind 2 - read window (idle)"
        self.assertTrue(st.shows_rename(wanted, wanted))
        self.assertTrue(st.shows_rename("Overmind 2 - read window (idle) 2", wanted))
        self.assertTrue(st.shows_rename("Overmind 2 (idle)", "Overmind 2 (idle)"))
        self.assertFalse(st.shows_rename("Overmind 2 - read window (working)", wanted))
        self.assertFalse(st.shows_rename("Overmind 2 - other work (idle)", wanted))

    def test_a_stop_with_no_transcript_leaves_the_title_alone(self):
        self.expect(None, "stop", {"transcript_path": "/no/such/file"})
        self.expect(None, "stop", rows=[])

    def test_a_subagent_or_another_event_or_session_does_nothing(self):
        rows = [human(), reply()]
        self.expect(None, "stop", {"agent_id": "a1"}, rows)
        self.expect(None, "stop", {"hook_event_name": "SubagentStop"}, rows)
        self.expect(None, "prompt", {"hook_event_name": "Stop"})
        self.expect(None, "stop", {"session_id": "other"}, rows)

    def test_the_work_name_is_never_changed(self):
        self.write_session("Overmind 2 - issue #9 other (working)")
        thread = self.serve()
        self.run_hook("stop", {}, [human(), reply()])
        thread.join(5)
        self.assertEqual(self.received[0]["name"], "Overmind 2 - issue #9 other (idle)")

    def test_every_failure_exits_0_without_a_word(self):
        self.run_hook("stop", {}, raw="not json")
        self.run_hook("stop", {}, raw="[]")
        self.run_hook("stop", {"transcript_path": "/no/such/file"})
        self.run_hook("stop", {}, [human(), reply()], config="/no/such/config.json")
        with mock.patch.dict(os.environ, {"SESSION_TITLE_PID": "999"}):
            self.run_hook("stop", {}, [human(), reply()])
        # The session's inbox is gone.
        self.server.close()
        os.remove(self.sock_path)
        self.run_hook("stop", {}, [human(), reply()])
        self.run_hook("prompt", {})

    def test_config_before_the_other_commands_is_accepted(self):
        thread = self.serve()
        code, _, _ = self.run_main("--config", CONFIG, "status", "stuck")
        thread.join(5)
        self.assertEqual(code, 0)
        self.assertEqual(self.received[0]["name"], "Overmind 2 - read window (stuck)")


if __name__ == "__main__":
    unittest.main()
