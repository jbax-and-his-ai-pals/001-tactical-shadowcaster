import pygame

from .constants import (
    COLOR_ACCENT,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VIEW_HEIGHT,
    TILE_SIZE,
)
from .rendering_primitives import (
    draw_tabs,
    wrap_text,
)


def render_completion_modal(game):
    now = pygame.time.get_ticks()
    if now >= game.completion_modal_until:
        return
    duration = max(1, game.completion_modal_until - game.completion_modal_started)
    progress = (now - game.completion_modal_started) / duration
    fade = max(0.0, 1.0 - progress)
    pop = min(1.0, progress / 0.18) if progress < 0.18 else 1.0
    detail_lines = wrap_text(game.small_font, game.completion_modal_text or "Reward claimed", (235, 240, 255), 440)
    title = game.font.render("Floor Cleared", True, (255, 244, 170))
    content_width = max([title.get_width(), *(line.get_width() for line in detail_lines)], default=title.get_width())
    base_width = max(320, min(500, content_width + 40))
    base_height = max(88, 34 + title.get_height() + len(detail_lines) * 22 + 18)
    modal_width = int(base_width * (0.92 + 0.08 * pop))
    modal_height = int(base_height * (0.92 + 0.08 * pop))
    alpha = int(225 * fade)
    modal_surface = pygame.Surface((modal_width, modal_height), pygame.SRCALPHA)
    modal_surface.fill((16, 22, 34, alpha))
    pygame.draw.rect(modal_surface, (255, 226, 120, min(255, alpha + 20)), modal_surface.get_rect(), 3, border_radius=12)
    modal_surface.blit(title, title.get_rect(center=(modal_width // 2, 24)))
    detail_y = 42 + title.get_height()
    for line in detail_lines:
        modal_surface.blit(line, line.get_rect(center=(modal_width // 2, detail_y)))
        detail_y += 22
    x = (SCREEN_WIDTH - modal_width) // 2
    y = (VIEW_HEIGHT * TILE_SIZE - modal_height) // 2
    game.screen.blit(modal_surface, (x, y))


def render_reward_choice_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 220))
    game.screen.blit(overlay, (0, 0))

    title_text, subtitle_text = game.current_choice_title_subtitle()
    title = game.font.render(title_text, True, (255, 244, 170))
    subtitle = game.small_font.render(subtitle_text, True, (220, 230, 245))
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 72)))
    game.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 42)))

    labels = game.current_choice_options()
    box_width = 200
    box_height = 96
    gap = 20
    total_width = box_width * len(labels) + gap * max(0, len(labels) - 1)
    start_x = (SCREEN_WIDTH - total_width) // 2
    top = (SCREEN_HEIGHT - box_height) // 2 + 30
    for index, (label_text, detail_text) in enumerate(labels):
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        selected = index == game.exploration_choice_index
        panel.fill((34, 42, 58, 240) if selected else (22, 28, 40, 234))
        border = (255, 222, 134, 255) if selected else (116, 142, 174, 255)
        pygame.draw.rect(panel, border, panel.get_rect(), 2, border_radius=12)
        label = game.font.render(label_text, True, (255, 246, 214) if selected else COLOR_TEXT)
        detail = game.small_font.render(detail_text, True, COLOR_ACCENT if selected else COLOR_TEXT)
        panel.blit(label, label.get_rect(center=(box_width // 2, 34)))
        panel.blit(detail, detail.get_rect(center=(box_width // 2, 68)))
        game.screen.blit(panel, (start_x + index * (box_width + gap), top))

    footer = game.small_font.render("Arrow keys or click to choose. Enter confirms.", True, COLOR_TEXT)
    game.screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, top + box_height + 34)))


def render_tuner_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 228))
    game.screen.blit(overlay, (0, 0))

    title = game.font.render("Balance Tuner", True, (248, 244, 224))
    subtitle = game.small_font.render("Adjust live balance values for the active run", True, (206, 220, 236))
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 82)))
    game.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 110)))

    entries = game.grouped_tuner_entries()
    panel_width = 720
    panel_height = 500
    left = (SCREEN_WIDTH - panel_width) // 2
    top = 120
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 26, 38, 236))
    pygame.draw.rect(panel, (116, 142, 174, 255), panel.get_rect(), 2, border_radius=14)

    draw_tabs(panel, game.small_font, game.tuner_tabs(), game.tuner_tab, 18, 18, panel_width - 36)
    y = 66
    for index, entry in enumerate(entries):
        selected = index == game.tuner_index
        row_rect = pygame.Rect(12, y - 4, panel_width - 24, 30)
        if selected:
            pygame.draw.rect(panel, (38, 48, 68, 220), row_rect, border_radius=8)
            pygame.draw.rect(panel, (255, 222, 134), row_rect, 2, border_radius=8)
        label = game.small_font.render(entry["label"], True, (255, 246, 214) if selected else COLOR_TEXT)
        value = game.small_font.render(entry["display"], True, COLOR_ACCENT if selected else (200, 220, 240))
        panel.blit(label, (18, y))
        panel.blit(value, (panel_width - value.get_width() - 22, y))
        y += 34

    help_text = [
        "Tab, Q, or E switches tuner groups",
        "Up/down selects a setting, left/right changes its value",
        "T or Esc closes the tuner",
    ]
    help_y = panel_height - 84
    for line in help_text:
        surface = game.small_font.render(line, True, COLOR_TEXT)
        panel.blit(surface, (18, help_y))
        help_y += 22
    game.screen.blit(panel, (left, top))


def render_inventory_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 228))
    game.screen.blit(overlay, (0, 0))

    title = game.font.render("Inventory", True, (248, 244, 224))
    gold_text = game.small_font.render(f"Gold: {game.gold}", True, (240, 210, 100))
    subtitle = game.small_font.render("Use a consumable, or equip/unequip a weapon and armor", True, (206, 220, 236))
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 82)))
    game.screen.blit(gold_text, gold_text.get_rect(center=(SCREEN_WIDTH // 2, 106)))
    game.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 124)))

    rows = game.inventory_rows()
    panel_width = 720
    panel_height = 500
    left = (SCREEN_WIDTH - panel_width) // 2
    top = 136
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 26, 38, 236))
    pygame.draw.rect(panel, (116, 142, 174, 255), panel.get_rect(), 2, border_radius=14)

    y = 20
    if not rows:
        empty = game.small_font.render("Your pack is empty.", True, COLOR_TEXT)
        panel.blit(empty, (18, y))
    for index, row in enumerate(rows):
        selected = index == game.inventory_index
        row_rect = pygame.Rect(12, y - 4, panel_width - 24, 30)
        if selected:
            pygame.draw.rect(panel, (38, 48, 68, 220), row_rect, border_radius=8)
            pygame.draw.rect(panel, (255, 222, 134), row_rect, 2, border_radius=8)
        pygame.draw.rect(panel, row["color"], (18, y + 4, 10, 18), border_radius=3)
        label = game.small_font.render(row["label"], True, (255, 246, 214) if selected else COLOR_TEXT)
        detail = game.small_font.render(row["detail"], True, COLOR_ACCENT if selected else (200, 220, 240))
        panel.blit(label, (38, y))
        panel.blit(detail, (panel_width - detail.get_width() - 22, y))
        y += 34

    help_text = [
        "Up/down selects an item",
        "Enter or Space uses a consumable, or equips/unequips gear",
        "I or Esc closes the inventory; controller users can open it from pause",
    ]
    help_y = panel_height - 84
    for line in help_text:
        surface = game.small_font.render(line, True, COLOR_TEXT)
        panel.blit(surface, (18, help_y))
        help_y += 22
    game.screen.blit(panel, (left, top))


def render_game_over_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((6, 8, 14, 236))
    game.screen.blit(overlay, (0, 0))

    rect = game.death_overlay_rect()
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((24, 20, 28, 244))
    pygame.draw.rect(panel, (210, 96, 96, 255), panel.get_rect(), 3, border_radius=16)

    title = game.font.render("You Died", True, (255, 220, 220))
    subtitle = game.small_font.render(f"Fallen in {game.region_name}", True, (230, 214, 220))
    cause = game.small_font.render(f"Killed by {game.death_cause_label()}", True, (255, 188, 188))
    panel.blit(title, title.get_rect(center=(rect.width // 2, 34)))
    panel.blit(subtitle, subtitle.get_rect(center=(rect.width // 2, 60)))
    panel.blit(cause, cause.get_rect(center=(rect.width // 2, 82)))

    draw_tabs(panel, game.small_font, game.death_stats_tabs(), game.death_stats_tab, 24, 104, rect.width - 48)

    y = 154
    for line in game.game_over_summary_lines():
        surface = game.small_font.render(line, True, COLOR_TEXT)
        panel.blit(surface, (48, y))
        y += 28

    button_rect = game.death_main_menu_rect().move(-rect.left, -rect.top)
    hovered_button = button_rect.collidepoint((game.mouse_screen_pos[0] - rect.left, game.mouse_screen_pos[1] - rect.top))
    button_fill = (110, 78, 84) if hovered_button else (78, 56, 62)
    button_border = (255, 214, 214) if hovered_button else (210, 164, 164)
    pygame.draw.rect(panel, button_fill, button_rect, border_radius=12)
    pygame.draw.rect(panel, button_border, button_rect, 2, border_radius=12)
    button_text = game.small_font.render("Main Menu", True, (255, 240, 240))
    panel.blit(button_text, button_text.get_rect(center=button_rect.center))

    footer = [
        "Click tabs or use left/right to change stat groups.",
        "Press Enter, Space, or Esc for the in-game menu.",
    ]
    y = button_rect.top - 70
    for line in footer:
        surface = game.small_font.render(line, True, COLOR_ACCENT)
        panel.blit(surface, surface.get_rect(center=(rect.width // 2, y)))
        y += 24

    game.screen.blit(panel, rect.topleft)


def render_travel_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, VIEW_HEIGHT * TILE_SIZE), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 210))
    game.screen.blit(overlay, (0, 0))

    title = game.font.render("Choose Your Next Route", True, (250, 244, 224))
    subtitle = game.small_font.render(f"Leaving {game.region_name} for floor {game.floor}", True, (205, 220, 240))
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 110)))
    game.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140)))

    box_width = 280
    box_height = 86
    gap = 18
    total_width = box_width * len(game.travel_choices) + gap * max(0, len(game.travel_choices) - 1)
    start_x = (SCREEN_WIDTH - total_width) // 2
    top = (VIEW_HEIGHT * TILE_SIZE - box_height) // 2 + 36

    for index, choice in enumerate(game.travel_choices):
        left = start_x + index * (box_width + gap)
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel.fill((24, 30, 44, 232))
        pygame.draw.rect(panel, (110, 145, 185, 255), panel.get_rect(), 2, border_radius=12)

        key_text = game.small_font.render(f"{index + 1}", True, (255, 232, 170))
        name_text = game.small_font.render(choice.name, True, (240, 240, 248))
        type_text = game.small_font.render(choice.region_type.title(), True, (165, 215, 255))
        summary_text = game.small_font.render(choice.summary, True, (210, 220, 232))

        panel.blit(key_text, (12, 10))
        panel.blit(name_text, (34, 10))
        panel.blit(type_text, (12, 34))
        panel.blit(summary_text, (12, 58))
        game.screen.blit(panel, (left, top))
