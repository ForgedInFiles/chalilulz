# AGENTS.md — Guidelines for agentic coding assistants

This repository contains `chalilulz.py`, a Python CLI for interacting with multiple LLM providers (OpenRouter, Ollama, Mistral, Groq, Gemini). Tests are located in the `tests/` directory.

## Build & Test Commands

### Run all tests
```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

### Run a single test module
```bash
python -m unittest tests.test_parsing -v
python -m unittest tests.test_schema -v
python -m unittest tests.test_tools -v
python -m unittest test_api.TestOpenRouterAPI.test_call_openrouter_success -v
```

### Run a single test class
```bash
python -m unittest tests.test_tools.TestReadTool -v
```

### Run a single test method
```bash
python -m unittest tests.test_parsing.TestModelParsing.test_parse_ollama -v
```

### Syntax check
```bash
python -m py_compile chalilulz.py
```

### Lint (recommended)
```bash
pip install ruff
ruff check chalilulz.py tests/
```

### Type checking (optional)
```bash
pip install mypy
mypy --ignore-missing-imports chalilulz.py
```

### Execute the CLI
```bash
python chalilulz.py --model openrouter:arcee-ai/trinity-large-preview:free
python chalilulz.py --model mistral:mistral-small-latest --mistral-key $MISTRAL_API_KEY
python chalilulz.py --model ollama:llama2 --ollama-host http://localhost:11434
```

## Code Style Guidelines

### General
- **Indentation**: 4 spaces, no tabs.
- **Line length**: aim for ≤100 columns.
- **Trailing whitespace**: remove.
- **Blank lines**: separate logical sections; two blank lines between top-level definitions.

### Imports
- Group imports: standard library, third-party, local.
- Sort alphabetically within groups.
- Use `import X` not `from X import *`.
- Current imports are combined on one line where short; break into multiple lines if >~80 chars.

Example:
```python
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
```

### Naming Conventions
- **Functions/variables**: `snake_case`.
- **Constants** (module-level, immutable): `SCREAMING_SNAKE_CASE`.
- **Classes**: `PascalCase` (none currently).
- **Private/internal tools**: leading underscore `_toolname`.
- **Global state**: minimize; when needed, use module-level with clear naming.

### Formatting
- Use UTF-8 encoding.
- Double quotes (`"`) for strings consistently.
- Maintain existing style when editing: the codebase uses compact formatting, minimal vertical whitespace, and one-line function bodies where readable.

### Functions
- Keep functions small and focused.
- Document non-obvious behavior with inline comments (not docstrings, unless public API).
- Tool functions (`_r`, `_w`, etc.) take a single dict argument `a` and return a string.
- Error handling: catch `Exception` and return `f"error:{e}"` string; no uncaught exceptions from tool functions.

### Arguments & Arguments Parsing
- Use `argparse.ArgumentParser` for CLI.
- When importing the module from tests, guard `parse_args()` under `if __name__ == "__main__":` to avoid `sys.argv` consumption.
- Provide sensible defaults and environment variable fallbacks.

### API Integration
- Provider selection: model string prefix (`provider:model-id`) determines endpoint:
  - `ollama:` → Ollama local API
  - `mistral:` → Mistral AI (`https://api.mistral.ai/v1`)
  - `groq:` → Groq (`https://api.groq.com/openai/v1`)
  - `gemini:` → Gemini (`https://generativelanguage.googleapis.com/v1beta/openai`)
  - `openrouter:` → OpenRouter (`https://openrouter.ai/api/v1`)
- No prefix → Ollama (default).
- API keys:
  - OpenRouter: `OPENROUTER_API_KEY`
  - Mistral: `MISTRAL_API_KEY` or `--mistral-key`
  - Groq: `GROQ_API_KEY` or `--groq-key`
  - Gemini: `GOOGLE_API_KEY` or `--gemini-key`
- OpenAI-compatible clients: use `Authorization: Bearer` except Gemini uses `x-goog-api-key`.
- Transform Ollama responses to OpenAI format internally.

### Tool Calls & Schema
- Tool schema is generated from `TOOLS` dict via `mk_schema()`.
- Optional parameters (no required enforcement) listed in `OPT`.
- Tool execution: `_do_tool_calls()` must handle both OpenAI format (`tool_call_id`) and Ollama format (`tool_name`) based on `PROVIDER`.
- System message includes skills prompt if available.

### Global State
- Module-level globals: `MODEL`, `PROVIDER`, `ACTUAL_MODEL`, `KEY`, `OLLAMA_HOST`, `MISTRAL_KEY`, `MISTRAL_HOST`, `GROQ_KEY`, `GROQ_HOST`, `GEMINI_KEY`, `GEMINI_HOST`, `SCHEMA`, `NO_TOOLS_MODELS`, `SP`, etc.
- When changing model at runtime (`/model` command), use `update_model(new_model)` to update `MODEL`, `PROVIDER`, and `ACTUAL_MODEL` consistently.

### Testing
- Use `unittest` framework.
- Tests should be isolated, use temporary directories (`tempfile.mkdtemp()`), and clean up.
- Mock external HTTP calls with `unittest.mock.patch` on `urllib.request.urlopen`.
- Provide fake response classes in tests to simulate API behavior.
- Resource warnings: close files properly (use `with open(...) as f:`).

### Security & Best Practices
- Never commit API keys or secrets.
- Validate paths and user input; tools should not crash on errors but return `error:` messages.
- Be mindful of shell injection risks: `bash` tool runs with `shell=True`; accept that risk as documented.
- Use `encoding="utf-8"` with `errors="replace"` for reading files.
- Limit recursion depth and timeouts in external calls.

### Compatibility
- Supports Python 3.8+ (type hints optional).
- No external dependencies beyond standard library.
- The file is both importable as a module and executable as a script.

## Repository-Specific Notes
- The `--model` default is `openrouter:arcee-ai/trinity-large-preview:free`.
- If a provider requires an API key and it's missing, the CLI prints an error and exits.
- The `NO_TOOLS_MODELS` set tracks models that returned 400 on tool use; they fall back to XML mode.
- Tool output includes styled icons (`TIC` dict); keep them as emojis/strings.
- **Cross-platform**: ANSI colors are auto-enabled on Windows 10+ via VT100. The `bash` tool uses the system's default shell (`/bin/sh` on Unix, `cmd.exe` on Windows). Commands should be appropriate for the target platform.