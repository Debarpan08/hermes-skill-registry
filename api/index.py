"""Vercel serverless entry point for Hermes Skill Registry."""
import sys
from pathlib import Path

# Add project root to Python path so 'registry' package imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from mangum import Mangum
from registry.main import app

handler = Mangum(app, lifespan="on")
