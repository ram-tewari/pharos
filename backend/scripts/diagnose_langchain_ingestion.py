"""
Diagnostic script to analyze LangChain ingestion state.

This script runs SELECT queries only (no writes) to determine:
1. How many LangChain resources exist
2. Their ingestion_status breakdown
3. Whether resources.embedding is populated
4. Whether chunks have semantic_summary/github_uri or content
5. Sample data to understand the actual state

Usage:
    cd backend
    python scripts/diagnose_langchain_ingestion.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    """Run diagnostics on LangChain resources."""
    
    # Connect to database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return
    
    # Convert asyncpg URL to psycopg2 for sync access
    if "asyncpg" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print("Connecting to database...")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Count total LangChain resources
        print_section("1. LangChain Resources Count")
        
        result = db.execute(text("""
            SELECT COUNT(*) as total
            FROM resources
            WHERE source LIKE '%langchain%'
        """))
        total = result.scalar()
        print(f"Total LangChain resources: {total}")
        
        # 2. Ingestion status breakdown
        print_section("2. Ingestion Status Breakdown")
        
        result = db.execute(text("""
            SELECT 
                ingestion_status,
                COUNT(*) as count
            FROM resources
            WHERE source LIKE '%langchain%'
            GROUP BY ingestion_status
            ORDER BY count DESC
        """))
        
        for row in result:
            print(f"  {row.ingestion_status or 'NULL'}: {row.count}")
        
        # 3. Embedding population
        print_section("3. Resources with Embeddings")
        
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(embedding) as with_embedding,
                COUNT(*) - COUNT(embedding) as without_embedding
            FROM resources
            WHERE source LIKE '%langchain%'
        """))
        
        row = result.fetchone()
        print(f"  Total resources: {row.total}")
        print(f"  With embedding: {row.with_embedding}")
        print(f"  Without embedding: {row.without_embedding}")
        print(f"  Percentage with embedding: {(row.with_embedding / row.total * 100):.1f}%")
        
        # 4. Chunks analysis
        print_section("4. Document Chunks Analysis")
        
        result = db.execute(text("""
            SELECT COUNT(DISTINCT dc.resource_id) as resources_with_chunks
            FROM document_chunks dc
            JOIN resources r ON dc.resource_id = r.id
            WHERE r.source LIKE '%langchain%'
        """))
        
        resources_with_chunks = result.scalar()
        print(f"  Resources with chunks: {resources_with_chunks}")
        
        result = db.execute(text("""
            SELECT COUNT(*) as total_chunks
            FROM document_chunks dc
            JOIN resources r ON dc.resource_id = r.id
            WHERE r.source LIKE '%langchain%'
        """))
        
        total_chunks = result.scalar()
        print(f"  Total chunks: {total_chunks}")
        
        # 5. Chunk content analysis
        print_section("5. Chunk Content Analysis")
        
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(dc.content) as with_content,
                COUNT(dc.semantic_summary) as with_semantic_summary,
                COUNT(dc.github_uri) as with_github_uri,
                COUNT(dc.embedding) as with_embedding
            FROM document_chunks dc
            JOIN resources r ON dc.resource_id = r.id
            WHERE r.source LIKE '%langchain%'
        """))
        
        row = result.fetchone()
        print(f"  Total chunks: {row.total}")
        print(f"  With content: {row.with_content} ({(row.with_content / row.total * 100):.1f}%)")
        print(f"  With semantic_summary: {row.with_semantic_summary} ({(row.with_semantic_summary / row.total * 100):.1f}%)")
        print(f"  With github_uri: {row.with_github_uri} ({(row.with_github_uri / row.total * 100):.1f}%)")
        print(f"  With embedding: {row.with_embedding} ({(row.with_embedding / row.total * 100):.1f}%)")
        
        # 6. Sample resource
        print_section("6. Sample Resource Data")
        
        result = db.execute(text("""
            SELECT 
                id,
                title,
                type,
                format,
                source,
                ingestion_status,
                CASE WHEN embedding IS NOT NULL THEN 'YES' ELSE 'NO' END as has_embedding,
                created_at
            FROM resources
            WHERE source LIKE '%langchain%'
            LIMIT 3
        """))
        
        for idx, row in enumerate(result, 1):
            print(f"\n  Resource {idx}:")
            print(f"    ID: {row.id}")
            print(f"    Title: {row.title}")
            print(f"    Type: {row.type}")
            print(f"    Format: {row.format}")
            print(f"    Source: {row.source[:80]}...")
            print(f"    Ingestion Status: {row.ingestion_status}")
            print(f"    Has Embedding: {row.has_embedding}")
            print(f"    Created: {row.created_at}")
        
        # 7. Sample chunk
        print_section("7. Sample Chunk Data")
        
        result = db.execute(text("""
            SELECT 
                dc.id,
                dc.resource_id,
                dc.chunk_index,
                CASE WHEN dc.content IS NOT NULL THEN LENGTH(dc.content) ELSE 0 END as content_length,
                CASE WHEN dc.semantic_summary IS NOT NULL THEN LENGTH(dc.semantic_summary) ELSE 0 END as summary_length,
                dc.github_uri,
                dc.branch_reference,
                dc.start_line,
                dc.end_line,
                dc.ast_node_type,
                dc.symbol_name,
                CASE WHEN dc.embedding IS NOT NULL THEN 'YES' ELSE 'NO' END as has_embedding
            FROM document_chunks dc
            JOIN resources r ON dc.resource_id = r.id
            WHERE r.source LIKE '%langchain%'
            LIMIT 3
        """))
        
        for idx, row in enumerate(result, 1):
            print(f"\n  Chunk {idx}:")
            print(f"    ID: {row.id}")
            print(f"    Resource ID: {row.resource_id}")
            print(f"    Chunk Index: {row.chunk_index}")
            print(f"    Content Length: {row.content_length} chars")
            print(f"    Summary Length: {row.summary_length} chars")
            print(f"    GitHub URI: {row.github_uri[:80] if row.github_uri else 'NULL'}...")
            print(f"    Branch: {row.branch_reference}")
            print(f"    Lines: {row.start_line}-{row.end_line}")
            print(f"    AST Node Type: {row.ast_node_type}")
            print(f"    Symbol Name: {row.symbol_name}")
            print(f"    Has Embedding: {row.has_embedding}")
        
        # 8. Sample semantic_summary content
        print_section("8. Sample Semantic Summary Content")
        
        result = db.execute(text("""
            SELECT semantic_summary
            FROM document_chunks dc
            JOIN resources r ON dc.resource_id = r.id
            WHERE r.source LIKE '%langchain%'
              AND dc.semantic_summary IS NOT NULL
            LIMIT 2
        """))
        
        for idx, row in enumerate(result, 1):
            print(f"\n  Summary {idx}:")
            print(f"    {row.semantic_summary[:200]}...")
        
        # 9. Diagnosis summary
        print_section("9. DIAGNOSIS SUMMARY")
        
        # Re-fetch key metrics for summary
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(embedding) as with_embedding
            FROM resources
            WHERE source LIKE '%langchain%'
        """))
        row = result.fetchone()
        resources_total = row.total
        resources_with_embedding = row.with_embedding
        
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(semantic_summary) as with_summary,
                COUNT(embedding) as with_embedding
            FROM document_chunks dc
            JOIN resources r ON dc.resource_id = r.id
            WHERE r.source LIKE '%langchain%'
        """))
        row = result.fetchone()
        chunks_total = row.total
        chunks_with_summary = row.with_summary
        chunks_with_embedding = row.with_embedding
        
        print(f"\n  Resources: {resources_total} total, {resources_with_embedding} with embeddings")
        print(f"  Chunks: {chunks_total} total, {chunks_with_summary} with summaries, {chunks_with_embedding} with embeddings")
        
        print("\n  LIKELY ISSUE:")
        if resources_with_embedding == 0 and chunks_with_embedding == 0:
            print("    ❌ NO EMBEDDINGS GENERATED")
            print("    → Repo worker created resources/chunks but didn't generate embeddings")
            print("    → Need to backfill embeddings using edge worker GPU")
        elif resources_with_embedding > 0 and chunks_with_embedding == 0:
            print("    ❌ EMBEDDINGS IN WRONG PLACE")
            print("    → Resources have embeddings but chunks don't")
            print("    → Search reads from chunks.embedding, not resources.embedding")
            print("    → Need to copy or regenerate embeddings for chunks")
        elif chunks_with_summary > 0 and chunks_with_embedding == 0:
            print("    ❌ SUMMARIES EXIST BUT NOT EMBEDDED")
            print("    → Chunks have semantic_summary but no embeddings")
            print("    → Need to generate embeddings from semantic_summary")
        else:
            print("    ✅ DATA LOOKS GOOD")
            print("    → Check search query logic or vector similarity settings")
        
        print("\n  RECOMMENDED FIX:")
        if chunks_with_summary > 0 and chunks_with_embedding == 0:
            print("    1. Create backfill script to generate embeddings from semantic_summary")
            print("    2. Use edge worker GPU for fast embedding generation")
            print("    3. Update document_chunks.embedding column")
            print("    4. Test search again")
        
    finally:
        db.close()
    
    print("\n" + "=" * 80)
    print("  Diagnosis Complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
