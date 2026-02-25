---
name: refactor-code
description: Automated code refactoring and modernization tool
---
# Refactor Code Skill

This skill automates code refactoring to improve maintainability, readability, and performance. It applies modern patterns and removes technical debt.

## Features

- Extract functions/methods
- Rename variables for clarity
- Convert callbacks to async/await
- Simplify conditional logic
- Remove duplicate code
- Apply DRY principles

## Usage

```bash
python refactor.py --target ./src --rules all --dry-run
```

Options:
- `--target`: Path to refactor
- `--rules`: Comma-separated rules (or "all")
- `--dry-run`: Preview changes without applying
- `--aggressive`: Enable more invasive transformations
- `--backup`: Create .bak files before changes

## Safety

Always use `--dry-run` first to review proposed changes. The refactor tool respects git and can undo changes.
