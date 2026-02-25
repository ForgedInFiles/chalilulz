"""
test_tools — Individual tool function tests (read, write, edit, etc.)
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import (
    _r,
    _w,
    _e,
    _gl,
    _gp,
    _b,
    _ls,
    _mk,
    _rm,
    _mv,
    _cp,
    _fd,
    _sk,
    TOOLS,
    run_tool,
)


class TestReadTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_basic(self):
        result = _r({"path": self.test_file})
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)
        # Should have line numbers
        self.assertRegex(result, r"^\s*\d+│")

    def test_read_with_offset_limit(self):
        result = _r({"path": self.test_file, "offset": 1, "limit": 1})
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 1)
        self.assertIn("Line 2", lines[0])

    def test_read_missing_file(self):
        result = _r({"path": "/nonexistent/file.txt"})
        self.assertTrue(result.startswith("error:"))


class TestWriteTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_new_file(self):
        filepath = os.path.join(self.test_dir, "new.txt")
        result = _w({"path": filepath, "content": "Hello World"})
        self.assertIn("wrote", result)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), "Hello World")

    def test_write_auto_mkdir(self):
        nested_path = os.path.join(self.test_dir, "a/b/c/file.txt")
        result = _w({"path": nested_path, "content": "nested"})
        self.assertIn("wrote", result)
        self.assertTrue(os.path.exists(nested_path))


class TestEditTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "edit.txt")
        with open(self.test_file, "w") as f:
            f.write("Hello World\nTest\nHello World\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_edit_simple(self):
        result = _e({"path": self.test_file, "old": "Test", "new": "Hi"})
        self.assertIn("ok", result)
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertIn("Hi\n", content)
        self.assertNotIn("Test", content)

    def test_edit_multiple_hits_without_all(self):
        result = _e({"path": self.test_file, "old": "Hello World", "new": "Hi"})
        self.assertTrue("error:" in result and "hits" in result)

    def test_edit_all(self):
        result = _e(
            {"path": self.test_file, "old": "Hello World", "new": "Hi", "all": True}
        )
        self.assertIn("ok(2", result)
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content.count("Hi"), 2)

    def test_edit_old_not_found(self):
        result = _e({"path": self.test_file, "old": "Nonexistent", "new": "X"})
        self.assertTrue(result.startswith("error:old_string not found"))


class TestGlobTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create some files
        Path(os.path.join(self.test_dir, "a.txt")).touch()
        Path(os.path.join(self.test_dir, "b.py")).touch()
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        Path(os.path.join(subdir, "c.txt")).touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_glob_simple(self):
        result = _gl({"pat": "*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertGreater(len(files), 0)
        self.assertTrue(all(f.endswith(".txt") for f in files))

    def test_glob_recursive(self):
        result = _gl({"pat": "**/*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertGreaterEqual(len(files), 2)


class TestGrepTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        with open(self.test_file, "w") as f:
            f.write("def hello():\n    return 'world'\nimport os\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_grep_find(self):
        result = _gp({"pat": "def ", "path": self.test_dir})
        self.assertIn("test.py", result)
        self.assertIn("def hello", result)

    def test_grep_not_found(self):
        result = _gp({"pat": "nonexistentpattern", "path": self.test_dir})
        self.assertEqual(result.strip(), "none")


class TestBashTool(unittest.TestCase):
    def test_bash_simple(self):
        result = _b({"cmd": "echo 'Hello World'"})
        self.assertIn("Hello World", result)
        self.assertIn("[exit 0]", result)

    def test_bash_with_cwd(self):
        # Use Python to print cwd cross-platform
        import sys

        cmd = f'"{sys.executable}" -c "import os; print(os.getcwd())"'
        result = _b({"cmd": cmd, "cwd": "/tmp"})
        # Should output a path
        self.assertTrue(result.strip() != "")

    def test_bash_error(self):
        # Use Python to exit with code 1 cross-platform
        import sys

        cmd = f'"{sys.executable}" -c "import sys; sys.exit(1)"'
        result = _b({"cmd": cmd})
        self.assertIn("[exit 1]", result)


class TestLsTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_ls_directory(self):
        # Create some files and dirs
        Path(os.path.join(self.test_dir, "file1.txt")).touch()
        os.makedirs(os.path.join(self.test_dir, "subdir"))
        result = _ls({"path": self.test_dir})
        self.assertIn("file1.txt", result)
        self.assertIn("subdir/", result)

    def test_ls_empty(self):
        result = _ls({"path": self.test_dir})
        self.assertEqual(result.strip(), "(empty)")


class TestMkdirTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_mkdir_simple(self):
        newdir = os.path.join(self.test_dir, "newdir")
        result = _mk({"path": newdir})
        self.assertEqual(result.strip(), "created")
        self.assertTrue(os.path.isdir(newdir))

    def test_mkdir_recursive(self):
        nested = os.path.join(self.test_dir, "a/b/c")
        result = _mk({"path": nested})
        self.assertEqual(result.strip(), "created")
        self.assertTrue(os.path.isdir(nested))


class TestRmTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "delete.txt")
        Path(self.test_file).touch()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_rm_file(self):
        result = _rm({"path": self.test_file})
        self.assertEqual(result.strip(), "deleted")
        self.assertFalse(os.path.exists(self.test_file))

    def test_rm_dir(self):
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        result = _rm({"path": subdir})
        self.assertEqual(result.strip(), "deleted")
        self.assertFalse(os.path.exists(subdir))

    def test_rm_not_found(self):
        result = _rm({"path": "/nonexistent"})
        self.assertTrue(result.startswith("error:not found"))


class TestMvTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.src = os.path.join(self.test_dir, "src.txt")
        with open(self.src, "w") as f:
            f.write("content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_mv_file(self):
        dest = os.path.join(self.test_dir, "dest.txt")
        result = _mv({"src": self.src, "dest": dest})
        self.assertEqual(result.strip(), f"→{dest}")
        self.assertTrue(os.path.exists(dest))
        self.assertFalse(os.path.exists(self.src))


class TestCpTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.src = os.path.join(self.test_dir, "original.txt")
        with open(self.src, "w") as f:
            f.write("copy me")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cp_file(self):
        dest = os.path.join(self.test_dir, "copy.txt")
        result = _cp({"src": self.src, "dest": dest})
        self.assertEqual(result.strip(), f"→{dest}")
        self.assertTrue(os.path.exists(dest))
        with open(dest, "r") as f:
            self.assertEqual(f.read(), "copy me")
        with open(dest, "r") as f:
            self.assertEqual(f.read(), "copy me")


class TestFindTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        Path(os.path.join(self.test_dir, "file1.txt")).touch()
        Path(os.path.join(self.test_dir, "file2.py")).touch()
        Path(os.path.join(self.test_dir, "file3.txt")).touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_pattern(self):
        result = _fd({"pat": "*.txt", "path": self.test_dir})
        files = result.strip().split("\n")
        self.assertEqual(len(files), 2)
        self.assertTrue(all(f.endswith(".txt") for f in files))


class TestLoadSkillTool(unittest.TestCase):
    def test_load_skill_not_found(self):
        result = _sk({"name": "nonexistent_skill"})
        self.assertIn("not found", result)


class TestRunTool(unittest.TestCase):
    def test_run_unknown_tool(self):
        result = run_tool("unknown_tool", {})
        self.assertTrue(result.startswith("error:unknown tool"))

    def test_run_tool_with_args(self):
        # Test with read (requires path)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            path = f.name
        try:
            result = run_tool("read", {"path": path, "offset": 0, "limit": 10})
            self.assertIn("test content", result)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
