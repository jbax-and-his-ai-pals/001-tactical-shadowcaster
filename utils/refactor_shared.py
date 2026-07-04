from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
BUILTIN_NAMES = set(dir(builtins))


@dataclass
class MethodBlock:
    name: str
    lineno: int
    end_lineno: int
    text: str
    node: ast.FunctionDef | ast.AsyncFunctionDef


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
        rel_source = source.relative_to(ROOT)
        rel_dest = dest.relative_to(ROOT)
        print(f"Would move {len(chosen)} methods from {rel_source}:{source_class} to {rel_dest}:{dest_class}")
        for block in chosen:
            print(f"  - {block.name}: {block.lineno}-{block.end_lineno}")
        return
    ensure_destination_class(dest, dest_class)
    insert_methods_into_class(dest, dest_class, chosen)
    remove_methods_from_class(source, source_class, set(method_names))
    print(f"Moved {len(chosen)} methods to {dest.relative_to(ROOT)}")
