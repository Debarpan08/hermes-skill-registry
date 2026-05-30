"""Test suite for the Hermes Skill Registry API.

Prerequisites:
  - Registry server running on localhost:8000
  - pip install pytest httpx

Run:
  python3.11 -m pytest tests/test_api.py -v
"""
import httpx
import pytest

BASE = "http://localhost:8000"
KEY = "hermes-dev-key-2026"
CLIENT = httpx.Client(follow_redirects=True, timeout=30)


def get(path, **kw):
    return CLIENT.get(f"{BASE}{path}", **kw)

def post(path, json=None, headers=None):
    return CLIENT.post(f"{BASE}{path}", json=json, headers=headers or {})

def delete(path, headers=None):
    return CLIENT.delete(f"{BASE}{path}", headers=headers or {})


def api_headers():
    return {"X-API-Key": KEY}


import os as _os
_publish_counter = _os.getpid() * 1000

def unique_name():
    global _publish_counter
    _publish_counter += 1
    return f"test-pub-{_publish_counter}"


def create_skill(name=None, desc="Test skill"):
    payload = {
        "name": name or unique_name(),
        "description": desc,
        "author": "test-runner",
        "version": "1.0.0",
        "skill_md": f"---\nname: test\n---\n# Test\n",
    }
    r = post("/api/v1/skills", json=payload, headers=api_headers())
    assert r.status_code == 201, f"create_skill failed: {r.status_code} {r.text}"
    return r.json()


# ========== Health & Root ==========

def test_health():
    r = get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_root():
    r = get("/")
    assert r.status_code == 200
    assert "Hermes Skill Registry" in r.json()["service"]


# ========== Search ==========

def test_search_all():
    r = get("/api/v1/search")
    assert r.status_code == 200
    data = r.json()
    assert "skills" in data
    assert data["total"] >= 7

def test_search_with_query():
    r = get("/api/v1/search?q=test")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1

def test_search_by_category():
    r = get("/api/v1/search?category=software-development")
    assert r.status_code == 200
    for s in r.json()["skills"]:
        assert s["category"] == "software-development"

def test_search_sort_options():
    for sort in ["score", "newest", "popular", "rating"]:
        r = get(f"/api/v1/search?sort={sort}")
        assert r.status_code == 200, f"sort={sort} returned {r.status_code}"

def test_search_pagination():
    r = get("/api/v1/search?page=1&page_size=2")
    data = r.json()
    assert len(data["skills"]) <= 2


# ========== Skills CRUD ==========

def test_get_skill():
    r = get("/api/v1/skills/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert "name" in data
    assert "skill_md" in data

def test_get_skill_not_found():
    r = get("/api/v1/skills/99999")
    assert r.status_code == 404

def test_download_increments_count():
    r = get("/api/v1/skills/2")
    before = r.json()["downloads"]
    r = get("/api/v1/skills/2/download")
    assert r.status_code == 200
    assert "skill_md" in r.json()
    r = get("/api/v1/skills/2")
    assert r.json()["downloads"] == before + 1


# ========== Publish ==========

def test_publish_skill():
    skill = create_skill()
    assert skill["name"].startswith("test-pub-")
    assert skill["downloads"] == 0

def test_publish_duplicate_rejected():
    name = unique_name()
    create_skill(name=name, desc="First")
    r = post("/api/v1/skills", json={
        "name": name, "description": "Duplicate", "version": "1.0.0",
        "skill_md": "---\nname: dup\n---\n",
    }, headers=api_headers())
    assert r.status_code == 409

def test_publish_no_key_rejected():
    r = post("/api/v1/skills", json={
        "name": unique_name(), "description": "No key",
        "skill_md": "---\nname: no-key\n---\n",
    })
    assert r.status_code == 403

def test_publish_bad_key_rejected():
    r = post("/api/v1/skills", json={
        "name": unique_name(), "description": "Bad key",
        "skill_md": "---\nname: bad-key\n---\n",
    }, headers={"X-API-Key": "wrong"})
    assert r.status_code == 403


# ========== Ratings ==========

def test_rate_skill():
    r = get("/api/v1/search?limit=1")
    sid = r.json()["skills"][0]["id"]
    r = post(f"/api/v1/skills/{sid}/rate",
             json={"score": 4, "review": "Good", "user_id": "tester"},
             headers=api_headers())
    assert r.status_code == 200
    assert r.json()["score"] == 4

def test_rate_invalid_score():
    r = get("/api/v1/search?limit=1")
    sid = r.json()["skills"][0]["id"]
    r = post(f"/api/v1/skills/{sid}/rate",
             json={"score": 99, "user_id": "tester"},
             headers=api_headers())
    assert r.status_code == 422

def test_get_ratings():
    r = get("/api/v1/skills/1/ratings")
    assert r.status_code == 200
    assert "ratings" in r.json()

def test_rate_updates_avg():
    skill = create_skill(desc="Rating avg test")
    sid = skill["id"]
    post(f"/api/v1/skills/{sid}/rate", json={"score": 5, "user_id": "u1"}, headers=api_headers())
    post(f"/api/v1/skills/{sid}/rate", json={"score": 3, "user_id": "u2"}, headers=api_headers())
    r = get(f"/api/v1/skills/{sid}")
    assert r.json()["avg_rating"] == 4.0


# ========== Stars ==========

def test_star_skill():
    skill = create_skill(desc="Star test")
    sid = skill["id"]
    r = post(f"/api/v1/skills/{sid}/star")
    assert r.status_code == 200
    assert r.json()["stars"] >= 1


# ========== Trending ==========

def test_trending():
    r = get("/api/v1/trending")
    assert r.status_code == 200
    assert "skills" in r.json()

def test_trending_params():
    r = get("/api/v1/trending?days=14&limit=5")
    assert r.status_code == 200
    assert len(r.json()["skills"]) <= 5


# ========== Delete ==========

def test_delete_skill():
    skill = create_skill(desc="Delete me")
    sid = skill["id"]
    r = delete(f"/api/v1/skills/{sid}", headers=api_headers())
    assert r.status_code == 204
    r = get(f"/api/v1/skills/{sid}")
    assert r.status_code == 404

def test_delete_no_key_rejected():
    r = delete("/api/v1/skills/1")
    assert r.status_code == 403
