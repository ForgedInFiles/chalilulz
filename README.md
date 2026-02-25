# chalilulz

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/LLM-Cli-orange.svg" alt="LLM CLI">
  <img src="https://img.shields.io/badge/open-source-green.svg" alt="Open Source">
  <img src="https://img.shields.io/badge/platform-cross--platform-yellow.svg" alt="Cross Platform">
</p>

<p align="center">
  <strong>Agentic coding CLI with multi-provider LLM support</strong><br>
  <em>OpenRouter · Ollama · Mistral · Groq · Gemini</em>
</p>

---

## ✨ Features

- **Multi-Provider Support** — Seamlessly switch between OpenRouter, Ollama, Mistral, Groq, and Gemini
- **Built-in Tools** — File operations, grep search, glob patterns, bash execution, and more
- **Agent Skills** — Load custom skill sets from `.skills/` directory
- **Cross-Platform** — Works on Linux, macOS, and Windows with ANSI color support
- **Zero Dependencies** — Pure Python standard library — no external packages required

---

## 🚀 Quick Start

```bash
# Clone and run
python chalilulz.py

# Or set a specific model
python chalilulz.py --model openrouter:arcee-ai/trinity-large-preview:free

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

## 📦 Installation

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

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `r` | Read files with syntax highlighting |
| `w` | Write content to files |
| `e` | Edit specific sections of files |
| `gl` | Glob pattern matching for files |
| `gp` | Grep search through file contents |
| `b` | Execute bash commands |
| `ls` | List directory contents |
| `mk` | Create new directories |
| `rm` | Remove files or directories |
| `mv` | Move/rename files |
| `cp` | Copy files |
| `fd` | Find files by name |
| `sk` | Execute agent skills |

---

## 📁 Project Structure

```
chalilulz.py          # Main CLI application
chalminilulz.py       # Lightweight variant
tests/                # Test suite
  ├── test_parsing.py
  ├── test_schema.py
  ├── test_tools.py
  └── test_api.py
AGENTS.md             # Development guidelines
```

---

## 🧪 Testing

```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Run specific test module
python -m unittest tests.test_parsing -v
python -m unittest tests.test_tools -v

# Syntax check
python -m py_compile chalilulz.py

# Lint (requires ruff)
pip install ruff
ruff check chalilulz.py tests/
```

---

## 💡 Usage Examples

### Interactive Chat

```bash
$ python chalilulz.py
> Write a hello world program in Python
```

### With Custom Skills

Place skill files in `.skills/` directory and the CLI will automatically load them:

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
```

---

## 🔧 Configuration

### Model Syntax

```
provider:model-id
```

**Supported Providers:**

| Prefix | Endpoint |
|--------|----------|
| `ollama:` | `http://localhost:11434` |
| `mistral:` | `https://api.mistral.ai/v1` |
| `groq:` | `https://api.groq.com/openai/v1` |
| `gemini:` | `https://generativelanguage.googleapis.com/v1beta/openai` |
| `openrouter:` | `https://openrouter.ai/api/v1` |

---

## 📝 License

MIT License — Feel free to use, modify, and distribute.

---

<p align="center">
  <sub>Built with ♡ for developers who love CLI tools</sub>
</p>
