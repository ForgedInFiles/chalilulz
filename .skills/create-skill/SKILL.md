---
name: create-skill
description: Skill creation framework - teaches how to create skills
---

# Skill Creation Framework

## Overview

This skill teaches Chalice how to create its own skills, enabling it to extend its capabilities when users request specialized functionality.

## Core Concepts

### Skill Structure

Every skill follows this format:

```markdown
---
name: skill-name
description: Brief explanation of what this skill teaches
license: MIT (optional)
---

# Skill Title

Content goes here...
```

### Directory Structure

Skills are stored in these locations:
- `~/.config/chalice/skills/` (global user)
- `.chalice/skills/` (project local)
- Built-in: `packages/chalice/skills/`

### Skill Types

1. **Technology Skills**: React, Python, Docker, etc.
2. **Framework Skills**: Express, Django, Spring, etc.
3. **Process Skills**: Git workflows, testing strategies
4. **Domain Skills**: Finance, healthcare, education

## Skill Creation Process

### Step 1: Identify Need

When a user requests specialized functionality:
1. Determine if existing skills cover the request
2. If not, identify the domain/topic
3. Plan the skill scope and structure

### Step 2: Choose Name

Follow naming conventions:
- `kebab-case` (e.g., `testing-jest`)
- Descriptive and unique
- Avoid generic terms

### Step 3: Create Structure

```markdown
---
name: my-skill
description: Brief explanation
---

# Skill Title

## Overview
## Quick Start
## Core Concepts
## Examples
## Best Practices
## Remember
```

### Step 4: Write Content

Include:
- Practical examples with code
- Clear explanations
- Best practices
- Common pitfalls

### Step 5: Save and Test

1. Save to appropriate skills directory
2. Run `/capability` to verify loading
3. Test skill provides useful context

## Examples

### Simple Skill

```markdown
---
name: hello-world
description: Basic greeting skill
---

# Hello World

## Overview

Simple skill that teaches Chalice to greet users.

## Quick Start

```python
print("Hello, World!")
```

## Remember

Always greet users warmly.
```

### Technology Skill

```markdown
---
name: python-basics
description: Python programming fundamentals
---

# Python Basics

## Overview

Core Python concepts and syntax.

## Variables

```python
name = "Alice"
age = 25
is_student = True
```

## Control Flow

```python
if age >= 18:
    print("Adult")
else:
    print("Minor")
```

## Remember

Python uses indentation for blocks.
```

## Skill Validation

### Testing

1. Create skill file
2. Place in skills directory
3. Restart Chalice
4. Run `/capability` to verify

### Quality Checks

- [ ] Unique name
- [ ] Clear description
- [ ] Working examples
- [ ] Proper formatting
- [ ] Relevant content

## Best Practices

### Naming
- Use descriptive names
- Follow kebab-case convention
- Avoid abbreviations

### Content
- Keep focused on one topic
- Include practical examples
- Use clear headings
- Add code blocks with syntax highlighting

### Structure
- Start with overview
- Provide quick start
- Include examples
- Add best practices
- End with key takeaways

## Remember

**Key Principles:**
1. Skills expand Chalice's knowledge
2. Each skill covers one focused area
3. Include practical, real-world examples
4. Structure content for easy scanning
5. Keep skills up-to-date

**File Standards:**
- YAML frontmatter with name/description
- Markdown content (.md extension)
- Place in skills/ directory
- Recursive directory scanning supported

## Workflow Checklist

- [ ] Identify user need for specialized skill
- [ ] Choose appropriate skill name
- [ ] Create proper YAML frontmatter
- [ ] Write comprehensive content
- [ ] Include working code examples
- [ ] Add best practices section
- [ ] Test skill loading
- [ ] Verify skill provides useful context

## Advanced Topics

### Reference Materials

Create subdirectories for complex skills:

```
skill-name/
├── SKILL.md
└── reference/
    ├── api.md
    ├── examples.md
    └── config.md
```

### Multi-File Skills

Split large skills into multiple files for better organization.

### Skill Dependencies

Reference other skills when needed:

```markdown
This skill builds on concepts from [python-basics](python-basics.md).
```

## Troubleshooting

### Skill Not Loading

1. Check file extension is `.md`
2. Verify frontmatter includes `name` and `description`
3. Ensure YAML frontmatter is valid
4. Check file permissions
5. Look for parsing errors
6. Restart Chalice if needed

### Common Issues

| Problem | Solution |
|---------|----------|
| Invalid YAML | Run through YAML validator |
| Duplicate name | Rename to unique identifier |
| Wrong location | Move to correct skills directory |
| Syntax errors | Validate Markdown rendering |

## Advanced Examples

### API Design Skill

```markdown
---
name: api-design
description: Principles for designing clean REST APIs
license: MIT
---

# API Design Guidelines

## Resource Naming

Use plural nouns for resource endpoints.

- ✅ `/users`
- ❌ `/user`

## HTTP Methods

- GET: Read
- POST: Create
- PUT: Update (full)
- PATCH: Update (partial)
- DELETE: Remove

## Status Codes

- 200: Success
- 201: Created
- 400: Bad request
- 404: Not found
- 500: Server error

## Remember

Keep APIs consistent and intuitive.
```

### Testing Framework Skill

```markdown
---
name: testing-jest
description: Writing effective tests with Jest framework
---

# Jest Testing Best Practices

## Test Structure

```javascript
describe("UserService", () => {
  beforeEach(() => {
    // Setup
  });

  test("creates user with valid data", async () => {
    const user = await createUser({ name: "John" });
    expect(user.id).toBeDefined();
  });
});
```

## Best Practices

- Use descriptive test names
- Test one thing per test
- Use `beforeEach` for setup
- Mock external dependencies
- Test edge cases and errors

## Remember

Write tests that are reliable and maintainable.
```

## Remember

**Skill Creation Principles:**
1. Skills expand Chalice's domain knowledge
2. Each skill should cover one focused area
3. Include practical, real-world examples
4. Structure content for easy scanning
5. Keep skills up-to-date with current best practices

**Best Practices:**
- Use descriptive kebab-case names
- Write clear 1-2 sentence descriptions
- Include complete working examples
- Organize with consistent headings
- Add troubleshooting section for complex skills
- Test by loading and checking `/capability`

**File Standards:**
- YAML frontmatter with `name` and `description`
- Markdown content (`.md` extension)
- Place in `skills/` directory
- Recursive directory scanning supported