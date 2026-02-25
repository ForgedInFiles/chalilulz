# AGENTS.md — Agentic Coding Guidelines

This file provides guidelines for AI agents operating in this repository.

---

## Project Overview

- **Name**: chalilulz
- **Type**: Agentic coding CLI tool
- **Language**: Python 3.8+
- **Dependencies**: None (pure stdlib)

---

## Build / Lint / Test Commands

```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Run specific test file
python -m unittest tests.test_tools -v
python -m unittest tests.test_api -v
python -m unittest tests.test_parsing -v
python -m unittest tests.test_main -v
python -m unittest tests.test_skills -v
python -m unittest tests.test_utils -v
python -m unittest tests.test_schema -v
python -m unittest tests.test_do_tool_calls -v

# Run single test method
python -m unittest tests.test_tools.TestReadTool.test_read_basic -v

# Syntax & Linting
python -m py_compile chalilulz.py
pip install ruff && ruff check .
```

---

## Code Style Guidelines

### General Principles

- **Minimal dependencies**: Use Python stdlib only
- **Concise code**: Prefer compact, readable implementations
- **No comments**: Unless absolutely necessary
- **Error handling**: Tool functions return `f"error:{e}"` strings

### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 100 chars preferred, 120 hard limit
- **Blank lines**: Two between top-level definitions

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions/variables | snake_case | `parse_model`, `run_tool` |
| Constants | SCREAMING_SNAKE_CASE | `OLLAMA_HOST`, `SCHEMA` |
| Classes | PascalCase | `Spin`, `FakeHTTPResponse` |
| Private functions | _leading_underscore | `_r()`, `_e()` |

### Imports

Single line, comma-separated, alphabetically sorted with short aliases:

```python
import argparse, glob as G, json, os, pathlib, re, shutil, subprocess, sys, threading, time, urllib.request, urllib.error
```

### Error Handling

```python
def _r(a):
    try:
        ls = open(a["path"], encoding="utf-8", errors="replace").readlines()
        return "".join(f"{o+i+1:5}│{ln}" for i, ln in enumerate(ls[o:o+l]))
    except Exception as e:
        return f"error:{e}"
```

---

## Architecture

### Tools Dictionary

```python
TOOLS = {
    "read": ("Read file w/ line numbers", {"path": "string", "offset": "integer", "limit": "integer"}, _r),
    "write": ("Write/create file (auto mkdir)", {"path": "string", "content": "string"}, _w),
    # Format: (description, params_dict, function)
}
OPT = {"offset", "limit", "path", "cwd", "all"}  # optional params
```

### Supported Providers

| Provider | Prefix | Key Env Var |
|----------|--------|-------------|
| OpenRouter | `openrouter:` | `OPENROUTER_API_KEY` |
| Ollama | `ollama:` (default) | None |
| Mistral | `mistral:` | `MISTRAL_API_KEY` |
| Groq | `groq:` | `GROQ_API_KEY` |
| Gemini | `gemini:` | `GOOGLE_API_KEY` |

### Environment Variables

```bash
CHALILULZ_MODEL           # Default model slug
CHALILULZ_OLLAMA_HOST     # Ollama host URL
OPENROUTER_API_KEY        # OpenRouter API key
MISTRAL_API_KEY           # Mistral API key
GROQ_API_KEY              # Groq API key
GOOGLE_API_KEY            # Gemini API key
```

---

## Testing Guidelines

- Use `unittest` framework
- Mock HTTP calls with `@patch("urllib.request.urlopen")`
- Create temp directories with `tempfile.mkdtemp()`
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

---

## File Organization

```
chalilulz.py              # Main application
setup.py                  # Installation script
pyproject.toml           # Package configuration
tests/
  test_tools.py           # Tool function tests
  test_api.py             # API mocking tests
  test_parsing.py         # Model parsing tests
  test_main.py            # REPL/command tests
  test_skills.py          # Skill loading tests
  test_utils.py           # UI utility tests
  test_schema.py          # Schema generation tests
  test_do_tool_calls.py   # Tool execution tests
```

---

## REPL Commands (Runtime)

| Command | Description |
|---------|-------------|
| `/q`, `exit`, `quit` | Exit the program |
| `/c` | Clear conversation history |
| `/model <slug>` | Switch LLM model |
| `/skills` | List loaded skills |

---

## Remember

- Use environment variables for configuration
- Maintain zero external dependencies
