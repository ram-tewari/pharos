#!/usr/bin/env python
"""Test production app routes."""
from app import create_app

app = create_app()

print("Production app created")
print(f"Total routes: {len([r for r in app.routes])}")

routes = [r.path for r in app.routes if hasattr(r, 'path') and '/api/' in r.path]
print(f"API routes: {len(routes)}")
print(f"Sample API routes:")
for r in sorted(routes)[:20]:
    print(f"  - {r}")
