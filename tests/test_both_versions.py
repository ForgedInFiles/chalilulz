"""
test_both_versions — Comprehensive tests for both chalilulz.py and chalminilulz.py
Run with: python -m unittest tests.test_both_versions -v
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
import pathlib
import urllib.error
from io import BytesIO
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "golfed"),
)

import chalilulz
import chalminilulz


def get_module_functions(module):
    """Extract all relevant functions from a module for testing."""
    return {
        "_r": getattr(module, "_r", None),
        "_w": getattr(module, "_w", None),
        "_e": getattr(module, "_e", None),
        "_gl": getattr(module, "_gl", None),
        "_gp": getattr(module, "_gp", None),
        "_b": getattr(module, "_b", None),
        "_ls": getattr(module, "_ls", None),
        "_mk": getattr(module, "_mk", None),
        "_rm": getattr(module, "_rm", None),
        "_mv": getattr(module, "_mv", None),
        "_cp": getattr(module, "_cp", None),
        "_fd": getattr(module, "_fd", None),
        "_sk": getattr(module, "_sk", None),
        "TOOLS": getattr(module, "TOOLS", None),
        "SCHEMA": getattr(module, "SCHEMA", None),
        "parse_model": getattr(module, "parse_model", None),
        "update_model": getattr(module, "update_model", None),
        "get_required_key": getattr(module, "get_required_key", None),
        "run_tool": getattr(module, "run_tool", None),
        "call_openrouter": getattr(module, "call_openrouter", None),
        "call_ollama": getattr(module, "call_ollama", None),
        "call_api": getattr(module, "call_api", None),
        "load_skills": getattr(module, "load_skills", None),
        "skills_prompt": getattr(module, "skills_prompt", None),
        "mk_schema": getattr(module, "mk_schema", None),
        "MODEL": getattr(module, "MODEL", None),
        "PROVIDER": getattr(module, "PROVIDER", None),
        "ACTUAL_MODEL": getattr(module, "ACTUAL_MODEL", None),
        "KEY": getattr(module, "KEY", None),
    }


class FakeHTTPResponse:
    def __init__(self, data, status=200):
        self.data = json.dumps(data).encode()
        self.status = status

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def make_mock_urlopen(response_data):
    def _mock(req, timeout=None):
        return FakeHTTPResponse(response_data)

    return _mock


def make_mock_urlopen_error(code, error_data):
    def _mock(req, timeout=None):
        raise urllib.error.HTTPError(
            "http://test", code, "Error", {}, BytesIO(json.dumps(error_data).encode())
        )

    return _mock


class TestBothVersionsTools(unittest.TestCase):
    """Test that both versions have identical tool functions."""

    def test_tools_have_same_keys(self):
        chalilulz_keys = set(chalilulz.TOOLS.keys())
        chalminilulz_keys = set(chalminilulz.TOOLS.keys())
        self.assertEqual(
            chalilulz_keys,
            chalminilulz_keys,
            "Both versions should have the same tool keys",
        )

    def test_tools_descriptions_match(self):
        for key in chalilulz.TOOLS:
            self.assertEqual(
                chalilulz.TOOLS[key][0],
                chalminilulz.TOOLS[key][0],
                f"Tool '{key}' should have same description in both versions",
            )

    def test_tools_parameters_match(self):
        for key in chalilulz.TOOLS:
            self.assertEqual(
                chalilulz.TOOLS[key][1],
                chalminilulz.TOOLS[key][1],
                f"Tool '{key}' should have same parameters in both versions",
            )

    def test_schema_is_identical(self):
        self.assertEqual(
            json.dumps(chalilulz.SCHEMA, sort_keys=True),
            json.dumps(chalminilulz.SCHEMA, sort_keys=True),
            "SCHEMA should be identical in both versions",
        )


class TestBothVersionsRead(unittest.TestCase):
    """Test read tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_chalilulz(self):
        result = chalilulz._r({"path": self.test_file})
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)
        self.assertRegex(result, r"^\s*\d+│")

    def test_read_chalminilulz(self):
        result = chalminilulz._r({"path": self.test_file})
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)
        self.assertRegex(result, r"^\s*\d+│")

    def test_read_offset_limit_chalilulz(self):
        result = chalilulz._r({"path": self.test_file, "offset": 1, "limit": 1})
        self.assertIn("Line 2", result)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 1)

    def test_read_offset_limit_chalminilulz(self):
        result = chalminilulz._r({"path": self.test_file, "offset": 1, "limit": 1})
        self.assertIn("Line 2", result)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 1)

    def test_read_missing_file_chalilulz(self):
        result = chalilulz._r({"path": "/nonexistent/file.txt"})
        self.assertTrue(result.startswith("error:"))

    def test_read_missing_file_chalminilulz(self):
        result = chalminilulz._r({"path": "/nonexistent/file.txt"})
        self.assertTrue(result.startswith("error:"))


class TestBothVersionsWrite(unittest.TestCase):
    """Test write tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_chalilulz(self):
        filepath = os.path.join(self.test_dir, "new.txt")
        result = chalilulz._w({"path": filepath, "content": "Hello World"})
        self.assertIn("wrote", result)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), "Hello World")

    def test_write_chalminilulz(self):
        filepath = os.path.join(self.test_dir, "new.txt")
        result = chalminilulz._w({"path": filepath, "content": "Hello World"})
        self.assertIn("wrote", result)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), "Hello World")

    def test_write_auto_mkdir_chalilulz(self):
        nested = os.path.join(self.test_dir, "a/b/c/file.txt")
        result = chalilulz._w({"path": nested, "content": "nested"})
        self.assertIn("wrote", result)
        self.assertTrue(os.path.exists(nested))

    def test_write_auto_mkdir_chalminilulz(self):
        nested = os.path.join(self.test_dir, "a/b/c/file.txt")
        result = chalminilulz._w({"path": nested, "content": "nested"})
        self.assertIn("wrote", result)
        self.assertTrue(os.path.exists(nested))


class TestBothVersionsEdit(unittest.TestCase):
    """Test edit tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "edit.txt")
        with open(self.test_file, "w") as f:
            f.write("Hello World\nTest\nHello World\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_edit_simple_chalilulz(self):
        result = chalilulz._e({"path": self.test_file, "old": "Test", "new": "Hi"})
        self.assertIn("ok", result)
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertIn("Hi\n", content)

    def test_edit_simple_chalminilulz(self):
        result = chalminilulz._e({"path": self.test_file, "old": "Test", "new": "Hi"})
        self.assertIn("ok", result)
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertIn("Hi\n", content)

    def test_edit_multiple_hits_chalilulz(self):
        result = chalilulz._e(
            {"path": self.test_file, "old": "Hello World", "new": "Hi"}
        )
        self.assertTrue("error:" in result and "hits" in result)

    def test_edit_multiple_hits_chalminilulz(self):
        result = chalminilulz._e(
            {"path": self.test_file, "old": "Hello World", "new": "Hi"}
        )
        self.assertTrue("error:" in result and "hits" in result)

    def test_edit_all_chalilulz(self):
        result = chalilulz._e(
            {"path": self.test_file, "old": "Hello World", "new": "Hi", "all": True}
        )
        self.assertIn("ok(2", result)
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content.count("Hi"), 2)

    def test_edit_all_chalminilulz(self):
        result = chalminilulz._e(
            {"path": self.test_file, "old": "Hello World", "new": "Hi", "all": True}
        )
        self.assertIn("ok(2", result)
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content.count("Hi"), 2)


class TestBothVersionsGlob(unittest.TestCase):
    """Test glob tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        pathlib.Path(os.path.join(self.test_dir, "a.txt")).touch()
        pathlib.Path(os.path.join(self.test_dir, "b.py")).touch()
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        pathlib.Path(os.path.join(subdir, "c.txt")).touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_glob_chalilulz(self):
        result = chalilulz._gl({"pat": "*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertGreater(len(files), 0)
        self.assertTrue(all(f.endswith(".txt") for f in files))

    def test_glob_chalminilulz(self):
        result = chalminilulz._gl({"pat": "*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertGreater(len(files), 0)
        self.assertTrue(all(f.endswith(".txt") for f in files))

    def test_glob_recursive_chalilulz(self):
        result = chalilulz._gl({"pat": "**/*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertGreaterEqual(len(files), 2)

    def test_glob_recursive_chalminilulz(self):
        result = chalminilulz._gl({"pat": "**/*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertGreaterEqual(len(files), 2)


class TestBothVersionsGrep(unittest.TestCase):
    """Test grep tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        with open(self.test_file, "w") as f:
            f.write("def hello():\n    return 'world'\nimport os\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_grep_chalilulz(self):
        result = chalilulz._gp({"pat": "def ", "path": self.test_dir})
        self.assertIn("test.py", result)
        self.assertIn("def hello", result)

    def test_grep_chalminilulz(self):
        result = chalminilulz._gp({"pat": "def ", "path": self.test_dir})
        self.assertIn("test.py", result)
        self.assertIn("def hello", result)

    def test_grep_not_found_chalilulz(self):
        result = chalilulz._gp({"pat": "nonexistent", "path": self.test_dir})
        self.assertEqual(result.strip(), "none")

    def test_grep_not_found_chalminilulz(self):
        result = chalminilulz._gp({"pat": "nonexistent", "path": self.test_dir})
        self.assertEqual(result.strip(), "none")


class TestBothVersionsBash(unittest.TestCase):
    """Test bash tool in both versions."""

    def test_bash_chalilulz(self):
        result = chalilulz._b({"cmd": "echo 'Hello'"})
        self.assertIn("Hello", result)
        self.assertIn("[exit 0]", result)

    def test_bash_chalminilulz(self):
        result = chalminilulz._b({"cmd": "echo 'Hello'"})
        self.assertIn("Hello", result)
        self.assertIn("[exit 0]", result)

    def test_bash_error_chalilulz(self):
        import sys

        cmd = f'"{sys.executable}" -c "import sys; sys.exit(1)"'
        result = chalilulz._b({"cmd": cmd})
        self.assertIn("[exit 1]", result)

    def test_bash_error_chalminilulz(self):
        import sys

        cmd = f'"{sys.executable}" -c "import sys; sys.exit(1)"'
        result = chalminilulz._b({"cmd": cmd})
        self.assertIn("[exit 1]", result)


class TestBothVersionsLs(unittest.TestCase):
    """Test ls tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_ls_chalilulz(self):
        pathlib.Path(os.path.join(self.test_dir, "file1.txt")).touch()
        os.makedirs(os.path.join(self.test_dir, "subdir"))
        result = chalilulz._ls({"path": self.test_dir})
        self.assertIn("file1.txt", result)
        self.assertIn("subdir/", result)

    def test_ls_chalminilulz(self):
        pathlib.Path(os.path.join(self.test_dir, "file1.txt")).touch()
        os.makedirs(os.path.join(self.test_dir, "subdir"))
        result = chalminilulz._ls({"path": self.test_dir})
        self.assertIn("file1.txt", result)
        self.assertIn("subdir/", result)

    def test_ls_empty_chalilulz(self):
        result = chalilulz._ls({"path": self.test_dir})
        self.assertEqual(result.strip(), "(empty)")

    def test_ls_empty_chalminilulz(self):
        result = chalminilulz._ls({"path": self.test_dir})
        self.assertEqual(result.strip(), "(empty)")


class TestBothVersionsMkdir(unittest.TestCase):
    """Test mkdir tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_mkdir_chalilulz(self):
        newdir = os.path.join(self.test_dir, "newdir")
        result = chalilulz._mk({"path": newdir})
        self.assertEqual(result.strip(), "created")
        self.assertTrue(os.path.isdir(newdir))

    def test_mkdir_chalminilulz(self):
        newdir = os.path.join(self.test_dir, "newdir")
        result = chalminilulz._mk({"path": newdir})
        self.assertEqual(result.strip(), "created")
        self.assertTrue(os.path.isdir(newdir))

    def test_mkdir_recursive_chalilulz(self):
        nested = os.path.join(self.test_dir, "a/b/c")
        result = chalilulz._mk({"path": nested})
        self.assertEqual(result.strip(), "created")
        self.assertTrue(os.path.isdir(nested))

    def test_mkdir_recursive_chalminilulz(self):
        nested = os.path.join(self.test_dir, "a/b/c")
        result = chalminilulz._mk({"path": nested})
        self.assertEqual(result.strip(), "created")
        self.assertTrue(os.path.isdir(nested))


class TestBothVersionsRm(unittest.TestCase):
    """Test rm tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_rm_file_chalilulz(self):
        test_file = os.path.join(self.test_dir, "delete.txt")
        pathlib.Path(test_file).touch()
        result = chalilulz._rm({"path": test_file})
        self.assertEqual(result.strip(), "deleted")
        self.assertFalse(os.path.exists(test_file))

    def test_rm_file_chalminilulz(self):
        test_file = os.path.join(self.test_dir, "delete.txt")
        pathlib.Path(test_file).touch()
        result = chalminilulz._rm({"path": test_file})
        self.assertEqual(result.strip(), "deleted")
        self.assertFalse(os.path.exists(test_file))

    def test_rm_dir_chalilulz(self):
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        result = chalilulz._rm({"path": subdir})
        self.assertEqual(result.strip(), "deleted")

    def test_rm_dir_chalminilulz(self):
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        result = chalminilulz._rm({"path": subdir})
        self.assertEqual(result.strip(), "deleted")


class TestBothVersionsMv(unittest.TestCase):
    """Test mv tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_mv_chalilulz(self):
        src = os.path.join(self.test_dir, "src.txt")
        with open(src, "w") as f:
            f.write("content")
        dest = os.path.join(self.test_dir, "dest.txt")
        result = chalilulz._mv({"src": src, "dest": dest})
        self.assertEqual(result.strip(), f"→{dest}")
        self.assertTrue(os.path.exists(dest))
        self.assertFalse(os.path.exists(src))

    def test_mv_chalminilulz(self):
        src = os.path.join(self.test_dir, "src.txt")
        with open(src, "w") as f:
            f.write("content")
        dest = os.path.join(self.test_dir, "dest.txt")
        result = chalminilulz._mv({"src": src, "dest": dest})
        self.assertEqual(result.strip(), f"→{dest}")
        self.assertTrue(os.path.exists(dest))
        self.assertFalse(os.path.exists(src))


class TestBothVersionsCp(unittest.TestCase):
    """Test cp tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cp_file_chalilulz(self):
        src = os.path.join(self.test_dir, "original.txt")
        with open(src, "w") as f:
            f.write("copy me")
        dest = os.path.join(self.test_dir, "copy.txt")
        result = chalilulz._cp({"src": src, "dest": dest})
        self.assertEqual(result.strip(), f"→{dest}")
        self.assertTrue(os.path.exists(dest))
        with open(dest, "r") as f:
            self.assertEqual(f.read(), "copy me")

    def test_cp_file_chalminilulz(self):
        src = os.path.join(self.test_dir, "original.txt")
        with open(src, "w") as f:
            f.write("copy me")
        dest = os.path.join(self.test_dir, "copy.txt")
        result = chalminilulz._cp({"src": src, "dest": dest})
        self.assertEqual(result.strip(), f"→{dest}")
        self.assertTrue(os.path.exists(dest))
        with open(dest, "r") as f:
            self.assertEqual(f.read(), "copy me")


class TestBothVersionsFind(unittest.TestCase):
    """Test find tool in both versions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        pathlib.Path(os.path.join(self.test_dir, "file1.txt")).touch()
        pathlib.Path(os.path.join(self.test_dir, "file2.py")).touch()
        pathlib.Path(os.path.join(self.test_dir, "file3.txt")).touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_chalilulz(self):
        result = chalilulz._fd({"pat": "*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertEqual(len(files), 2)
        self.assertTrue(all(f.endswith(".txt") for f in files))

    def test_find_chalminilulz(self):
        result = chalminilulz._fd({"pat": "*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertEqual(len(files), 2)
        self.assertTrue(all(f.endswith(".txt") for f in files))


class TestBothVersionsModelParsing(unittest.TestCase):
    """Test model parsing in both versions."""

    def test_parse_ollama_default_chalilulz(self):
        provider, model_id = chalilulz.parse_model("llama2")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model_id, "llama2")

    def test_parse_ollama_default_chalminilulz(self):
        provider, model_id = chalminilulz.parse_model("llama2")
        self.assertEqual(provider, "ollama")
        self.assertEqual(model_id, "llama2")

    def test_parse_mistral_chalilulz(self):
        provider, model_id = chalilulz.parse_model("mistral:mistral-small")
        self.assertEqual(provider, "mistral")
        self.assertEqual(model_id, "mistral-small")

    def test_parse_mistral_chalminilulz(self):
        provider, model_id = chalminilulz.parse_model("mistral:mistral-small")
        self.assertEqual(provider, "mistral")
        self.assertEqual(model_id, "mistral-small")

    def test_parse_groq_chalilulz(self):
        provider, model_id = chalilulz.parse_model("groq:llama-3.3-70b")
        self.assertEqual(provider, "groq")
        self.assertEqual(model_id, "llama-3.3-70b")

    def test_parse_groq_chalminilulz(self):
        provider, model_id = chalminilulz.parse_model("groq:llama-3.3-70b")
        self.assertEqual(provider, "groq")
        self.assertEqual(model_id, "llama-3.3-70b")

    def test_parse_gemini_chalilulz(self):
        provider, model_id = chalilulz.parse_model("gemini:gemini-2.0-flash")
        self.assertEqual(provider, "gemini")
        self.assertEqual(model_id, "gemini-2.0-flash")

    def test_parse_gemini_chalminilulz(self):
        provider, model_id = chalminilulz.parse_model("gemini:gemini-2.0-flash")
        self.assertEqual(provider, "gemini")
        self.assertEqual(model_id, "gemini-2.0-flash")

    def test_parse_openrouter_chalilulz(self):
        provider, model_id = chalilulz.parse_model("openrouter:model/id:free")
        self.assertEqual(provider, "openrouter")
        self.assertEqual(model_id, "model/id:free")

    def test_parse_openrouter_chalminilulz(self):
        provider, model_id = chalminilulz.parse_model("openrouter:model/id:free")
        self.assertEqual(provider, "openrouter")
        self.assertEqual(model_id, "model/id:free")


class TestBothVersionsGetKey(unittest.TestCase):
    """Test get_required_key/get_key in both versions."""

    def test_ollama_no_key_chalilulz(self):
        self.assertIsNone(chalilulz.get_required_key("ollama"))

    def test_ollama_no_key_chalminilulz(self):
        # chalminilulz uses get_key instead of get_required_key
        self.assertIsNone(chalminilulz.get_key("ollama"))

    def test_mistral_key_chalilulz(self):
        key = chalilulz.get_required_key("mistral")
        self.assertIsNotNone(key)

    def test_mistral_key_chalminilulz(self):
        key = chalminilulz.get_key("mistral")
        self.assertIsNotNone(key)

    def test_groq_key_chalilulz(self):
        key = chalilulz.get_required_key("groq")
        self.assertIsNotNone(key)

    def test_groq_key_chalminilulz(self):
        key = chalminilulz.get_key("groq")
        self.assertIsNotNone(key)

    def test_gemini_key_chalilulz(self):
        key = chalilulz.get_required_key("gemini")
        self.assertIsNotNone(key)

    def test_gemini_key_chalminilulz(self):
        key = chalminilulz.get_key("gemini")
        self.assertIsNotNone(key)

    def test_openrouter_key_chalilulz(self):
        key = chalilulz.get_required_key("openrouter")
        self.assertIsNotNone(key)

    def test_openrouter_key_chalminilulz(self):
        key = chalminilulz.get_key("openrouter")
        self.assertIsNotNone(key)


class TestBothVersionsRunTool(unittest.TestCase):
    """Test run_tool in both versions."""

    def test_unknown_tool_chalilulz(self):
        result = chalilulz.run_tool("unknown_tool", {})
        self.assertTrue(result.startswith("error:unknown tool"))

    def test_unknown_tool_chalminilulz(self):
        result = chalminilulz.run_tool("unknown_tool", {})
        self.assertTrue(result.startswith("error:unknown tool"))

    def test_run_read_tool_chalilulz(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            path = f.name
        try:
            result = chalilulz.run_tool("read", {"path": path})
            self.assertIn("test content", result)
        finally:
            os.unlink(path)

    def test_run_read_tool_chalminilulz(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            path = f.name
        try:
            result = chalminilulz.run_tool("read", {"path": path})
            self.assertIn("test content", result)
        finally:
            os.unlink(path)


class TestBothVersionsAPI(unittest.TestCase):
    """Test API calls in both versions."""

    def setUp(self):
        self.orig_ACTUAL_MODEL = chalilulz.ACTUAL_MODEL
        self.orig_PROVIDER = chalilulz.PROVIDER
        self.orig_ACTUAL_MODEL_mini = chalminilulz.ACTUAL_MODEL
        self.orig_PROVIDER_mini = chalminilulz.PROVIDER

    def tearDown(self):
        chalilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL
        chalilulz.PROVIDER = self.orig_PROVIDER
        chalminilulz.ACTUAL_MODEL = self.orig_ACTUAL_MODEL_mini
        chalminilulz.PROVIDER = self.orig_PROVIDER_mini

    @patch("urllib.request.urlopen")
    def test_openrouter_chalilulz(self, mock_urlopen):
        mock_urlopen.side_effect = make_mock_urlopen(
            {
                "choices": [{"message": {"content": "Hello"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        )
        chalilulz.ACTUAL_MODEL = "test-model"
        chalilulz.PROVIDER = "openrouter"
        result = chalilulz.call_openrouter([], "System")
        self.assertIsInstance(result, tuple)
        resp, use_tools = result
        self.assertIn("choices", resp)

    @patch("urllib.request.urlopen")
    def test_openrouter_chalminilulz(self, mock_urlopen):
        mock_urlopen.side_effect = make_mock_urlopen(
            {
                "choices": [{"message": {"content": "Hello"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        )
        chalminilulz.ACTUAL_MODEL = "test-model"
        chalminilulz.PROVIDER = "openrouter"
        result = chalminilulz.call_openrouter([], "System")
        self.assertIsInstance(result, tuple)
        resp, use_tools = result
        self.assertIn("choices", resp)

    @patch("urllib.request.urlopen")
    def test_ollama_chalilulz(self, mock_urlopen):
        mock_urlopen.side_effect = make_mock_urlopen(
            {
                "message": {"content": "Hello from Ollama"},
                "prompt_eval_count": 5,
                "eval_count": 10,
            }
        )
        chalilulz.ACTUAL_MODEL = "mistral"
        chalilulz.PROVIDER = "ollama"
        result = chalilulz.call_ollama([], "System")
        resp, use_tools = result
        self.assertIn("choices", resp)
        self.assertEqual(resp["choices"][0]["message"]["content"], "Hello from Ollama")

    @patch("urllib.request.urlopen")
    def test_ollama_chalminilulz(self, mock_urlopen):
        mock_urlopen.side_effect = make_mock_urlopen(
            {
                "message": {"content": "Hello from Ollama"},
                "prompt_eval_count": 5,
                "eval_count": 10,
            }
        )
        chalminilulz.ACTUAL_MODEL = "mistral"
        chalminilulz.PROVIDER = "ollama"
        result = chalminilulz.call_ollama([], "System")
        resp, use_tools = result
        self.assertIn("choices", resp)
        self.assertEqual(resp["choices"][0]["message"]["content"], "Hello from Ollama")

    @patch("chalilulz.call_ollama")
    def test_call_api_ollama_chalilulz(self, mock_ollama):
        chalilulz.PROVIDER = "ollama"
        mock_ollama.return_value = ({"choices": []}, False)
        result = chalilulz.call_api([], "System")
        mock_ollama.assert_called_once()

    @patch("chalminilulz.call_ollama")
    def test_call_api_ollama_chalminilulz(self, mock_ollama):
        chalminilulz.PROVIDER = "ollama"
        mock_ollama.return_value = ({"choices": []}, False)
        result = chalminilulz.call_api([], "System")
        mock_ollama.assert_called_once()

    @patch("chalilulz.call_openrouter")
    def test_call_api_openrouter_chalilulz(self, mock_openrouter):
        chalilulz.PROVIDER = "openrouter"
        mock_openrouter.return_value = ({"choices": []}, False)
        result = chalilulz.call_api([], "System")
        mock_openrouter.assert_called_once()

    @patch("chalminilulz.call_openrouter")
    def test_call_api_openrouter_chalminilulz(self, mock_openrouter):
        chalminilulz.PROVIDER = "openrouter"
        mock_openrouter.return_value = ({"choices": []}, False)
        result = chalminilulz.call_api([], "System")
        mock_openrouter.assert_called_once()

    @patch("chalilulz.call_mistral")
    def test_call_api_mistral_chalilulz(self, mock_mistral):
        chalilulz.PROVIDER = "mistral"
        mock_mistral.return_value = ({"choices": []}, False)
        result = chalilulz.call_api([], "System")
        mock_mistral.assert_called_once()

    @patch("chalminilulz._call_oc")
    def test_call_api_mistral_chalminilulz(self, mock_mistral):
        chalminilulz.PROVIDER = "mistral"
        mock_mistral.return_value = ({"choices": []}, False)
        result = chalminilulz.call_api([], "System")
        mock_mistral.assert_called_once()

    def test_call_api_unknown_chalilulz(self):
        chalilulz.PROVIDER = "unknown"
        with self.assertRaises(RuntimeError):
            chalilulz.call_api([], "System")

    def test_call_api_unknown_chalminilulz(self):
        chalminilulz.PROVIDER = "unknown"
        with self.assertRaises(RuntimeError):
            chalminilulz.call_api([], "System")


class TestBothVersionsSkills(unittest.TestCase):
    """Test skills loading in both versions."""

    def test_load_skills_chalilulz(self):
        skills = chalilulz.load_skills()
        self.assertIsInstance(skills, list)

    def test_load_skills_chalminilulz(self):
        skills = chalminilulz.load_skills()
        self.assertIsInstance(skills, list)

    def test_skills_prompt_empty_chalilulz(self):
        prompt = chalilulz.skills_prompt([])
        self.assertEqual(prompt, "")

    def test_skills_prompt_empty_chalminilulz(self):
        prompt = chalminilulz.skills_prompt([])
        self.assertEqual(prompt, "")

    def test_skills_prompt_with_skills_chalilulz(self):
        skills = [{"name": "test", "desc": "test description"}]
        prompt = chalilulz.skills_prompt(skills)
        self.assertIn("test", prompt)
        self.assertIn("test description", prompt)

    def test_skills_prompt_with_skills_chalminilulz(self):
        skills = [{"name": "test", "desc": "test description"}]
        prompt = chalminilulz.skills_prompt(skills)
        self.assertIn("test", prompt)
        self.assertIn("test description", prompt)


class TestBothVersionsGlobals(unittest.TestCase):
    """Test that global variables are consistent in both versions."""

    def test_default_model_both(self):
        # The default model should start as openrouter for both
        self.assertTrue(
            chalilulz.MODEL.startswith("openrouter:"),
            "Default MODEL should start with openrouter",
        )
        self.assertTrue(
            chalminilulz.MODEL.startswith("openrouter:"),
            "Default MODEL should start with openrouter",
        )

    def test_provider_parsing_identical(self):
        # Parse various models and verify both versions produce same results
        test_models = [
            "ollama:llama2",
            "mistral:test",
            "groq:model",
            "gemini:gemini-1",
            "openrouter:model/id",
            "plainmodel",
        ]

        for model in test_models:
            p1, m1 = chalilulz.parse_model(model)
            p2, m2 = chalminilulz.parse_model(model)
            self.assertEqual(p1, p2, f"Provider mismatch for {model}")
            self.assertEqual(m1, m2, f"Model mismatch for {model}")

    def test_schema_identical(self):
        # Verify both modules produce identical schema
        self.assertEqual(
            json.dumps(chalilulz.SCHEMA, sort_keys=True),
            json.dumps(chalminilulz.SCHEMA, sort_keys=True),
            "SCHEMA should be identical",
        )
        self.assertTrue(
            chalminilulz.MODEL.startswith("openrouter:"),
            "Default MODEL should start with openrouter",
        )

    def test_default_provider_both(self):
        # Parse the default model and verify provider detection works identically
        # Both should default to openrouter when no prefix is given (via env var)
        default_model = "openrouter:arcee-ai/trinity-large-preview:free"

        p1, m1 = chalilulz.parse_model(default_model)
        p2, m2 = chalminilulz.parse_model(default_model)

        self.assertEqual(p1, p2, "Provider parsing should match")
        self.assertEqual(m1, m2, "Model parsing should match")

    def test_default_actual_model_both(self):
        # Verify both modules produce identical schema
        self.assertEqual(
            json.dumps(chalilulz.SCHEMA, sort_keys=True),
            json.dumps(chalminilulz.SCHEMA, sort_keys=True),
            "SCHEMA should be identical",
        )


class TestBothVersionsUpdateModel(unittest.TestCase):
    """Test update_model function in both versions."""

    def test_update_model_chalilulz(self):
        chalilulz.update_model("groq:test-model")
        self.assertEqual(chalilulz.MODEL, "groq:test-model")
        self.assertEqual(chalilulz.PROVIDER, "groq")
        self.assertEqual(chalilulz.ACTUAL_MODEL, "test-model")

    def test_update_model_chalminilulz(self):
        chalminilulz.update_model("groq:test-model")
        self.assertEqual(chalminilulz.MODEL, "groq:test-model")
        self.assertEqual(chalminilulz.PROVIDER, "groq")
        self.assertEqual(chalminilulz.ACTUAL_MODEL, "test-model")

    def test_update_model_ollama_chalilulz(self):
        chalilulz.update_model("llama2")
        self.assertEqual(chalilulz.PROVIDER, "ollama")

    def test_update_model_ollama_chalminilulz(self):
        chalminilulz.update_model("llama2")
        self.assertEqual(chalminilulz.PROVIDER, "ollama")


class TestBothVersionsMkSchema(unittest.TestCase):
    """Test mk_schema function in both versions."""

    def test_mk_schema_chalilulz(self):
        schema = chalilulz.mk_schema()
        self.assertIsInstance(schema, list)
        self.assertGreater(len(schema), 0)

    def test_mk_schema_chalminilulz(self):
        schema = chalminilulz.mk_schema()
        self.assertIsInstance(schema, list)
        self.assertGreater(len(schema), 0)

    def test_schema_contains_all_tools_chalilulz(self):
        schema = chalilulz.mk_schema()
        tool_names = {s["function"]["name"] for s in schema}
        self.assertEqual(tool_names, set(chalilulz.TOOLS.keys()))

    def test_schema_contains_all_tools_chalminilulz(self):
        schema = chalminilulz.mk_schema()
        tool_names = {s["function"]["name"] for s in schema}
        self.assertEqual(tool_names, set(chalminilulz.TOOLS.keys()))


class TestBothVersionsLoadSkill(unittest.TestCase):
    """Test load_skill tool in both versions."""

    def test_load_skill_not_found_chalilulz(self):
        result = chalilulz._sk({"name": "nonexistent_skill"})
        self.assertIn("not found", result)

    def test_load_skill_not_found_chalminilulz(self):
        result = chalminilulz._sk({"name": "nonexistent_skill"})
        self.assertIn("not found", result)


if __name__ == "__main__":
    unittest.main()
