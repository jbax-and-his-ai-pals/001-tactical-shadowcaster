"""
Low-level map primitives shared by regions.py and all regions_*.py generators.
Kept in a separate module so the generators can import these without creating
a circular dependency with regions.py.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Iterable

from .models import RectRoom


class RegionMap:
    def __init__(self, width: int, height: int, fill: int = 1):
        self.width: int = width
        self.height: int = height
        self.tiles: list[list[int]] = [[fill for _ in range(height)] for _ in range(width)]
        self.rooms: list[RectRoom] = []
        self.metadata: dict = {}
        self.transparent_tiles: set[tuple[int, int]] = set()

    def carve_rect(self, x: int, y: int, w: int, h: int) -> RectRoom:
        room = RectRoom(x, y, w, h)
        self.rooms.append(room)
        for tx in range(x, x + w):
            for ty in range(y, y + h):
                self.tiles[tx][ty] = 0
        return room

    def is_blocked(self, x: int, y: int) -> bool:
        return not (0 <= x < self.width and 0 <= y < self.height) or self.tiles[x][y] == 1


def path_tiles(start: tuple[int, int], end: tuple[int, int], width: int = 1) -> set[tuple[int, int]]:
    tiles: set[tuple[int, int]] = set()
    x1, y1 = start
    x2, y2 = end
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            tiles.add((x, y1 + offset))
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            tiles.add((x2 + offset, y))
    return tiles


def walkable_path_tiles(
    region_map: RegionMap,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    if start == end:
        return [start]
    frontier: deque[tuple[int, int]] = deque([start])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while frontier:
        current = frontier.popleft()
        if current == end:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in came_from:
                continue
            if not (0 < neighbor[0] < region_map.width - 1 and 0 < neighbor[1] < region_map.height - 1):
                continue
            if region_map.is_blocked(*neighbor) and neighbor != end:
                continue
            came_from[neighbor] = current
            frontier.append(neighbor)
    if end not in came_from:
        return []
    path: list[tuple[int, int]] = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def widen_path_tiles(
    tiles: Iterable[tuple[int, int]], width: int = 1
) -> set[tuple[int, int]]:
    widened: set[tuple[int, int]] = set()
    for x, y in tiles:
        for offset_x in range(-(width // 2), width - (width // 2)):
            for offset_y in range(-(width // 2), width - (width // 2)):
                widened.add((x + offset_x, y + offset_y))
    return widened


def feature_footprint_tiles(
    region_map: RegionMap,
    anchor: tuple[int, int],
    kind: str,
    preferred_tiles: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    if kind != "notice_board":
        return {anchor}
    preferred = set(preferred_tiles or set())
    candidates = [
        [(0, 0), (1, 0), (0, -1), (1, -1)],
        [(-1, 0), (0, 0), (-1, -1), (0, -1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(-1, 0), (0, 0), (-1, 1), (0, 1)],
    ]
    best_tiles: set[tuple[int, int]] = {anchor}
    best_score = (-1, -1)
    for offsets in candidates:
        tiles_list: list[tuple[int, int]] = []
        valid = True
        for dx, dy in offsets:
            tile = (anchor[0] + dx, anchor[1] + dy)
            if not (1 <= tile[0] < region_map.width - 1 and 1 <= tile[1] < region_map.height - 1):
                valid = False
                break
            if region_map.tiles[tile[0]][tile[1]] != 0:
                valid = False
                break
            tiles_list.append(tile)
        if not valid:
            continue
        preferred_count = sum(1 for tile in tiles_list if tile in preferred)
        score = (preferred_count, len(tiles_list))
        if score > best_score:
            best_score = score
            best_tiles = set(tiles_list)
    return best_tiles


def carve_path(
    region_map: Any,
    start: tuple[int, int],
    end: tuple[int, int],
    width: int = 1,
) -> None:
    x1, y1 = start
    x2, y2 = end
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            py = max(1, min(region_map.height - 2, y1 + offset))
            region_map.tiles[x][py] = 0
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            px = max(1, min(region_map.width - 2, x2 + offset))
            region_map.tiles[px][y] = 0
