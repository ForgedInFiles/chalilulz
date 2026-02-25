---
name: prompt_engineering
description: Design, test, and optimize LLM prompts with evaluation harnesses
license: MIT
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Ls, Mkdir, Cp, Rm, Find
compatibility:
  - chalilulz
  - Claude Code
  - Cursor
---

# Prompt Engineering Skill

Create, test, and optimize LLM prompts with modern techniques and evaluation frameworks.

## Quick Start

1. Define prompt template with variables
2. Create few-shot examples
3. Build evaluation dataset (inputs + expected outputs)
4. Run tests and measure metrics
5. Iterate based on results

## Techniques (2026)

### Core Patterns
- **Chain-of-Thought (CoT)**: Add "Let's think step by step" for reasoning tasks
- **ReAct**: Interleave reasoning + tool use for complex workflows
- **Few-shot**: Include 3-5 input→output examples in prompt
- **Zero-shot with instructions**: Clear, specific instructions with format examples
- **Self-consistency**: Generate multiple reasoning paths, take majority vote

### Advanced Methods
- **Prompt chaining**: Break complex tasks into sequential prompts
- **Automatic prompt optimization**: Use LLM to generate/refine prompts (OPRO, ALE)
- **Retrieval-augmented**: Include relevant context from knowledge base
- **Tool-augmented**: Integrate tool use capabilities (already supported by chalilulz)
- **Constitutional AI**: Add principles/rules to guide responses

### Evaluation
- **Metrics**: Accuracy, BLEU, ROUGE, semantic similarity (cosine), human rating
- **Test suite**: 20-100 diverse examples covering edge cases
- **A/B testing**: Compare prompt variants side-by-side
- **Regression testing**: Ensure changes don't break existing performance

## File Structure

```
prompts/
  ├── templates/
  │   ├── classification.txt      # Jinja2-style templates
  │   ├── extraction.txt
  │   └── reasoning.txt
  ├── examples/
  │   ├── few_shot_classification.jsonl
  │   └── few_shot_extraction.jsonl
  ├── eval/
  │   ├── dataset.jsonl           # Test inputs + expected outputs
  │   ├── metrics.py              # Custom scoring functions
  │   └── golden_set.json         # High-quality reference answers
  ├── experiments/
  │   ├── v1_baseline/
  │   ├── v2_cot/
  │   └── v3_few_shot/
  └── README.md                   # Track what works
```

## Implementation Steps

### 1. Create Template

Use clear variable names and delimiters:

```
You are a {{role}} specializing in {{domain}}.

Task: {{task}}

{% if examples %}
Examples:
{% for ex in examples %}
Input: {{ex.input}}
Output: {{ex.output}}
{% endfor %}
{% endif %}

Now process:
{{input}}

Provide your answer in this exact JSON format:
{{schema}}
```

### 2. Build Evaluation Dataset

Create `eval/dataset.jsonl`:
```json
{"input": "What is the capital of France?", "expected": "Paris", "type": "factual"}
{"input": "Summarize: Lorem ipsum...", "expected": "Brief summary...", "type": "summarization"}
```

### 3. Write Test Runner

Use bash script or Python to:
- Load dataset
- Format prompts with templates
- Call LLM via chalilulz API or direct
- Score responses (exact match, semantic similarity, or custom metric)
- Generate report (accuracy by category, failure examples)

### 4. Iterate

- Run baseline → identify failure modes
- Add examples to few-shot → re-test
- Try CoT → measure improvement
- Refine instructions → optimize
- Document results in experiments/ subdirectories

## Modern 2026 Practices

- **Prompt versioning**: Store all prompt variants with git tags
- **Automated regression**: CI runs eval suite on every prompt change
- **Hybrid approaches**: Combine multiple techniques (CoT + few-shot + retrieval)
- **Cost optimization**: Use smaller models for evaluation, larger for final
- **Bias testing**: Include diverse inputs to catch unwanted biases
- **Adversarial examples**: Test edge cases and jailbreak attempts
- **Human-in-the-loop**: Periodic human review of AI-generated labels

## Integration with chalilulz

- Use `bash` tool to run evaluation scripts
- Use `write`/`edit` to create/modify prompt templates
- Use `read` to review experiment results
- Store datasets in project repo for reproducibility

## Tools You'll Use

- `write` - Create templates and config files
- `edit` - Refine prompts based on test results
- `bash` - Run evaluation scripts, call LLM
- `ls`/`glob` - Navigate experiment directories
- `cp` - Duplicate prompt versions for A/B testing
- `find` - Locate evaluation artifacts

## Remember

- Prompts are code: version control, test, refactor
- Start simple → add complexity only if needed
- Measure everything; intuition is unreliable
- Document what works and what fails
- Chain-of-thought helps reasoning but increases tokens
- Few-shot helps consistency but requires good examples
- LLM capabilities evolve: re-test when switching models
