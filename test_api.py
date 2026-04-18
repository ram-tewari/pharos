"""
Comprehensive Pharos API test — search + graph + github modules.
Usage: python test_api.py
"""
import urllib.request, urllib.error, json, time, sys

BASE = "https://pharos-cloud-api.onrender.com"
FASTAPI_ID = "918765a9-c055-438a-bdb7-60ff12c0a706"
ORIGIN = BASE

def req(url, method="GET", body=None, timeout=45):
    headers = {"Origin": ORIGIN, "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return True, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return False, json.loads(e.read())
        except Exception:
            return False, {"error": f"HTTP {e.code}"}
    except Exception as ex:
        return False, {"error": str(ex)[:120]}

def summarise(d):
    if "total" in d and isinstance(d["total"], (int, float)):
        items = d.get("items") or d.get("results") or []
        extra = ""
        if "latency_ms" in d:
            extra = f" latency={d['latency_ms']:.0f}ms"
        if "method_contributions" in d:
            mc = d["method_contributions"]
            extra += f" contrib(fts5={mc.get('fts5',0)},dense={mc.get('dense',0)},sparse={mc.get('sparse',0)})"
        if "code_metrics" in d and d["code_metrics"]:
            cm = d["code_metrics"]
            extra += f" code_metrics(local={cm.get('local_chunks',0)},remote={cm.get('remote_chunks',0)})"
        return "total=%d items=%d%s" % (d["total"], len(items), extra)
    if "status" in d:
        extra = ""
        if "cache_available" in d:
            extra = f" cache={d['cache_available']} token={d.get('github_token_configured')}"
        return "status=%s%s" % (d["status"], extra)
    if "entities" in d:
        return "entities=%d (total=%d)" % (len(d["entities"]), d.get("total_count", 0))
    if "nodes" in d:
        return "nodes=%d edges=%d" % (len(d["nodes"]), len(d["edges"]))
    if "methods" in d:
        methods = {k: v.get("total", 0) for k, v in d["methods"].items()}
        return "methods=%s" % methods
    if "hypotheses" in d:
        return "hypotheses=%d exec=%.2fs" % (d.get("count", 0), d.get("execution_time", 0))
    if "code" in d:
        snippet = (d.get("code") or "")[:50].replace("\n", " ")
        return "code=%r cache_hit=%s latency=%.0fms" % (snippet, d.get("cache_hit"), d.get("latency_ms", 0))
    if "metrics" in d and isinstance(d["metrics"], dict):
        return "cached=%s computation_ms=%.0f" % (d.get("cached"), d.get("computation_time_ms", 0))
    if "detail" in d:
        return "ERROR: %s" % str(d["detail"])[:100]
    return str(list(d.keys())[:6])

tests = [
    # --- SEARCH ---
    ("SEARCH", "search/health",              f"{BASE}/api/search/search/health", "GET", None),
    ("SEARCH", "standard: 'langchain'",      f"{BASE}/api/search/search", "POST",
        {"text": "langchain", "limit": 5}),
    ("SEARCH", "standard: 'FastAPI'",        f"{BASE}/api/search/search", "POST",
        {"text": "FastAPI", "limit": 5}),
    ("SEARCH", "hybrid: 'langchain'",        f"{BASE}/api/search/search/three-way-hybrid?query=langchain&limit=5", "GET", None),
    ("SEARCH", "hybrid: 'FastAPI framework'",f"{BASE}/api/search/search/three-way-hybrid?query=FastAPI+framework&limit=5", "GET", None),
    ("SEARCH", "compare-methods: 'FastAPI'", f"{BASE}/api/search/search/compare-methods?query=FastAPI&limit=3", "GET", None),
    # --- ADVANCED SEARCH ---
    ("ADV",    "parent-child: FastAPI",      f"{BASE}/api/search/advanced", "POST",
        {"query": "FastAPI dependency injection", "strategy": "parent-child", "top_k": 5, "context_window": 1}),
    ("ADV",    "graphrag: routing",          f"{BASE}/api/search/advanced", "POST",
        {"query": "routing endpoints middleware", "strategy": "graphrag", "top_k": 5}),
    ("ADV",    "hybrid: web framework",      f"{BASE}/api/search/advanced", "POST",
        {"query": "web framework performance", "strategy": "hybrid", "top_k": 5}),
    ("ADV",    "include_code=True",          f"{BASE}/api/search/advanced", "POST",
        {"query": "FastAPI", "strategy": "parent-child", "top_k": 3, "include_code": True}),
    # --- GRAPH ---
    ("GRAPH",  "overview",                   f"{BASE}/api/graph/overview?limit=20", "GET", None),
    ("GRAPH",  "entities (all)",             f"{BASE}/api/graph/entities?limit=10", "GET", None),
    ("GRAPH",  "entities: type=Concept",     f"{BASE}/api/graph/entities?entity_type=Concept&limit=5", "GET", None),
    ("GRAPH",  "entities: name=fastapi",     f"{BASE}/api/graph/entities?name_contains=fastapi&limit=5", "GET", None),
    ("GRAPH",  "neighbors: FastAPI",         f"{BASE}/api/graph/resource/{FASTAPI_ID}/neighbors?limit=5", "GET", None),
    ("GRAPH",  "discover A=fastapi C=python",f"{BASE}/api/graph/discover?concept_a=fastapi&concept_c=python&limit=10", "POST", None),
    ("GRAPH",  "centrality: FastAPI",        f"{BASE}/api/graph/centrality?resource_ids={FASTAPI_ID}", "GET", None),
    # --- GITHUB ---
    ("GH",     "github/health",              f"{BASE}/api/github/health", "GET", None),
    ("GH",     "fetch: langchain README L1-10", f"{BASE}/api/github/fetch", "POST", {
        "github_uri": "https://raw.githubusercontent.com/langchain-ai/langchain/master/README.md",
        "branch_reference": "master", "start_line": 1, "end_line": 10}),
    ("GH",     "fetch-batch: 2 chunks",      f"{BASE}/api/github/fetch-batch", "POST", {
        "chunks": [
            {"github_uri": "https://raw.githubusercontent.com/langchain-ai/langchain/master/README.md",
             "branch_reference": "master", "start_line": 1, "end_line": 5},
            {"github_uri": "https://raw.githubusercontent.com/tiangolo/fastapi/master/README.md",
             "branch_reference": "master", "start_line": 1, "end_line": 5},
        ]}),
]

passed = failed = 0
print("=" * 72)
print("PHAROS API COMPREHENSIVE TEST")
print("=" * 72)
print()

current_section = None
for section, label, url, method, body in tests:
    if section != current_section:
        print(f"--- {section} {'---' * 15}")
        current_section = section

    t0 = time.time()
    ok, d = req(url, method, body)
    ms = (time.time() - t0) * 1000

    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1

    summary = summarise(d)
    print("[%s] %-35s %5.0fms  %s" % (status, label, ms, summary))

print()
print("=" * 72)
print("RESULTS: %d/%d passed" % (passed, passed + failed))
print("=" * 72)
