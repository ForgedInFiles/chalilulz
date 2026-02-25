"""
test_do_tool_calls — Tool call execution and response handling
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import _do_tool_calls, SCHEMA, ACTUAL_MODEL, PROVIDER


class TestDoToolCalls(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        import chalilulz

        # Save original globals
        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL
        # Set up a known tool call
        self.msgs = []
        self.tool_call = {
            "function": {
                "name": "read",
                "arguments": json.dumps({"path": "/etc/hosts"}),
            },
            "id": "call_123",
        }

    def tearDown(self):
        import chalilulz

        chalilulz.PROVIDER = self.orig_PROVIDER
        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL

    def test_xml_mode_always_same(self):
        xml_call = {"name": "ls", "args": {"path": "/tmp"}}
        results = _do_tool_calls([xml_call], self.msgs, xml_mode=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["role"], "user")
        self.assertIn("<tool_result>", results[0]["content"])

    def test_openai_format_uses_tool_call_id(self):
        import chalilulz

        chalilulz.PROVIDER = "groq"  # any non-ollama
        chalilulz.ACTUAL_MODEL = "test-model"
        results = _do_tool_calls([self.tool_call], self.msgs, xml_mode=False)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["role"], "tool")
        self.assertIn("tool_call_id", results[0])
        self.assertEqual(results[0]["tool_call_id"], "call_123")

    def test_ollama_format_uses_tool_name(self):
        import chalilulz

        chalilulz.PROVIDER = "ollama"
        chalilulz.ACTUAL_MODEL = "mistral:latest"
        results = _do_tool_calls([self.tool_call], self.msgs, xml_mode=False)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["role"], "tool")
        self.assertIn("tool_name", results[0])
        self.assertEqual(results[0]["tool_name"], "read")
        self.assertNotIn("tool_call_id", results[0])

    def test_msgs_extended(self):
        import chalilulz

        chalilulz.PROVIDER = "groq"
        chalilulz.ACTUAL_MODEL = "test-model"
        initial_len = len(self.msgs)
        _do_tool_calls([self.tool_call], self.msgs, xml_mode=False)
        self.assertEqual(len(self.msgs), initial_len + 1)
        self.assertEqual(self.msgs[-1]["role"], "tool")


if __name__ == "__main__":
    unittest.main()
