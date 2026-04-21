"""
Backfill resources.embedding for rows that have NULL.

Reads each missing resource, builds a summary text (title + description +
first chunk's semantic_summary if available), calls the local edge /embed
server, and stores the result.

Usage:
    python backend/scripts/backfill_resource_embeddings.py
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


EMBED_URL = os.getenv("LOCAL_EMBED_URL", "http://127.0.0.1:8001/embed")
BATCH_COMMIT = 25


def build_summary(row) -> str:
    parts = [row.title or ""]
    if row.description:
        desc = row.description
        if desc.startswith("{"):
            try:
                meta = json.loads(desc)
                fns = ", ".join(meta.get("functions", [])[:10])
                cls = ", ".join(meta.get("classes", [])[:10])
                imps = ", ".join(meta.get("imports", [])[:10])
                desc = f"Functions: {fns} | Classes: {cls} | Imports: {imps}"
            except Exception:
                pass
        parts.append(desc)
    if row.chunk_summary:
        parts.append(row.chunk_summary)
    return " | ".join(p for p in parts if p)[:8000]


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return
    if "asyncpg" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"DB: {database_url.split('@')[-1]}")
    print(f"Embed URL: {EMBED_URL}")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    rows = db.execute(text("""
        SELECT r.id, r.title, r.description,
               (SELECT dc.semantic_summary FROM document_chunks dc
                WHERE dc.resource_id = r.id
                ORDER BY dc.chunk_index ASC LIMIT 1) AS chunk_summary
        FROM resources r
        WHERE r.embedding IS NULL
    """)).all()

    total = len(rows)
    print(f"Resources missing embedding: {total}")
    if total == 0:
        return

    client = httpx.Client(timeout=30.0)
    done = 0
    failed = 0

    for i, row in enumerate(rows, 1):
        try:
            summary = build_summary(row)
            if not summary.strip():
                failed += 1
                continue
            resp = client.post(EMBED_URL, json={"text": summary})
            resp.raise_for_status()
            vec = resp.json().get("embedding")
            if not vec:
                failed += 1
                continue
            db.execute(
                text("UPDATE resources SET embedding = :e WHERE id = :id"),
                {"e": json.dumps(vec), "id": row.id},
            )
            done += 1
            if i % BATCH_COMMIT == 0:
                db.commit()
                print(f"  {i}/{total} (done={done}, failed={failed})")
        except Exception as exc:
            failed += 1
            print(f"  WARN resource {row.id}: {exc}")

    db.commit()
    db.close()
    client.close()
    print(f"\nDone. embedded={done} failed={failed} total={total}")


if __name__ == "__main__":
    main()
