from __future__ import annotations

import pygame

from .constants import COLOR_TEXT, SCREEN_HEIGHT, SCREEN_WIDTH

_BG        = (18, 16, 14)
_PANEL_BG  = (26, 24, 22)
_BORDER    = (80, 72, 60)
_SELECT    = (220, 190, 80)
_DIM       = (100, 92, 80)
_GOLD      = (220, 190, 60)
_RED       = (200, 80, 80)
_GREEN     = (100, 190, 100)
_CRAFT     = (140, 200, 160)
_WHITE     = (230, 220, 210)

_BOX_W = 760
_BOX_H = 440
_LEFT  = (SCREEN_WIDTH - _BOX_W) // 2
_TOP   = (SCREEN_HEIGHT - _BOX_H) // 2

_STOCK_COL_W  = _BOX_W // 2
_PACK_COL_W   = _BOX_W - _STOCK_COL_W
_HEADER_H     = 42
_FOOTER_H     = 32
_ROW_H        = 26
_CONTENT_TOP  = _TOP + _HEADER_H + 4
_CONTENT_BOT  = _TOP + _BOX_H - _FOOTER_H - 4
_CONTENT_H    = _CONTENT_BOT - _CONTENT_TOP
_MAX_ROWS     = _CONTENT_H // _ROW_H


def _draw_bg(screen):
    surf = pygame.Surface((_BOX_W, _BOX_H), pygame.SRCALPHA)
    surf.fill((*_BG, 240))
    pygame.draw.rect(surf, _BORDER, surf.get_rect(), 2, border_radius=8)
    screen.blit(surf, (_LEFT, _TOP))


def _draw_header(game, screen):
    font = game.font
    # Title
    title = font.render("PROVISIONER", True, _WHITE)
    screen.blit(title, (_LEFT + 16, _TOP + 10))
    # Player gold
    gold_text = font.render(f"Your gold: {game.gold}g", True, _GOLD)
    screen.blit(gold_text, (_LEFT + _BOX_W - gold_text.get_width() - 16, _TOP + 10))
    # Divider
    pygame.draw.line(screen, _BORDER, (_LEFT, _TOP + _HEADER_H), (_LEFT + _BOX_W, _TOP + _HEADER_H))


def _draw_footer(game, screen):
    font = game.small_font
    active = game.trade_panel
    if active == 0:
        hint = "Enter: Buy  |  Tab: Switch to Pack  |  Esc: Close"
    else:
        hint = "Enter: Sell  |  Tab: Switch to Stock  |  Esc: Close"
    text = font.render(hint, True, _DIM)
    pygame.draw.line(screen, _BORDER,
                     (_LEFT, _TOP + _BOX_H - _FOOTER_H),
                     (_LEFT + _BOX_W, _TOP + _BOX_H - _FOOTER_H))
    screen.blit(text, (_LEFT + 16, _TOP + _BOX_H - _FOOTER_H + 8))


def _draw_stock_panel(game, screen):
    font = game.small_font
    panel_left = _LEFT + 2
    panel_right = _LEFT + _STOCK_COL_W - 2

    # Column header
    active = game.trade_panel == 0
    header_color = _WHITE if active else _DIM
    label = font.render("FOR SALE", True, header_color)
    screen.blit(label, (panel_left + 8, _CONTENT_TOP - 22))
    trader_gold_text = font.render(f"Trader's coin: {game.trader_gold}g", True, _DIM)
    screen.blit(trader_gold_text, (panel_left + 8, _CONTENT_TOP - 8))

    # Vertical divider
    pygame.draw.line(screen, _BORDER,
                     (_LEFT + _STOCK_COL_W, _TOP + _HEADER_H),
                     (_LEFT + _STOCK_COL_W, _TOP + _BOX_H - _FOOTER_H))

    stock = getattr(game, "trader_stock", [])
    sel_idx = game.trade_stock_index
    # Scroll to keep selection visible
    offset = max(0, sel_idx - _MAX_ROWS + 1)

    for row_i, entry in enumerate(stock[offset: offset + _MAX_ROWS]):
        abs_i = row_i + offset
        y = _CONTENT_TOP + row_i * _ROW_H
        is_sel = active and abs_i == sel_idx

        if is_sel:
            pygame.draw.rect(screen, (40, 36, 28),
                             (panel_left, y, _STOCK_COL_W - 4, _ROW_H - 2))
            pygame.draw.rect(screen, _SELECT,
                             (panel_left, y, _STOCK_COL_W - 4, _ROW_H - 2), 1, border_radius=3)

        entry_type = entry.get("type")
        name = entry.get("name", "")
        if entry_type == "craft":
            name_color = _CRAFT if is_sel else _DIM
            label_text = font.render(name, True, name_color)
            screen.blit(label_text, (panel_left + 10, y + 4))
            sub = font.render(entry.get("label", ""), True, _DIM)
            screen.blit(sub, (panel_left + 10, y + 14) if _ROW_H >= 26 else (panel_left + 140, y + 4))
        else:
            price = entry.get("price", 0)
            qty = entry.get("qty")
            can_afford = game.gold >= price
            name_color = _WHITE if (is_sel or can_afford) else _DIM
            if entry_type in ("weapon", "armor") and game.owns_item(entry.get("key", "")):
                name_color = _DIM
                name = name + " (owned)"
            label_text = font.render(name, True, name_color)
            screen.blit(label_text, (panel_left + 10, y + 4))
            price_color = _GOLD if can_afford else _RED
            price_str = f"{price}g" + (f" ×{qty}" if qty is not None else "")
            price_surf = font.render(price_str, True, price_color)
            screen.blit(price_surf, (panel_right - price_surf.get_width() - 6, y + 4))


def _draw_pack_panel(game, screen):
    font = game.small_font
    panel_left = _LEFT + _STOCK_COL_W + 2

    active = game.trade_panel == 1
    header_color = _WHITE if active else _DIM
    label = font.render("YOUR PACK", True, header_color)
    screen.blit(label, (panel_left + 8, _CONTENT_TOP - 22))

    rows = game._trade_pack_rows()
    sel_idx = game.trade_pack_index
    offset = max(0, sel_idx - _MAX_ROWS + 1)

    if not rows:
        nothing = font.render("(nothing to sell)", True, _DIM)
        screen.blit(nothing, (panel_left + 10, _CONTENT_TOP + 4))
        return

    panel_right = _LEFT + _BOX_W - 2

    for row_i, item in enumerate(rows[offset: offset + _MAX_ROWS]):
        abs_i = row_i + offset
        y = _CONTENT_TOP + row_i * _ROW_H
        is_sel = active and abs_i == sel_idx

        if is_sel:
            pygame.draw.rect(screen, (40, 36, 28),
                             (panel_left, y, _PACK_COL_W - 4, _ROW_H - 2))
            pygame.draw.rect(screen, _SELECT,
                             (panel_left, y, _PACK_COL_W - 4, _ROW_H - 2), 1, border_radius=3)

        sell_price = game._item_sell_price(item)
        trader_can_buy = game.trader_gold >= sell_price

        if item.equipped:
            name_str = f"{item.name} (equipped)"
            name_color = _DIM
            price_str = "—"
            price_color = _DIM
        else:
            qty = getattr(item, "quantity", 1)
            name_str = item.name + (f" ×{qty}" if qty > 1 else "")
            name_color = _WHITE if is_sel else (_WHITE if trader_can_buy else _DIM)
            price_str = f"{sell_price}g"
            price_color = _GREEN if trader_can_buy else _DIM

        label_surf = font.render(name_str, True, name_color)
        screen.blit(label_surf, (panel_left + 10, y + 4))
        price_surf = font.render(price_str, True, price_color)
        screen.blit(price_surf, (panel_right - price_surf.get_width() - 6, y + 4))


def render_trade_overlay(game):
    screen = game.screen
    _draw_bg(screen)
    _draw_header(game, screen)
    _draw_footer(game, screen)
    _draw_stock_panel(game, screen)
    _draw_pack_panel(game, screen)
