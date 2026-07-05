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
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))
    game.screen.blit(gold_text, gold_text.get_rect(center=(SCREEN_WIDTH // 2, 116)))

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
        locked = row.get("locked", False)
        selected = index == game.inventory_index
        row_rect = pygame.Rect(12, y - 4, panel_width - 24, 30)
        if locked:
            pygame.draw.rect(panel, (28, 32, 40, 180), row_rect, border_radius=8)
        elif selected:
            pygame.draw.rect(panel, (38, 48, 68, 220), row_rect, border_radius=8)
            pygame.draw.rect(panel, (255, 222, 134), row_rect, 2, border_radius=8)
        swatch_color = row["color"] if not locked else (60, 55, 48)
        pygame.draw.rect(panel, swatch_color, (18, y + 4, 10, 18), border_radius=3)
        label_color = (120, 110, 90) if locked else ((255, 246, 214) if selected else COLOR_TEXT)
        detail_color = (100, 95, 80) if locked else (COLOR_ACCENT if selected else (200, 220, 240))
        label = game.small_font.render(row["label"], True, label_color)
        detail = game.small_font.render(row["detail"], True, detail_color)
        panel.blit(label, (38, y))
        panel.blit(detail, (panel_width - detail.get_width() - 22, y))
        y += 34

    rects = game.inventory_action_button_rects()
    rows = game.inventory_rows()
    sel_row = rows[game.inventory_index] if rows and game.inventory_index < len(rows) else None
    can_use = sel_row and sel_row["action"] == "use"
    can_equip = sel_row and sel_row["action"] == "equip"
    for btn_key, btn_label, enabled in [("use", "Use", can_use), ("equip", "Equip / Unequip", can_equip)]:
        r = rects[btn_key]
        bx, by = r.left - left, r.top - top
        br = pygame.Rect(bx, by, r.width, r.height)
        fill = (38, 56, 38, 240) if enabled else (28, 32, 38, 160)
        border = (120, 200, 120, 255) if enabled else (60, 72, 88, 180)
        txt_color = (200, 240, 200) if enabled else (80, 90, 100)
        pygame.draw.rect(panel, fill, br, border_radius=8)
        pygame.draw.rect(panel, border, br, 2, border_radius=8)
        lbl = game.small_font.render(btn_label, True, txt_color)
        panel.blit(lbl, lbl.get_rect(center=br.center))
    help_text = [
        "↑↓ selects · Enter / Space acts directly",
        "I or Esc closes  ·  controller: open from pause menu",
    ]
    help_y = panel_height - 56
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

    mouse_rel = (game.mouse_screen_pos[0] - rect.left, game.mouse_screen_pos[1] - rect.top)

    # Respawn button
    respawn_rect = game.death_respawn_rect().move(-rect.left, -rect.top)
    hovered_respawn = respawn_rect.collidepoint(mouse_rel)
    respawn_fill = (50, 100, 80) if hovered_respawn else (34, 72, 58)
    respawn_border = (140, 220, 180) if hovered_respawn else (90, 170, 130)
    pygame.draw.rect(panel, respawn_fill, respawn_rect, border_radius=12)
    pygame.draw.rect(panel, respawn_border, respawn_rect, 2, border_radius=12)
    respawn_text = game.small_font.render("Respawn", True, (200, 255, 230))
    panel.blit(respawn_text, respawn_text.get_rect(center=respawn_rect.center))

    # Main Menu button
    button_rect = game.death_main_menu_rect().move(-rect.left, -rect.top)
    hovered_button = button_rect.collidepoint(mouse_rel)
    button_fill = (110, 78, 84) if hovered_button else (78, 56, 62)
    button_border = (255, 214, 214) if hovered_button else (210, 164, 164)
    pygame.draw.rect(panel, button_fill, button_rect, border_radius=12)
    pygame.draw.rect(panel, button_border, button_rect, 2, border_radius=12)
    button_text = game.small_font.render("Main Menu", True, (255, 240, 240))
    panel.blit(button_text, button_text.get_rect(center=button_rect.center))

    footer = [
        "Click tabs or use left/right to change stat groups.",
        "Enter/Space to Respawn. Esc for Main Menu.",
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


def render_service_modal(game):
    if not game.service_modal_open:
        return
    modal_width = 360
    line_h = 24
    modal_height = max(120, 56 + len(game.service_modal_lines) * line_h + 52)
    x = (SCREEN_WIDTH - modal_width) // 2
    y = (VIEW_HEIGHT * TILE_SIZE - modal_height) // 2

    dim = pygame.Surface((SCREEN_WIDTH, VIEW_HEIGHT * TILE_SIZE), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 140))
    game.screen.blit(dim, (0, 0))

    modal = pygame.Surface((modal_width, modal_height), pygame.SRCALPHA)
    modal.fill((18, 24, 36, 245))
    pygame.draw.rect(modal, (180, 210, 240, 220), modal.get_rect(), 2, border_radius=14)

    title_surf = game.font.render(game.service_modal_title, True, (255, 244, 170))
    modal.blit(title_surf, title_surf.get_rect(centerx=modal_width // 2, y=14))
    pygame.draw.line(modal, (80, 110, 150, 180), (20, 42), (modal_width - 20, 42), 1)

    text_y = 52
    for line in game.service_modal_lines:
        surf = game.small_font.render(line, True, COLOR_TEXT)
        modal.blit(surf, surf.get_rect(centerx=modal_width // 2, y=text_y))
        text_y += line_h

    ok_rect = game.service_modal_ok_rect().move(-x, -y)
    pygame.draw.rect(modal, (44, 62, 88, 240), ok_rect, border_radius=8)
    pygame.draw.rect(modal, (120, 168, 210, 220), ok_rect, 1, border_radius=8)
    ok_label = game.small_font.render("OK", True, (220, 236, 252))
    modal.blit(ok_label, ok_label.get_rect(center=ok_rect.center))

    game.screen.blit(modal, (x, y))


from .rendering_levelup import render_levelup_overlay  # noqa: F401
