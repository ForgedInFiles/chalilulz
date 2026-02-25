---
name: refactor-code
description: AI-powered systematic refactoring: design patterns, architecture, performance, security hardening
license: MIT
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Ls, Find, Cp
compatibility:
  - chalilulz
  - Claude Code
  - Cursor
---

# Refactor Code (2026)

Systematic, safe, measurable code transformation with AI assistance. Apply design patterns, improve architecture, boost performance, and remove tech debt.

## Philosophy

**Refactoring ≠ Rewriting**
- Preserve behavior while improving structure
- One structural change at a time
- Tests required before & after
- Measure before/after (complexity, performance, coverage)

## When to Refactor

| Trigger | Action |
|---------|--------|
| Function > 30 lines | Extract methods |
| Class > 300 lines | Split responsibilities |
| Cyclomatic complexity > 10 | Simplify conditionals |
| Duplicated code (>3 copies) | DRY it |
| > 5 parameters in function | Use object parameter or builder |
| Feature envy (method uses other class data) | Move method |
| Shotgun surgery (change touches many files) | Introduce abstraction |

## 2026 Refactoring Toolkit

### 1. Extract Function/Method

**Before:**
```python
def process_order(order):
    # validate
    if not order.id:
        raise ValueError("Missing ID")
    if order.total < 0:
        raise ValueError("Negative total")
    # calculate tax
    tax = order.total * 0.08
    # apply discount
    if order.customer.is_vip:
        discount = order.total * 0.1
        order.total -= discount
    # save
    db.save(order)
    # send email
    send_confirmation(order.customer.email, order)
```

**After:**
```python
def process_order(order):
    validate_order(order)
    tax = calculate_tax(order.total)
    apply_discounts(order)
    persist_order(order)
    notify_customer(order)
    return order
```

**Checklist:**
- ✓ Extracted function name describes *what*, not *how*
- ✓ Original function reads like a sentence
- ✓ Extracted function has no side effects (or clearly documents them)

### 2. Replace Conditional with Strategy/Polymorphism

**Before:**
```python
def process_payment(payment_type, amount):
    if payment_type == "credit":
        charge_credit_card(amount)
    elif payment_type == "debit":
        charge_debit_card(amount)
    elif payment_type == "paypal":
        charge_paypal(amount)
    else:
        raise ValueError("Unknown type")
```

**After:**
```python
class PaymentProcessor:
    def process(self, amount):
        raise NotImplementedError

class CreditProcessor(PaymentProcessor):
    def process(self, amount):
        charge_credit_card(amount)

class DebitProcessor(PaymentProcessor):
    def process(self, amount):
        charge_debit_card(amount)

# Usage
processor = PROCESSOR_MAP[payment_type]()
processor.process(amount)
```

### 3. Introduce Parameter Object

**Before:**
```python
def send_notification(user_id, message, subject, from_email, to_email, cc=None, bcc=None, priority="normal"):
    ...
```

**After:**
```python
from dataclasses import dataclass

@dataclass
class NotificationConfig:
    message: str
    subject: str
    from_email: str
    to_email: str
    cc: list = None
    bcc: list = None
    priority: str = "normal"

def send_notification(user_id: int, config: NotificationConfig):
    ...
```

Benefits: type safety, extensibility, readability.

### 4. Replace Magic Numbers with Named Constants

**Before:**
```python
if status == 3:  # WTF is 3?
    handle_error()
timeout = 3600  # seconds? hours?
```

**After:**
```python
class OrderStatus:
    PENDING = 1
    CONFIRMED = 2
    SHIPPED = 3
    DELIVERED = 4
    CANCELLED = 5

TIMEOUT_ONE_HOUR = 3600  # seconds
```

### 5. Decompose Conditional (Guard Clauses)

**Before:**
```python
def process_user(user):
    if user is not None:
        if user.is_active:
            if user.has_paid:
                send_email(user)
            else:
                raise UnpaidError()
        else:
            raise InactiveError()
    else:
        raise ValueError("No user")
```

**After:**
```python
def process_user(user):
    if user is None:
        raise ValueError("No user")
    if not user.is_active:
        raise InactiveError()
    if not user.has_paid:
        raise UnpaidError()
    send_email(user)
```

### 6. Extract Class (Split God Object)

**Before:**
```python
class System:
    def handle_user(self, user): ...
    def process_order(self, order): ...
    def send_invoice(self, invoice): ...
    def generate_report(self): ...
    def authenticate(self, creds): ...
    # 50 methods, 1000 lines
```

**After:**
```python
class UserService:
    def handle_user(self, user): ...

class OrderService:
    def process_order(self, order): ...

class BillingService:
    def send_invoice(self, invoice): ...

class ReportingService:
    def generate_report(self): ...

class AuthService:
    def authenticate(self, creds): ...
```

### 7. Replace Type Checks with Polymorphism

**Before:**
```python
def visit(node):
    if isinstance(node, Document):
        render_document(node)
    elif isinstance(node, Image):
        render_image(node)
    elif isinstance(node, Video):
        render_video(node)
```

**After:**
```python
class Node:
    def render(self): raise NotImplementedError

class Document(Node):
    def render(self):
        return render_document(self)

class Image(Node):
    def render(self):
        return render_image(self)

# Now:
node.render()  # Polymorphic, easy to extend
```

### 8. Introduce Assertions (EAFP → LBYL where appropriate)

**Before:**
```python
def get_user_data(user_id):
    try:
        user = db.get(user_id)
        profile = user.profile
        settings = profile.settings
        return settings
    except AttributeError:
        return {}
```

**After:**
```python
def get_user_data(user_id):
    user = db.get(user_id)
    assert user is not None, f"User {user_id} not found"
    assert user.profile is not None, "User profile missing"
    assert user.profile.settings is not None, "Settings missing"
    return user.profile.settings
```

*Or better*: handle None explicitly, don't assert on expected conditions.

### 9. Separate Query from Command

**Before:**
```python
def get_user_and_log(user_id):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    logger.info(f"Fetched user {user_id}")
    return user
```

**After:**
```python
def get_user(user_id):
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

def log_fetch(user_id):
    logger.info(f"Fetched user {user_id}")

# Caller decides:
user = get_user(user_id)
log_fetch(user_id)  # Can omit, replace, or reorder
```

### 10. Security Hardening Refactorings

**Strip secrets from logs:**
```python
# Before: secrets exposed
logger.debug(f"Request: {request.json}")

# After: sanitize
safe_data = {k: "***" if k in SECRET_KEYS else v for k, v in request.json.items()}
logger.debug(f"Request: {safe_data}")
```

**Validate all inputs:**
```python
def create_user(data):
    # Before: no validation
    user = User(**data)
    
    # After: validate before construct
    validate_email(data["email"])
    validate_password_strength(data["password"])
    user = User(**data)
```

**Use constant-time comparisons for secrets:**
```python
# Before: timing attack
if user_token == request_token: ...

# After: constant-time
if secrets.compare_digest(user_token, request_token): ...
```

## AI-Assisted Refactoring Workflow

### Step 1: Analyze
```bash
# Use chalilulz to analyze codebase
load_skill code-review
"Perform full red team audit"
# Review findings, prioritize CRITICAL/HIGH
```

### Step 2: Create Refactoring Plan
```
"Refactor [file/module] to:
1. Extract function X (currently 50 lines)
2. Replace conditional Y with strategy pattern
3. Introduce parameter object for Z
4. Add comprehensive tests before refactoring
Provide step-by-step plan with before/after snippets."
```

### Step 3: Implement Safely
1. Write tests for current behavior (green)
2. Make one small refactoring
3. Run tests (should still be green)
4. Commit "Refactor: extracted method X"
5. Repeat

### Step 4: Verify
```bash
# Check metrics improved
radon cc -a src/  # Cyclomatic complexity before/after
python -m pytest --cov=src  # Coverage maintained or improved
python -m mutmut run  # Mutation score not decreased
```

## Measurable Improvements

Track these metrics **before and after**:

| Metric | Tool | Target |
|--------|------|--------|
| Cyclomatic complexity | `radon cc` | < 10 per function |
| Maintainability Index | `radon mi` | > 60 (A/B grade) |
| Duplication | `radon dup` | < 5% |
| Test coverage | `pytest --cov` | > 90% |
| Mutation score | `mutmut` | > 80% |
| Mean Time To Repair (MTTR) | incident logs | ↓ 50% |

## Safety Checklist (Don't Refactor Without)

- [ ] Tests exist for code being refactored (≥ 80% coverage)
- [ ] Tests pass **before** refactoring (green baseline)
- [ ] Refactoring is **one** change at a time (not "clean up everything")
- [ ] Code still works after each small change (commit frequently)
- [ ] No behavior change (only structure improvement)
- [ ] Performance not degraded (benchmark before/after)
- [ ] All imports still valid (run static analysis)

## Common Pitfalls

❌ **Refactoring without tests** → You're gambling
✅ Write tests first, then refactor

❌ **Changing multiple things at once** → Can't isolate what broke it
✅ One structural change per commit

❌ **Ignoring performance** → Made code cleaner but 2x slower
✅ Benchmark critical paths

❌ **Over-engineering** → 5 layers of abstraction for simple case
✅ YAGNI: You Aren't Gonna Need It

❌ **Not communicating** → Team can't find refactored code
✅ Update documentation, code comments, architecture diagrams

## Recommended Tools (2026)

| Tool | Use |
|------|-----|
| `pytest` | Test framework |
| `hypothesis` | Property-based testing |
| `mutmut` | Mutation testing |
| `radon` | Complexity analysis |
| `black` + `isort` | Auto-formatting |
| `ruff` / `pyright` | Linting & type checking |
| `pre-commit` | Git hooks for quality |
| `mypy` | Static type checking |

## Integration with chalilulz

1. `load_skill code-review` to identify refactoring targets
2. `read` source files to understand current structure
3. `write` new test files (ensure coverage before refactor)
4. `bash` to run: `pytest --cov`, `radon cc`, `mutmut`
5. `edit` code incrementally, run tests after each edit
6. `grep` to find duplicate patterns across codebase
7. `ls`/`find` to locate files needing attention

## Remember

- **Refactoring is a continuous process**, not a one-time cleanup
- **Tests enable refactoring** — no tests = no refactor
- **Small steps** reduce risk
- **Measure before/after** to prove improvement
- **Boy Scout Rule**: Leave code cleaner than you found it
- **Technical debt compounds**: pay it down incrementally
- **Refactor when you're in the code anyway** (opportunistic refactoring)

## Quick Refactoring Checklist

- [ ] Added failing test **first** (or tests exist, passing)
- [ ] One structural change (function extraction, class split, etc.)
- [ ] Tests still passing after change
- [ ] No new `# TODO` or `# FIXME` comments
- [ ] Code is simpler (fewer parameters, less nesting)
- [ ] Duplication eliminated
- [ ] Commit message is clear: "Refactor: <what> → <why>"
- [ ] CI metrics improved or stable (complexity ↓, coverage stable)

Ready? `load_skill refactor-code` and start cleaning up that tech debt!
