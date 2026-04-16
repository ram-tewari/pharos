#!/usr/bin/env python3
"""
Verify that CLOUD mode doesn't load ML models.

This script tests that the app can start in CLOUD mode without loading
sentence-transformers or torch, which would cause OOM on Render.
"""

import os
import sys

# Set CLOUD mode before any imports
os.environ['MODE'] = 'CLOUD'
os.environ['TESTING'] = 'false'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

print("=" * 70)
print("CLOUD MODE VERIFICATION")
print("=" * 70)
print()

print("Step 1: Setting environment variables...")
print(f"  MODE={os.environ['MODE']}")
print(f"  TESTING={os.environ['TESTING']}")
print(f"  DATABASE_URL={os.environ['DATABASE_URL']}")
print()

print("Step 2: Importing app...")
try:
    from app import create_app
    print("  ✓ App import successful")
except Exception as e:
    print(f"  ✗ App import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 3: Checking for ML model imports...")

# Check if sentence-transformers was imported
if 'sentence_transformers' in sys.modules:
    print("  ✗ FAIL: sentence-transformers was imported!")
    print("    This will cause OOM on Render (512MB RAM)")
    sys.exit(1)
else:
    print("  ✓ PASS: sentence-transformers NOT imported")

# Check if torch was imported
if 'torch' in sys.modules:
    print("  ✗ FAIL: torch was imported!")
    print("    This will cause OOM on Render (512MB RAM)")
    sys.exit(1)
else:
    print("  ✓ PASS: torch NOT imported")

# Check if transformers was imported
if 'transformers' in sys.modules:
    print("  ⚠ WARNING: transformers was imported")
    print("    This might increase memory usage")
else:
    print("  ✓ PASS: transformers NOT imported")

print()
print("Step 4: Creating app instance...")
try:
    app = create_app()
    print("  ✓ App created successfully")
except Exception as e:
    print(f"  ✗ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 5: Checking circuit breakers...")
try:
    from app.shared.circuit_breaker import ai_embedding_breaker, ai_llm_breaker
    
    if ai_embedding_breaker is None:
        print("  ✓ PASS: ai_embedding_breaker is None (not created in CLOUD mode)")
    else:
        print("  ✗ FAIL: ai_embedding_breaker was created in CLOUD mode")
        sys.exit(1)
    
    if ai_llm_breaker is None:
        print("  ✓ PASS: ai_llm_breaker is None (not created in CLOUD mode)")
    else:
        print("  ✗ FAIL: ai_llm_breaker was created in CLOUD mode")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Circuit breaker check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✓ ALL CHECKS PASSED")
print("=" * 70)
print()
print("The app can start in CLOUD mode without loading ML models.")
print("This should prevent OOM errors on Render (512MB RAM).")
print()
print("Expected memory usage: <300MB (without ML models)")
print("Render limit: 512MB")
print()
