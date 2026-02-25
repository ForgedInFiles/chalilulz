---
name: code-review
description: Reviews code for bugs, security issues, and best practices
---
# Code Review Skill

This skill provides automated code review functionality. It analyzes code files to identify:

- Potential bugs and logical errors
- Security vulnerabilities
- Performance issues
- Style violations
- Best practice deviations

The skill can be configured to match your project's coding standards and integrates with existing CI/CD pipelines.

## Usage

Run the review script to analyze your code:

```bash
python review.py --path ./src --format md
```

Options:
- `--path`: Directory or file to review
- `--format`: Output format (md, json, html)
- `--strict`: Enable strict mode with more checks
- `--exclude`: Patterns to exclude (e.g., "tests/*")

## Output

Provides detailed line-by-line feedback with severity ratings and suggested fixes.
