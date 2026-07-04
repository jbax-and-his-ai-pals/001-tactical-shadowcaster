from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from refactor_shared import (
    BUILTIN_NAMES,
    MethodBlock,
    ROOT,
    method_blocks,
    parse_module,
    read_text,
    require_end_lineno,
    write_text,
)


@dataclass
class ImportStatement:
    lineno: int
    end_lineno: int
    text: str
    names: set[str]


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
        end_lineno = require_end_lineno(node, "import statement")
        statements.append(
            ImportStatement(
                lineno=node.lineno,
                end_lineno=end_lineno,
                text="".join(lines[node.lineno - 1 : end_lineno]).rstrip() + "\n",
                names=names,
            )
        )
    return statements


def extract_target_names(target: ast.AST) -> set[str]:
    names: set[str] = set()
    if isinstance(target, ast.Name):
        names.add(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            names.update(extract_target_names(elt))
    return names


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

    def _visit_nested_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        if node.returns:
            self.visit(node.returns)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_nested_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_nested_function(node)

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
    insertion = [statement if statement.endswith("\n") else statement + "\n" for statement in statements]
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
        statement = next(
            (
                item
                for item in source_imports
                if name in item.names and item.text.strip() not in dest_import_texts
            ),
            None,
        )
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
