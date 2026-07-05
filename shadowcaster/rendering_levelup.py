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
    panel_w, panel_h = 560, 320
    x = (SCREEN_WIDTH - panel_w) // 2
    y = (SCREEN_HEIGHT - panel_h) // 2

    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((6, 8, 14, 200))
    game.screen.blit(dim, (0, 0))

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((20, 28, 20, 248))
    pygame.draw.rect(panel, (100, 200, 120, 255), panel.get_rect(), 3, border_radius=16)

    head = game.font.render(f"Level Up — {title}", True, (180, 255, 200))
    panel.blit(head, head.get_rect(center=(panel_w // 2, 36)))

    lvl_surf = game.small_font.render(f"You are now level {level}.", True, (160, 230, 180))
    panel.blit(lvl_surf, lvl_surf.get_rect(center=(panel_w // 2, 70)))

    y_text = 104
    for line in wrap_text_lines(game.small_font, unlock, panel_w - 64):
        surf = game.small_font.render(line, True, COLOR_TEXT)
        panel.blit(surf, surf.get_rect(center=(panel_w // 2, y_text)))
        y_text += 26

    if next_xp is not None:
        xp_now = getattr(game, "player_xp", 0)
        needed = next_xp - xp_now
        progress = game.small_font.render(
            f"XP: {xp_now} / {next_xp}  ({needed} to level {next_level})",
            True, COLOR_ACCENT,
        )
        panel.blit(progress, progress.get_rect(center=(panel_w // 2, panel_h - 80)))

    footer = game.small_font.render("Press Space or Enter to continue.", True, (130, 190, 150))
    panel.blit(footer, footer.get_rect(center=(panel_w // 2, panel_h - 50)))

    game.screen.blit(panel, (x, y))
