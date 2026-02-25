#!/usr/bin/env python3
import argparse, glob as G, json, os, pathlib, re, shutil, subprocess, sys, threading, time, urllib.request, urllib.error


def _wa():
    if sys.platform == "win32":
        try:
            from ctypes import windll, byref
            from ctypes.wintypes import DWORD

            EVTP = 0x0004
            h = windll.kernel32.GetStdHandle(-10)
            CM = DWORD()
            if windll.kernel32.GetConsoleMode(h, byref(CM)):
                if not (CM.value & EVTP):
                    CM.value |= EVTP
                    windll.kernel32.SetConsoleMode(h, CM)
        except:
            pass


_wa()
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


def _gda():
    class _:
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

    return _()


if __name__ == "__main__":
    A = argparse.ArgumentParser(prog="chalilulz")
    A.add_argument(
        "--model", "-m", default="openrouter:arcee-ai/trinity-large-preview:free"
    )
    A.add_argument("--ollama-host", default="http://localhost:11434")
    A.add_argument("--mistral-key", default=os.environ.get("MISTRAL_API_KEY", ""))
    A.add_argument("--groq-key", default=os.environ.get("GROQ_API_KEY", ""))
    A.add_argument("--gemini-key", default=os.environ.get("GOOGLE_API_KEY", ""))
    A.add_argument("--mistral-host", default="https://api.mistral.ai/v1")
    A.add_argument("--groq-host", default="https://api.groq.com/openai/v1")
    A.add_argument(
        "--gemini-host",
        default="https://generativelanguage.googleapis.com/v1beta/openai",
    )
    ARGS = A.parse_args()
else:
    ARGS = _gda()
MODEL = ARGS.model
KEY = os.environ.get("OPENROUTER_API_KEY", "")
OLLAMA_HOST = ARGS.ollama_host
MISTRAL_KEY = ARGS.mistral_key
MISTRAL_HOST = ARGS.mistral_host
GROQ_KEY = ARGS.groq_key
GROQ_HOST = ARGS.groq_host
GEMINI_KEY = ARGS.gemini_key
GEMINI_HOST = ARGS.gemini_host


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
        return "created"
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
    nm = a["name"]
    for d in _sdirs():
        sm = d / nm / "SKILL.md"
        if sm.exists():
            try:
                b = sm.read_text(encoding="utf-8")
                if b.startswith("---"):
                    e = b.find("---", 3)
                    b = b[e + 3 :].strip() if e > 0 else b
                sc = d / nm / "scripts"
                x = ""
                if sc.is_dir():
                    x = "\n\nScripts:\n" + "\n".join(
                        str(p) for p in sc.rglob("*") if p.is_file()
                    )
                return b + x
            except Exception as e:
                return f"error:{e}"
    return f"skill '{nm}' not found"


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


def parse_model(m):
    px, sp, rest = m.partition(":")
    return (
        (px, rest)
        if sp and px in ["ollama", "mistral", "groq", "gemini", "openrouter"]
        else ("ollama", m)
    )


def update_model(m):
    global MODEL, PROVIDER, ACTUAL_MODEL
    MODEL = m
    PROVIDER, ACTUAL_MODEL = parse_model(m)


PROVIDER = ACTUAL_MODEL = None
update_model(MODEL)


def get_key(p):
    return {
        "openrouter": KEY,
        "mistral": MISTRAL_KEY,
        "groq": GROQ_KEY,
        "gemini": GEMINI_KEY,
    }.get(p)


def run_tool(n, a):
    return TOOLS[n][2](a) if n in TOOLS else f"error:unknown tool {n!r}"


def _sdirs():
    c = [pathlib.Path(os.getcwd())]
    p = pathlib.Path(os.getcwd())
    while True:
        c += [p / ".agents" / "skills", p / ".skills", p / "skills"]
        if (p / ".git").exists() or p.parent == p:
            break
        p = p.parent
    c += [
        pathlib.Path.home() / ".agents" / "skills",
        pathlib.Path.home() / ".local" / "share" / "agent-skills",
    ]
    return [d for d in c if d.is_dir()]


def _pfm(t):
    if not t.startswith("---"):
        return {}
    e = t.find("---", 3)
    if e < 0:
        return {}
    fm = {}
    for ln in t[3:e].splitlines():
        if ":" in ln:
            k, _, v = ln.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def load_skills():
    found = {}
    for sd in _sdirs():
        for sd2 in sd.iterdir():
            sm = sd2 / "SKILL.md"
            if sm.is_file() and sd2.name not in found:
                try:
                    fm = _pfm(sm.read_text(encoding="utf-8"))
                    if "name" in fm and "description" in fm:
                        found[sd2.name] = {
                            "name": fm["name"],
                            "desc": fm["description"],
                            "path": str(sd2),
                        }
                except:
                    pass
    return list(found.values())


def skills_prompt(sk):
    if not sk:
        return ""
    return (
        "\n## Available Skills (use load_skill to activate full instructions):\n"
        + "\n".join(f"- {s['name']}: {s['desc'][:120]}" for s in sk)
    )


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
TC_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.S)


def parse_xml_calls(t):
    calls = []
    for m in TC_RE.finditer(t):
        try:
            calls.append(json.loads(m.group(1).strip()))
        except:
            pass
    return calls


XML_TOOL_INST = (
    '\nWhen you need a tool, output ONLY this format (one per action, then STOP and wait):\n<tool_call>{"name":"TOOLNAME","args":{"key":"val"}}</tool_call>\nAvailable tools:\n'
    + "\n".join(f"  {k}: {v[0]} | args:{list(v[1].keys())}" for k, v in TOOLS.items())
)
NO_TOOLS_MODELS = set()


def _call_oc(base, key, msgs, sysp, fnt=False, ah="Bearer"):
    ut = not fnt and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "temperature": 0.3,
    }
    if ut:
        body["tools"] = SCHEMA
        body["tool_choice"] = "auto"
    hd = {"Content-Type": "application/json"}
    if ah == "Bearer":
        hd["Authorization"] = f"Bearer {key}"
    elif ah == "x-goog-api-key":
        hd["x-goog-api-key"] = key
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers=hd,
        method="POST",
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and ut:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return _call_oc(base, key, msgs, sysp, True, ah)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return resp, ut


def call_openrouter(msgs, sysp, fnt=False):
    ut = not fnt and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "temperature": 0.3,
    }
    if ut:
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
        if e.code == 400 and ut:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_openrouter(msgs, sysp, True)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return resp, ut


def call_ollama(msgs, sysp, fnt=False):
    ut = not fnt and ACTUAL_MODEL not in NO_TOOLS_MODELS
    body = {
        "model": ACTUAL_MODEL,
        "messages": [{"role": "system", "content": sysp}] + msgs,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    if ut:
        body["tools"] = SCHEMA
    req = urllib.request.Request(
        OLLAMA_HOST.rstrip("/") + "/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        if e.code == 400 and ut:
            NO_TOOLS_MODELS.add(ACTUAL_MODEL)
            print(f" {Y}⚠ model doesn't support tools — switching to XML mode{R}")
            return call_ollama(msgs, sysp, True)
        raise RuntimeError(f"HTTP {e.code}: {raw[:300]}")
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return {
        "choices": [{"message": resp["message"]}],
        "usage": {
            "prompt_tokens": resp.get("prompt_eval_count", 0),
            "completion_tokens": resp.get("eval_count", 0),
        },
    }, ut


def call_api(msgs, sysp, fnt=False):
    if PROVIDER == "openrouter":
        return call_openrouter(msgs, sysp, fnt)
    if PROVIDER == "ollama":
        return call_ollama(msgs, sysp, fnt)
    if PROVIDER == "mistral":
        return _call_oc(MISTRAL_HOST, MISTRAL_KEY, msgs, sysp, fnt)
    if PROVIDER == "groq":
        return _call_oc(GROQ_HOST, GROQ_KEY, msgs, sysp, fnt)
    if PROVIDER == "gemini":
        return _call_oc(GEMINI_HOST, GEMINI_KEY, msgs, sysp, fnt, "x-goog-api-key")
    raise RuntimeError(f"Unknown provider: {PROVIDER}")


def cols():
    return min(shutil.get_terminal_size((88, 24)).columns, 100)


def sep(c="─", col=D):
    print(f"{col}{c * cols()}{R}")


def pvw(s, n=74):
    ls = s.split("\n")
    p = ls[0][:n]
    return p + (
        f"{D} +{len(ls) - 1}L{R}"
        if len(ls) > 1
        else (f"{D}…{R}" if len(ls[0]) > n else "")
    )


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


def _dtc(calls, msgs, xm):
    results = []
    for tc in calls:
        if xm:
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
        if not xm:
            if PROVIDER == "ollama":
                results.append({"role": "tool", "tool_name": name, "content": str(res)})
            else:
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


def main():
    global MODEL
    k = get_key(PROVIDER)
    if k is not None and not k:
        print(f"\n {Re}✗ set API key for {PROVIDER} provider{R}\n")
        sys.exit(1)
    cwd = os.getcwd()
    skills = load_skills()
    sep("═", Bo + C)
    print(f" {Bo}◆ chalilulz{R}  {D}{MODEL}{R}")
    print(f" {D}cwd:{cwd}  skills:{len(skills)}{R}")
    sep("═", Bo + C)
    print(f" {D}/q quit  /c clear  /model <slug>  /skills list{R}\n")
    SP_ = skills_prompt(skills)
    SYS = f"Expert concise coding assistant. cwd:{cwd} os:{sys.platform}\nPrefer minimal edits. No filler. Think step by step silently.{SP_}"
    XSYS = SYS + XML_TOOL_INST
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
                nm = ui[7:].strip()
                update_model(nm)
                k = get_key(PROVIDER)
                if k is not None and not k:
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
                    resp, ut = call_api(
                        msgs, SYS if ACTUAL_MODEL not in NO_TOOLS_MODELS else XSYS
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
                if ut:
                    msgs.append(msg)
                    if text:
                        print(f"\n {C}◆{R} {rmd(text)}\n")
                    if not calls:
                        break
                    _dtc(calls, msgs, False)
                else:
                    disp = TC_RE.sub("", text).strip()
                    if disp:
                        print(f"\n {C}◆{R} {rmd(disp)}\n")
                    xc = parse_xml_calls(text)
                    msgs.append({"role": "assistant", "content": text})
                    if not xc:
                        break
                    _dtc(xc, msgs, True)
                print()
        except Exception as e:
            SP.stop()
            print(f"\n {Re}✗ {e}{R}\n")


if __name__ == "__main__":
    main()
