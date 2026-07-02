from __future__ import annotations

import argparse
from pathlib import Path


def count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        if any(part in {"__pycache__", ".git", ".venv", "venv"} for part in path.parts):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the largest Python files in the project by line count.")
    parser.add_argument("root", nargs="?", default=".", help="Root folder to scan. Defaults to the current directory.")
    parser.add_argument("--top", type=int, default=20, help="How many files to show. Defaults to 20.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows: list[tuple[int, Path]] = []
    for path in iter_python_files(root):
        rows.append((count_lines(path), path))

    rows.sort(key=lambda item: (-item[0], str(item[1])))
    root_display = str(root)
    for line_count, path in rows[: max(1, args.top)]:
        try:
            display = path.relative_to(root)
        except ValueError:
            display = path
        print(f"{line_count:5d}  {display}")

    if not rows:
        print(f"No Python files found under {root_display}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
