import pygame

from .constants import COLOR_ACCENT, COLOR_TEXT, SCREEN_HEIGHT, SCREEN_WIDTH
from .rendering_primitives import wrap_text, wrap_text_lines


def render_levelup_overlay(game):
    from .mixins.game_xp import LEVEL_TITLES, LEVEL_UNLOCKS, XP_THRESHOLDS
    from .mixins.game_abilities import ABILITY_POOL
    level = getattr(game, "levelup_pending", game.player_level)
    title = LEVEL_TITLES.get(level, "???")
    unlock = LEVEL_UNLOCKS.get(level, "")
    next_level = level + 1
    next_xp = XP_THRESHOLDS.get(next_level)
    ability_choices = getattr(game, "levelup_ability_choices", [])
    ability_index = getattr(game, "levelup_ability_index", 0)

    # Ability selection mode (level 4)
    if ability_choices:
        panel_w, panel_h = 680, 380
        px = (SCREEN_WIDTH - panel_w) // 2
        py = (SCREEN_HEIGHT - panel_h) // 2
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((6, 8, 14, 200))
        game.screen.blit(dim, (0, 0))
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((20, 28, 20, 248))
        pygame.draw.rect(panel, (180, 160, 80, 255), panel.get_rect(), 3, border_radius=16)
        head = game.font.render(f"Level Up — {title}", True, (255, 230, 140))
        panel.blit(head, head.get_rect(center=(panel_w // 2, 30)))
        sub = game.small_font.render("Choose your combat signature ability:", True, (200, 190, 160))
        panel.blit(sub, sub.get_rect(center=(panel_w // 2, 58)))
        card_w, card_h = 190, 140
        gap = 20
        total_cards_w = len(ability_choices) * card_w + (len(ability_choices) - 1) * gap
        card_x = (panel_w - total_cards_w) // 2
        card_y = 82
        for i, key in enumerate(ability_choices):
            spec = ABILITY_POOL.get(key, {})
            selected = i == ability_index
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill((38, 34, 20, 220) if selected else (26, 24, 16, 200))
            border_color = (255, 210, 80, 255) if selected else (120, 110, 70, 200)
            pygame.draw.rect(card_surf, border_color, card_surf.get_rect(), 2, border_radius=10)
            name_surf = game.small_font.render(spec.get("name", key), True, (255, 230, 140) if selected else (200, 190, 140))
            card_surf.blit(name_surf, name_surf.get_rect(center=(card_w // 2, 20)))
            for di, dline in enumerate(wrap_text_lines(game.small_font, spec.get("description", ""), card_w - 16)):
                ds = game.small_font.render(dline, True, (220, 215, 200) if selected else COLOR_TEXT)
                card_surf.blit(ds, (8, 44 + di * 22))
            for fi, fline in enumerate(wrap_text_lines(game.small_font, spec.get("flavor", ""), card_w - 16)):
                fs = game.small_font.render(fline, True, (160, 150, 110) if selected else (120, 115, 90))
                card_surf.blit(fs, (8, card_h - 36 + fi * 18))
            panel.blit(card_surf, (card_x, card_y))
            card_x += card_w + gap
        footer = game.small_font.render("← → to select, Enter or Space to confirm.", True, (160, 150, 110))
        panel.blit(footer, footer.get_rect(center=(panel_w // 2, panel_h - 28)))
        game.screen.blit(panel, (px, py))
        return

    # Standard level-up modal
    gains = getattr(game, "levelup_gains", [])
    xp_now = getattr(game, "player_xp", 0)

    panel_w, panel_h = 580, 360
    px = (SCREEN_WIDTH - panel_w) // 2
    py = (SCREEN_HEIGHT - panel_h) // 2

    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((6, 8, 14, 210))
    game.screen.blit(dim, (0, 0))

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((20, 28, 20, 252))
    pygame.draw.rect(panel, (100, 200, 120, 255), panel.get_rect(), 3, border_radius=16)

    # Title
    head = game.font.render(f"Level {level}  —  {title}", True, (180, 255, 200))
    panel.blit(head, head.get_rect(center=(panel_w // 2, 34)))

    # Thin divider
    pygame.draw.line(panel, (60, 120, 70), (40, 56), (panel_w - 40, 56))

    # Gains list
    gy = 72
    bullet_color = (140, 220, 160)
    for line in gains:
        wrapped = wrap_text_lines(game.small_font, line, panel_w - 80)
        for i, wl in enumerate(wrapped):
            prefix = "▸ " if i == 0 else "  "
            s = game.small_font.render(prefix + wl, True, bullet_color if i == 0 else COLOR_TEXT)
            panel.blit(s, (48, gy))
            gy += 24
        gy += 4

    # XP bar toward next level
    bar_y = panel_h - 88
    pygame.draw.line(panel, (60, 120, 70), (40, bar_y - 8), (panel_w - 40, bar_y - 8))
    if next_xp is not None:
        prev_xp = XP_THRESHOLDS.get(level, 0)
        span = next_xp - prev_xp
        fill = max(0.0, min(1.0, (xp_now - prev_xp) / span)) if span > 0 else 0.0
        bar_w = panel_w - 80
        pygame.draw.rect(panel, (30, 60, 35), (40, bar_y, bar_w, 14), border_radius=4)
        if fill > 0:
            pygame.draw.rect(panel, (80, 200, 100), (40, bar_y, int(bar_w * fill), 14), border_radius=4)
        pygame.draw.rect(panel, (60, 120, 70), (40, bar_y, bar_w, 14), 1, border_radius=4)
        xp_label = game.small_font.render(
            f"XP {xp_now}/{next_xp}  —  {next_xp - xp_now} to level {next_level}", True, (130, 190, 150)
        )
        panel.blit(xp_label, xp_label.get_rect(center=(panel_w // 2, bar_y + 28)))
    else:
        maxed = game.small_font.render("Maximum level reached.", True, (180, 220, 140))
        panel.blit(maxed, maxed.get_rect(center=(panel_w // 2, bar_y + 14)))

    footer = game.small_font.render("Press Space or Enter to continue.", True, (100, 160, 120))
    panel.blit(footer, footer.get_rect(center=(panel_w // 2, panel_h - 26)))

    game.screen.blit(panel, (px, py))
