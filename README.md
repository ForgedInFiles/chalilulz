# chalilulz

<img align="right" width="180" src="https://placehold.co/180x120?text=Your+logo+here">

**[Professional][Warm] An agentic coding CLI that brings multiple LLM providers together with skills, tools, and a delightful REPL experience.**

Work with your codebase using natural language—read files, make edits, run commands, and get AI assistance—all from your terminal.

---

## ✨ Why chalilulz?

- **Provider freedom**: OpenRouter, Ollama (local), Mistral AI, Groq, Gemini—pick your AI, no lock-in
- **Smart tool use**: The assistant can read, edit, search, and run commands automatically
- **Skills system**: Import community or custom skills to extend capabilities
- **Zero dependencies**: Just Python 3.8+ and you're ready
- **Cross-platform**: Windows, macOS, Linux—ANSI colors work everywhere
- **Fully tested**: Comprehensive test suite ensures reliability

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- For cloud providers: respective API keys
- For Ollama: [Ollama](https://ollama.ai) running locally

### Installation

```bash
# Clone or download chalilullz.py
chmod +x chalilulz.py
```

### First run

```bash
# Uses OpenRouter by default (set OPENROUTER_API_KEY)
OPENROUTER_API_KEY=your-key python chalilulz.py
```

### Try other providers

```bash
# Mistral AI
MISTRAL_API_KEY=sk-... python chalilulz.py --model mistral:mistral-small-latest

# Groq (fast inference)
GROQ_API_KEY=... python chalilulz.py --model groq:llama-3.3-70b-versatile

# Google Gemini
GOOGLE_API_KEY=... python chalilulz.py --model gemini:gemini-2.0-flash

# Ollama (local, no API key needed)
python chalilulz.py --model ollama:llama2
```

---

## 🛠️ Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `-m MODEL`, `--model MODEL` | `openrouter:arcee-ai/trinity-large-preview:free` | LLM model to use (provider prefix optional) |
| `--ollama-host` | `http://localhost:11434` | Ollama API host |
| `--mistral-key` | `$MISTRAL_API_KEY` | Mistral API key |
| `--groq-key` | `$GROQ_API_KEY` | Groq API key |
| `--gemini-key` | `$GOOGLE_API_KEY` | Google Gemini API key |
| `--mistral-host` | `https://api.mistral.ai/v1` | Mistral API base URL |
| `--groq-host` | `https://api.groq.com/openai/v1` | Groq API base URL |
| `--gemini-host` | `https://generativelanguage.googleapis.com/v1beta/openai` | Gemini OpenAI-compatible base URL |

---

## 💬 REPL Commands

Inside the interactive session:

| Command | Description |
|---------|-------------|
| `/q`, `quit`, `exit` | Quit chalilulz |
| `/c` | Clear conversation history |
| `/model <slug>` | Switch model (e.g., `/model groq:llama-3.3-70b-versatile`) |
| `/skills` | List loaded skills |

---

## 🔧 Built-in Tools

chalilulz comes with powerful tools the AI can use to help you:

| Tool | Description |
|------|-------------|
| `read` | Read file with line numbers |
| `write` | Write/create file (auto mkdir) |
| `edit` | Replace unique string in file |
| `glob` | Find files by glob sorted by modification time |
| `grep` | Search files by regex |
| `bash` | Run shell command (uses system shell: `cmd.exe` on Windows, `/bin/sh` on Unix) |
| `ls` | List directory contents |
| `mkdir` | Create directory recursively |
| `rm` | Delete file or directory |
| `mv` | Move/rename |
| `cp` | Copy file or directory |
| `find` | Recursive find by name pattern |
| `load_skill` | Load full skill instructions by name |

---

## 🧠 Agent Skills

chalilulz supports the [Agent Skills](https://agentskills.io) format. Skills extend the assistant's capabilities with domain-specific knowledge, templates, and workflows.

### Skill Directory Structure

```
skills/
├── skill-name/
│   ├── SKILL.md          # Required (YAML frontmatter + Markdown)
│   ├── scripts/          # Optional: executable code
│   ├── references/       # Optional: additional docs
│   └── assets/           # Optional: templates, data
```

### Skill Discovery

Skills are auto-discovered from:

- `.skills/` (project root)
- `.agents/skills/`
- `skills/`
- `~/.agents/skills/`
- `~/.local/share/agent-skills/`

Each `SKILL.md` requires YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description of what this skill does
---
```

The skill appears in the system prompt at startup. Use the `load_skill` tool to retrieve full instructions when needed.

---

## 🌐 Provider Model Strings

Choose any model from these providers:

- **Ollama**: `model-name:tag` or just `model-name` (e.g., `llama2`, `mistral:latest`)
- **Mistral**: `mistral:mistral-small-latest`, `mistral:ministral-3-latest`
- **Groq**: `groq:llama-3.3-70b-versatile`, `groq:gemma2-9b-it`
- **Gemini**: `gemini:gemini-2.0-flash`, `gemini:gemini-1.5-pro`
- **OpenRouter**: `openrouter:arcee-ai/trinity-large-preview:free`, `openrouter:anthropic/claude-3-haiku`

The prefix determines the API endpoint and authentication method. No prefix? It's Ollama.

---

## 🧪 Testing

```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Run specific test module
python -m unittest tests.test_parsing -v

# Run specific test class
python -m unittest tests.test_tools.TestReadTool -v

# Run single test
python -m unittest tests.test_api.TestOpenRouterAPI.test_call_openrouter_success -v
```

---

## 📦 Environment Variables

| Variable | Provider | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter | API key |
| `MISTRAL_API_KEY` | Mistral | API key |
| `GROQ_API_KEY` | Groq | API key |
| `GOOGLE_API_KEY` | Gemini | API key |
| `CHALILULZ_MODEL` | All | Default model (overrides CLI default) |
| `CHALILULZ_OLLAMA_HOST` | Ollama | Override Ollama host |
| `MISTRAL_HOST` | Mistral | Override Mistral API base URL |
| `GROQ_HOST` | Groq | Override Groq base URL |
| `GEMINI_HOST` | Gemini | Override Gemini base URL |

---

## 🤝 Contributing

We welcome contributions! Please see `AGENTS.md` for code style guidelines and development workflow.

### Quick development pointers:

- 4 spaces, no tabs; line length ≤100
- Imports: standard → third-party → local, sorted alphabetically
- Functions/variables: `snake_case`; constants: `SCREAMING_SNAKE_CASE`
- Error handling: tool functions return `f"error:{e}"` strings
- Guard argparse with `if __name__ == "__main__":` for import safety

```bash
# Lint
pip install ruff
ruff check chalilulz.py tests/

# Type check (optional)
pip install mypy
mypy --ignore-missing-imports chalilulz.py
```

---

## 📄 License

MIT (or include license from project if different)

---

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai) — Unified access to many models
- [Ollama](https://ollama.ai) — Run LLMs locally
- [Mistral AI](https://mistral.ai) — High-performance European models
- [Groq](https://groq.com) — Ultra-fast inference
- [Google Gemini](https://ai.google.dev/gemini-api) — Google's multimodal AI
- [Agent Skills spec](https://agentskills.io) — Portable skill definitions

---

<p align="center">Built with care for developers who love AI and terminal tools. Enjoy! 🚀</p>
