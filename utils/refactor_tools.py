from __future__ import annotations

import argparse
import ast
import builtins
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, cast


ROOT = Path(__file__).resolve().parents[1]
BUILTIN_NAMES = set(dir(builtins))


@dataclass
class MethodBlock:
    name: str
    lineno: int
    end_lineno: int
    text: str
    node: ast.FunctionDef | ast.AsyncFunctionDef


@dataclass
class ImportStatement:
    lineno: int
    end_lineno: int
    text: str
    names: set[str]


def repo_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def module_import_path(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[0] == "shadowcaster":
        return "." + ".".join(parts[1:])
    return "." + ".".join(parts)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def parse_module(path: Path) -> tuple[str, ast.Module]:
    text = read_text(path)
    return text, ast.parse(text, filename=str(path))


def class_node(module: ast.Module, class_name: str) -> ast.ClassDef | None:
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def require_end_lineno(node: ast.AST, context: str) -> int:
    end_lineno = getattr(node, "end_lineno", None)
    if end_lineno is None:
        raise ValueError(f"missing end_lineno for {context}")
    return int(end_lineno)


def method_blocks(path: Path, class_name: str) -> list[MethodBlock]:
    text, module = parse_module(path)
    target = class_node(module, class_name)
    if target is None:
        raise ValueError(f"class {class_name!r} not found in {path}")
    lines = text.splitlines(keepends=True)
    blocks: list[MethodBlock] = []
    for node in target.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end_lineno = require_end_lineno(node, f"method {node.name}")
        block = "".join(lines[node.lineno - 1 : end_lineno])
        blocks.append(MethodBlock(node.name, node.lineno, end_lineno, block, node))
    return blocks


def print_inventory(base: Path, glob: str, top: int | None) -> None:
    rows = []
    for path in sorted(base.glob(glob)):
        if path.is_dir():
            continue
        try:
            line_count = sum(1 for _ in path.open("r", encoding="utf-8"))
        except UnicodeDecodeError:
            continue
        rows.append((line_count, path))
    rows.sort(reverse=True, key=lambda item: item[0])
    if top is not None:
        rows = rows[:top]
    for line_count, path in rows:
        rel = path.relative_to(ROOT)
        print(f"{line_count:5d}  {rel}")


def print_methods(path: Path, class_name: str) -> None:
    for block in method_blocks(path, class_name):
        print(f"{block.name}: {block.lineno}-{block.end_lineno}")


def ensure_destination_class(path: Path, class_name: str) -> None:
    if path.exists():
        text, module = parse_module(path)
        if class_node(module, class_name) is not None:
            return
        suffix = "\n\n" if not text.endswith("\n\n") else ""
        write_text(path, text + suffix + f"class {class_name}(GameMixinBase):\n    pass\n")
        if "GameMixinBase" not in text:
            sync_prelude_import(path)
        return
    content = "\n".join(
        [
            "from __future__ import annotations",
            "",
            "from .game_typing import GameMixinBase",
            "",
            "",
            f"class {class_name}(GameMixinBase):",
            "    pass",
            "",
        ]
    )
    write_text(path, content)


def sync_prelude_import(path: Path) -> None:
    text = read_text(path)
    if "from .game_typing import GameMixinBase" in text:
        return
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith("from __future__ import annotations"):
        insert_at = 1
        if len(lines) > 1 and lines[1].strip() == "":
            insert_at = 2
    lines.insert(insert_at, "from .game_typing import GameMixinBase\n")
    if insert_at == 1:
        lines.insert(insert_at + 1, "\n")
    write_text(path, "".join(lines))


def insert_methods_into_class(path: Path, class_name: str, blocks: Iterable[MethodBlock]) -> None:
    text, module = parse_module(path)
    target = class_node(module, class_name)
    if target is None:
        raise ValueError(f"class {class_name!r} not found in {path}")
    lines = text.splitlines(keepends=True)
    placeholder_pass = len(target.body) == 1 and isinstance(target.body[0], ast.Pass)
    if placeholder_pass:
        insert_at = target.body[0].lineno - 1
        tail_start = require_end_lineno(target.body[0], f"placeholder pass in {class_name}")
        body = list(lines[:insert_at])
        tail = list(lines[tail_start:])
    else:
        insert_at = require_end_lineno(target, f"class {class_name}") - 1
        body = list(lines[:insert_at])
        tail = list(lines[insert_at:])
    if body and body[-1].strip() != "":
        body.append("\n")
    for block in blocks:
        body.append(block.text.rstrip() + "\n\n")
    while body and body[-1] == "\n" and tail and tail[0] == "\n":
        body.pop()
    write_text(path, "".join(body + tail))


def remove_methods_from_class(path: Path, class_name: str, method_names: set[str]) -> None:
    text, _module = parse_module(path)
    blocks = [block for block in method_blocks(path, class_name) if block.name in method_names]
    if not blocks:
        raise ValueError("no matching methods found to remove")
    lines = text.splitlines(keepends=True)
    remove_ranges = {(block.lineno, block.end_lineno) for block in blocks}
    kept: list[str] = []
    line_no = 1
    while line_no <= len(lines):
        matching = next((rng for rng in remove_ranges if rng[0] == line_no), None)
        if matching is not None:
            line_no = matching[1] + 1
            while line_no <= len(lines) and lines[line_no - 1].strip() == "":
                line_no += 1
            if kept and kept[-1].strip():
                kept.append("\n")
            continue
        kept.append(lines[line_no - 1])
        line_no += 1
    write_text(path, "".join(kept).rstrip() + "\n")


def extract_methods(
    source: Path,
    dest: Path,
    source_class: str,
    dest_class: str,
    method_names: list[str],
    dry_run: bool,
) -> None:
    blocks = method_blocks(source, source_class)
    chosen = [block for block in blocks if block.name in method_names]
    missing = [name for name in method_names if name not in {block.name for block in chosen}]
    if missing:
        raise ValueError(f"missing methods in {source}: {', '.join(missing)}")
    if dry_run:
        print(f"Would move {len(chosen)} methods from {source.relative_to(ROOT)}:{source_class} to {dest.relative_to(ROOT)}:{dest_class}")
        for block in chosen:
            print(f"  - {block.name}: {block.lineno}-{block.end_lineno}")
        return
    ensure_destination_class(dest, dest_class)
    insert_methods_into_class(dest, dest_class, chosen)
    remove_methods_from_class(source, source_class, set(method_names))
    print(f"Moved {len(chosen)} methods to {dest.relative_to(ROOT)}")


def import_statements(path: Path) -> list[ImportStatement]:
    text, module = parse_module(path)
    lines = text.splitlines(keepends=True)
    statements: list[ImportStatement] = []
    for node in module.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        names = set()
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        else:
            for alias in node.names:
                names.add(alias.asname or alias.name)
        statements.append(
            ImportStatement(
                lineno=node.lineno,
                end_lineno=require_end_lineno(node, "import statement"),
                text="".join(lines[node.lineno - 1 : require_end_lineno(node, 'import statement')]).rstrip() + "\n",
                names=names,
            )
        )
    return statements


def module_defined_names(module: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in module.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if isinstance(node, ast.Import):
                    names.add(alias.asname or alias.name.split(".")[0])
                else:
                    names.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                names.update(extract_target_names(target))
    return names


def extract_target_names(target: ast.AST) -> set[str]:
    names: set[str] = set()
    if isinstance(target, ast.Name):
        names.add(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            names.update(extract_target_names(elt))
    return names


class ScopeCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.locals: set[str] = set()
        self.loads: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.loads.add(node.id)
        elif isinstance(node.ctx, (ast.Store, ast.Del)):
            self.locals.add(node.id)

    def visit_arg(self, node: ast.arg) -> None:
        self.locals.add(node.arg)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.decorator_list:
            for decorator in node.decorator_list:
                self.visit(decorator)
        if node.returns:
            self.visit(node.returns)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node.decorator_list:
            for decorator in node.decorator_list:
                self.visit(decorator)
        if node.returns:
            self.visit(node.returns)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.generic_visit(node.body)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.visit(node.iter)
        for if_clause in node.ifs:
            self.visit(if_clause)
        self.locals.update(extract_target_names(node.target))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.locals.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self.locals.add(alias.asname or alias.name)


def method_global_requirements(blocks: Iterable[MethodBlock]) -> set[str]:
    requirements: set[str] = set()
    for block in blocks:
        collector = ScopeCollector()
        collector.visit(block.node.args)
        for decorator in block.node.decorator_list:
            collector.visit(decorator)
        for statement in block.node.body:
            collector.visit(statement)
        unresolved = collector.loads - collector.locals - BUILTIN_NAMES
        requirements.update(name for name in unresolved if name not in {"self", "cls"})
    return requirements


def selected_method_blocks(path: Path, class_name: str, method_names: list[str] | None) -> list[MethodBlock]:
    blocks = method_blocks(path, class_name)
    if not method_names:
        return blocks
    selected = [block for block in blocks if block.name in set(method_names)]
    missing = [name for name in method_names if name not in {block.name for block in selected}]
    if missing:
        raise ValueError(f"missing methods in {path}: {', '.join(missing)}")
    return selected


def audit_imports(path: Path, class_name: str, method_names: list[str] | None) -> set[str]:
    _text, module = parse_module(path)
    available = module_defined_names(module)
    requirements = method_global_requirements(selected_method_blocks(path, class_name, method_names))
    missing = sorted(name for name in requirements if name not in available)
    for name in missing:
        print(name)
    return set(missing)


def insert_import_text(path: Path, statements: list[str]) -> None:
    if not statements:
        return
    text = read_text(path)
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith("from __future__ import annotations"):
        insert_at = 1
        if len(lines) > 1 and lines[1].strip() == "":
            insert_at = 2
    while insert_at < len(lines) and lines[insert_at].startswith(("import ", "from ")):
        insert_at += 1
    insertion = []
    for statement in statements:
        insertion.append(statement if statement.endswith("\n") else statement + "\n")
    if insertion and (insert_at >= len(lines) or lines[insert_at].strip() != ""):
        insertion.append("\n")
    write_text(path, "".join(lines[:insert_at] + insertion + lines[insert_at:]))


def sync_imports(
    source: Path,
    dest: Path,
    dest_class: str,
    method_names: list[str] | None,
    dry_run: bool,
) -> None:
    source_imports = import_statements(source)
    dest_text, dest_module = parse_module(dest)
    dest_import_texts = {statement.text.strip() for statement in import_statements(dest)}
    available = module_defined_names(dest_module)
    requirements = method_global_requirements(selected_method_blocks(dest, dest_class, method_names))
    missing = sorted(name for name in requirements if name not in available)
    chosen: list[str] = []
    resolved: set[str] = set()
    for name in missing:
        statement = next((item for item in source_imports if name in item.names and item.text.strip() not in dest_import_texts), None)
        if statement is None:
            continue
        if statement.text not in chosen:
            chosen.append(statement.text)
        resolved.update(statement.names)
    unresolved = [name for name in missing if name not in resolved]
    if dry_run:
        print(f"Would sync {len(chosen)} import statements into {dest.relative_to(ROOT)}")
        for statement in chosen:
            print("----")
            print(statement.rstrip())
        if unresolved:
            print("Unresolved names:")
            for name in unresolved:
                print(f"  - {name}")
        return
    insert_import_text(dest, chosen)
    print(f"Synced {len(chosen)} import statements into {dest.relative_to(ROOT)}")
    if unresolved:
        print("Still unresolved:")
        for name in unresolved:
            print(f"  - {name}")


def wire_mixin(game_path: Path, mixin_path: Path, mixin_class: str, owner_class: str, after: str | None, dry_run: bool) -> None:
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
        if after and after in base_names:
            index = base_names.index(after) + 1
        else:
            index = len(base_names)
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


if __name__ == "__main__":
    main()
