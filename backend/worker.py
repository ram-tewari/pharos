"""
Pharos worker dispatcher.

    python worker.py edge   # edge ingestion worker (GPU, polls pharos:tasks)
    python worker.py repo   # GitHub repo ingestion worker (polls ingest_queue)
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="worker.py",
        description="Pharos worker dispatcher",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser(
        "edge",
        help="Run the edge ingestion worker (GPU, polls pharos:tasks queue)",
    )
    subparsers.add_parser(
        "repo",
        help="Run the GitHub repository ingestion worker (polls ingest_queue)",
    )

    args = parser.parse_args()

    if args.command == "edge":
        import asyncio
        from app.workers.edge import main as edge_main
        try:
            asyncio.run(edge_main())
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Fatal error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "repo":
        from app.workers.repo import main as repo_main
        repo_main()


if __name__ == "__main__":
    main()
