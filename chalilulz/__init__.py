#!/usr/bin/env python3
"""chalilulz — agentic coding cli · openrouter · agent skills"""

import argparse, glob as G, importlib.resources as resources, json, os, pathlib, re, shutil, subprocess, sys, threading, time, urllib.request, urllib.error

__version__ = "0.0.1b6"


# Enable ANSI colors on Windows if needed
def _enable_windows_ansi():
    if sys.platform == "win32":
        try:
            from ctypes import windll, byref
            from ctypes.wintypes import DWORD

            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            IN_HANDLE = -10
            CONSOLE_MODE = DWORD()
            h = windll.kernel32.GetStdHandle(IN_HANDLE)
            if windll.kernel32.GetConsoleMode(h, byref(CONSOLE_MODE)):
                if not (CONSOLE_MODE.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                    CONSOLE_MODE.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
                    windll.kernel32.SetConsoleMode(h, CONSOLE_MODE)
        except Exception:
            pass  # Silently ignore - colors may not work


_enable_windows_ansi()

# ─ ansi
R = "\033[0m"
Bo = "\033[1m"
D = "\033[2m"
BL = "\033[34m"
C = "\033[36m"
Gr = "\033[32m"
Y = "\033[33m"
Re = "\033[31m"
M = "\033[35m"
I = "\033[3m"


# ─ args
def _get_default_args():
    conf_path = pathlib.Path.home() / ".config" / "chalilulz" / "config.json"
    conf = {}
    try:
        if conf_path.exists():
            with open(conf_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
    except Exception:
        pass

    class DefaultArgs:
        model = conf.get("model") or os.getenv(
            "CHALILULZ_MODEL", "openrouter:arcee-ai/trinity-large-preview:free"
        )
        ollama_host = conf.get("ollama_host") or os.getenv("CHALILULZ_OLLAMA_HOST", "http://localhost:11434")
        mistral_key = conf.get("mistral_key") or os.getenv("MISTRAL_API_KEY", "")
        groq_key = conf.get("groq_key") or os.getenv("GROQ_API_KEY", "")
        gemini_key = conf.get("gemini_key") or os.getenv("GOOGLE_API_KEY", "")
        mistral_host = conf.get("mistral_host") or os.getenv("MISTRAL_HOST", "https://api.mistral.ai/v1")
        groq_host = conf.get("groq_host") or os.getenv("GROQ_HOST", "https://api.groq.com/openai/v1")
        gemini_host = conf.get("gemini_host") or os.getenv(
            "GEMINI_HOST", "https://generativelanguage.googleapis.com/v1beta/openai"
        )
        yes = conf.get("yes", False)

    return DefaultArgs()


if __name__ == "__main__":
    _def = _get_default_args()
    A = argparse.ArgumentParser(prog="chalilulz")
    A.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
    A.add_argument(
        "--model", "-m", default=_def.model
    )
    A.add_argument(
        "--ollama-host", default=_def.ollama_host, help="Ollama API host"
    )
    A.add_argument(
        "--mistral-key", default=_def.mistral_key, help="Mistral API key"
    )
    A.add_argument(
        "--groq-key", default=_def.groq_key, help="Groq API key"
    )
    A.add_argument(
        "--gemini-key", default=_def.gemini_key, help="Google Gemini API key"
    )
    A.add_argument(
        "--mistral-host", default=_def.mistral_host, help="Mistral API base URL"
    )
    A.add_argument(
        "--groq-host", default=_def.groq_host, help="Groq API base URL"
    )
    A.add_argument(
        "--gemini-host", default=_def.gemini_host, help="Gemini OpenAI-compatible base URL"
    )
    A.add_argument(
        "--yes", "-y", action="store_true", default=_def.yes, help="Auto-approve tool execution"
    )
    ARGS = A.parse_args()
else:
    ARGS = _get_default_args()

MODEL = ARGS.model
KEY = os.environ.get("OPENROUTER_API_KEY", "")
OLLAMA_HOST = ARGS.ollama_host
MISTRAL_KEY = ARGS.mistral_key
MISTRAL_HOST = ARGS.mistral_host
GROQ_KEY = ARGS.groq_key
GROQ_HOST = ARGS.groq_host
GEMINI_KEY = ARGS.gemini_key
GEMINI_HOST = ARGS.gemini_host
AUTO_APPROVE = getattr(ARGS, "yes", False)


# ─ tools
def _r(a):
    try:
        with open(a["path"], encoding="utf-8", errors="replace") as f:
            ls = f.readlines()
        o, l = a.get("offset", 0), a.get("limit", 9999)
        return "".join(f"{o + i + 1:5}│{ln}" for i, ln in enumerate(ls[o : o + l]))
    except Exception as e:
        return f"error:{e}"


def _w(a):
    try:
        pathlib.Path(a["path"]).parent.mkdir(parents=True, exist_ok=True)
        with open(a["path"], "w", encoding="utf-8") as f:
            f.write(a["content"])
        return f"wrote {len(a['content'])}B"
    except Exception as e:
        return f"error:{e}"


def _e(a):
    try:
        with open(a["path"], encoding="utf-8") as f:
            t = f.read()
        o, n = a["old"], a["new"]
        if o not in t:
            return "error:old_string not found"
        c = t.count(o)
        if not a.get("all") and c > 1:
            return f"error:{c} hits — use all=true"
        with open(a["path"], "w", encoding="utf-8") as f:
            f.write(t.replace(o, n) if a.get("all") else t.replace(o, n, 1))
        return f"ok({c if a.get('all') else 1} replaced)"
    except Exception as e:
        return f"error:{e}"


def _me(a):
    try:
        with open(a["path"], encoding="utf-8") as f:
            t = f.read()
        rep = 0
        edits = json.loads(a["edits"]) if isinstance(a["edits"], str) else a["edits"]
        for e in edits:
            o, n = e.get("old", ""), e.get("new", "")
            if o and o in t:
                t = t.replace(o, n, 1)
                rep += 1
        with open(a["path"], "w", encoding="utf-8") as f:
            f.write(t)
        return f"ok({rep} replaced)"
    except Exception as e:
        return f"error:{e}"


def _ig(p):
    """Check if path is ignored (simple/common ignores)"""
    parts = pathlib.Path(p).parts
    for x in {".git", "__pycache__", "node_modules", "venv", ".venv", ".ruff_cache", "dist", "build", ".pytest_cache"}:
        if x in parts: return True
    return False


def _gl(a):
    try:
        b = a.get("path", ".")
        p = f"{b}/{a['pat']}".replace("//", "/")
        return (
            "\n".join(
                sorted(
                    (f for f in G.glob(p, recursive=True) if not _ig(f)),
                    key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0,
                    reverse=True,
                )
            )
            or "none"
        )
    except Exception as e:
        return f"error:{e}"


def _gp(a):
    try:
        rx = re.compile(a["pat"])
        h = []
        for fp in G.glob(a.get("path", ".") + "/**", recursive=True):
            if _ig(fp):
                continue
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    for i, ln in enumerate(f, 1):
                        if rx.search(ln):
                            h.append(f"{fp}:{i}:{ln.rstrip()}")
            except:
                pass
        return "\n".join(h[:100]) or "none"
    except Exception as e:
        return f"error:{e}"


def _b(a):
    try:
        with subprocess.Popen(
            a["cmd"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=a.get("cwd"),
        ) as p:
            out = []
            for ln in iter(p.stdout.readline, ""):
                print(f"  {D}│{ln.rstrip()}{R}", flush=True)
                out.append(ln)
            try:
                p.wait(timeout=120)
            except subprocess.TimeoutExpired:
                p.kill()
                out.append("(timeout)")
            return ("".join(out).strip() or "(empty)") + f"\n[exit {p.returncode}]"
    except Exception as e:
        return f"error:{e}"


def _ls(a):
    try:
        d = pathlib.Path(a.get("path", "."))
        lines = []
        for e in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name)):
            try:
                s = f"{e.stat().st_size:>10}"
            except:
                s = " " * 10
            lines.append(
                f"{'d' if e.is_dir() else 'f'} {s}  {e.name}{'/' if e.is_dir() else ''}"
            )
        return "\n".join(lines) or "(empty)"
    except Exception as e:
        return f"error:{e}"


def _mk(a):
    try:
        pathlib.Path(a["path"]).mkdir(parents=True, exist_ok=True)
        return f"created"
    except Exception as e:
        return f"error:{e}"


def _rm(a):
    try:
        p = pathlib.Path(a["path"])
        if not p.exists():
            return "error:not found"
        shutil.rmtree(p) if p.is_dir() else p.unlink()
        return "deleted"
    except Exception as e:
        return f"error:{e}"


def _mv(a):
    try:
        shutil.move(a["src"], a["dest"])
        return f"→{a['dest']}"
    except Exception as e:
        return f"error:{e}"


def _cp(a):
    try:
        s = pathlib.Path(a["src"])
        (shutil.copytree if s.is_dir() else shutil.copy2)(s, a["dest"])
        return f"→{a['dest']}"
    except Exception as e:
        return f"error:{e}"


def _fd(a):
    try:
        return (
            "\n".join(
                str(p)
                for p in sorted(
                    pathlib.Path(a.get("path", ".")).rglob(a.get("pat", "*"))
                )
                if not _ig(p)
            )[:2000]
            or "none"
        )
    except Exception as e:
        return f"error:{e}"


def _sk(a):
    """load full skill body by name"""
    name = a["name"]
    sd = _skill_dirs()
    for d in sd:
        sm = d / name / "SKILL.md"
        if sm.exists():
            try:
                body = sm.read_text(encoding="utf-8")
                # strip frontmatter
                if body.startswith("---"):
                    end = body.find("---", 3)
                    body = body[end + 3 :].strip() if end > 0 else body
                # also load scripts listing
                sc = d / name / "scripts"
                extra = ""
                if sc.is_dir():
                    extra = "\n\nScripts:\n" + "\n".join(
                        str(p) for p in sc.rglob("*") if p.is_file()
                    )
                return body + extra
            except Exception as e:
                return f"error:{e}"
    return f"skill '{name}' not found"


# (desc, params{k:type}, fn)
TOOLS = {
    "read": (
        "Read file w/ line numbers",
        {"path": "string", "offset": "integer", "limit": "integer"},
        _r,
    ),
    "write": (
        "Write/create file (auto mkdir)",
        {"path": "string", "content": "string"},
        _w,
    ),
    "edit": (
        "Replace unique string in file",
        {"path": "string", "old": "string", "new": "string", "all": "boolean"},
        _e,
    ),
    "multi_edit": (
        "Replace multiple blocks. edits is JSON array of {old,new} objects",
        {"path": "string", "edits": "string"},
        _me,
    ),
    "glob": (
        "Find files by glob sorted by mtime",
        {"pat": "string", "path": "string"},
        _gl,
    ),
    "grep": ("Search files by regex", {"pat": "string", "path": "string"}, _gp),
    "bash": ("Run shell command", {"cmd": "string", "cwd": "string"}, _b),
    "ls": ("List directory", {"path": "string"}, _ls),
    "mkdir": ("Create dir recursively", {"path": "string"}, _mk),
    "rm": ("Delete file or dir", {"path": "string"}, _rm),
    "mv": ("Move/rename", {"src": "string", "dest": "string"}, _mv),
    "cp": ("Copy file or dir", {"src": "string", "dest": "string"}, _cp),
    "find": ("rglob find by name pattern", {"pat": "string", "path": "string"}, _fd),
    "load_skill": ("Load full skill instructions by name", {"name": "string"}, _sk),
}
# optional params (types without required enforcement)
OPT = {"offset", "limit", "cwd", "all"}
# per-tool optional overrides (params that are optional for specific tools)
OPT_PARAMS = {
    "glob": {"path"},
    "grep": {"path"},
    "ls": {"path"},
    "find": {"path"},
}


def mk_schema():
    out = []
    for name, (desc, params, _) in TOOLS.items():
        props = {}
        req = []
        tool_opt = OPT | OPT_PARAMS.get(name, set())
        for k, v in params.items():
            props[k] = {"type": v}
            if k not in tool_opt:
                req.append(k)
        out.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                    "parameters": {
                        "type": "object",
                        "properties": props,
                        "required": req,
                    },
                },
            }
        )
    return out


SCHEMA = mk_schema()


# Provider handling
def parse_model(model_str):
    """Parse provider prefix from model string. Returns (provider, model_id)."""
    prefix, sep, rest = model_str.partition(":")
    if sep and prefix in ["ollama", "mistral", "groq", "gemini", "openrouter"]:
        return prefix, rest
    # No prefix: default to ollama
    return "ollama", model_str


def update_model(model_str):
    """Update global MODEL, PROVIDER, ACTUAL_MODEL."""
    global MODEL, PROVIDER, ACTUAL_MODEL
    MODEL = model_str
    PROVIDER, ACTUAL_MODEL = parse_model(model_str)


# Set initial values
PROVIDER = None
ACTUAL_MODEL = None
update_model(MODEL)


def get_required_key(provider):
    """Return the API key variable for the given provider, or None if no key needed."""
    if provider == "openrouter":
        return KEY
    elif provider == "mistral":
        return MISTRAL_KEY
    elif provider == "groq":
        return GROQ_KEY
    elif provider == "gemini":
        return GEMINI_KEY
    elif provider == "ollama":
        return None
    return None


def run_tool(name, args):
    if name not in TOOLS:
        return f"error:unknown tool {name!r}"
    if not AUTO_APPROVE and name in ("bash", "write", "edit", "rm", "mv", "cp"):
        print(f"\n {Y}⚠ Tool '{name}' requested with args: {args}{R}")
        ans = input(f" {Bo}Allow? [y/N]: {R}").strip().lower()
        if ans not in ("y", "yes"):
            return "error:user denied tool execution"
    return TOOLS[name][2](args)


# ─ bundled skills support
def _get_bundled_skills_dir():
    """Return path to skills bundled in the installed package, or None."""
    try:
        if hasattr(resources, "files"):  # Python 3.9+
            p = resources.files("chalilulz") / "skills"
        else:  # Python 3.8 fallback
            import importlib.resources

            p = pathlib.Path(importlib.resources.__path__[0]) / "chalilulz" / "skills"
        return p if p.is_dir() else None
    except:
        return None


def _ensure_global_skills():
    """Install bundled skills to global location on first run."""
    bundled = _get_bundled_skills_dir()
    if not bundled:
        return  # Not installed as package or no bundled skills

    global_dir = pathlib.Path.home() / ".local" / "share" / "chalilulz" / "skills"
    marker = global_dir / ".installed"

    # Skip if already installed
    if marker.exists():
        return

    # Create directory
    global_dir.mkdir(parents=True, exist_ok=True)

    # Copy each skill
    for skill_src in bundled.iterdir():
        if not skill_src.is_dir():
            continue
        skill_dst = global_dir / skill_src.name
        if skill_dst.exists():
            shutil.rmtree(skill_dst)
        shutil.copytree(skill_src, skill_dst)

    # Create marker file
    marker.touch()


# ─ agent skills (agentskills.io spec)
def _skill_dirs():
    _ensure_global_skills()  # Install bundled skills if needed

    cands = [pathlib.Path(os.getcwd())]
    # walk up to repo root looking for skills (agentskills.io spec locations)
    p = pathlib.Path(os.getcwd())
    while True:
        cands.append(p / ".agents" / "skills")
        cands.append(p / ".github" / "skills")
        cands.append(p / ".claude" / "skills")
        cands.append(p / ".skills")
        cands.append(p / "skills")
        if (p / ".git").exists() or p.parent == p:
            break
        p = p.parent
    cands += [
        pathlib.Path.home() / ".agents" / "skills",
        pathlib.Path.home() / ".github" / "skills",
        pathlib.Path.home() / ".claude" / "skills",
        pathlib.Path.home() / ".local" / "share" / "agent-skills",
        pathlib.Path.home() / ".local" / "share" / "chalilulz" / "skills",
    ]
    return [d for d in cands if d.is_dir()]


def _parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    fm = {}
    body = text[3:end]
    for ln in body.splitlines():
        if ":" in ln:
            k, _, v = ln.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def load_skills():
    """returns list of (name,description,path,full_loaded) — only name+desc at startup"""
    found = {}
    for sd in _skill_dirs():
        for skill_dir in sd.iterdir():
            if not skill_dir.is_dir():
                continue
            sm = skill_dir / "SKILL.md"
            if not sm.exists() or skill_dir.name in found:
                continue
            try:
                fm = _parse_frontmatter(sm.read_text(encoding="utf-8"))
                if "name" not in fm or "description" not in fm:
                    continue
                # validate dir name matches frontmatter name (agentskills.io spec)
                if fm["name"] != skill_dir.name:
                    continue
                found[skill_dir.name] = {
                    "name": fm["name"],
                    "desc": fm["description"],
                    "path": str(skill_dir),
                    "license": fm.get("license", ""),
                    "allowed_tools": fm.get("allowed-tools", ""),
                    "compatibility": fm.get("compatibility", ""),
                }
            except:
                pass
    return list(found.values())


def skills_prompt(skills):
    if not skills:
        return ""
    lines = ["\n## Available Skills (use load_skill to activate full instructions):"]
    for s in skills:
        parts = [f"- {s['name']}: {s['desc'][:120]}"]
        if s.get("license"):
            parts.append(f"  License: {s['license']}")
        if s.get("allowed_tools"):
            parts.append(f"  Tools: {s['allowed_tools']}")
        if s.get("compatibility"):
            parts.append(f"  Compat: {s['compatibility']}")
        lines.append("\n".join(parts))
    return "\n".join(lines)


# ─ spinner
class Spin:
    F = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self):
        self._e = threading.Event()
        self._t = None

    def start(self, msg="Thinking"):
        self._e.clear()

        def _r(i=0):
            w = len(msg) + 14
            while not self._e.is_set():
                print(
                    f"\r {C}{self.F[i % 10]}{R} {D}{I}{msg}{R}{D}…{R}",
                    end="",
                    flush=True,
                )
                i += 1
                time.sleep(0.08)
            print(f"\r{' ' * w}\r", end="", flush=True)

        self._t = threading.Thread(target=_r, daemon=True)
        self._t.start()

    def stop(self):
        self._e.set()
        self._t and self._t.join(0.3)


SP = Spin()
# ─ xml tool fallback parser (for models without native tool support)
TC_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.S)


def parse_xml_calls(text):
    calls = []
    for m in TC_RE.finditer(text):
        try:
            d = json.loads(m.group(1).strip())
            calls.append(d)
        except:
            pass
    return calls


XML_TOOL_INST = """
When you need a tool, output ONLY this format (one per action, then STOP and wait):
<tool_call>{"name":"TOOLNAME","args":{"key":"val"}}</tool_call>
Available tools:\n""" + "\n".join(
    f"  {k}: {v[0]} | args:{list(v[1].keys())}" for k, v in TOOLS.items()
)
# ─ api
NO_TOOLS_MODELS = set()


def read_sse_stream(resp):
    SP.stop()
    full_msg = {"role": "assistant", "content": ""}
    tool_calls = {}
    sys.stdout.write(f" {C}◆{R} ")
    sys.stdout.flush()
    usage = {}
    for line in resp:
        line = line.decode().strip()
        if not line.startswith("data: ") or line == "data: [DONE]":
            continue
        try:
            data = json.loads(line[6:])
            if "error" in data:
                raise RuntimeError(data["error"].get("message", str(data["error"])))
            if "usage" in data and data["usage"]:
                usage = data["usage"]
            if not data.get("choices"):
                continue
            delta = data["choices"][0].get("delta", {})
            if "content" in delta and delta["content"]:
                chunk = delta["content"]
                full_msg["content"] += chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
            if "tool_calls" in delta:
                for tc in delta["tool_calls"]:
                    idx = tc["index"]
                    if idx not in tool_calls:
                        tool_calls[idx] = {"id": tc.get("id", ""), "type": "function", "function": {"name": "", "arguments": ""}}
                    if tc.get("id"): tool_calls[idx]["id"] = tc["id"]
                    fn = tc.get("function", {})
                    if fn.get("name"): tool_calls[idx]["function"]["name"] += fn["name"]
                    if fn.get("arguments"): tool_calls[idx]["function"]["arguments"] += fn["arguments"]
        except Exception:
            pass
    if tool_calls:
        full_msg["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls.keys())]
    if full_msg["content"]:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return {"choices": [{"message": full_msg}], "usage": usage}


def read_ndjson_stream(resp):
    SP.stop()
    full_msg = {"role": "assistant", "content": ""}
    sys.stdout.write(f" {C}◆{R} ")
    sys.stdout.flush()
    usage = {}
    for line in resp:
        line = line.decode().strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if "error" in data:
                raise RuntimeError(data["error"].get("message", str(data["error"])))
            msg = data.get("message", {})
            if "content" in msg and msg["content"]:
                chunk = msg["content"]
                full_msg["content"] += chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
            if "tool_calls" in msg and msg["tool_calls"]:
                full_msg["tool_calls"] = msg["tool_calls"]
            if data.get("done"):
                usage = {"prompt_tokens": data.get("prompt_eval_count", 0), "completion_tokens": data.get("eval_count", 0)}
        except Exception:
            pass
    if full_msg["content"]:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return {"choices": [{"message": full_msg}], "usage": usage}


def call_openrouter(msgs, sysp, force_no_tools=False):
    use_tools = not force_no_tools and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "temperature": 0.3,
        "stream": True,
    }
    if use_tools:
        body["tools"] = SCHEMA
        body["tool_choice"] = "auto"
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}",
            "HTTP-Referer": "https://github.com/chalilulz",
            "X-Title": "chalilulz",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = read_sse_stream(resp)
        return result, use_tools
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and use_tools:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_openrouter(msgs, sysp, force_no_tools=True)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")



def call_ollama(msgs, sysp, force_no_tools=False):
    use_tools = not force_no_tools and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "stream": True,
        "options": {"temperature": 0.3},
    }
    if use_tools:
        body["tools"] = SCHEMA
    url = OLLAMA_HOST.rstrip("/") + "/api/chat"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        return read_ndjson_stream(resp), use_tools
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and use_tools:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_ollama(msgs, sysp, force_no_tools=True)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")



def call_openai_compatible(
    base_url, api_key, msgs, sysp, force_no_tools=False, auth_header="Bearer"
):
    use_tools = not force_no_tools and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "temperature": 0.3,
        "stream": True,
    }
    if use_tools:
        body["tools"] = SCHEMA
        body["tool_choice"] = "auto"
    headers = {"Content-Type": "application/json"}
    if auth_header == "Bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_header == "x-goog-api-key":
        headers["x-goog-api-key"] = api_key
    url = base_url.rstrip("/") + "/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers=headers,
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        return read_sse_stream(resp), use_tools
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and use_tools:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_openai_compatible(
                base_url,
                api_key,
                msgs,
                sysp,
                force_no_tools=True,
                auth_header=auth_header,
            )
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")



def call_mistral(msgs, sysp, force_no_tools=False):
    return call_openai_compatible(
        MISTRAL_HOST, MISTRAL_KEY, msgs, sysp, force_no_tools, "Bearer"
    )


def call_groq(msgs, sysp, force_no_tools=False):
    return call_openai_compatible(
        GROQ_HOST, GROQ_KEY, msgs, sysp, force_no_tools, "Bearer"
    )


def call_gemini(msgs, sysp, force_no_tools=False):
    return call_openai_compatible(
        GEMINI_HOST, GEMINI_KEY, msgs, sysp, force_no_tools, "x-goog-api-key"
    )


def call_api(msgs, sysp, force_no_tools=False):
    if PROVIDER == "openrouter":
        return call_openrouter(msgs, sysp, force_no_tools)
    elif PROVIDER == "ollama":
        return call_ollama(msgs, sysp, force_no_tools)
    elif PROVIDER == "mistral":
        return call_mistral(msgs, sysp, force_no_tools)
    elif PROVIDER == "groq":
        return call_groq(msgs, sysp, force_no_tools)
    elif PROVIDER == "gemini":
        return call_gemini(msgs, sysp, force_no_tools)
    else:
        raise RuntimeError(f"Unknown provider: {PROVIDER}")


# ─ ui helpers
def cols():
    return min(shutil.get_terminal_size((88, 24)).columns, 100)


def sep(c="─", col=D):
    print(f"{col}{c * cols()}{R}")


def pvw(s, n=74):
    ls = s.split("\n")
    p = ls[0][:n]
    if len(ls) > 1:
        p += f"{D} +{len(ls) - 1}L{R}"
    elif len(ls[0]) > n:
        p += f"{D}…{R}"
    return p


def rmd(t):
    t = re.sub(r"```\w*\n(.*?)```", f"{D}[code]{R}\\1{D}[/code]{R}", t, flags=re.S)
    t = re.sub(r"`([^`\n]+)`", f"{Y}\\1{R}", t)
    t = re.sub(r"\*\*(.+?)\*\*", f"{Bo}\\1{R}", t)
    t = re.sub(r"\*([^*\n]+)\*", f"{I}\\1{R}", t)
    t = re.sub(r"^(#{1,6})\s+(.+)$", lambda m: f"{Bo}{C}{m.group(1)} {m.group(2)}{R}", t, flags=re.M)
    t = re.sub(r"^(\s*[-*])\s+(.+)$", lambda m: f"{Bo}{M}{m.group(1)}{R} {m.group(2)}", t, flags=re.M)
    return t


TIC = {
    "read": "📖",
    "write": "✏️",
    "edit": "🔧",
    "glob": "🔍",
    "grep": "🔎",
    "bash": "⚡",
    "ls": "📂",
    "mkdir": "📁",
    "rm": "🗑",
    "mv": "↪",
    "cp": "📋",
    "find": "🔎",
    "load_skill": "🧠",
}


def show_tc(name, args, res):
    ic = TIC.get(name, "⚙")
    av = str(list(args.values())[0])[:64] if args else ""
    print(f"\n {Gr}{ic} {Bo}{name}{R}{D}({av}){R}")
    print(f"   {D}⎿ {pvw(str(res))}{R}")


# ─ agentic loop helpers
def _do_tool_calls(calls, msgs, xml_mode):
    """execute tool calls (list of dicts: name+args or id+function), append results, return result msgs"""
    results = []
    for tc in calls:
        if xml_mode:
            name = tc.get("name", "")
            args = tc.get("args", {})
        else:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"].get("arguments") or "{}")
            except:
                args = {}
        res = run_tool(name, args)
        show_tc(name, args, res)
        if not xml_mode:
            if PROVIDER == "ollama":  # Ollama format
                results.append({"role": "tool", "tool_name": name, "content": str(res)})
            else:  # OpenAI-compatible format (openrouter, mistral, groq, gemini)
                results.append(
                    {"role": "tool", "tool_call_id": tc["id"], "content": str(res)}
                )
        else:
            results.append(
                {
                    "role": "user",
                    "content": f"<tool_result>{json.dumps({'name': name, 'result': str(res)})}</tool_result>",
                }
            )
    msgs.extend(results)
    return results


# ─ main
def main():
    try:
        import readline, glob
        COMMANDS = ["/model ", "/skills", "/save ", "/load ", "/yes", "/no", "/q", "/c", "/help", "exit", "quit"]
        def completer(text, state):
            line = readline.get_line_buffer()
            if not line or line.startswith("/"):
                matches = [c for c in COMMANDS if c.startswith(text)]
            else:
                matches = glob.glob(text + '*')
                matches = [m + os.sep if os.path.isdir(m) else m for m in matches]
            try:
                return matches[state]
            except IndexError:
                return None
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims(" \t\n;")
    except ImportError:
        pass

    global MODEL, AUTO_APPROVE
    # Check API key for current provider
    required_key = get_required_key(PROVIDER)
    if required_key is not None and not required_key:
        print(f"\n {Re}✗ set API key for {PROVIDER} provider{R}\n")
        sys.exit(1)
        
    MAX_TOOL_ROUNDS = 25
    cwd = os.getcwd()
    skills = load_skills()
    sep("═", Bo + C)
    print(f" {Bo}◆ chalilulz{R}  {D}{MODEL}{R}")
    print(f" {D}cwd:{cwd}  skills:{len(skills)}{R}")
    sep("═", Bo + C)
    print(f" {D}/q quit  /c clear  /model <slug>  /skills list  /help{R}\n")
    SP_PART = skills_prompt(skills)
    SYS = f"""You are Chalilulz, an expert, concise agentic coding assistant.
Environment: OS={sys.platform}, CWD={cwd}

Guidelines:
1. Be extremely concise. No filler, pleasantries, or wrapping text.
2. Think step-by-step silently before acting.
3. Use tools efficiently. Chain them together to analyze, plan, and execute.
4. When writing/editing files, ensure you understand the surrounding code. Use the read tool first if unsure.
5. Stop and ask the user for clarification if you are stuck or need architectural decisions.
6. Do not enter infinite loops. If you encounter the same error multiple times, ask the user for help.
{SP_PART}"""
    XML_SYS = SYS + XML_TOOL_INST
    msgs = []
    while True:
        try:
            sep()
            try:
                ui = input(f" {Bo}{BL}❯ {R}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n {D}bye{R}")
                break
            if not ui:
                continue
            if ui in ("/q", "exit", "quit"):
                print(f"\n {D}bye{R}")
                break
            if ui == "/c":
                msgs = []
                print(f"\n {Gr}✓ cleared{R}")
                continue
            if ui == "/yes":
                AUTO_APPROVE = True
                print(f"\n {Gr}✓ auto-approve enabled{R}")
                continue
            if ui == "/no":
                AUTO_APPROVE = False
                print(f"\n {Gr}✓ auto-approve disabled{R}")
                continue
            if ui.startswith("/save "):
                name = ui[6:].strip()
                p = pathlib.Path.home() / ".local" / "share" / "chalilulz" / "sessions" / f"{name}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(msgs), encoding="utf-8")
                print(f"\n {Gr}✓ saved session to {name}{R}")
                continue
            if ui.startswith("/load "):
                name = ui[6:].strip()
                p = pathlib.Path.home() / ".local" / "share" / "chalilulz" / "sessions" / f"{name}.json"
                if p.exists():
                    try:
                        msgs = json.loads(p.read_text(encoding="utf-8"))
                        print(f"\n {Gr}✓ loaded session {name} ({len(msgs)} msgs){R}")
                    except Exception as e:
                        print(f"\n {Re}✗ failed to load session: {e}{R}")
                else:
                    print(f"\n {Re}✗ session {name} not found{R}")
                continue
            if ui == "/help":
                print(f"\n {Bo}Commands:{R}")
                print(f"  {C}/q, quit, exit{R}  Quit")
                print(f"  {C}/c{R}               Clear session")
                print(f"  {C}/model <slug>{R}    Change model (e.g., ollama:llama3)")
                print(f"  {C}/skills{R}          List loaded skills")
                print(f"  {C}/yes, /no{R}        Toggle auto-approve for tools")
                print(f"  {C}/save <name>{R}     Save current session")
                print(f"  {C}/load <name>{R}     Load a saved session")
                print(f"  {C}/help{R}            Show this help")
                continue
            if ui.startswith("/model "):
                new_model = ui[7:].strip()
                update_model(new_model)
                required_key = get_required_key(PROVIDER)
                if required_key is None:
                    pass
                elif not required_key:
                    print(f"\n {Y}⚠ missing API key for {PROVIDER} provider{R}")
                print(f"\n {Gr}✓ model→{Bo}{MODEL}{R}")
                continue
            if ui == "/skills":
                if not skills:
                    print(f"\n {D}no skills found{R}")
                else:
                    print(f"\n {Bo}Skills:{R}")
                    for s in skills:
                        print(f"  {C}{s['name']}{R} {D}{s['desc'][:80]}{R}")
                    print(f"  {D}paths:{[s['path'] for s in skills]}{R}")
                continue
            msgs.append({"role": "user", "content": ui})
            sep()
            rounds = 0
            while True:
                curr_tokens = len(json.dumps(msgs)) // 4
                while curr_tokens > 60000 and len(msgs) > 5:
                    print(f"\n {Y}⚠ context large (~{curr_tokens} tokens) — auto-truncating oldest messages{R}")
                    msgs.pop(0)
                    curr_tokens = len(json.dumps(msgs)) // 4
                
                if rounds >= MAX_TOOL_ROUNDS:
                    print(f"\n {Y}⚠ max tool rounds ({MAX_TOOL_ROUNDS}) reached — stopping to prevent infinite loop{R}\n")
                    break
                rounds += 1
                SP.start()
                try:
                    resp, use_tools = call_api(
                        msgs, SYS if ACTUAL_MODEL not in NO_TOOLS_MODELS else XML_SYS
                    )
                except Exception as e:
                    SP.stop()
                    print(f"\n {Re}✗ {e}{R}\n")
                    msgs.pop()
                    break
                SP.stop()
                ch = resp["choices"][0]
                msg = ch["message"]
                usage = resp.get("usage", {})
                if usage:
                    print(
                        f" {D}↑{usage.get('prompt_tokens', '-')} ↓{usage.get('completion_tokens', '-')}{R}"
                    )
                text = (msg.get("content") or "").strip()
                calls = msg.get("tool_calls") or []
                if use_tools:
                    msgs.append(msg)
                    if not calls:
                        break
                    _do_tool_calls(calls, msgs, xml_mode=False)
                else:
                    # xml mode: strip tool_call tags from display just to clean history if needed
                    display = TC_RE.sub("", text).strip()
                    xml_calls = parse_xml_calls(text)
                    msgs.append({"role": "assistant", "content": text})
                    if not xml_calls:
                        break
                    _do_tool_calls(xml_calls, msgs, xml_mode=True)
                print()
        except Exception as e:
            SP.stop()
            print(f"\n {Re}✗ {e}{R}\n")


if __name__ == "__main__":
    main()
