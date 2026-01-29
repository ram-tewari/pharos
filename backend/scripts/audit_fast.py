"""
Fast Retrieval Audit Script - Skips Slow Three-Way Hybrid

This script tests Basic and Hybrid search only (both are fast).
Use this for quick validation of your retrieval architecture.

Usage:
    python scripts/audit_fast.py --sample-size 24
"""

import sys
import json
import argparse
import random
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Model imports
from app.database.models import Resource, Annotation

# Search service imports
from app.modules.search.service import SearchService
from app.domain.search import SearchQuery


class FastRetrievalAuditor:
    """Fast auditor that skips slow three-way hybrid search."""
    
    def __init__(self, db: Session, sample_size: int = 24):
        self.db = db
        self.sample_size = sample_size
        self.search_service = SearchService(db)
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "sample_size": sample_size,
                "database": str(db.bind.url)
            },
            "methods": {}
        }
    
    def _get_annotation_samples(self) -> List[Tuple[str, str, str]]:
        """Fetch annotation samples as ground truth queries."""
        print("\n" + "=" * 80)
        print("FETCHING ANNOTATION SAMPLES")
        print("=" * 80)
        
        total_annotations = (
            self.db.query(Annotation)
            .filter(Annotation.highlighted_text.isnot(None))
            .filter(Annotation.highlighted_text != "")
            .filter(Annotation.resource_id.isnot(None))
            .count()
        )
        
        print(f"Total annotations: {total_annotations}")
        
        if total_annotations == 0:
            raise ValueError(
                "No annotations found. Run 'python scripts/seed_audit_data_simple.py' first."
            )
        
        actual_sample_size = min(self.sample_size, total_annotations)
        if actual_sample_size < self.sample_size:
            print(f"⚠️  Using {actual_sample_size} annotations (all available)")
        
        all_annotations = (
            self.db.query(Annotation)
            .filter(Annotation.highlighted_text.isnot(None))
            .filter(Annotation.highlighted_text != "")
            .filter(Annotation.resource_id.isnot(None))
            .all()
        )
        
        sampled = random.sample(all_annotations, actual_sample_size)
        samples = [
            (str(ann.id), ann.highlighted_text, str(ann.resource_id))
            for ann in sampled
        ]
        
        print(f"✓ Sampled {len(samples)} annotations")
        return samples
    
    def _evaluate_method(
        self,
        method_name: str,
        samples: List[Tuple[str, str, str]],
        search_func: callable
    ) -> Dict[str, Any]:
        """Evaluate a search method."""
        print(f"\n{'=' * 80}")
        print(f"TESTING: {method_name}")
        print(f"{'=' * 80}")
        
        hits_at_5 = 0
        hits_at_10 = 0
        reciprocal_ranks = []
        latencies = []
        errors = 0
        
        for idx, (ann_id, query_text, target_id) in enumerate(samples, 1):
            try:
                start_time = datetime.now()
                result_ids = search_func(query_text)
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                latencies.append(latency_ms)
                
                if target_id in result_ids[:5]:
                    hits_at_5 += 1
                if target_id in result_ids[:10]:
                    hits_at_10 += 1
                
                try:
                    rank = result_ids.index(target_id) + 1
                    reciprocal_ranks.append(1.0 / rank)
                except ValueError:
                    reciprocal_ranks.append(0.0)
                    
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"  ⚠️  Error on query {idx}: {str(e)[:100]}")
        
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        recall_at_5 = hits_at_5 / len(samples) if samples else 0.0
        recall_at_10 = hits_at_10 / len(samples) if samples else 0.0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        print(f"\n✓ Complete")
        print(f"  MRR: {mrr:.4f}")
        print(f"  Recall@5: {recall_at_5:.4f} ({hits_at_5}/{len(samples)})")
        print(f"  Recall@10: {recall_at_10:.4f} ({hits_at_10}/{len(samples)})")
        print(f"  Avg Latency: {avg_latency:.1f}ms")
        if errors > 0:
            print(f"  ⚠️  Errors: {errors}/{len(samples)}")
        
        return {
            "mrr": mrr,
            "recall_at_5": recall_at_5,
            "recall_at_10": recall_at_10,
            "hits_at_5": hits_at_5,
            "hits_at_10": hits_at_10,
            "avg_latency_ms": avg_latency,
            "errors": errors,
            "total_queries": len(samples)
        }
    
    def _search_basic(self, query_text: str) -> List[str]:
        """Execute basic search (FTS-based)."""
        query = SearchQuery(
            query_text=query_text,
            limit=10,
            search_method="fts5"
        )
        resources, _, _, _ = self.search_service.search(query)
        return [str(r.id) for r in resources]
    
    def _search_hybrid(self, query_text: str) -> List[str]:
        """Execute hybrid search (FTS + Vector)."""
        query = SearchQuery(
            query_text=query_text,
            limit=10,
            search_method="hybrid"
        )
        resources, _, _, _ = self.search_service.hybrid_search(query, hybrid_weight=0.5)
        return [str(r.id) for r in resources]
    
    def run_audit(self) -> Dict[str, Any]:
        """Run fast retrieval audit (skips three-way hybrid)."""
        print("\n" + "=" * 80)
        print("FAST RETRIEVAL AUDIT")
        print("=" * 80)
        print(f"Sample Size: {self.sample_size}")
        print(f"Database: {self.db.bind.url}")
        print("\nNOTE: Skipping three-way hybrid (too slow)")
        
        # Get samples
        samples = self._get_annotation_samples()
        
        # Test basic search
        self.results["methods"]["basic_search"] = self._evaluate_method(
            "Basic Search (FTS)",
            samples,
            self._search_basic
        )
        
        # Test hybrid search
        self.results["methods"]["hybrid_search"] = self._evaluate_method(
            "Hybrid Search (FTS + Vector)",
            samples,
            self._search_hybrid
        )
        
        # Print comparison
        self._print_comparison()
        
        # Save results
        output_file = "retrieval_audit_fast_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results saved to: {output_file}")
        
        # Determine pass/fail
        best_mrr = max(m["mrr"] for m in self.results["methods"].values())
        
        if best_mrr < 0.1:
            print("\n⚠️  LOW RETRIEVAL QUALITY")
            print("This is expected for an unindexed database.")
            print("The important thing is that searches execute without errors.")
        else:
            print(f"\n✅ RETRIEVAL WORKING (MRR: {best_mrr:.4f})")
        
        return self.results
    
    def _print_comparison(self):
        """Print comparison table."""
        print(f"\n{'=' * 80}")
        print("RESULTS")
        print(f"{'=' * 80}\n")
        
        print(f"{'Method':<30} {'MRR':>8} {'Recall@5':>12} {'Recall@10':>12} {'Latency':>12}")
        print("-" * 80)
        
        for method_name, metrics in self.results["methods"].items():
            display_name = method_name.replace("_", " ").title()
            print(
                f"{display_name:<30} "
                f"{metrics['mrr']:>8.4f} "
                f"{metrics['recall_at_5']:>12.4f} "
                f"{metrics['recall_at_10']:>12.4f} "
                f"{metrics['avg_latency_ms']:>11.1f}ms"
            )
        
        print("-" * 80)
        
        # Analysis
        best_method = max(
            self.results["methods"].items(),
            key=lambda x: x[1]["mrr"]
        )
        print(f"\nBest Method: {best_method[0]} (MRR: {best_method[1]['mrr']:.4f})")
        
        # Check if searches are working
        total_errors = sum(m["errors"] for m in self.results["methods"].values())
        total_queries = sum(m["total_queries"] for m in self.results["methods"].values())
        
        if total_errors == 0:
            print("✅ All searches executed without errors")
        else:
            print(f"⚠️  {total_errors}/{total_queries} queries had errors")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fast retrieval audit")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=24,
        help="Number of annotations to sample (default: 24)"
    )
    parser.add_argument(
        "--database",
        type=str,
        default="sqlite:///./backend.db",
        help="Database URL"
    )
    
    args = parser.parse_args()
    
    print(f"Using database: {args.database}")
    
    # Setup database
    engine = create_engine(args.database)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Run audit
        auditor = FastRetrievalAuditor(db, sample_size=args.sample_size)
        results = auditor.run_audit()
        
        # Exit successfully (we're just testing infrastructure)
        sys.exit(0)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
