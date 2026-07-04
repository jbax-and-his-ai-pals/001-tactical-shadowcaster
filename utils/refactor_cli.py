from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import cast

from refactor_imports import audit_imports, import_statements, sync_imports
from refactor_shared import (
    ROOT,
    class_node,
    extract_methods,
    module_import_path,
    parse_module,
    print_inventory,
    print_methods,
    repo_path,
    write_text,
)


def wire_mixin(
    game_path: Path,
    mixin_path: Path,
    mixin_class: str,
    owner_class: str,
    after: str | None,
    dry_run: bool,
) -> None:
    text, module = parse_module(game_path)
    game_class = class_node(module, owner_class)
    if game_class is None:
        raise ValueError(f"class {owner_class!r} not found in {game_path}")
    base_names = [ast.unparse(base) for base in game_class.bases]
    import_line = f"from {module_import_path(mixin_path)} import {mixin_class}"
    new_text = text
    changed = False
    if import_line not in text:
        lines = text.splitlines(keepends=True)
        insert_at = 0
        while insert_at < len(lines) and lines[insert_at].startswith(("from ", "import ")):
            insert_at += 1
        lines.insert(insert_at, import_line + "\n")
        new_text = "".join(lines)
        changed = True
    if mixin_class not in base_names:
        updated_module = ast.parse(new_text, filename=str(game_path))
        updated_class = class_node(updated_module, owner_class)
        if updated_class is None:
            raise ValueError(f"class {owner_class!r} not found in updated {game_path}")
        index = base_names.index(after) + 1 if after and after in base_names else len(base_names)
        base_names.insert(index, mixin_class)
        lines = new_text.splitlines(keepends=True)
        header_index = cast(int, updated_class.lineno) - 1
        lines[header_index] = f"class {owner_class}({', '.join(base_names)}):\n"
        new_text = "".join(lines)
        changed = True
    if dry_run:
        print(f"Would wire {mixin_class} into {game_path.relative_to(ROOT)}::{owner_class}")
        if import_line not in text:
            print(f"  - add import: {import_line}")
        if mixin_class not in [ast.unparse(base) for base in game_class.bases]:
            print(f"  - add base after {after or 'end'}")
        return
    if changed:
        write_text(game_path, new_text)
    print(f"Wired {mixin_class} into {game_path.relative_to(ROOT)}::{owner_class}")


def smoke_game() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    root_str = str(ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    import pygame

    pygame.init()
    pygame.display.set_mode((100, 100))
    from shadowcaster.game import Game

    game = Game()
    game.start_new_game()
    print(f"Smoke ok: {game.region_name} [{game.region_type}] at {game.world_position}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Utility commands for file management and low-risk refactors.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory", help="Show file line counts.")
    inventory.add_argument("path", nargs="?", default="shadowcaster", help="Directory to scan.")
    inventory.add_argument("--glob", default="**/*.py", help="Glob pattern relative to path.")
    inventory.add_argument("--top", type=int, default=None, help="Show only the largest N matches.")

    methods = subparsers.add_parser("methods", help="List methods for a class with line ranges.")
    methods.add_argument("path", help="Python file to inspect.")
    methods.add_argument("class_name", help="Class to inspect.")

    extract = subparsers.add_parser("extract-methods", help="Move methods from one class file into another.")
    extract.add_argument("source", help="Source Python file.")
    extract.add_argument("dest", help="Destination Python file.")
    extract.add_argument("--source-class", required=True, help="Source class name.")
    extract.add_argument("--dest-class", required=True, help="Destination class name.")
    extract.add_argument("--methods", nargs="+", required=True, help="Method names to move.")
    extract.add_argument("--dry-run", action="store_true", help="Preview the move without writing changes.")

    audit = subparsers.add_parser("audit-imports", help="Report unresolved global names used by selected methods.")
    audit.add_argument("path", help="Python file to audit.")
    audit.add_argument("class_name", help="Class to inspect.")
    audit.add_argument("--methods", nargs="*", default=None, help="Optional method subset.")

    sync = subparsers.add_parser("sync-imports", help="Copy import statements from the source file to satisfy missing names in the destination methods.")
    sync.add_argument("source", help="Source Python file that still has the needed imports.")
    sync.add_argument("dest", help="Destination Python file containing the moved methods.")
    sync.add_argument("--dest-class", required=True, help="Destination class name.")
    sync.add_argument("--methods", nargs="*", default=None, help="Optional method subset.")
    sync.add_argument("--dry-run", action="store_true", help="Preview copied imports without writing changes.")

    wire = subparsers.add_parser("wire-mixin", help="Add a mixin import and compose it into the Game class.")
    wire.add_argument("game_path", help="Usually shadowcaster/game.py.")
    wire.add_argument("mixin_path", help="Mixin module to import, e.g. shadowcaster/mixins/game_inspect.py.")
    wire.add_argument("mixin_class", help="Mixin class name.")
    wire.add_argument("--owner-class", default="Game", help="Composed game class to update.")
    wire.add_argument("--after", default=None, help="Existing base class after which the new mixin should be inserted.")
    wire.add_argument("--dry-run", action="store_true", help="Preview the composition change without writing changes.")

    smoke = subparsers.add_parser("smoke-game", help="Headless pygame smoke test for Game().start_new_game().")
    smoke.set_defaults(_smoke=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "inventory":
        print_inventory(repo_path(args.path), args.glob, args.top)
    elif args.command == "methods":
        print_methods(repo_path(args.path), args.class_name)
    elif args.command == "extract-methods":
        extract_methods(
            repo_path(args.source),
            repo_path(args.dest),
            args.source_class,
            args.dest_class,
            args.methods,
            args.dry_run,
        )
    elif args.command == "audit-imports":
        audit_imports(repo_path(args.path), args.class_name, args.methods)
    elif args.command == "sync-imports":
        sync_imports(
            repo_path(args.source),
            repo_path(args.dest),
            args.dest_class,
            args.methods,
            args.dry_run,
        )
    elif args.command == "wire-mixin":
        wire_mixin(
            repo_path(args.game_path),
            repo_path(args.mixin_path),
            args.mixin_class,
            args.owner_class,
            args.after,
            args.dry_run,
        )
    elif args.command == "smoke-game":
        smoke_game()
