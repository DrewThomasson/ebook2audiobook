#!/usr/bin/env python3
"""Cases for sessions.py. usage: python3 sessions_test.py"""
import json
import os
import tempfile
import unittest

import sessions


class ListSessions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, "sessions")
        self.proc = os.path.join(self.tmp.name, "proc")
        os.mkdir(self.dir)
        os.mkdir(self.proc)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, pid, alive=True, **fields):
        entry = {"pid": pid, "sessionId": "id-%d" % pid, "name": "S%d" % pid, "cwd": "/x/app",
                 "kind": "interactive", "status": "idle", "messagingSocketPath": "/s/%d.sock" % pid}
        entry.update(fields)
        with open(os.path.join(self.dir, "%d.json" % pid), "w") as f:
            json.dump(entry, f)
        if alive:
            os.mkdir(os.path.join(self.proc, str(pid)))

    def listed(self):
        return sessions.list_sessions(self.dir, self.proc)

    def test_stale_process_is_skipped(self):
        self.add(10)
        self.add(11, alive=False)
        self.assertEqual([s["pid"] for s in self.listed()], [10])

    def test_background_and_busy_are_marked(self):
        self.add(10, kind="bg", status="busy")
        s = self.listed()[0]
        self.assertTrue(s["background"])
        self.assertTrue(s["busy"])

    def test_other_kinds_and_socketless_entries_are_skipped(self):
        self.add(10, kind="daemon")
        self.add(11, messagingSocketPath="")
        self.assertEqual(self.listed(), [])

    def test_duplicate_names_are_numbered_in_pid_order(self):
        self.add(30, name="Overmind")
        self.add(20, name="overmind")
        self.add(40, name="Overmind")
        self.assertEqual([s["name"] for s in self.listed()], ["overmind", "Overmind 2", "Overmind 3"])

    def test_status_suffix_is_stripped_before_numbering(self):
        self.add(10, name="Merge")
        self.add(11, name="Merge (idle)")
        self.add(12, name="Ship (stuck) 2")
        self.assertEqual([s["name"] for s in self.listed()], ["Merge", "Merge 2", "Ship 2"])

    def test_a_number_another_session_holds_is_skipped(self):
        self.add(10, name="Merge")
        self.add(11, name="Merge (idle)")
        self.add(12, name="Merge (idle) 2")
        self.assertEqual([s["name"] for s in self.listed()], ["Merge", "Merge 3", "Merge 2"])

    def test_blank_name_falls_back_to_folder(self):
        self.add(10, name=" ", cwd="/home/me/widget")
        self.assertEqual(self.listed()[0]["name"], "widget")

    def test_key_files_are_never_opened(self):
        self.add(10)
        fifo = os.path.join(self.dir, "10.key")
        os.mkfifo(fifo)  # opening it for reading would block forever
        self.assertEqual(len(self.listed()), 1)

    def test_missing_folder_is_empty(self):
        self.assertEqual(sessions.list_sessions(os.path.join(self.dir, "none"), self.proc), [])


class FindSession(unittest.TestCase):
    ALL = [{"id": "abc-1", "name": "Overmind"}, {"id": "abd-2", "name": "Overmind 2"},
           {"id": "xyz-3", "name": "Conky widget"}]

    def test_by_id_prefix_name_and_part(self):
        self.assertEqual(sessions.find_session(self.ALL, "xyz-3")["name"], "Conky widget")
        self.assertEqual(sessions.find_session(self.ALL, "abc")["id"], "abc-1")
        self.assertEqual(sessions.find_session(self.ALL, "overmind 2")["id"], "abd-2")
        self.assertEqual(sessions.find_session(self.ALL, "conky")["id"], "xyz-3")

    def test_ambiguous_and_unknown_raise(self):
        with self.assertRaises(LookupError):
            sessions.find_session(self.ALL, "ab")
        with self.assertRaises(LookupError):
            sessions.find_session(self.ALL, "nothing")


if __name__ == "__main__":
    unittest.main()
