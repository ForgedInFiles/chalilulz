"""
test_api — API calling functions with mocked HTTP requests
"""

import unittest
import sys
import os
import json
import urllib.error
from unittest.mock import patch, MagicMock
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import (
    call_openrouter,
    call_ollama,
    call_mistral,
    call_groq,
    call_gemini,
    call_api,
    ACTUAL_MODEL,
    PROVIDER,
    NO_TOOLS_MODELS,
    SCHEMA,
)


class FakeHTTPResponse:
    def __init__(self, data, status=200):
        self.data = json.dumps(data).encode()
        self.status = status
        self._reason = "OK"

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def info(self):
        return {}


def make_http_error(code, data):
    return urllib.error.HTTPError(
        "http://test", code, "Error", {}, BytesIO(json.dumps(data).encode())
    )


def mock_urlopen_success(response_data):
    def _mock(req, timeout=None):
        return FakeHTTPResponse(response_data)

    return _mock


def mock_urlopen_error(code, error_data):
    def _mock(req, timeout=None):
        raise make_http_error(code, error_data)

    return _mock


class TestOpenRouterAPI(unittest.TestCase):
    def setUp(self):
        import chalilulz

        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL
        self.orig_PROVIDER = chalilulz.PROVIDER

    def tearDown(self):
        import chalilulz

        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL
        chalilulz.PROVIDER = self.orig_PROVIDER

    @patch("urllib.request.urlopen")
    def test_call_openrouter_success(self, mock_urlopen):
        mock_urlopen.side_effect = mock_urlopen_success(
            {
                "choices": [{"message": {"content": "Hello"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        )
        # Need to set global ACTUAL_MODEL
        import chalilulz

        chalilulz.ACTUAL_MODEL = "test-model"
        chalilulz.PROVIDER = "openrouter"
        result = call_openrouter([], "System")
        self.assertIsInstance(result, tuple)
        resp, use_tools = result
        self.assertIn("choices", resp)
        self.assertTrue(use_tools)  # Tools supported by default

    @patch("urllib.request.urlopen")
    def test_call_openrouter_with_tools(self, mock_urlopen):
        mock_urlopen.side_effect = mock_urlopen_success(
            {
                "choices": [{"message": {"content": "", "tool_calls": []}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 0},
            }
        )
        import chalilulz

        chalilulz.ACTUAL_MODEL = "test-model"
        chalilulz.PROVIDER = "openrouter"
        # Ensure SCHEMA is defined
        self.assertIsNotNone(SCHEMA)
        result = call_openrouter([], "System")
        resp, use_tools = result
        self.assertTrue(use_tools)

    @patch("urllib.request.urlopen")
    def test_call_openrouter_error_400(self, mock_urlopen):
        mock_urlopen.side_effect = mock_urlopen_error(
            400, {"error": {"message": "Bad request"}}
        )
        import chalilulz

        chalilulz.ACTUAL_MODEL = "test-model"
        chalilulz.PROVIDER = "openrouter"
        # Should fall back to XML mode on 400
        with self.assertRaises(RuntimeError):
            call_openrouter([], "System", force_no_tools=True)


class TestOllamaAPI(unittest.TestCase):
    def setUp(self):
        import chalilulz

        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL
        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_OLLAMA_HOST = chalilulz.OLLAMA_HOST

    def tearDown(self):
        import chalilulz

        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL
        chalilulz.PROVIDER = self.orig_PROVIDER
        chalilulz.OLLAMA_HOST = self.orig_OLLAMA_HOST

    @patch("urllib.request.urlopen")
    def test_call_ollama_success(self, mock_urlopen):
        mock_urlopen.side_effect = mock_urlopen_success(
            {
                "message": {"content": "Hello from Ollama"},
                "prompt_eval_count": 5,
                "eval_count": 10,
            }
        )
        import chalilulz

        chalilulz.ACTUAL_MODEL = "mistral:latest"
        chalilulz.PROVIDER = "ollama"
        chalilulz.OLLAMA_HOST = "http://localhost:11434"
        result = call_ollama([], "System")
        resp, use_tools = result
        self.assertIn("choices", resp)
        self.assertEqual(resp["choices"][0]["message"]["content"], "Hello from Ollama")


class TestOpenAICompatible(unittest.TestCase):
    def setUp(self):
        import chalilulz

        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL
        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_MISTRAL_KEY = chalilulz.MISTRAL_KEY
        self.orig_GROQ_KEY = chalilulz.GROQ_KEY
        self.orig_GEMINI_KEY = chalilulz.GEMINI_KEY

    def tearDown(self):
        import chalilulz

        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL
        chalilulz.PROVIDER = self.orig_PROVIDER
        chalilulz.MISTRAL_KEY = self.orig_MISTRAL_KEY
        chalilulz.GROQ_KEY = self.orig_GROQ_KEY
        chalilulz.GEMINI_KEY = self.orig_GEMINI_KEY

    @patch("urllib.request.urlopen")
    def test_call_mistral_success(self, mock_urlopen):
        mock_urlopen.side_effect = mock_urlopen_success(
            {
                "choices": [{"message": {"content": "Mistral here"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 7},
            }
        )
        import chalilulz

        chalilulz.ACTUAL_MODEL = "mistral-small-latest"
        chalilulz.PROVIDER = "mistral"
        chalilulz.MISTRAL_KEY = "dummy-key"
        result = call_mistral([], "System")
        resp, use_tools = result
        self.assertEqual(resp["choices"][0]["message"]["content"], "Mistral here")

    @patch("urllib.request.urlopen")
    def test_call_gemini_with_correct_header(self, mock_urlopen):
        mock_urlopen.side_effect = mock_urlopen_success(
            {
                "choices": [{"message": {"content": "Gemini here"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 4},
            }
        )
        import chalilulz

        chalilulz.ACTUAL_MODEL = "gemini-2.0-flash"
        chalilulz.PROVIDER = "gemini"
        chalilulz.GEMINI_KEY = "google-key"
        result = call_gemini([], "System")
        resp, use_tools = result
        self.assertEqual(resp["choices"][0]["message"]["content"], "Gemini here")
        # Check that the request had x-goog-api-key header (case-insensitive)
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        headers_lower = {k.lower(): v for k, v in req.headers.items()}
        self.assertIn("x-goog-api-key", headers_lower)
        self.assertEqual(headers_lower["x-goog-api-key"], "google-key")


class TestCallAPIDispatcher(unittest.TestCase):
    def setUp(self):
        import chalilulz

        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL

    def tearDown(self):
        import chalilulz

        chalilulz.PROVIDER = self.orig_PROVIDER
        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL

    @patch("chalilulz.call_ollama")
    def test_dispatcher_ollama(self, mock_ollama):
        import chalilulz

        chalilulz.PROVIDER = "ollama"
        mock_ollama.return_value = ({"choices": []}, False)
        result = call_api([], "System")
        mock_ollama.assert_called_once()

    @patch("chalilulz.call_openrouter")
    def test_dispatcher_openrouter(self, mock_openrouter):
        import chalilulz

        chalilulz.PROVIDER = "openrouter"
        mock_openrouter.return_value = ({"choices": []}, False)
        result = call_api([], "System")
        mock_openrouter.assert_called_once()

    @patch("chalilulz.call_mistral")
    def test_dispatcher_mistral(self, mock_mistral):
        import chalilulz

        chalilulz.PROVIDER = "mistral"
        mock_mistral.return_value = ({"choices": []}, False)
        result = call_api([], "System")
        mock_mistral.assert_called_once()

    @patch("chalilulz.call_groq")
    def test_dispatcher_groq(self, mock_groq):
        import chalilulz

        chalilulz.PROVIDER = "groq"
        mock_groq.return_value = ({"choices": []}, False)
        result = call_api([], "System")
        mock_groq.assert_called_once()

    @patch("chalilulz.call_gemini")
    def test_dispatcher_gemini(self, mock_gemini):
        import chalilulz

        chalilulz.PROVIDER = "gemini"
        mock_gemini.return_value = ({"choices": []}, False)
        result = call_api([], "System")
        mock_gemini.assert_called_once()

    def test_dispatcher_unknown(self):
        import chalilulz

        chalilulz.PROVIDER = "unknown"
        with self.assertRaises(RuntimeError):
            call_api([], "System")


class TestNoToolsModels(unittest.TestCase):
    def setUp(self):
        import chalilulz

        self.original = chalilulz.NO_TOOLS_MODELS.copy()
        chalilulz.NO_TOOLS_MODELS.clear()

    def tearDown(self):
        import chalilulz

        chalilulz.NO_TOOLS_MODELS.clear()
        chalilulz.NO_TOOLS_MODELS.update(self.original)

    @patch("urllib.request.urlopen")
    def test_ollama_fallback_on_400(self, mock_urlopen):
        # Simulate 400 error on first call, then success on retry
        call_count = 0

        def side_effect(req, timeout=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise make_http_error(400, {"error": {"message": "no tools"}})
            else:
                return FakeHTTPResponse(
                    {
                        "message": {"content": "Fallback worked"},
                        "prompt_eval_count": 1,
                        "eval_count": 5,
                    }
                )

        mock_urlopen.side_effect = side_effect

        import chalilulz

        chalilulz.ACTUAL_MODEL = "test-model"
        chalilulz.PROVIDER = "ollama"
        resp, use_tools = call_ollama([], "System")
        self.assertIn(resp["choices"][0]["message"]["content"], "Fallback worked")
        self.assertIn(chalilulz.ACTUAL_MODEL, chalilulz.NO_TOOLS_MODELS)


if __name__ == "__main__":
    unittest.main()
