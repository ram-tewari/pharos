#!/usr/bin/env python3
"""API integration test for Phase 1 search fixes.

This script tests the /api/search/advanced endpoint with include_code=true
to verify that file_name, github_uri, start_line, end_line, and code are
properly populated in the response.

Prerequisites:
1. API server running: uvicorn app.main:app --reload
2. At least one repository ingested with GitHub URIs
3. PHAROS_ADMIN_TOKEN environment variable set (if auth enabled)
"""

import os
import sys
import json
import httpx
from typing import Optional

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("PHAROS_ADMIN_TOKEN", "")

def get_headers() -> dict:
    """Build request headers with optional auth."""
    headers = {"Content-Type": "application/json"}
    if ADMIN_TOKEN:
        headers["Authorization"] = f"Bearer {ADMIN_TOKEN}"
    return headers

def test_advanced_search(query: str = "authentication", strategy: str = "parent-child"):
    """Test advanced search with include_code=true."""
    print(f"\n{'='*80}")
    print(f"Testing: POST /api/search/advanced")
    print(f"Query: {query}")
    print(f"Strategy: {strategy}")
    print(f"{'='*80}\n")
    
    payload = {
        "query": query,
        "strategy": strategy,
        "top_k": 5,
        "context_window": 2,
        "include_code": True,
    }
    
    try:
        response = httpx.post(
            f"{API_BASE}/api/search/advanced",
            json=payload,
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Latency: {data.get('latency_ms', 0):.1f}ms")
        print(f"✅ Results: {data.get('total', 0)}")
        
        # Check code_metrics
        if "code_metrics" in data and data["code_metrics"]:
            metrics = data["code_metrics"]
            print(f"\n📊 Code Fetch Metrics:")
            print(f"   Total chunks: {metrics.get('total_chunks', 0)}")
            print(f"   Fetched: {metrics.get('fetched', 0)}")
            print(f"   Cache hits: {metrics.get('cache_hits', 0)}")
            print(f"   Errors: {metrics.get('errors', 0)}")
            print(f"   Fetch time: {metrics.get('fetch_time_ms', 0):.1f}ms")
        
        # Validate first result
        results = data.get("results", [])
        if not results:
            print("\n⚠️  No results returned (database may be empty)")
            return True
        
        print(f"\n🔍 Validating first result...")
        result = results[0]
        chunk = result.get("chunk", {})
        
        # Phase 1 critical fields
        checks = {
            "id": chunk.get("id"),
            "file_name": chunk.get("file_name"),
            "github_uri": chunk.get("github_uri"),
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
            "symbol_name": chunk.get("symbol_name"),
            "ast_node_type": chunk.get("ast_node_type"),
            "code": chunk.get("code"),
            "source": chunk.get("source"),
        }
        
        all_ok = True
        for field, value in checks.items():
            if value is None:
                print(f"   ❌ {field}: None (MISSING)")
                all_ok = False
            elif isinstance(value, str) and not value:
                print(f"   ❌ {field}: empty string (MISSING)")
                all_ok = False
            else:
                preview = str(value)[:60]
                if len(str(value)) > 60:
                    preview += "..."
                print(f"   ✅ {field}: {preview}")
        
        # Check surrounding chunks
        surrounding = result.get("surrounding_chunks", [])
        print(f"\n📦 Surrounding chunks: {len(surrounding)}")
        if surrounding:
            for i, sc in enumerate(surrounding[:2], 1):
                code_present = "✅" if sc.get("code") else "❌"
                print(f"   {code_present} Chunk {i}: code={'present' if sc.get('code') else 'MISSING'}")
        
        if all_ok:
            print(f"\n{'='*80}")
            print("✅ PHASE 1 VERIFICATION PASSED")
            print("All critical fields are populated correctly!")
            print(f"{'='*80}")
            return True
        else:
            print(f"\n{'='*80}")
            print("❌ PHASE 1 VERIFICATION FAILED")
            print("Some fields are missing or empty")
            print(f"{'='*80}")
            return False
            
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:500]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Test API health endpoint."""
    print(f"\n{'='*80}")
    print("Testing: GET /health")
    print(f"{'='*80}\n")
    
    try:
        response = httpx.get(f"{API_BASE}/health", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status: {data.get('status')}")
        print(f"✅ Database: {data.get('database')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    print(f"\n{'='*80}")
    print("PHASE 1 API INTEGRATION TEST")
    print(f"API Base: {API_BASE}")
    print(f"Auth: {'Enabled' if ADMIN_TOKEN else 'Disabled'}")
    print(f"{'='*80}")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ API server not responding. Start with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Test 2: Advanced search with include_code
    success = test_advanced_search()
    
    if success:
        print("\n✅ All API tests passed!")
        print("\nNext: Re-ingest a non-Python repo to test Phase 2 polyglot AST:")
        print("  POST /api/v1/ingestion/ingest/github.com/owner/repo")
        sys.exit(0)
    else:
        print("\n❌ API tests failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
