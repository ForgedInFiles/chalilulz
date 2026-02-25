# chalilulz

**An agentic coding CLI with multi-provider LLM support and skills.**

```bash
python chalilulz.py --model mistral:mistral-small-latest --mistral-key $MISTRAL_API_KEY
```

```bash
python chalilulz.py --model ollama:ministral-3:latest
```

```bash
python chalilulz.py --model gemini:gemini-2.0-flash --gemini-key $GOOGLE_API_KEY
```

---

## Features

- **Multi-provider support**: OpenRouter, Ollama (local), Mistral AI, Groq, Google Gemini
- **Automatic provider detection**: Use prefixes like `mistral:`, `groq:`, `gemini:`, `openrouter:`; no prefix → Ollama (default `ministral-3:latest`)
- **Tool calling** with fallback to XML mode for models without native tool support
- **Agent Skills** (agentskills.io compatible): Load skill instructions from `.skills/` or `~/.config/chalice/skills/`
- **Rich interactive REPL** with `/commands` for control
- **Built-in tools**: read, write, edit, glob, grep, bash, ls, mkdir, rm, mv, cp, find, load_skill
- **Zero dependencies** beyond Python standard library

---

## Quick Start

### Prerequisites

- Python 3.8+
- For Ollama: [Ollama](https://ollama.ai) running locally (`ollama serve`)
- For cloud providers: API keys

### Installation

```bash
# Clone or download chalilulz.py
chmod +x chalilulz.py
```

### Running

```bash
# Default (Ollama, local)
python chalilulz.py

# With specific provider
MISTRAL_API_KEY=sk-... python chalilulz.py --model mistral:mistral-small-latest
GROQ_API_KEY=... python chalilulz.py --model groq:llama-3.3-70b-versatile
GOOGLE_API_KEY=... python chalilulz.py --model gemini:gemini-2.0-flash
OPENROUTER_API_KEY=... python chalilulz.py --model openrouter:arcee-ai/trinity-large-preview:free
```

---

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `-m MODEL`, `--model MODEL` | `ministral-3:latest` | LLM model to use (provider prefix optional) |
| `--ollama-host` | `http://localhost:11434` | Ollama API host |
| `--mistral-key` | `$MISTRAL_API_KEY` | Mistral API key |
| `--groq-key` | `$GROQ_API_KEY` | Groq API key |
| `--gemini-key` | `$GOOGLE_API_KEY` | Google Gemini API key |
| `--mistral-host` | `https://api.mistral.ai/v1` | Mistral API base URL |
| `--groq-host` | `https://api.groq.com/openai/v1` | Groq API base URL |
| `--gemini-host` | `https://generativelanguage.googleapis.com/v1beta/openai` | Gemini OpenAI-compatible base URL |

---

## REPL Commands

Inside the interactive session:

| Command | Description |
|---------|-------------|
| `/q`, `quit`, `exit` | Quit |
| `/c` | Clear conversation history |
| `/model <slug>` | Switch model (e.g., `/model groq:llama-3.3-70b-versatile`) |
| `/skills` | List loaded skills |

---

## Provider Model Strings

- **Ollama** (default): `model-name:tag` or just `model-name` (e.g., `ministral-3:latest`, `llama2`)
- **Mistral**: `mistral:mistral-small-latest`, `mistral:ministral-3-latest`
- **Groq**: `groq:llama-3.3-70b-versatile`, `groq:gemma2-9b-it`
- **Gemini**: `gemini:gemini-2.0-flash`, `gemini:gemini-1.5-pro`
- **OpenRouter**: `openrouter:arcee-ai/trinity-large-preview:free`, `openrouter:anthropic/claude-3-haiku`

The prefix determines the API endpoint and authentication method.

---

## Agent Skills

chalilulz supports the [Agent Skills](https://agentskills.io) format. Skills extend the agent's capabilities with domain-specific knowledge and workflows.

### Skill Directory Structure

```
skills/
├── skill-name/
│   ├── SKILL.md          # Required (YAML frontmatter + Markdown)
│   ├── scripts/          # Optional: executable code
│   ├── references/       # Optional: additional docs
│   └── assets/           # Optional: templates, data
```

### Loading Skills

Skills are auto-discovered from:

- `.skills/` (project root)
- `.agents/skills/`
- `skills/`
- `~/.agents/skills/`
- `~/.local/share/agent-skills/`

Each `SKILL.md` must have YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description of what this skill does
---
```

The skill appears in the system prompt at startup. Use the `load_skill` tool to retrieve full instructions when needed.

### Built-in Skills

- `code-review`: Reviews code for bugs, security, and best practices
- `create-skill`: Framework for creating new skills
- `refactor-code`: Code refactoring guidance
- `codebase-architecting`: Codebase analysis and architecture
- `voxel-game-developing`: 3D voxel game creation (HTML/JS)
- `voxel-game-rust`: 3D voxel game creation (Rust/Bevy)

---

## Built-in Tools

| Tool | Description |
|------|-------------|
| `read` | Read file with line numbers |
| `write` | Write/create file (auto mkdir) |
| `edit` | Replace unique string in file |
| `glob` | Find files by glob sorted by mtime |
| `grep` | Search files by regex |
| `bash` | Run shell command (with optional cwd) |
| `ls` | List directory contents |
| `mkdir` | Create directory recursively |
| `rm` | Delete file or directory |
| `mv` | Move/rename |
| `cp` | Copy file or directory |
| `find` | Recursive find by name pattern |
| `load_skill` | Load full skill instructions by name |

---

## How It Works

1. **Provider selection**: Model string prefix determines API endpoint and auth header
2. **Tool schema**: Dynamic JSON Schema generated from `TOOLS` dict
3. **Tool calls**: Native tool calls for OpenAI-compatible providers; Ollama uses custom format; fallback XML mode for non-tool models
4. **Response transformation**: Ollama responses normalized to OpenAI format
5. **Skills integration**: Frontmatter parsed at startup; full content loaded on demand via `load_skill`

---

## Testing

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

## Development

### Code Style

- 4 spaces, no tabs; line length ≤100
- Imports: standard → third-party → local, sorted alphabetically
- Functions/variables: `snake_case`; constants: `SCREAMING_SNAKE_CASE`
- Error handling: tool functions return `f"error:{e}"` strings
- Guard argparse with `if __name__ == "__main__":` for import safety

See `AGENTS.md` for complete guidelines.

### Lint & Type Check

```bash
pip install ruff
ruff check chalilulz.py tests/

pip install mypy
mypy --ignore-missing-imports chalilulz.py
```

---

## Environment Variables

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

## License

MIT (or include license from project if different)

---

## Acknowledgments

- [OpenRouter](https://openrouter.ai)
- [Ollama](https://ollama.ai)
- [Mistral AI](https://mistral.ai)
- [Groq](https://groq.com)
- [Google Gemini](https://ai.google.dev/gemini-api)
- [Agent Skills spec](https://agentskills.io)
