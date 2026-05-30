"""Hermes Skill Registry — CLI client"""
from __future__ import annotations
import os
import sys
import click
import httpx
import yaml
from pathlib import Path

REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:8000")
API_KEY = os.getenv("PUBLISH_API_KEY", "hermes-dev-key-2026")
TIMEOUT = 30.0


def api(method: str, path: str, data: dict = None, key: str = None) -> dict:
    url = f"{REGISTRY_URL}{path}"
    headers = {}
    if key:
        headers["X-API-Key"] = key
    try:
        client = httpx.Client(follow_redirects=True, timeout=TIMEOUT)
        client.headers.update(headers)
        if method == "GET":
            r = client.get(url)
        elif method == "POST":
            r = client.post(url, json=data)
        elif method == "PUT":
            r = client.put(url, json=data)
        elif method == "DELETE":
            r = client.delete(url)
        else:
            raise ValueError(f"Unknown method: {method}")
        client.close()
        if r.status_code == 204:
            return {}
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail", r.text)
            except Exception:
                detail = r.text
            click.echo(f"Error ({r.status_code}): {detail}", err=True)
            sys.exit(1)
        return r.json() if r.text else {}
    except httpx.ConnectError:
        click.echo(f"Cannot connect to registry at {REGISTRY_URL}", err=True)
        sys.exit(1)
    except httpx.TimeoutException:
        click.echo("Request timed out", err=True)
        sys.exit(1)


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter (---)")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid SKILL.md frontmatter format")
    return yaml.safe_load(parts[1]) or {}


@click.group()
@click.option("--registry", default=REGISTRY_URL, help="Registry URL")
@click.pass_context
def cli(ctx, registry):
    """Hermes Skill Registry — npm for Hermes skills"""
    global REGISTRY_URL
    REGISTRY_URL = registry
    ctx.ensure_object(dict)


@cli.command()
@click.argument("query", default="")
@click.option("--category", default="")
@click.option("--tags", default="")
@click.option("--sort", default="score", type=click.Choice(["score", "newest", "popular", "rating"]))
@click.option("--page", default=1, type=int)
@click.option("--limit", default=20, type=int)
def search(query, category, tags, sort, page, limit):
    """Search skills."""
    params = f"?q={query}&category={category}&tags={tags}&sort={sort}&page={page}&page_size={limit}"
    result = api("GET", f"/api/v1/search{params}")
    skills = result.get("skills", [])
    total = result.get("total", 0)
    click.echo(f"Found {total} skills (showing {len(skills)}):\n")
    for s in skills:
        rating_str = "* {0:.1f}".format(s.get("avg_rating", 0)) if s.get("avg_rating") else "no ratings"
        click.echo("  [{0}] {1} v{2}  by {3}".format(s["id"], s["name"], s.get("version", "?"), s["author"]))
        click.echo("       {0}".format(str(s["description"])[:80]))
        click.echo("       {0} dl | {1} stars | {2} | {3}".format(
            s.get("downloads", 0), s.get("stars", 0), rating_str, s.get("category", "?")))
        click.echo()


@cli.command()
@click.argument("skill_id", type=int)
@click.option("--output", "-o", help="Output file path")
def install(skill_id, output):
    """Install a skill to ~/.hermes/skills/"""
    result = api("GET", f"/api/v1/skills/{skill_id}/download")
    skill_md = result["skill_md"]
    name = result.get("name", f"skill-{skill_id}")
    category = result.get("category", "uncategorized")
    if output:
        install_path = Path(output)
    else:
        skills_dir = Path.home() / ".hermes" / "skills" / category / name
        skills_dir.mkdir(parents=True, exist_ok=True)
        install_path = skills_dir / "SKILL.md"
    install_path.parent.mkdir(parents=True, exist_ok=True)
    install_path.write_text(skill_md)
    click.echo(f"Installed: {install_path}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--api-key", default=API_KEY)
def publish(path, api_key):
    """Publish a skill from SKILL.md."""
    p = Path(path)
    if p.is_dir():
        skill_file = p / "SKILL.md"
        if not skill_file.exists():
            click.echo(f"No SKILL.md in {p}", err=True)
            sys.exit(1)
    else:
        skill_file = p
    content = skill_file.read_text()
    try:
        fm = parse_frontmatter(content)
    except ValueError as e:
        click.echo(f"Invalid SKILL.md: {e}", err=True)
        sys.exit(1)
    result = api("POST", "/api/v1/skills", data={**fm, "skill_md": content}, key=api_key)
    name = fm.get("name", skill_file.parent.name)
    version = fm.get("version", "1.0.0")
    click.echo(f"Published: {name} v{version}")


@cli.command()
@click.argument("skill_id", type=int)
@click.argument("score", type=click.IntRange(1, 5))
@click.option("--review", default="")
@click.option("--user", default="anonymous")
@click.option("--api-key", default=API_KEY)
def rate(skill_id, score, review, user, api_key):
    """Rate a skill 1-5."""
    api("POST", f"/api/v1/skills/{skill_id}/rate",
        data={"score": score, "review": review or None, "user_id": user},
        key=api_key)
    click.echo(f"Rated {skill_id}: {score}/5")


@cli.command()
@click.argument("skill_id", type=int)
def inspect(skill_id):
    """Preview a skill."""
    s = api("GET", f"/api/v1/skills/{skill_id}")
    click.echo("Name: {0}\nVersion: {1}\nAuthor: {2}\nCategory: {3}\nTags: {4}".format(
        s["name"], s.get("version", "?"), s["author"], s.get("category", "?"), s.get("tags", "")))
    click.echo("Downloads: {0} | Stars: {1} | Rating: {2:.1f}".format(
        s.get("downloads", 0), s.get("stars", 0), s.get("avg_rating", 0)))
    click.echo("Description: {0}".format(s["description"]))
    md = s.get("skill_md", "")
    if md:
        click.echo("\n--- SKILL.md ---\n{0}...".format(md[:500]))


@cli.command()
@click.option("--days", default=7, type=int)
@click.option("--limit", default=10, type=int)
def trending(days, limit):
    """Show trending skills."""
    result = api("GET", f"/api/v1/trending?days={days}&limit={limit}")
    skills = result.get("skills", [])
    click.echo("Trending (last {0} days):\n".format(days))
    for s in skills:
        click.echo("  [{0}] {1} — {2} downloads".format(s["id"], s["name"], s.get("downloads", 0)))


@cli.command()
@click.argument("skill_id", type=int)
def star(skill_id):
    """Star a skill."""
    result = api("POST", f"/api/v1/skills/{skill_id}/star")
    click.echo("Skill {0} now has {1} stars".format(skill_id, result["stars"]))


if __name__ == "__main__":
    cli()
