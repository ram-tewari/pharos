"""Commands module for Pharos CLI."""

from pharos_cli.commands.auth import auth_app
from pharos_cli.commands.collection import collection_app
from pharos_cli.commands.search import search_app
from pharos_cli.commands.recommend import recommend_app
from pharos_cli.commands.graph import graph_app
from pharos_cli.commands.quality import quality_app
from pharos_cli.commands.system import system_app

__all__ = ["auth_app", "collection_app", "search_app", "recommend_app", "graph_app", "quality_app", "system_app"]