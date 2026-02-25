# chalilulz

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/LLM-Cli-orange.svg" alt="LLM CLI">
  <img src="https://img.shields.io/badge/Open-Source-green.svg" alt="Open Source">
  <img src="https://img.shields.io/badge/Platform-Cross--Platform-yellow.svg" alt="Cross Platform">
</p>

<p align="center">
  <strong>Agentic coding CLI with multi-provider LLM support</strong><br>
  <em>OpenRouter · Ollama · Mistral · Groq · Gemini</em>
</p>

---

## Two Versions

| Version | File | Description |
|---------|------|-------------|
| **Standard** | `chalilulz.py` | Full-featured, readable source (867 lines) |
| **Golfed** | `golfed/chalminilulz.py` | Minified, compact version (310 lines) |

Both versions provide identical functionality — choose based on your preference for code readability vs. compactness.

---

## Features

- **Multi-Provider Support** — Seamlessly switch between OpenRouter, Ollama, Mistral, Groq, and Gemini
- **Built-in Tools** — File operations, grep search, glob patterns, bash execution, and more
- **Agent Skills** — Load custom skill sets from `.skills/` directory
- **Cross-Platform** — Works on Linux, macOS, and Windows with ANSI color support
- **Zero Dependencies** — Pure Python standard library — no external packages required

---

## Quick Start

### Standard Version

```bash
# Clone and run
python chalilulz.py

# Or set a specific model
python chalilulz.py --model openrouter:arcee-ai/trinity-large-preview:free
```

### Golfed Version

```bash
# Run the minified version
python golfed/chalminilulz.py

# With custom model
python golfed/chalminilulz.py --model ollama:llama2
```

### Provider Examples

```bash
# Use with Ollama (default)
python chalilulz.py --model ollama:llama2

# Use with Mistral
python chalilulz.py --model mistral:mistral-small-latest --mistral-key $MISTRAL_API_KEY

# Use with Groq
python chalilulz.py --model groq:llama-3.1-70b-versatile --groq-key $GROQ_API_KEY

# Use with Gemini
python chalilulz.py --model gemini:gemini-2.0-flash --gemini-key $GOOGLE_API_KEY
```

---

## Installation

### Requirements

- Python 3.8 or higher
- API keys for your chosen provider (optional for local Ollama)

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | API key for OpenRouter |
| `MISTRAL_API_KEY` | API key for Mistral AI |
| `GROQ_API_KEY` | API key for Groq |
| `GOOGLE_API_KEY` | API key for Gemini |
| `CHALILULZ_MODEL` | Default model (e.g., `openrouter:arcee-ai/trinity-large-preview:free`) |
| `CHALILULZ_OLLAMA_HOST` | Ollama host (default: `http://localhost:11434`) |

---

## Available Tools

| Tool | Description |
|------|-------------|
| `read` | Read files with line numbers |
| `write` | Write/create files (auto mkdir) |
| `edit` | Replace unique string in files |
| `glob` | Find files by glob pattern sorted by mtime |
| `grep` | Search files by regex |
| `bash` | Execute shell commands |
| `ls` | List directory contents |
| `mkdir` | Create directories recursively |
| `rm` | Delete files or directories |
| `mv` | Move/rename files |
| `cp` | Copy files or directories |
| `find` | Recursive find by name pattern |
| `load_skill` | Load full skill instructions by name |

---

## Project Structure

```
chalilulz.py              # Standard version (full source)
golfed/
  chalminilulz.py         # Golfed version (minified)
tests/                    # Comprehensive test suite
  test_both_versions.py   # Tests for both versions
  test_tools.py           # Tool function tests
  test_parsing.py         # Model parsing tests
  test_api.py             # API call tests
  test_skills.py          # Skills loading tests
  test_schema.py          # Schema generation tests
  test_main.py            # Main loop tests
  test_utils.py           # Utility function tests
  test_do_tool_calls.py   # Tool call execution tests
AGENTS.md                 # Development guidelines
```

---

## Testing

```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Run specific test module
python -m unittest tests.test_both_versions -v
python -m unittest tests.test_tools -v
python -m unittest tests.test_parsing -v

# Test both versions specifically
python -m unittest tests.test_both_versions.TestBothVersionsTools -v
python -m unittest tests.test_both_versions.TestBothVersionsAPI -v

# Syntax check
python -m py_compile chalilulz.py
python -m py_compile golfed/chalminilulz.py

# Lint (requires ruff)
pip install ruff
ruff check chalilulz.py golfed/chalminilulz.py tests/
```

---

## Usage Examples

### Interactive Chat

```bash
$ python chalilulz.py
> Write a hello world program in Python
```

### With Custom Skills

Place skill files in `.skills/` directory:

```
.skills/
├── code-review/
│   └── SKILL.md
└── refactor/
    └── SKILL.md
```

### Model Switching

During runtime, use `/model` command to switch providers:

```
/model ollama:codellama
/model groq:llama-3.1-70b-versatile
```

---

## Configuration

### Model Syntax

```
provider:model-id
```

### Supported Providers

| Prefix | Endpoint |
|--------|----------|
| `ollama:` | `http://localhost:11434` |
| `mistral:` | `https://api.mistral.ai/v1` |
| `groq:` | `https://api.groq.com/openai/v1` |
| `gemini:` | `https://generativelanguage.googleapis.com/v1beta/openai` |
| `openrouter:` | `https://openrouter.ai/api/v1` |

---

## License

MIT License — Feel free to use, modify, and distribute.

---

<p align="center">
  Built with love for developers who love CLI tools
</p>
