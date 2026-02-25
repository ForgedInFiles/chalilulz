# AGENTS.md — Agentic Coding Guidelines

This file provides guidelines for AI agents operating in this repository.

---

## Project Overview

- **Name**: chalilulz
- **Type**: Agentic coding CLI tool
- **Language**: Python 3.8+
- **Dependencies**: None (pure stdlib)

### Two Versions

| Version | Path | Lines |
|---------|------|-------|
| Standard | `chalilulz.py` | 867 |
| Golfed | `golfed/chalminilulz.py` | 310 |

Both versions provide identical functionality.

---

## Build / Lint / Test Commands

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Run all tests (short)
python -m unittest discover -s tests -p 'test_*.py'

# Run specific test file
python -m unittest tests.test_tools -v
python -m unittest tests.test_api -v
python -m unittest tests.test_parsing -v
python -m unittest tests.test_both_versions -v

# Run specific test class
python -m unittest tests.test_both_versions.TestBothVersionsTools -v
python -m unittest tests.test_both_versions.TestBothVersionsAPI -v

# Run specific test method
python -m unittest tests.test_tools.TestReadTool.test_read_basic -v

# Run single test from any module
python -m unittest tests.test_both_versions.TestBothVersionsRead.test_read_chalilulz -v
```

### Syntax Checking

```bash
# Check syntax for both versions
python -m py_compile chalilulz.py
python -m py_compile golfed/chalminilulz.py

# Check all test files
python -m py_compile tests/*.py
```

### Linting

```bash
# Install ruff
pip install ruff

# Lint main files
ruff check chalilulz.py golfed/chalminilulz.py

# Lint tests
ruff check tests/

# Lint entire project
ruff check .
```

---

## Code Style Guidelines

### General Principles

- **Minimal dependencies**: Use Python stdlib only. No external packages.
- **Concise code**: Prefer compact, readable implementations.
- **No comments**: Unless absolutely necessary for clarity.
- **Error handling**: Tool functions return `f"error:{e}"` strings on failure.

### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 100 characters preferred, 120 hard limit
- **Blank lines**: Two between top-level definitions, one between functions
- **Golfed version**: Uses 2-space indentation, minified style

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions/variables | snake_case | `parse_model`, `run_tool` |
| Constants | SCREAMING_SNAKE_CASE | `OLLAMA_HOST`, `SCHEMA` |
| Classes | PascalCase | `Spin`, `FakeHTTPResponse` |
| Private functions | _leading_underscore | `_r()`, `_e()` |
| Golfed short names | Single letters allowed | `_r`, `_w`, `_gl` |

### Imports

- **Order**: stdlib → third-party → local (not applicable - stdlib only)
- **Style**: Alphabetical within groups
- **Golfed**: Combine into single line where possible

```python
# Standard version
import argparse
import glob as G
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error

# Golfed version
import argparse,glob as G,json,os,pathlib,re,shutil,subprocess,sys,threading,time,urllib.request,urllib.error
```

### Type Annotations

- Not required but acceptable where it improves clarity
- Use inline comments for complex type logic

### Error Handling

- **Tool functions**: Return error strings starting with `error:`
- **API functions**: Raise `RuntimeError` with descriptive messages
- **Silent failures**: Where appropriate (e.g., non-critical file operations)

```python
def _r(a):
    try:
        ls = open(a["path"], encoding="utf-8", errors="replace").readlines()
        return "".join(f"{o+i+1:5}│{ln}" for i, ln in enumerate(ls[o:o+l]))
    except Exception as e:
        return f"error:{e}"
```

### Function Structure

- Keep functions small and focused
- Single responsibility per function
- Use early returns for error cases
- No docstrings unless complex logic requires it

### Testing Guidelines

- Test both versions (chalilulz.py and golfed/chalminilulz.py) when adding features
- Use `unittest` framework
- Mock HTTP calls using `@patch("urllib.request.urlopen")`
- Create temp directories/files with `tempfile` module
- Clean up in `tearDown()` methods

```python
class TestReadTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_basic(self):
        result = _r({"path": self.test_file})
        self.assertIn("Line 1", result)
```

### File Organization

```
chalilulz.py           # Main application (standard version)
golfed/
  chalminilulz.py     # Minified version
tests/
  test_*.py           # Test modules
```

### REPL Commands (Runtime)

| Command | Description |
|---------|-------------|
| `/q`, `exit`, `quit` | Exit the program |
| `/c` | Clear conversation history |
| `/model <slug>` | Switch LLM model |
| `/skills` | List loaded skills |

### Tool Functions

All tool functions follow this pattern:
- Accept dict argument `a` with parameters
- Return string result or `f"error:{e}"` on failure
- Log output to stdout for transparency

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `chalilulz.py` | Main CLI application |
| `golfed/chalminilulz.py` | Minified version |
| `tests/test_both_versions.py` | Cross-version tests |
| `tests/test_tools.py` | Tool function tests |
| `tests/test_api.py` | API mocking tests |
| `tests/test_parsing.py` | Model parsing tests |

---

## Remember

- Always test both versions when modifying functionality
- Keep the golfed version in sync with the standard version
- Use environment variables for configuration
- Maintain zero external dependencies
