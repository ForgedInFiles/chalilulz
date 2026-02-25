---
name: write-tests
description: Writes comprehensive tests for code
license: MIT
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
compatibility:
  - chalilulz
  - Claude Code
  - Cursor
  - VS Code
  - GitHub Copilot
---

# Write Tests Skill

Generates comprehensive test coverage for code using unittest framework.

## Quick Start

Use the `read` tool to view code, then write test files using the `write` tool.

## Testing Guidelines

- Test one thing per test function
- Use descriptive test names
- Test happy path and edge cases
- Mock external dependencies
- Clean up in tearDown methods

## Test Structure

```python
import unittest
import sys
import os

class TestYourCode(unittest.TestCase):
    def setUp(self):
        # Setup test fixtures
    
    def tearDown(self):
        # Cleanup
    
    def test_something(self):
        # Your test code here

if __name__ == "__main__":
    unittest.main()
```

## Remember

- Aim for high coverage but prioritize meaningful tests
- Test edge cases and error conditions
- Keep tests fast and independent
