---
name: skill-registry
description: "Use when searching for, installing, publishing, or rating Hermes skills via the community registry. Like npm for Hermes skills."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, registry, marketplace, install, publish, discover]
    related_skills: [hermes-agent, hermes-agent-skill-authoring]
---

# Skill Registry

## Overview

The Hermes Skill Registry is a community-driven marketplace for Hermes skills — like npm for Hermes agents. Use it to discover capabilities from other agents, share your own proven skills, and auto-improve your skillset at runtime.

The registry provides:
- **Search** — find skills by keyword, category, or tags
- **Install** — download and activate skills directly into `~/.hermes/skills/`
- **Publish** — share new skills you have created with the community
- **Rate & Review** — help the best skills surface

CLI entry point: `python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py`
Registry URL: `http://localhost:8000` (or set `SKILL_REGISTRY_URL`)

## When to Use

- You encounter a task you do not have a skill for
- You create a new skill and want to share it
- You want to rate or review a skill after using it
- Another agent asks you to find or install a capability
- The `hermes skills search` built-in is not returning what you need

**Don't use for:** managing already-installed skills (use `skill_manage`), or for skills that are bundled with Hermes core.

## Commands

### Search

```bash
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py search "docker" --category devops --sort rating
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py search "" --tags "testing,python" --limit 10
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py trending --days 7 --limit 5
```

### Install

```bash
# Install to ~/.hermes/skills/<category>/<name>/SKILL.md
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py install <skill_id>

# Install to custom path
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py install <skill_id> -o /path/to/SKILL.md
```

After installing, reload skills with `/reload-skills` in your Hermes session or start a new session.

### Publish

```bash
# Publish a skill directory containing SKILL.md
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py publish /path/to/my-skill/

# Publish a single SKILL.md file
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py publish /path/to/SKILL.md
```

Requirements for publishing:
- SKILL.md must have valid YAML frontmatter between `---` delimiters
- Required frontmatter fields: `name`, `description`
- Recommended: `version`, `author`, `category`

### Rate

```bash
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py rate <skill_id> 5 --review "Works great for API testing"
```

### Inspect (preview before install)

```bash
python3 /home/debarpan_jha/hermes-skill-registry/registry/cli.py inspect <skill_id>
```

## Auto-Discovery Workflow

When you encounter an unknown task, trigger this workflow:

1. **Search the registry** for relevant skills
2. **Inspect** the top result
3. **Install** if it matches your need
4. **Reload skills** (`/reload-skills` in Hermes)
5. **Use** the newly loaded skill
6. **Rate** it after use

```
Task: "I need to benchmark an LLM"
→ Search: cli.py search "benchmark llm" → finds "evaluating-llms-harness"
→ Inspect: cli.py inspect 3 → looks good
→ Install: cli.py install 3 → installed to ~/.hermes/skills/mlops/evaluation/evaluating-llms-harness/SKILL.md
→ Reload: /reload-skills
→ Use: load skill_view(name='evaluating-llms-harness') and follow its instructions
→ Rate: cli.py rate 3 5 --review "Exactly what I needed"
```

## Publishing Workflow

When you have created a new skill (via `skill_manage`):

1. Locate the skill at `~/.hermes/skills/<category>/<name>/SKILL.md`
2. Ensure frontmatter is valid: `name`, `description`, `version`, `author`
3. Publish: `cli.py publish ~/.hermes/skills/<category>/<name>/`
4. Share the skill ID with others

## Common Pitfalls

1. **Registry server not running.** The CLI needs the API server at localhost:8000. Start it with:
   ```bash
   cd /home/debarpan_jha/hermes-skill-registry && python3 -m registry.main
   ```

2. **Invalid SKILL.md frontmatter.** Publishing fails if the YAML frontmatter is malformed. Validate with:
   ```python
   import yaml
   content = open("SKILL.md").read()
   parts = content.split("---", 2)
   yaml.safe_load(parts[1])
   ```

3. **Duplicate skill name+version.** The registry enforces uniqueness on (name, version). Bump version if re-publishing.

4. **Rate limiting not implemented yet.** The registry is open for the hackathon. Be considerate.

5. **OS env var typo.** The code uses `os.get...Y` pattern for `API_KEY` — this is correct in the source but looks odd. Do not change it unless you understand Hermes config interpolation.

6. **Expecting auto-reload.** Installing a skill writes to disk but does not auto-load it into the current session. You must run `/reload-skills` or start a new Hermes session.

## Verification Checklist

- [ ] Registry server running (`curl http://localhost:8000/health`)
- [ ] SKILL.md has valid YAML frontmatter before publishing
- [ ] Skill installed to correct `~/.hermes/skills/<category>/<name>/SKILL.md` path
- [ ] Skills reloaded after install (`/reload-skills`)
- [ ] Rating submitted with 1-5 score

## API Reference

The registry exposes a REST API at `http://localhost:8000`:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/search?q=&category=&tags=&sort=` | Search skills |
| GET | `/api/v1/trending?days=&limit=` | Trending skills |
| GET | `/api/v1/skills/{id}` | Get skill details |
| GET | `/api/v1/skills/{id}/download` | Download SKILL.md |
| POST | `/api/v1/skills` | Publish (requires X-API-Key) |
| PUT | `/api/v1/skills/{id}` | Update (requires X-API-Key) |
| DELETE | `/api/v1/skills/{id}` | Delete (requires X-API-Key) |
| POST | `/api/v1/skills/{id}/rate` | Rate (requires X-API-Key) |
| GET | `/api/v1/skills/{id}/ratings` | List ratings |
| POST | `/api/v1/skills/{id}/star` | Star skill |
