from __future__ import annotations

import pygame

from .constants import SCREEN_HEIGHT, SCREEN_WIDTH
from .skills import SKILL_REGISTRY, SKILL_ORDER, SKILL_GROUPS

_BG     = (18, 16, 14)
_PANEL  = (26, 24, 22)
_BORDER = (80, 72, 60)
_SELECT = (220, 190, 80)
_DIM    = (100, 92, 80)
_GOLD   = (220, 190, 60)
_RED    = (200, 80, 80)
_GREEN  = (100, 190, 100)
_WHITE  = (230, 220, 210)
_TEAL   = (120, 200, 180)
_MAXED  = (160, 140, 100)

_BOX_W     = 600
_BOX_H     = 440
_LEFT      = (SCREEN_WIDTH - _BOX_W) // 2
_TOP       = (SCREEN_HEIGHT - _BOX_H) // 2
_HEADER_H  = 42
_FOOTER_H  = 32
_ROW_H     = 30
_CONTENT_Y = _TOP + _HEADER_H + 8
_FOOTER_Y  = _TOP + _BOX_H - _FOOTER_H
_CONTENT_H = _FOOTER_Y - _CONTENT_Y
_MAX_ROWS  = _CONTENT_H // _ROW_H


def render_trainer_overlay(game):
    screen = game.screen

    surf = pygame.Surface((_BOX_W, _BOX_H), pygame.SRCALPHA)
    surf.fill((*_BG, 245))
    pygame.draw.rect(surf, _BORDER, surf.get_rect(), 2, border_radius=8)
    screen.blit(surf, (_LEFT, _TOP))

    font  = game.font
    small = game.small_font

    # Header
    title = font.render("GUILD TRAINER", True, _WHITE)
    screen.blit(title, (_LEFT + 16, _TOP + 10))
    gold_surf = font.render(f"Your gold: {game.gold}g", True, _GOLD)
    screen.blit(gold_surf, (_LEFT + _BOX_W - gold_surf.get_width() - 16, _TOP + 10))
    pygame.draw.line(screen, _BORDER, (_LEFT, _TOP + _HEADER_H), (_LEFT + _BOX_W, _TOP + _HEADER_H))

    rows = game.trainer_skill_rows()
    sel  = getattr(game, "trainer_skill_index", 0)
    sel  = min(sel, max(0, len(rows) - 1))
    offset = max(0, sel - _MAX_ROWS + 1)

    if not rows:
        msg = small.render("No skills available.", True, _DIM)
        screen.blit(msg, (_LEFT + 16, _CONTENT_Y + 16))
    else:
        for row_i, row in enumerate(rows[offset: offset + _MAX_ROWS]):
            abs_i = row_i + offset
            y = _CONTENT_Y + row_i * _ROW_H
            is_sel = abs_i == sel

            if is_sel:
                pygame.draw.rect(screen, (40, 36, 28), (_LEFT + 4, y, _BOX_W - 8, _ROW_H - 2))
                pygame.draw.rect(screen, _SELECT,      (_LEFT + 4, y, _BOX_W - 8, _ROW_H - 2), 1, border_radius=3)

            if row.get("is_header"):
                grp = small.render(row["label"], True, _TEAL)
                screen.blit(grp, (_LEFT + 14, y + 7))
                continue

            rank    = row["rank"]
            max_r   = row["max_rank"]
            cost    = row["cost"]
            maxed   = rank >= max_r
            can_buy = not maxed and game.gold >= cost

            # Skill name + pips
            pips  = "●" * rank + "○" * (max_r - rank)
            label = f"{row['name']}  {pips}"
            name_color = _MAXED if maxed else (_WHITE if is_sel else row.get("color", _WHITE))
            name_surf = small.render(label, True, name_color)
            screen.blit(name_surf, (_LEFT + 24, y + 7))

            # Cost or MAXED
            if maxed:
                cost_surf = small.render("MAXED", True, _MAXED)
            else:
                cost_str  = f"{cost}g"
                cost_surf = small.render(cost_str, True, (_GOLD if can_buy else _RED))
            screen.blit(cost_surf, (_LEFT + _BOX_W - cost_surf.get_width() - 14, y + 7))

    # Description strip for selected non-header row
    if rows:
        sel_row = rows[sel] if sel < len(rows) else None
        if sel_row and not sel_row.get("is_header"):
            desc = sel_row.get("description", "")
            desc_surf = small.render(desc[:72], True, _DIM)
            screen.blit(desc_surf, (_LEFT + 14, _FOOTER_Y - 22))

    # Footer
    pygame.draw.line(screen, _BORDER, (_LEFT, _FOOTER_Y), (_LEFT + _BOX_W, _FOOTER_Y))
    hint = "Enter: Train  |  ↑↓: Select  |  Esc: Close"
    hint_surf = small.render(hint, True, _DIM)
    screen.blit(hint_surf, (_LEFT + 16, _FOOTER_Y + 8))
