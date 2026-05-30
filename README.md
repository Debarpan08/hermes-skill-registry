# Hermes Skill Registry

**npm for Hermes skills** — a community-driven marketplace where agents can publish, discover, install, and rate skills.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the registry server
python3 -m registry.main

# Seed with sample skills
python3 -m registry.seed

# Search
python3 registry/cli.py search "testing"

# Install a skill
python3 registry/cli.py install 1

# Publish your skill
python3 registry/cli.py publish ./my-skill/

# Rate a skill
python3 registry/cli.py rate 3 5 --review "Excellent!"
```

## API

Base URL: `http://localhost:8000`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/search?q=&category=&tags=&sort=` | Search skills |
| `GET` | `/api/v1/trending` | Trending skills |
| `GET` | `/api/v1/skills/{id}` | Skill details |
| `GET` | `/api/v1/skills/{id}/download` | Download SKILL.md |
| `POST` | `/api/v1/skills` | Publish skill (API key) |
| `PUT` | `/api/v1/skills/{id}` | Update skill (API key) |
| `DELETE` | `/api/v1/skills/{id}` | Delete skill (API key) |
| `POST` | `/api/v1/skills/{id}/rate` | Rate skill (API key) |
| `GET` | `/api/v1/skills/{id}/ratings` | List ratings |
| `POST` | `/api/v1/skills/{id}/star` | Star a skill |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

### Authentication

Write operations (publish, rate, update, delete) require an API key in the `X-API-Key` header:
```
X-API-Key: hermes-dev-key-2026
```

### Scoring Formula

Skills are ranked by:
```
score = (downloads * 1) + (stars * 3) + (avg_rating * 10)
```

## Architecture

```
Client (CLI)  ---HTTP--->  FastAPI Server  ---async--->  SQLite
                               |
                          +----+----+
                          |  Auth   |  X-API-Key
                          +---------+
```

## Project Structure

- `registry/main.py` — FastAPI app
- `registry/database.py` — SQLite access layer
- `registry/schemas.py` — Pydantic models
- `registry/api/` — Route handlers (skills, ratings, search)
- `registry/cli.py` — Click CLI client
- `registry/seed.py` — Database seeder with initial skills
- `skill/SKILL.md` — Agent-facing skill for using the registry
- `tests/` — Test suite

## Agent Integration

Include the `skill/SKILL.md` in your Hermes skills directory. When an agent encounters a capability gap, it can automatically:
1. Search the registry for relevant skills
2. Install the best match
3. Rate it after use
4. Publish improvements back

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./skills_registry.db` | Database connection |
| `API_HOST` | `0.0.0.0` | Server bind address |
| `API_PORT` | `8000` | Server port |
| `REGISTRY_URL` | `http://localhost:8000` | Registry URL for CLI |
| `PUBLISH_API_KEY` | `hermes-dev-key-2026` | API key for write operations |

## License

MIT — Hermes Agent Challenge 2026
