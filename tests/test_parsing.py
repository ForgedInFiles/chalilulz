"""
test_parsing — Model parsing, provider detection, and key management
"""

import unittest
import sys
import os

# Add parent directory to path to import chalilulz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import (
    parse_model,
    update_model,
    get_required_key,
    MODEL,
    PROVIDER,
    ACTUAL_MODEL,
    MISTRAL_KEY,
    GROQ_KEY,
    GEMINI_KEY,
    KEY,
)


class TestModelParsing(unittest.TestCase):
    def test_parse_ollama_default(self):
        provider, model_id = parse_model("ministral-3:latest")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model_id, "ministral-3:latest")

    def test_parse_ollama_without_tag(self):
        provider, model_id = parse_model("llama2")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model_id, "llama2")

    def test_parse_ollama_explicit(self):
        provider, model_id = parse_model("ollama:mistral")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model_id, "mistral")

    def test_parse_mistral(self):
        provider, model_id = parse_model("mistral:mistral-small-latest")
        self.assertEqual(provider, "mistral")
        self.assertEqual(model_id, "mistral-small-latest")

    def test_parse_groq(self):
        provider, model_id = parse_model("groq:llama-3.3-70b-versatile")
        self.assertEqual(provider, "groq")
        self.assertEqual(model_id, "llama-3.3-70b-versatile")

    def test_parse_gemini(self):
        provider, model_id = parse_model("gemini:gemini-2.0-flash")
        self.assertEqual(provider, "gemini")
        self.assertEqual(model_id, "gemini-2.0-flash")

    def test_parse_openrouter(self):
        provider, model_id = parse_model(
            "openrouter:arcee-ai/trinity-large-preview:free"
        )
        self.assertEqual(provider, "openrouter")
        self.assertEqual(model_id, "arcee-ai/trinity-large-preview:free")

    def test_parse_unknown_provider_defaults_to_ollama(self):
        provider, model_id = parse_model("some-random-model")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model_id, "some-random-model")


class TestUpdateModel(unittest.TestCase):
    def setUp(self):
        # Save original globals
        import chalilulz

        self.orig_MODEL = chalilulz.MODEL
        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL

    def tearDown(self):
        # Restore original globals
        import chalilulz

        chalilulz.MODEL = self.orig_MODEL
        chalilulz.PROVIDER = self.orig_PROVIDER
        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL

    def test_update_model_ollama(self):
        import chalilulz

        chalilulz.update_model("mistral:7b")
        self.assertEqual(chalilulz.MODEL, "mistral:7b")
        self.assertEqual(chalilulz.PROVIDER, "mistral")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "7b")

    def test_update_model_groq(self):
        import chalilulz

        chalilulz.update_model("groq:gemma2-9b-it")
        self.assertEqual(chalilulz.MODEL, "groq:gemma2-9b-it")
        self.assertEqual(chalilulz.PROVIDER, "groq")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "gemma2-9b-it")

    def test_update_model_default_ollama(self):
        import chalilulz

        chalilulz.update_model("llama2")
        self.assertEqual(chalilulz.MODEL, "llama2")
        self.assertEqual(chalilulz.PROVIDER, "ollama")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "llama2")


class TestGetRequiredKey(unittest.TestCase):
    def test_ollama_no_key(self):
        self.assertIsNone(get_required_key("ollama"))

    def test_mistral_requires_key(self):
        # Even if empty, it returns the key variable (which may be empty string)
        key = get_required_key("mistral")
        self.assertIsNotNone(key)
        self.assertIsInstance(key, str)

    def test_groq_requires_key(self):
        key = get_required_key("groq")
        self.assertIsNotNone(key)
        self.assertIsInstance(key, str)

    def test_gemini_requires_key(self):
        key = get_required_key("gemini")
        self.assertIsNotNone(key)
        self.assertIsInstance(key, str)

    def test_openrouter_requires_key(self):
        key = get_required_key("openrouter")
        self.assertIsNotNone(key)
        self.assertIsInstance(key, str)

    def test_unknown_provider(self):
        key = get_required_key("unknown")
        self.assertIsNone(key)


class TestDefaultProvider(unittest.TestCase):
    def test_default_model_uses_openrouter_prefix(self):
        # Reload chalilulz to get fresh defaults unaffected by other tests
        import importlib
        import chalilulz

        importlib.reload(chalilulz)
        # When imported as module (not __main__), defaults should be OpenRouter
        self.assertTrue(chalilulz.MODEL.startswith("openrouter:"))
        self.assertEqual(chalilulz.PROVIDER, "openrouter")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "arcee-ai/trinity-large-preview:free")


if __name__ == "__main__":
    unittest.main()
