#!/usr/bin/env python
"""Test imports to find circular dependency."""
import os
os.environ["TESTING"] = "true"

print("1. Testing basic imports...")
from pydantic import BaseModel
print("✓ Pydantic")

print("2. Testing resources schema...")
from app.modules.resources.schema import ResourceRead
print("✓ ResourceRead")

print("3. Testing search schema import...")
import app.modules.search.schema as search_schema
print("✓ Search schema imported")

print("4. Testing SearchQuery...")
print(f"SearchQuery: {search_schema.SearchQuery}")
print("✓ All imports successful!")
