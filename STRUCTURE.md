hermes-skill-registry/
├── registry/
│   ├── __init__.py
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # Configuration
│   ├── database.py        # SQLite setup + connection
│   ├── models.py          # SQLAlchemy-style table definitions
│   ├── schemas.py         # Pydantic request/response models
│   ├── scoring.py         # Ranking/scoring algorithm
│   ├── auth.py            # Simple API key auth
│   ├── api/
│   │   ├── __init__.py
│   │   ├── skills.py      # CRUD endpoints for skills
│   │   ├── ratings.py     # Rating + review endpoints
│   │   └── search.py      # Search, filter, trending endpoints
│   └── cli.py             # Click-based CLI client
├── skill/
│   └── SKILL.md           # The skill-registry agent skill
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_cli.py
├── seed_data/
│   └── (seed skill fixtures)
├── requirements.txt
├── docker-compose.yml
├── README.md
└── setup.py
