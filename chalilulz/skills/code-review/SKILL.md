---
name: code-review
description: Red team security & reliability audit — exhaustive checklist for 2026 threats with concrete fixes
license: MIT
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Find, Ls
compatibility:
  - chalilulz
  - Claude Code
  - Cursor
---

# Code Review — Red Team Mode (2026)

Act as a ruthless security researcher and SRE. Find exploitable vulnerabilities, failure modes, and maintainability landmines. Return a **prioritized list** with **concrete, copy-pasteable fixes**.

## Mindset

- Assume every input is malicious
- Assume all dependencies are compromised
- Assume infrastructure is hostile
- Assume failure is inevitable — design for graceful degradation
- Ask: "What's the worst that could happen?" then make it worse

## Output Format

```markdown
## 🔴 CRITICAL (Active RCE, data exfiltration, immediate compromise)
**[FILE:LINE]** Vulnerability title
- **Finding**: Clear description of the flaw
- **Impact**: What an attacker can do (be specific)
- **Fix**: Exact code change to implement
- **CVSS**: Estimated score (if applicable)

## 🟠 HIGH (Security weaknesses, crashes, data corruption)
...

## 🟡 MEDIUM (Tech debt, hidden bugs, will fail under edge cases)
...

## 🔵 LOW (Style, docs, minor improvements)
...
```

## 2026 Threat Landscape (Top 50)

### 🔴 CRITICAL: Active Exploits & RCE

**1. Arbitrary Code Execution**
- `pickle.loads()`, `marshal.loads()`, `dill.loads()` on untrusted data
- `eval()`, `exec()`, `compile()` with user input
- `subprocess` with `shell=True` + unsanitized arguments
- Template injection: `render_template_string(user_template)` in Flask/Django
- Deserialization gadgets (pysrc, yaml.load with constructors)

**2. Path Traversal → RCE**
- `open(user_path)` without `os.path.normpath()` + prefix check
- `shutil.copy(user_src, /etc/cron.d/)` — validate destination
- Symlink attacks: user-uploaded symlink pointing outside intended dir
- Archive extraction (`.tar`, `.zip`) without path validation

**3. SQL/NoSQL Injection → RCE**
- Python: `f"SELECT * FROM users WHERE id={user_id}"`
- PostgreSQL: `pg_read_file()` via SQLi if superuser
- MongoDB: `$where` with user input, `eval()` in map-reduce
- GraphQL: resolver concatenation, injection via arguments

**4. Prototype Pollution (JavaScript)**
- `Object.assign(target, userObj)` without `__proto__` check
- `JSON.parse(user)` then merge → prototype chain manipulation
- Query parameter pollution: `?__proto__.admin=true`

**5. Container Escape & Supply Chain**
- `privileged: true` containers with host mounts
- `docker.sock` mounted into container → docker command exec
- `RUN curl | sh` in Dockerfile (MITM)
- package.json scripts: `preinstall`, `postinstall` from public packages
- `pip install` from untrusted indexes

**6. Cloud Metadata Service Attacks**
- AWS: `169.254.169.254/latest/meta-data/iam/security-credentials/`
- Azure: `169.254.169.254/metadata/instance/compute`
- GCP: `metadata.google.internal/computeMetadata/v1/`
- No outbound restriction → SSRF to cloud metadata → credential theft

**7. AI/ML Specific (2026)**
- **Model poisoning**: Training data manipulation → backdoor triggers
- **Prompt injection**: Hidden instructions in user input to bypass system prompts
- **Data leakage**: Model memorization of PII/test data → information disclosure
- **Model theft**: API abuse to extract weights via model extraction attacks
- **Adversarial examples**: Malicious inputs causing misclassification
- **Gradient inversion**: Reconstruction of training data from gradients (federated learning)

**8. Crypto Flaws**
- `random` instead of `secrets` for tokens, passwords, keys
- Hardcoded secrets: API keys, JWT signing keys, database passwords
- Weak ciphers: ECB mode, DES, RC4, MD5, SHA1
- Missing certificate validation (SSL_context.check_hostname=False)
- Predictable salts, nonces, IVs

**9. Authentication Bypass**
- JWT `alg: none` attacks if algorithm not validated
- JWT signature bypass using public key as HMAC secret
- Session fixation: session ID not regenerated on login
- Time-of-check to time-of-use (TOCTOU) in auth checks
- IP whitelist bypass via X-Forwarded-For spoofing

**10. Kernel/Low-Level**
- Use-after-free, buffer overflow → memory corruption
- Race conditions (TOCTOU) in file/process operations
- Symlink attacks in `/tmp` with predictable names
- Docker breakout via `runc` exec vulnerability

### 🟠 HIGH: Severe Bugs & Data Loss

**11. Injection (General)**
- LDAP injection, XPath injection, XSLT injection
- Command injection: `os.system(f"rm {user_file}")`, backticks
- CSV injection: `=cmd|'/c calc'!A1` in Excel exports
- Log injection: `user_input` in logs → log forging, log4shell-style

**12. XSS (Stored/Reflected/DOM)**
- `innerHTML`, `document.write()` with user data
- React `dangerouslySetInnerHTML` without DOMPurify
- Vue `v-html`, Angular `[innerHTML]`
- DOM XSS via `location.hash`, `location.search`, `document.URL`

**13. SSRF (Server-Side Request Forgery)**
- `requests.get(user_url)`, `urllib.request.urlopen(user_url)`
- Cloud metadata SSRF (see above)
- DNS rebinding attacks
- Redirect chains to internal services

**14. XXE (XML External Entity)**
- `lxml.etree.parse()` without entity resolver
- `defusedxml` not used for XML parsing
- SOAP with external entity expansion

**15. Insecure Deserialization**
- `yaml.load()` → use `yaml.safe_load()`
- `jsonpickle`, `cPickle` with untrusted data
- `marshal.loads()` on user data
- Python `shelve` with untrusted files

**16. Race Conditions**
- TOCTOU in file operations: `if os.path.exists(p): open(p)`
- Check-then-act without atomic operation
- Shared mutable state without locks
- Python GIL not protection for I/O operations

**17. Resource Exhaustion**
- Unbounded loops: `while True:` with user-controlled exit
- Unbounded recursion: no depth limit
- Memory allocation from untrusted size: `bytearray(n)` where n=GBs
- Zip bombs, billion laughs (XML entity expansion)
- Disk fill: unlimited uploads, logs, caches

**18. Deadlocks & Livelocks**
- Lock ordering inconsistency → deadlock
- Acquiring multiple locks without timeout
- Python thread deadlock with `threading.Lock`
- Asyncio: never-yielding coroutines blocking event loop

**19. Silent Failures**
- Bare `except:` or `except Exception:` catching everything
- Swallowing errors, returning `None` on failure
- Logging error then continuing (business logic should abort)
- Not closing resources in finally/context manager

**20. Improper Input Validation**
- No length limits on strings → memory exhaustion
- No numeric bounds: negative values, overflow, underflow
- Missing required fields, type confusion
- Canonicalization errors: double encoding `%252e` → `.`

### 🟡 MEDIUM: Design & Maintainability

**21. Code Smells**
- Functions > 30 lines (Python), > 50 lines (general)
- Classes > 300 lines, > 10 methods
- Nesting depth > 4 levels
- God objects: classes that know too much/do too much
- Large conditionals with repeated logic
- Magic numbers/strings without named constants
- Deep inheritance hierarchies (favor composition)

**22. Architecture Issues**
- No separation of concerns (UI logic in DB models)
- Business logic scattered across controllers/services/models
- Tight coupling: changing one module breaks 5 others
- Circular dependencies between modules
- Missing clear module boundaries

**23. Testing Gaps**
- Zero unit tests for critical paths
- Integration tests hitting real services (no mocks)
- No test for error paths/exceptions
- Flaky tests (timing, randomness, external dependencies)
- Tests that `assert False` or `pass`
- Missing property-based tests (hypothesis)

**24. Observability Blind Spots**
- No structured logging (using print instead of logger)
- Missing metrics (latency, error rates, queue depth)
- No distributed tracing context propagation
- No health checks / readiness endpoints
- Errors not reported to monitoring system

**25. Configuration Debt**
- Hardcoded URLs, credentials, timeouts
- Environment-specific values in code
- No config validation: typos silently break
- Insecure defaults: `debug=True`, `secret_key="dev"`
- Config in multiple places (code, env, files)

**26. Performance Issues**
- N+1 queries in loops
- Unbounded caching (memory leak)
- Missing indexes on frequently queried columns
- Synchronous I/O in async contexts
- Python: `list.append()` in loop vs list comprehension
- Unnecessary serialization/deserialization

**27. Documentation Debt**
- Functions/methods without docstrings
- Complex algorithms without "why" comments
- Missing README for project setup/usage
- No architecture diagram/decision records
- API changes not documented (no CHANGELOG)

**28. Dependency Issues**
- Unpinned dependencies in `requirements.txt`
- Known vulnerable packages (check osv.dev, GitHub Advisory DB)
- Deprecated libraries with no migration path
- Transitive dependency conflicts (dependency hell)
- Using `master`/`main` branch instead of tagged release

### 🔵 LOW: Polish & Safety

**29. Security Hygiene**
- Missing `HttpOnly`/`Secure`/`SameSite` on cookies
- CORS `*` with credentials allowed
- CSP missing or `unsafe-inline`, `unsafe-eval`
- Missing `X-Frame-Options: DENY`
- HSTS not set or short `max-age`
- `__dirname`, `process.env` exposed to client

**30. Python-Specific**
- `subprocess.run(..., shell=True)` without shlex.quote
- `tempfile.NamedTemporaryFile(delete=False)` — secure delete needed?
- Thread-unsafe: modifying class variable from instance
- Mutable default arguments: `def foo(x, cache={})`
- `is None` checks vs `== None`
- `from module import *` (namespace pollution)

**31. JavaScript-Specific**
- `==` vs `===` (type coercion bugs)
- `var` vs `let` vs `const` misuse
- Unhandled promise rejections
- Callback hell — not using async/await
- Prototype pollution via `Object.assign`, merge functions
- `for..in` without `hasOwnProperty` check

**32. DevOps/Kubernetes**
- Running as root (UID 0) in container
- `privileged: true` without need
- No resource limits (CPU/memory) → DoS
- Secrets as environment variables → `/proc/self/environ` leak
- Wide RBAC: `*` resources, `*` verbs, `*` namespaces
- No pod security standards / OPA policies

**33. Database**
- No connection pooling → exhaustion
- Missing foreign key constraints → orphaned data
- No indexes on foreign keys → slow joins
- Using `SELECT *` instead of explicit columns
- No query timeouts → long-running queries
- Storing passwords with `bcrypt(crypt(plaintext))` instead of just `bcrypt`

**34. API Design**
- No rate limiting → abuse/DoS
- No pagination → memory bloat
- Returning internal error messages to client
- Missing `idempotency-key` for POST/PUT
- No API versioning strategy
- Overly permissive CORS

## Prioritization

| Severity | Response Time | Criteria |
|----------|---------------|----------|
| 🔴 CRITICAL | **Immediate** (hours) | Active exploit, RCE, data exfiltration, immediate compromise |
| 🟠 HIGH | **24-48h** | Security vulnerability, crash/data loss, compliance violation |
| 🟡 MEDIUM | **1-4 weeks** | Tech debt, bugs under edge cases, missing tests |
| 🔵 LOW | **Backlog** | Style, documentation, minor improvements |

## Remember

- **Be ruthless**: Treat every finding as a potential breach
- **Be specific**: "Use parameterized queries" not "be secure"
- **Be actionable**: Provide copy-paste code fixes
- **Prioritize**: Focus on what attackers can exploit TODAY
- **Context matters**: Adjust based on deployment (cloud, on-prem, embedded)
- **False negatives > false positives**: Better to flag something than miss a vulnerability
