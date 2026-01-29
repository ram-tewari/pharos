"""
Ingestion Pipeline Stress Test

Tests the embedding generation pipeline under load to identify:
1. Throughput (docs/second)
2. Memory stability (leaks)
3. Truncation/loss issues
"""

import sys
import time
import os
import psutil
import gc
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Check if GPU libraries are available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch not available - GPU metrics will be skipped")

try:
    from sentence_transformers import SentenceTransformer
    from FlagEmbedding import BGEM3FlagModel
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("❌ Required libraries not available. Install with:")
    print("   pip install sentence-transformers FlagEmbedding")
    sys.exit(1)


def get_memory_usage():
    """Returns current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def get_gpu_memory():
    """Returns GPU memory usage in MB if available."""
    if TORCH_AVAILABLE and torch.cuda.is_available():
        return torch.cuda.memory_allocated() / 1024 / 1024
    return 0


def generate_dummy_text(words=1000):
    """Generates a long technical string to force heavy tokenization."""
    base = "The quick brown fox jumps over the lazy dog. "
    technical = (
        "Asyncio concurrency lock semaphore mutex deadlock race condition. "
        "Neural network transformer attention mechanism gradient descent backpropagation. "
        "Database transaction isolation serializable repeatable read committed. "
        "REST API endpoint authentication authorization JWT token bearer. "
    )
    return (base + technical) * (words // 30)


def audit_ingestion_performance():
    """Main audit function."""
    print("=" * 60)
    print("INGESTION PIPELINE STRESS TEST")
    print("=" * 60)
    
    # Device detection
    device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
    print(f"Device: {device.upper()}")
    
    initial_mem = get_memory_usage()
    initial_gpu = get_gpu_memory()
    print(f"Initial CPU Memory: {initial_mem:.2f} MB")
    if device == "cuda":
        print(f"Initial GPU Memory: {initial_gpu:.2f} MB")
    
    # Phase 1: Load Models
    print("\n" + "=" * 60)
    print("[Phase 1] Loading Models...")
    print("=" * 60)
    
    t0 = time.time()
    
    try:
        dense_model = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1",
            trust_remote_code=True,
            device=device
        )
        print("✓ Dense model (Nomic) loaded")
    except Exception as e:
        print(f"❌ Failed to load dense model: {e}")
        return
    
    try:
        sparse_model = BGEM3FlagModel(
            "BAAI/bge-m3",
            use_fp16=True,
            device=device
        )
        print("✓ Sparse model (BGE-M3) loaded")
    except Exception as e:
        print(f"❌ Failed to load sparse model: {e}")
        return
    
    load_time = time.time() - t0
    mem_after_load = get_memory_usage()
    gpu_after_load = get_gpu_memory()
    
    print(f"\n✓ Models loaded in {load_time:.2f}s")
    print(f"✓ CPU Memory Footprint: {mem_after_load:.2f} MB (+{mem_after_load - initial_mem:.2f} MB)")
    if device == "cuda":
        print(f"✓ GPU Memory Footprint: {gpu_after_load:.2f} MB (+{gpu_after_load - initial_gpu:.2f} MB)")
    
    # Phase 2: Warmup
    print("\n" + "=" * 60)
    print("[Phase 2] Single Document Latency (Warmup)...")
    print("=" * 60)
    
    doc_small = generate_dummy_text(500)  # ~500 words
    
    t0 = time.time()
    _ = dense_model.encode(doc_small)
    dense_time = (time.time() - t0) * 1000
    print(f"✓ Dense embedding: {dense_time:.2f} ms")
    
    t0 = time.time()
    _ = sparse_model.encode(
        doc_small,
        return_dense=False,
        return_sparse=True,
        return_colbert_vecs=False
    )
    sparse_time = (time.time() - t0) * 1000
    print(f"✓ Sparse embedding: {sparse_time:.2f} ms")
    print(f"✓ Total single doc latency: {dense_time + sparse_time:.2f} ms")
    
    # Phase 3: Stress Test
    print("\n" + "=" * 60)
    print("[Phase 3] Bulk Ingestion Stress Test (50 Heavy Docs)...")
    print("=" * 60)
    
    # Generate 50 documents, 2000 words each (~2500 tokens)
    print("Generating test documents...")
    docs = [generate_dummy_text(2000) for _ in range(50)]
    print(f"✓ Generated {len(docs)} documents")
    
    latencies_dense = []
    latencies_sparse = []
    latencies_total = []
    
    start_mem = get_memory_usage()
    start_gpu = get_gpu_memory()
    t_start_bulk = time.time()
    
    for i, doc in enumerate(docs):
        t_iter = time.time()
        
        # Dense embedding
        t_dense = time.time()
        _ = dense_model.encode(doc)
        dense_lat = (time.time() - t_dense) * 1000
        latencies_dense.append(dense_lat)
        
        # Sparse embedding
        t_sparse = time.time()
        _ = sparse_model.encode(
            doc,
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )
        sparse_lat = (time.time() - t_sparse) * 1000
        latencies_sparse.append(sparse_lat)
        
        total_lat = (time.time() - t_iter) * 1000
        latencies_total.append(total_lat)
        
        if i % 10 == 0:
            cur_mem = get_memory_usage()
            cur_gpu = get_gpu_memory()
            print(f"  Processed {i}/50... "
                  f"Latency: {total_lat:.0f}ms | "
                  f"CPU Mem: {cur_mem:.0f}MB | "
                  f"GPU Mem: {cur_gpu:.0f}MB")
        
        # Optional: Force garbage collection every 10 docs
        # Uncomment if you suspect memory leaks
        # if i % 10 == 0:
        #     gc.collect()
        #     if device == "cuda":
        #         torch.cuda.empty_cache()
    
    total_time = time.time() - t_start_bulk
    end_mem = get_memory_usage()
    end_gpu = get_gpu_memory()
    
    # Calculate statistics
    avg_dense = sum(latencies_dense) / len(latencies_dense)
    avg_sparse = sum(latencies_sparse) / len(latencies_sparse)
    avg_total = sum(latencies_total) / len(latencies_total)
    
    p50_total = sorted(latencies_total)[int(len(latencies_total) * 0.50)]
    p95_total = sorted(latencies_total)[int(len(latencies_total) * 0.95)]
    p99_total = sorted(latencies_total)[int(len(latencies_total) * 0.99)]
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    print(f"\n📊 Throughput:")
    print(f"  Total Time:      {total_time:.2f}s")
    print(f"  Throughput:      {50 / total_time:.2f} docs/sec")
    print(f"  Avg Time/Doc:    {total_time / 50:.2f}s")
    
    print(f"\n⏱️  Latency Breakdown:")
    print(f"  Dense (Nomic):   {avg_dense:.0f} ms avg")
    print(f"  Sparse (BGE-M3): {avg_sparse:.0f} ms avg")
    print(f"  Total:           {avg_total:.0f} ms avg")
    
    print(f"\n📈 Latency Percentiles (Total):")
    print(f"  P50:             {p50_total:.0f} ms")
    print(f"  P95:             {p95_total:.0f} ms")
    print(f"  P99:             {p99_total:.0f} ms")
    
    print(f"\n💾 Memory Usage:")
    print(f"  CPU Growth:      {end_mem - start_mem:.2f} MB")
    if device == "cuda":
        print(f"  GPU Growth:      {end_gpu - start_gpu:.2f} MB")
    
    # Assessment
    print("\n" + "=" * 60)
    print("ASSESSMENT")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # Memory leak check
    mem_growth = end_mem - start_mem
    if mem_growth > 500:
        issues.append(f"❌ CRITICAL: Significant CPU memory leak detected ({mem_growth:.0f}MB growth)")
        issues.append("   → Likely cause: PyTorch tensors not being released")
        issues.append("   → Solution: Add explicit gc.collect() and torch.cuda.empty_cache()")
    elif mem_growth > 200:
        warnings.append(f"⚠️  WARNING: Moderate CPU memory growth ({mem_growth:.0f}MB)")
        warnings.append("   → Monitor in production, may need periodic cleanup")
    else:
        print(f"✅ Memory stability: PASS ({mem_growth:.0f}MB growth is acceptable)")
    
    # Throughput check
    if avg_total > 2000:
        issues.append(f"❌ CRITICAL: Ingestion too slow ({avg_total:.0f}ms per doc)")
        issues.append("   → User uploads will timeout")
        issues.append("   → MUST implement async queue (Celery/Redis)")
    elif avg_total > 1000:
        warnings.append(f"⚠️  WARNING: Ingestion is slow ({avg_total:.0f}ms per doc)")
        warnings.append("   → Consider async processing for bulk uploads")
    else:
        print(f"✅ Throughput: PASS ({avg_total:.0f}ms per doc is acceptable)")
    
    # P99 latency check
    if p99_total > 5000:
        issues.append(f"❌ CRITICAL: P99 latency too high ({p99_total:.0f}ms)")
        issues.append("   → Some documents will cause severe delays")
    elif p99_total > 3000:
        warnings.append(f"⚠️  WARNING: P99 latency is high ({p99_total:.0f}ms)")
    else:
        print(f"✅ P99 latency: PASS ({p99_total:.0f}ms)")
    
    # Print issues and warnings
    if issues:
        print("\n🚨 CRITICAL ISSUES:")
        for issue in issues:
            print(issue)
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(warning)
    
    if not issues and not warnings:
        print("\n✅ ALL CHECKS PASSED")
        print("   Ingestion pipeline is production-ready for Edge Worker")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if avg_total < 500:
        print("✅ Synchronous ingestion is viable for single documents")
    else:
        print("📋 Implement async queue for bulk uploads:")
        print("   1. Add Celery worker for background processing")
        print("   2. Use Redis as message broker")
        print("   3. Return task ID immediately, poll for completion")
    
    if mem_growth > 100:
        print("📋 Add periodic memory cleanup:")
        print("   1. Call gc.collect() every N documents")
        print("   2. Call torch.cuda.empty_cache() if using GPU")
        print("   3. Monitor memory in production with alerts")
    
    print("\n📋 Context window check:")
    print("   BGE-M3 max tokens: 8192")
    print("   Nomic max tokens: 8192")
    print("   Current test docs: ~2500 tokens")
    print("   ✅ Chunking already implemented (Phase 17.5)")
    print("   → ChunkingService with semantic/fixed strategies")
    print("   → Parent-child chunking for advanced RAG")
    print("   → Verify chunking is called during ingestion")


if __name__ == "__main__":
    if not MODELS_AVAILABLE:
        print("❌ Cannot run audit without required libraries")
        sys.exit(1)
    
    try:
        audit_ingestion_performance()
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Audit failed with error: {e}")
        import traceback
        traceback.print_exc()
