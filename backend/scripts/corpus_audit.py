"""Which langchain partner packages are actually in the corpus?"""
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def _async(url):
    return url.replace("postgresql://", "postgresql+asyncpg://", 1) if url.startswith("postgresql://") else url


async def main():
    engine = create_async_engine(_async(os.environ["DATABASE_URL"]))
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as s:
        # Partner packages expected in langchain monorepo
        r = await s.execute(text(
            r"SELECT "
            r"  regexp_replace(title, '^libs[/\\]partners[/\\]([^/\\]+).*', '\1') AS pkg, "
            r"  COUNT(*) AS files "
            r"FROM resources "
            r"WHERE title ~ '^libs[/\\]partners[/\\]' "
            r"GROUP BY pkg "
            r"ORDER BY files DESC"
        ))
        print(f"{'partner':30s} {'files':>6}")
        print("-" * 40)
        for row in r.fetchall():
            print(f"{row[0]:30s} {row[1]:>6}")

        print()
        r = await s.execute(text(
            r"SELECT COUNT(*) FROM resources WHERE title ~ '^libs[/\\]partners[/\\]pinecone'"
        ))
        print(f"pinecone files specifically: {r.scalar()}")

        r = await s.execute(text(
            r"SELECT COUNT(*) FROM resources WHERE description ILIKE '%pinecone%'"
        ))
        print(f"resources mentioning pinecone anywhere: {r.scalar()}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
