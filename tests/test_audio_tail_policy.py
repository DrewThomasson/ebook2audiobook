"""Dependency-light regression tests for the shared audio tail policy."""

import ast
import pathlib
import unittest


def _load_policy_helpers():
    source_path = pathlib.Path(__file__).parents[1] / "lib/classes/tts_engines/common/audio.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    wanted = {"NATURAL_TAIL_TARGET_SEC", "NATURAL_TAIL_MAX_SEC", "_bounded_natural_tail_sec", "_trimmed_end_index"}
    nodes = []
    for node in tree.body:
        name = getattr(node, "name", None)
        if name in wanted:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(getattr(target, "id", None) in wanted for target in node.targets):
            nodes.append(node)
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


class AudioTailPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = _load_policy_helpers()

    def test_tail_buffer_is_at_least_natural_target_and_capped(self):
        bounded = self.policy["_bounded_natural_tail_sec"]
        self.assertEqual(bounded(0.002), 0.020)
        self.assertEqual(bounded(0.035), 0.035)
        self.assertEqual(bounded(0.100), 0.050)

    def test_end_boundary_includes_last_audible_sample(self):
        end_index = self.policy["_trimmed_end_index"]
        self.assertEqual(end_index(7, 20, 1, 0.0), 8)

    def test_end_boundary_is_clamped_to_audio_length(self):
        end_index = self.policy["_trimmed_end_index"]
        self.assertEqual(end_index(990, 1000, 24000, 0.006), 1000)


if __name__ == "__main__":
    unittest.main()
