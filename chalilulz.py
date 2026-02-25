#!/usr/bin/env python3
"""chalilulz — agentic coding cli · openrouter · agent skills"""

import argparse, glob as G, json, os, pathlib, re, shutil, subprocess, sys, threading, time, urllib.request, urllib.error


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
    class DefaultArgs:
        model = os.getenv(
            "CHALILULZ_MODEL", "openrouter:arcee-ai/trinity-large-preview:free"
        )
        ollama_host = os.getenv("CHALILULZ_OLLAMA_HOST", "http://localhost:11434")
        mistral_key = os.getenv("MISTRAL_API_KEY", "")
        groq_key = os.getenv("GROQ_API_KEY", "")
        gemini_key = os.getenv("GOOGLE_API_KEY", "")
        mistral_host = os.getenv("MISTRAL_HOST", "https://api.mistral.ai/v1")
        groq_host = os.getenv("GROQ_HOST", "https://api.groq.com/openai/v1")
        gemini_host = os.getenv(
            "GEMINI_HOST", "https://generativelanguage.googleapis.com/v1beta/openai"
        )

    return DefaultArgs()


if __name__ == "__main__":
    A = argparse.ArgumentParser(prog="chalilulz")
    A.add_argument(
        "--model", "-m", default="openrouter:arcee-ai/trinity-large-preview:free"
    )
    A.add_argument(
        "--ollama-host", default="http://localhost:11434", help="Ollama API host"
    )
    A.add_argument(
        "--mistral-key",
        default=os.environ.get("MISTRAL_API_KEY", ""),
        help="Mistral API key",
    )
    A.add_argument(
        "--groq-key", default=os.environ.get("GROQ_API_KEY", ""), help="Groq API key"
    )
    A.add_argument(
        "--gemini-key",
        default=os.environ.get("GOOGLE_API_KEY", ""),
        help="Google Gemini API key",
    )
    A.add_argument(
        "--mistral-host",
        default="https://api.mistral.ai/v1",
        help="Mistral API base URL",
    )
    A.add_argument(
        "--groq-host",
        default="https://api.groq.com/openai/v1",
        help="Groq API base URL",
    )
    A.add_argument(
        "--gemini-host",
        default="https://generativelanguage.googleapis.com/v1beta/openai",
        help="Gemini OpenAI-compatible base URL",
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


# ─ tools
def _r(a):
    try:
        ls = open(a["path"], encoding="utf-8", errors="replace").readlines()
        o, l = a.get("offset", 0), a.get("limit", 9999)
        return "".join(f"{o + i + 1:5}│{ln}" for i, ln in enumerate(ls[o : o + l]))
    except Exception as e:
        return f"error:{e}"


def _w(a):
    try:
        pathlib.Path(a["path"]).parent.mkdir(parents=True, exist_ok=True)
        open(a["path"], "w", encoding="utf-8").write(a["content"])
        return f"wrote {len(a['content'])}B"
    except Exception as e:
        return f"error:{e}"


def _e(a):
    try:
        t = open(a["path"], encoding="utf-8").read()
        o, n = a["old"], a["new"]
        if o not in t:
            return "error:old_string not found"
        c = t.count(o)
        if not a.get("all") and c > 1:
            return f"error:{c} hits — use all=true"
        open(a["path"], "w", encoding="utf-8").write(
            t.replace(o, n) if a.get("all") else t.replace(o, n, 1)
        )
        return f"ok({c if a.get('all') else 1} replaced)"
    except Exception as e:
        return f"error:{e}"


def _gl(a):
    try:
        b = a.get("path", ".")
        p = f"{b}/{a['pat']}".replace("//", "/")
        return (
            "\n".join(
                sorted(
                    G.glob(p, recursive=True),
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
            try:
                for i, ln in enumerate(open(fp, encoding="utf-8", errors="replace"), 1):
                    if rx.search(ln):
                        h.append(f"{fp}:{i}:{ln.rstrip()}")
            except:
                pass
        return "\n".join(h[:100]) or "none"
    except Exception as e:
        return f"error:{e}"


def _b(a):
    try:
        p = subprocess.Popen(
            a["cmd"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=a.get("cwd"),
        )
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
                )[:200]
            )
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
OPT = {"offset", "limit", "path", "cwd", "all"}


def mk_schema():
    out = []
    for name, (desc, params, _) in TOOLS.items():
        props = {}
        req = []
        for k, v in params.items():
            props[k] = {"type": v}
            if k not in OPT:
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
    return TOOLS[name][2](args)


# ─ agent skills (agentskills.io spec)
def _skill_dirs():
    cands = [pathlib.Path(os.getcwd())]
    # walk up to repo root looking for .agents/skills
    p = pathlib.Path(os.getcwd())
    while True:
        cands.append(p / ".agents" / "skills")
        cands.append(p / "skills")
        if (p / ".git").exists() or p.parent == p:
            break
        p = p.parent
    cands += [
        pathlib.Path.home() / ".agents" / "skills",
        pathlib.Path.home() / ".local" / "share" / "agent-skills",
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
            sm = skill_dir / "SKILL.md"
            if sm.is_file() and skill_dir.name not in found:
                try:
                    fm = _parse_frontmatter(sm.read_text(encoding="utf-8"))
                    if "name" in fm and "description" in fm:
                        found[skill_dir.name] = {
                            "name": fm["name"],
                            "desc": fm["description"],
                            "path": str(skill_dir),
                        }
                except:
                    pass
    return list(found.values())


def skills_prompt(skills):
    if not skills:
        return ""
    lines = ["\n## Available Skills (use load_skill to activate full instructions):"]
    for s in skills:
        lines.append(f"- {s['name']}: {s['desc'][:120]}")
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


def call_openrouter(msgs, sysp, force_no_tools=False):
    use_tools = not force_no_tools and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "temperature": 0.3,
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
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and use_tools:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_openrouter(msgs, sysp, force_no_tools=True)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return resp, use_tools


def call_ollama(msgs, sysp, force_no_tools=False):
    use_tools = not force_no_tools and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "stream": False,
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
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and use_tools:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_ollama(msgs, sysp, force_no_tools=True)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    # Transform Ollama response to OpenRouter-compatible format
    transformed = {
        "choices": [{"message": resp["message"]}],
        "usage": {
            "prompt_tokens": resp.get("prompt_eval_count", 0),
            "completion_tokens": resp.get("eval_count", 0),
        },
    }
    return transformed, use_tools


def call_openai_compatible(
    base_url, api_key, msgs, sysp, force_no_tools=False, auth_header="Bearer"
):
    use_tools = not force_no_tools and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "temperature": 0.3,
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
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
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
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return resp, use_tools


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
    global MODEL
    # Check API key for current provider
    required_key = get_required_key(PROVIDER)
    if required_key is not None and not required_key:
        print(f"\n {Re}✗ set API key for {PROVIDER} provider{R}\n")
        sys.exit(1)
    cwd = os.getcwd()
    skills = load_skills()
    sep("═", Bo + C)
    print(f" {Bo}◆ chalilulz{R}  {D}{MODEL}{R}")
    print(f" {D}cwd:{cwd}  skills:{len(skills)}{R}")
    sep("═", Bo + C)
    print(f" {D}/q quit  /c clear  /model <slug>  /skills list{R}\n")
    SP_PART = skills_prompt(skills)
    SYS = f"""Expert concise coding assistant. cwd:{cwd} os:{sys.platform}
Prefer minimal edits. No filler. Think step by step silently.{SP_PART}"""
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
            while True:
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
                    if text:
                        print(f"\n {C}◆{R} {rmd(text)}\n")
                    if not calls:
                        break
                    _do_tool_calls(calls, msgs, xml_mode=False)
                else:
                    # xml mode: strip tool_call tags from display
                    display = TC_RE.sub("", text).strip()
                    if display:
                        print(f"\n {C}◆{R} {rmd(display)}\n")
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
