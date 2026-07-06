from __future__ import annotations

import pygame

from .constants import SCREEN_HEIGHT, SCREEN_WIDTH

_BG        = (12, 10, 8)
_WALL      = (35, 30, 25)
_FLOOR     = (65, 58, 48)
_UNSEEN    = (18, 15, 12)
_PLAYER    = (220, 210, 140)
_ENEMY     = (200, 70, 60)
_STAIRS    = (100, 190, 240)
_EXIT      = (140, 200, 120)
_ITEM      = (180, 160, 80)
_TRAP      = (210, 100, 40)
_FEATURE   = (80, 120, 90)
_BORDER    = (80, 72, 60)
_WHITE     = (230, 220, 210)
_DIM       = (100, 92, 80)
_GOLD      = (220, 190, 60)

_TILE_SIZE = 4   # pixels per map tile
_MAX_MAP_W = SCREEN_WIDTH  - 80
_MAX_MAP_H = SCREEN_HEIGHT - 120
_HEADER_H  = 36
_FOOTER_H  = 28


def render_minimap_overlay(game):
    screen = game.screen

    dungeon = game.dungeon
    mw, mh = dungeon.width, dungeon.height

    # Scale so the map fits on screen
    ts = _TILE_SIZE
    while ts > 1 and (mw * ts > _MAX_MAP_W or mh * ts > _MAX_MAP_H):
        ts -= 1

    map_px_w = mw * ts
    map_px_h = mh * ts
    panel_w = map_px_w + 20
    panel_h = map_px_h + _HEADER_H + _FOOTER_H + 10
    panel_w = min(panel_w, SCREEN_WIDTH - 40)
    panel_h = min(panel_h, SCREEN_HEIGHT - 20)

    px = (SCREEN_WIDTH  - panel_w) // 2
    py = (SCREEN_HEIGHT - panel_h) // 2

    # Dim background
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((6, 6, 6, 200))
    screen.blit(dim, (0, 0))

    # Panel
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((*_BG, 248))
    pygame.draw.rect(panel, _BORDER, panel.get_rect(), 2, border_radius=8)

    # Header
    font  = game.font
    small = game.small_font
    title = font.render(f"MAP — {game.region_name}", True, _WHITE)
    panel.blit(title, (12, 8))
    floor_txt = small.render(f"Floor {getattr(game, 'floor', 1)}", True, _DIM)
    panel.blit(floor_txt, (panel_w - floor_txt.get_width() - 12, 12))

    pygame.draw.line(panel, _BORDER, (8, _HEADER_H), (panel_w - 8, _HEADER_H))

    # Map surface
    map_surf = pygame.Surface((map_px_w, map_px_h))
    map_surf.fill(_UNSEEN)

    seen    = game.seen_tiles
    player  = game.player
    fieldcraft_rank = game.get_skill_rank("fieldcraft") if hasattr(game, "get_skill_rank") else 0

    # Draw tiles
    for x in range(mw):
        for y in range(mh):
            pos = (x, y)
            rx, ry = x * ts, y * ts
            if pos not in seen:
                color = _UNSEEN
            elif dungeon.tiles[x][y] == 1:
                color = _WALL
            else:
                color = _FLOOR
            if ts == 1:
                map_surf.set_at((rx, ry), color)
            else:
                pygame.draw.rect(map_surf, color, (rx, ry, ts - 1, ts - 1))

    # Special tiles (only in seen area)
    def _draw_dot(surf, pos, color, size=None):
        x, y = pos
        if (x, y) not in seen and pos != player:
            return
        rx, ry = x * ts + ts // 2, y * ts + ts // 2
        r = size or max(1, ts // 2)
        pygame.draw.circle(surf, color, (rx, ry), r)

    # Stairs / exits
    if game.stairs and game.stairs in seen:
        _draw_dot(map_surf, game.stairs, _STAIRS)
    if game.up_stairs and game.up_stairs in seen:
        _draw_dot(map_surf, game.up_stairs, _STAIRS)
    if game.delve_goal and game.delve_goal in seen:
        _draw_dot(map_surf, game.delve_goal, _GOLD)
    for tile in game.edge_exits.values():
        if tile and tile in seen:
            _draw_dot(map_surf, tile, _EXIT)

    # Floor items
    for gi in getattr(game, "floor_items", []):
        if gi.position in seen:
            _draw_dot(map_surf, gi.position, _ITEM, max(1, ts // 3))

    # Traps — always shown if fieldcraft >= 2 AND in seen area
    terrain = getattr(game, "terrain_features", {})
    for pos, kind in terrain.items():
        if kind.startswith("trap_") and pos in seen:
            if fieldcraft_rank >= 2 or pos in getattr(game, "_triggered_traps", set()):
                _draw_dot(map_surf, pos, _TRAP, max(1, ts // 2))

    # Enemies (visible only)
    visible = getattr(game, "visible_tiles", set())
    for enemy in getattr(game, "enemies", []):
        if enemy.position in visible:
            _draw_dot(map_surf, enemy.position, _ENEMY)

    # Player — always shown
    ex, ey = player[0] * ts + ts // 2, player[1] * ts + ts // 2
    pygame.draw.circle(map_surf, _PLAYER, (ex, ey), max(2, ts // 2 + 1))

    # Blit map centered in panel
    map_x = (panel_w - map_px_w) // 2
    map_y = _HEADER_H + 6
    panel.blit(map_surf, (map_x, map_y))

    # Legend
    legend_y = panel_h - _FOOTER_H + 4
    pygame.draw.line(panel, _BORDER, (8, legend_y - 4), (panel_w - 8, legend_y - 4))
    legend_items = [
        (_PLAYER, "You"), (_ENEMY, "Enemy"), (_STAIRS, "Stairs"),
        (_EXIT, "Exit"), (_ITEM, "Item"), (_TRAP, "Trap"),
    ]
    lx = 12
    for color, label in legend_items:
        pygame.draw.circle(panel, color, (lx + 5, legend_y + 10), 4)
        ls = small.render(label, True, _DIM)
        panel.blit(ls, (lx + 13, legend_y + 3))
        lx += ls.get_width() + 26

    screen.blit(panel, (px, py))
