"""
Pharos worker dispatcher.

    python worker.py combined   # single process: /embed server + edge + repo tasks
    python worker.py edge       # edge ingestion worker only
    python worker.py repo       # GitHub repo ingestion worker only
"""

import argparse
import sys
from pathlib import Path

# Load .env before any app imports so env vars are available to check_environment()
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Workaround: Python 3.13 platform.*() uses WMI on Windows which can hang indefinitely.
# Affected: sqlalchemy/util/compat.py (platform.machine) and
#           prometheus_client/platform_collector.py (platform.system).
# Fix: cache a synthetic uname_result so all platform.*() calls bypass WMI.
try:
    import platform as _platform
    import os as _os

    _cached_uname = _platform.uname_result(
        system="Windows",
        node=_os.environ.get("COMPUTERNAME", "localhost"),
        release="11",
        version="10.0.0",
        machine=_os.environ.get("PROCESSOR_ARCHITECTURE", "AMD64"),
    )
    _platform.uname = lambda: _cached_uname
except Exception:
    pass


def main():
    parser = argparse.ArgumentParser(
        prog="worker.py",
        description="Pharos worker dispatcher",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser(
        "combined",
        help="Run the combined worker: /embed server + edge + repo dispatch",
    )
    subparsers.add_parser(
        "edge",
        help="Run the edge ingestion worker (GPU, polls pharos:tasks queue)",
    )
    subparsers.add_parser(
        "repo",
        help="Run the GitHub repository ingestion worker (polls pharos:tasks)",
    )

    args = parser.parse_args()

    if args.command == "combined":
        import asyncio
        from app.workers.combined import main as combined_main
        try:
            asyncio.run(combined_main())
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Fatal error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "edge":
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
