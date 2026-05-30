*This is a submission for the [Hermes Agent Challenge](https://dev.to/challenges/hermes-agent-2026-05-15): Build With Hermes Agent*

## What I Built

**Hermes Skill Registry** — npm for Hermes skills. A publish-discover-install-rate marketplace where any agent can share skills and any agent can find them.

Hermes has 85+ skills covering everything from GitHub workflows to Spotify to Minecraft servers. They're what make Hermes different from Claude Code or Codex — the ability to persist procedural knowledge across sessions. But they have a distribution problem: when an agent creates a new skill, it lives in `~/.hermes/skills/` on that one machine. There's no way for other agents to discover it, install it, or rate it. Every agent learns from scratch.

The registry fixes that. It turns skills from local artifacts into shared infrastructure.

It's three things:

- **FastAPI registry server** — REST API with search, publish, install, rate, star, and trending endpoints backed by SQLite. Skills are stored as raw SKILL.md files with metadata extracted from frontmatter.
- **CLI client** — 7 commands: `search`, `install`, `publish`, `rate`, `inspect`, `trending`, `star`. Install writes directly to `~/.hermes/skills/<category>/<name>/SKILL.md`. Publish reads a local SKILL.md and POSTs to the registry.
- **Web frontend** — Single HTML file, dark theme, no external CDN dependencies. Searchable skill cards, category filters, trending sidebar, install button that copies the CLI command, modal preview of SKILL.md.

There's also a `skill-registry` SKILL.md that teaches agents the auto-discovery workflow: when you encounter a task you don't have a skill for, search the registry, inspect the top result, install it, use it, rate it.

## Demo

```
# Start the server
cd ~/hermes-skill-registry && python3 -m registry.main

# Search for skills
python3 registry/cli.py search "testing" --sort rating

# Install a skill (writes to ~/.hermes/skills/)
python3 registry/cli.py install 3

# Publish your own skill
python3 registry/cli.py publish ./my-skill/

# Rate and star
python3 registry/cli.py rate 3 5 --review "Works great"
python3 registry/cli.py star 3
```

The web UI is a single `index.html` — open in any browser while the server runs on `localhost:8000`. No build step, no dependencies, no CDN.

API docs at `http://localhost:8000/docs` (Swagger UI).

Docker one-liner: `docker-compose up --build`.

## Code

Repository: `~/hermes-skill-registry/`

Structure:
```
registry/
├── main.py          # FastAPI app
├── database.py      # SQLite layer (skills + ratings)
├── schemas.py       # Pydantic models
├── cli.py           # Click CLI client
├── seed.py          # 7 seeded skills
├── config.py
├── auth.py
└── api/
    ├── skills.py    # CRUD endpoints
    ├── ratings.py   # Rate + star endpoints
    └── search.py    # Search + trending endpoints
web/
└── index.html       # Frontend
tests/
└── test_api.py      # 23 pytest tests
docker-compose.yml
Dockerfile
```

### My Tech Stack

- **Python 3.11** + FastAPI + uvicorn (async API server)
- **SQLite** + aiosqlite (zero-config persistence)
- **Pydantic v2** (request/response validation)
- **Click** (CLI client)
- **httpx** (API client, test client)
- **pytest** (23 tests, all passing)
- **Docker + docker-compose** (one-command deploy)
- **Vanilla HTML/CSS/JS** (frontend, no framework)

No ORM. No build pipeline. No external runtime dependencies.

## How I Used Hermes Agent

This project was built entirely through Hermes Agent — I directed, it executed.

**Hermes did:** project scaffolding, writing all Python files (server, database, CLI, routes, schemas, auth, seed data), writing the web frontend (HTML/CSS/JS), creating the test suite, debugging the FastAPI 307 redirect issue, fixing test data collision across sessions, writing the Dockerfile and docker-compose.yml, git init and commit.

**I directed:** the architecture (FastAPI + SQLite, not PostgreSQL), the scoring formula (`downloads + stars × 3 + avg_rating × 10`), the CLI command names and flags, the web UI design (dark theme, GitHub-inspired, single file), and the scope (API key auth only, no complex versioning for v1).

The iteration loop: Hermes writes code → I review → I flag issues → Hermes patches → I verify. The 23 tests passed on the first real run after the redirect fix. Total development time: a few hours of agent time across two sessions, with a 3-hour break in between. The files survived sleep; the session didn't. Recovery was seamless — I told Hermes "resume," it read the plan document and picked up where we left off.

The agent built it. I directed it — and that distinction matters.
