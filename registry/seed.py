"""Hermes Skill Registry — YAML and filesystem seed loader"""
from __future__ import annotations
import os
import yaml
from pathlib import Path
from registry.database import get_db, create_skill, init_db


SEED_SKILLS = [
    {
        "name": "requesting-code-review",
        "description": "Use when preparing code for review: security scan, quality gates, auto-fix. Run pre-commit checks before PRs.",
        "author": "hermes-agent",
        "category": "software-development",
        "tags": "review,quality,pr,security",
        "version": "1.0.0",
        "skill_md": """---
name: requesting-code-review
description: "Use when preparing code for review: security scan, quality gates, auto-fix."
version: 1.0.0
author: Hermes Agent
category: software-development
license: MIT
metadata:
  hermes:
    tags: [review, quality, pr, security]
---

# Requesting Code Review

Automated pre-commit code quality workflow.

## Overview

Run security scans, linting, and auto-fixes before submitting pull requests.

## When to Use

- Before creating a PR
- Before pushing to main
- As part of CI pipeline

## Steps

1. Run linter (ruff, eslint, etc.)
2. Run type checker (mypy, tsc)
3. Run security scan (bandit, semgrep)
4. Auto-fix where possible
5. Report remaining issues
""",
    },
    {
        "name": "systematic-debugging",
        "description": "Use when debugging complex issues: 4-phase root cause analysis. Understand before fixing.",
        "author": "hermes-agent",
        "category": "software-development",
        "tags": "debugging,root-cause,testing",
        "version": "1.0.0",
        "skill_md": """---
name: systematic-debugging
description: "Use when debugging complex issues: 4-phase root cause analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [debugging, root-cause, testing]
---

# Systematic Debugging

4-phase root cause analysis methodology.

## Phases

1. **Reproduce** — Confirm the bug is real and reproducible
2. **Isolate** — Narrow down the exact trigger and scope
3. **Diagnose** — Identify the root cause
4. **Fix + Verify** — Patch and confirm resolution

## When to Use

- Non-trivial bugs
- Intermittent failures
- Production incidents
""",
    },
    {
        "name": "test-driven-development",
        "description": "Use when implementing new features: enforce RED-GREEN-REFACTOR cycle. Tests before code.",
        "author": "hermes-agent",
        "category": "software-development",
        "tags": "tdd,testing,pytest,red-green-refactor",
        "version": "1.0.0",
        "skill_md": """---
name: test-driven-development
description: "Use when implementing new features: enforce RED-GREEN-REFACTOR."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tdd, testing, pytest]
---

# Test-Driven Development

Enforce RED-GREEN-REFACTOR cycle for all new code.

## Cycle

1. **RED** — Write a failing test
2. **GREEN** — Write minimum code to pass
3. **REFACTOR** — Clean up while tests pass

## When to Use

- New feature implementation
- Bug fix (write test that reproduces first)
- Refactoring (ensure no regressions)
""",
    },
    {
        "name": "github-pr-workflow",
        "description": "Use when creating or managing pull requests via gh CLI: branch, commit, open, CI, merge.",
        "author": "hermes-agent",
        "category": "github",
        "tags": "github,pr,gh-cli,ci,merge",
        "version": "1.0.0",
        "skill_md": """---
name: github-pr-workflow
description: "Use when creating or managing PRs via gh CLI: branch, commit, open, CI, merge."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pr, gh-cli]
---

# GitHub PR Workflow

Branch, commit, open PR, check CI, merge.

## Steps

1. Create feature branch: `git checkout -b feat/my-feature`
2. Commit changes
3. Push: `git push -u origin feat/my-feature`
4. Open PR: `gh pr create --title "..." --body "..."`
5. Check CI status: `gh pr checks`
6. Merge: `gh pr merge --squash`
""",
    },
    {
        "name": "arxiv-search",
        "description": "Use when searching academic papers on arXiv: by keyword, author, category, or ID.",
        "author": "hermes-agent",
        "category": "research",
        "tags": "arxiv,papers,research,academic",
        "version": "1.0.0",
        "skill_md": """---
name: arxiv-search
description: "Use when searching academic papers on arXiv: by keyword, author, category, or ID."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [arxiv, papers, research]
---

# arXiv Search

Search and retrieve papers from arXiv.

## Usage

Search by keyword, author, category (cs.AI, cs.LG, etc.), or arXiv ID.

## Tools

Use web_search or the arXiv API directly via curl:
curl "https://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=5"
""",
    },
    {
        "name": "himalaya-email",
        "description": "Use when sending, receiving, or managing email from the terminal via Himalaya CLI.",
        "author": "hermes-agent",
        "category": "email",
        "tags": "himalaya,email,imap,smtp,terminal",
        "version": "1.0.0",
        "skill_md": """---
name: himalaya-email
description: "Use when sending, receiving, or managing email from terminal via Himalaya CLI."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [himalaya, email, imap, smtp]
---

# Himalaya Email

IMAP/SMTP email from the terminal.

## Setup

1. Install: `cargo install himalaya`
2. Configure: `himalaya account configure`
3. Read: `himalaya list`
4. Write: `himalaya write`
5. Send: `himalaya send`
""",
    },
    {
        "name": "jupyter-live-kernel",
        "description": "Use when running iterative Python workflows: live Jupyter kernel for exploratory coding.",
        "author": "hermes-agent",
        "category": "data-science",
        "tags": "jupyter,kernel,python,iterative,data",
        "version": "1.0.0",
        "skill_md": """---
name: jupyter-live-kernel
description: "Use when running iterative Python workflows: live Jupyter kernel."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [jupyter, kernel, python, data]
---

# Jupyter Live Kernel

Interactive Python execution via Jupyter kernel.

## When to Use

- Data exploration
- Iterative analysis
- Quick prototyping

## Workflow

1. Start kernel
2. Execute cells interactively
3. Export results
""",
    },
]


async def seed_database():
    """Load seed skills into the database."""
    await init_db()
    db = await get_db()
    count = 0
    for skill in SEED_SKILLS:
        try:
            await create_skill(
                db,
                name=skill["name"],
                description=skill["description"],
                author=skill["author"],
                category=skill["category"],
                tags=skill["tags"],
                version=skill["version"],
                skill_md=skill["skill_md"],
            )
            count += 1
        except Exception as e:
            if "UNIQUE" in str(e):
                pass  # Already exists, skip
            else:
                print("Seed error for {0}: {1}".format(skill["name"], e))
    await db.close()
    print("Seeded {0} skills".format(count))


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())
