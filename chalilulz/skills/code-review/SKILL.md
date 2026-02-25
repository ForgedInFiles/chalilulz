---
name: code-review
description: Red team code review: security, failure modes, maintainability — prioritized with concrete fixes
license: MIT
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Find, Ls
compatibility:
  - chalilulz
  - Claude Code
  - Cursor
---

# Code Review — Red Team Mode

Act as a ruthless reviewer. Find security vulnerabilities, failure modes, maintainability issues. Return a **prioritized list** (CRITICAL/HIGH/MEDIUM/LOW) with concrete fixes.

## Red Team Mindset

Assume everything is broken. Look for:
- What can go wrong?
- What an attacker could exploit
- Where systems will fail under load/edge cases
- What will make future developers curse your name

## Output Format

```
## CRITICAL (0-day security / data loss / RCE)
- [FILE:LINE] Issue description
  Impact: What can happen
  Fix: Concrete code change

## HIGH (security weaknesses, crashes, data corruption)
...

## MEDIUM (maintainability, tech debt, hidden bugs)
...

## LOW (style, documentation, minor improvements)
...
```

## Security Checklist (CRITICAL/HIGH)

### Injection Flaws
- **SQL/NoSQL injection**: String concatenation in queries, unsanitized user input
- **Command injection**: `subprocess`, `os.system`, `eval`, `exec` with user data
- **XSS**: Unsanitized output in HTML/JS, `innerHTML`, React `dangerouslySetInnerHTML`
- **Path traversal**: User-controlled paths in `open()`, `os.path.join` without validation
- **Deserialization**: `pickle`, `yaml.load` without safe loader, JSON with reviver

### Authentication & Authorization
- Hardcoded secrets, API keys, passwords
- Missing/invalid JWT verification
- Broken session management (predictable IDs, missing expiry)
- Principle of least privilege violations
- API endpoints without auth checks

### Crypto & Data Protection
- Weak random (`random` vs `secrets`), predictable salts
- Insecure ciphers (ECB mode, DES, RC4)
- Storing plaintext passwords, PII, credit cards
- Missing encryption for sensitive data at rest/in transit

### Supply Chain
- Unpinned dependencies (`requirements.txt` without versions)
- Using known vulnerable packages (check against osv.dev)
- Auto-running code from untrusted sources (e.g., `pickle`, `marshal`)
- Using deprecated/abandoned libraries

### Cloud/Infrastructure
- Overly permissive IAM policies (s3:* , admin:*, public-read)
- Hardcoded credentials in config files
- Missing input validation on public endpoints
- No rate limiting → DoS vulnerability
- Unauthenticated access to admin APIs

## Failure Modes (HIGH/MEDIUM)

### Error Handling
- Bare `except:` or `except Exception:` catching everything
- Silent failures (returning `None` on error, logging then continuing)
- Not closing resources (files, DB connections, sockets)
- Unchecked `None` returns, missing guard clauses

### Concurrency
- Race conditions, TOCTOU bugs
- Unprotected shared state (no locks, atomic operations)
- Thread-unsafe collections (list/dict instead of `queue.Queue`)
- Deadlock potential (lock ordering issues)
- Missing timeouts on locks/waits

### Resource Management
- Memory leaks (unbounded caches, event listener not removed)
- File descriptor leaks (not closing files/sockets)
- Infinite loops without exit condition
- Unbounded recursion → stack overflow
- Disk space exhaustion (no size limits on uploads/logs)

### Edge Cases
- No input validation (negative numbers, empty strings, null bytes)
- Integer overflow/underflow
- Timezone/DST issues, leap seconds
- Unicode/encoding errors (emoji, right-to-left override)
- Clock skew assumptions

## Maintainability (MEDIUM/LOW)

### Code Smells
- Functions > 50 lines, classes > 300 lines
- Deep nesting (>4 levels)
- Magic numbers/strings (use named constants)
- Duplicated code (copy-paste programming)
- God objects (classes that know too much)

### Testing Gaps
- No unit tests for critical paths
- Integration tests hitting real external services (use mocks)
- Missing error case tests
- Flaky tests (timing issues, non-deterministic)
- Tests thatAssert False or `pass`

### Documentation Debt
- Functions without docstrings
- Complex algorithms without comments explaining "why"
- Missing README for setup/usage
- No architecture diagram for complex systems
- API changes not documented

### Configuration
- Hardcoded URLs, credentials, timeouts
- Environment-specific values in code (use env vars/config files)
- No config validation (typos in config silently break things)
- Default values that are insecure (debug=True in prod)

## Technology-Specific Checks

### Python
- `os.system`, `subprocess` with shell=True and unsanitized input
- `pickle.loads`, `yaml.load` (use `pickle.load` only for trusted data, `yaml.safe_load`)
- `eval()`, `exec()`, `compile()` on user input
- SQL string formatting: `f"SELECT * FROM users WHERE id={user_id}"` → use parameters
- Django: missing `{% csrf_token %}`, `Model.objects.raw()` with interpolation
- Flask: `render_template_string(request.args.get('template'))` → SSTI

### JavaScript/TypeScript
- `eval()`, `new Function()`, `setTimeout(string)`
- `innerHTML` with user data → use `textContent` or sanitize
- Prototype pollution: `Object.assign(target, userObj)` without prototype check
- Insecure JWT: `jwt.sign(payload, secret)` with weak secret, no expiration
- Node.js: `child_process.exec` with unsanitized input, path traversal in `fs.readFile`

### Web (Any)
- CORS misconfiguration: `Access-Control-Allow-Origin: *` with credentials
- CSP missing or `unsafe-inline`, `unsafe-eval`
- Session fixation, missing `HttpOnly`/`Secure` flags
- Clickjacking: missing `X-Frame-Options: DENY`
- HSTS not set or short max-age

### Kubernetes/DevOps
- `privileged: true` containers without need
- Running as root (securityContext.runAsUser: 0)
- secrets mounted as env vars (use volume mounts with 0444)
- No resource limits → DoS via resource exhaustion
- Wide RBAC permissions (`*` resources, `*` verbs)

## Prioritization Logic

**CRITICAL**: Active exploit in wild, RCE, data exfiltration, immediate data loss
**HIGH**: Security vulnerability requiring auth/bypass, crashes in production, data corruption
**MEDIUM**: Code that WILL fail under edge cases, significant tech debt
**LOW**: Code smells, missing docs, style issues

## Remember

- Be ruthless. Assume the attacker is smarter than you.
- Every "should be fine" is a potential vulnerability.
- If you're not sure, err on the side of HIGH.
- Provide **concrete, copy-pasteable fixes**, not vague advice.
- Focus on what matters: security, reliability, maintainability.
- Don't waste time on nitpicks (naming, style) unless they enable bugs.
