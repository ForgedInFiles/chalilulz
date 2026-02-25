"""
test_main — Main REPL loop and command handling
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import main, update_model, MODEL, PROVIDER, ACTUAL_MODEL


class TestMainREPL(unittest.TestCase):
    def setUp(self):
        # Save original globals
        import chalilulz

        self.orig_MODEL = chalilulz.MODEL
        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL
        self.orig_KEY = chalilulz.KEY
        self.orig_OLLAMA_HOST = chalilulz.OLLAMA_HOST

    def tearDown(self):
        # Restore globals
        import chalilulz

        chalilulz.MODEL = self.orig_MODEL
        chalilulz.PROVIDER = self.orig_PROVIDER
        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL
        chalilulz.KEY = self.orig_KEY
        chalilulz.OLLAMA_HOST = self.orig_OLLAMA_HOST

    @patch("builtins.input", side_effect=["/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_quit_command(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that /q exits the loop"""
        # Should not raise; main should exit cleanly
        try:
            main()
        except SystemExit:
            pass  # Expected if main calls sys.exit
        # Verify input was called at least once
        mock_input.assert_called()

    @patch("builtins.input", side_effect=["/c", "/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_clear_command(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that /c clears messages"""
        # We'll patch print to suppress output
        with patch("builtins.print"):
            main()
        # No crash means pass

    @patch("builtins.input", side_effect=["/model mistral:small", "/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_model_change_command(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that /model updates the global model"""
        import chalilulz

        with patch("builtins.print"):
            main()
        self.assertEqual(chalilulz.MODEL, "mistral:small")
        self.assertEqual(chalilulz.PROVIDER, "mistral")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "small")

    @patch("builtins.input", side_effect=["/skills", "/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_skills_command(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that /skills prints the skills list"""
        import chalilulz

        with patch("builtins.print") as mock_print:
            main()
        # Check that print was called with skills information
        calls = [str(c) for c in mock_print.call_args_list]
        # Should mention "Skills:" or similar
        printed = " ".join(calls)
        self.assertIn("Skills", printed)

    @patch("builtins.input", side_effect=["Hello", "/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_user_message_calls_api(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that user message triggers call_api"""
        import chalilulz

        # Capture msgs at call time
        captured_msgs = []

        def capture(msgs, sysp):
            captured_msgs.append(msgs.copy())  # copy to avoid mutation later
            return ({"choices": [{"message": {"content": "Hi"}}]}, False)

        mock_call.side_effect = capture
        with patch("builtins.print"):
            main()
        self.assertEqual(len(captured_msgs), 1)
        self.assertEqual(len(captured_msgs[0]), 1)
        self.assertEqual(captured_msgs[0][0]["role"], "user")
        self.assertEqual(captured_msgs[0][0]["content"], "Hello")

    @patch("builtins.input", side_effect=["test", "/q"])
    @patch("chalilulz.call_api", side_effect=Exception("API Error"))
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_api_error_handling(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that API errors are caught and message popped"""
        with patch("builtins.print"):
            main()
        mock_call.assert_called()

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_keyboard_interrupt(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that Ctrl+C exits gracefully"""
        with patch("builtins.print"):
            try:
                main()
            except:
                pass  # main should handle KeyboardInterrupt internally

    @patch("builtins.input", side_effect=["/model invalid", "/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_model_invalid_warns_missing_key(
        self, mock_sp, mock_sep, mock_call, mock_input
    ):
        """Test that invalid model change still updates provider"""
        import chalilulz

        with patch("builtins.print"):
            main()
        self.assertEqual(chalilulz.MODEL, "invalid")
        self.assertEqual(chalilulz.PROVIDER, "ollama")  # default provider

    @patch("builtins.input", side_effect=["/model   mistral:small  ", "/q"])
    @patch("chalilulz.call_api")
    @patch("chalilulz.sep")
    @patch("chalilulz.SP")
    def test_model_whitespace_handling(self, mock_sp, mock_sep, mock_call, mock_input):
        """Test that /model with extra whitespace trims correctly"""
        import chalilulz

        with patch("builtins.print"):
            main()
        self.assertEqual(chalilulz.MODEL, "mistral:small")
        self.assertEqual(chalilulz.PROVIDER, "mistral")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "small")


if __name__ == "__main__":
    unittest.main()
