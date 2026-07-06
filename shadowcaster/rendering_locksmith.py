from __future__ import annotations

import pygame

from .constants import SCREEN_HEIGHT, SCREEN_WIDTH
from .mixins.game_locksmith import LOCKED_CONTAINER_DEFS

_BG      = (18, 16, 14)
_PANEL   = (26, 24, 22)
_BORDER  = (80, 72, 60)
_SELECT  = (220, 190, 80)
_DIM     = (100, 92, 80)
_GOLD    = (220, 190, 60)
_RED     = (200, 80, 80)
_WHITE   = (230, 220, 210)
_TAN     = (190, 160, 100)

_BOX_W      = 520
_BOX_H      = 380
_LEFT       = (SCREEN_WIDTH - _BOX_W) // 2
_TOP        = (SCREEN_HEIGHT - _BOX_H) // 2
_HEADER_H   = 42
_FOOTER_H   = 32
_ROW_H      = 32
_CONTENT_Y  = _TOP + _HEADER_H + 8
_FOOTER_Y   = _TOP + _BOX_H - _FOOTER_H
_CONTENT_H  = _FOOTER_Y - _CONTENT_Y
_MAX_ROWS   = _CONTENT_H // _ROW_H


def render_locksmith_overlay(game):
    screen = game.screen

    # Background
    surf = pygame.Surface((_BOX_W, _BOX_H), pygame.SRCALPHA)
    surf.fill((*_BG, 245))
    pygame.draw.rect(surf, _BORDER, surf.get_rect(), 2, border_radius=8)
    screen.blit(surf, (_LEFT, _TOP))

    font = game.font
    small = game.small_font

    # Header
    title = font.render("LOCKSMITH", True, _WHITE)
    screen.blit(title, (_LEFT + 16, _TOP + 10))
    gold_surf = font.render(f"Your gold: {game.gold}g", True, _GOLD)
    screen.blit(gold_surf, (_LEFT + _BOX_W - gold_surf.get_width() - 16, _TOP + 10))
    pygame.draw.line(screen, _BORDER, (_LEFT, _TOP + _HEADER_H), (_LEFT + _BOX_W, _TOP + _HEADER_H))

    items = game.locksmith_items()

    if not items:
        msg = small.render("You have no locked containers.", True, _DIM)
        screen.blit(msg, (_LEFT + 16, _CONTENT_Y + 16))
        sub = small.render("Defeat enemies — they sometimes carry sealed chests.", True, _DIM)
        screen.blit(sub, (_LEFT + 16, _CONTENT_Y + 36))
    else:
        sel = min(game.locksmith_index, len(items) - 1)
        offset = max(0, sel - _MAX_ROWS + 1)
        visible = items[offset: offset + _MAX_ROWS]

        for row_i, item in enumerate(visible):
            abs_i = row_i + offset
            y = _CONTENT_Y + row_i * _ROW_H
            is_sel = abs_i == sel
            defn = LOCKED_CONTAINER_DEFS.get(item.key, {})
            cost = defn.get("cost", 10)
            can_afford = game.gold >= cost

            if is_sel:
                pygame.draw.rect(screen, (40, 36, 28), (_LEFT + 4, y, _BOX_W - 8, _ROW_H - 2))
                pygame.draw.rect(screen, _SELECT, (_LEFT + 4, y, _BOX_W - 8, _ROW_H - 2), 1, border_radius=3)

            qty = getattr(item, "quantity", 1)
            name_str = item.name + (f" ×{qty}" if qty > 1 else "")
            name_color = _WHITE if is_sel else _TAN
            name_surf = small.render(name_str, True, name_color)
            screen.blit(name_surf, (_LEFT + 14, y + 8))

            cost_str = f"{cost}g to unlock"
            cost_color = _GOLD if can_afford else _RED
            cost_surf = small.render(cost_str, True, cost_color)
            screen.blit(cost_surf, (_LEFT + _BOX_W - cost_surf.get_width() - 14, y + 8))

        # Description of selected item
        if items:
            sel_item = items[min(sel, len(items) - 1)]
            defn = LOCKED_CONTAINER_DEFS.get(sel_item.key, {})
            gold_min, gold_max = defn.get("loot_gold", (3, 10))
            loot_key, loot_chance = defn.get("loot_item", ("medkit", 0))
            loot_names = {"medkit": "Healing Potion", "tonic": "Ward Tonic"}
            detail = f"Contains {gold_min}–{gold_max}g + {int(loot_chance*100)}% chance of {loot_names.get(loot_key, 'item')}."
            detail_surf = small.render(detail, True, _DIM)
            detail_y = _FOOTER_Y - 22
            screen.blit(detail_surf, (_LEFT + 14, detail_y))

    # Footer
    pygame.draw.line(screen, _BORDER, (_LEFT, _FOOTER_Y), (_LEFT + _BOX_W, _FOOTER_Y))
    hint = "Enter: Unlock  |  ↑↓: Select  |  Esc: Close"
    hint_surf = small.render(hint, True, _DIM)
    screen.blit(hint_surf, (_LEFT + 16, _FOOTER_Y + 8))
