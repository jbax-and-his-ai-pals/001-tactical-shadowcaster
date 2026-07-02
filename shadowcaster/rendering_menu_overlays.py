import pygame

from .constants import (
    COLOR_ACCENT,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .rendering_primitives import (
    draw_section_header,
    draw_tabs,
    wrap_text,
)
from .rendering_journal_overlays import (
    render_notice_board_overlay,
    render_journal_overlay,
    render_log_overlay,
)


def render_menu_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 232))
    game.screen.blit(overlay, (0, 0))

    if game.menu_mode == "main":
        title = "Tactical Shadowcaster"
        subtitle = None
    elif game.menu_mode == "controls":
        title = "Controls"
        subtitle = None
    elif game.menu_mode == "load":
        title = "Load Game"
        subtitle = "Select a save snapshot"
    else:
        title = "Game Menu"
        subtitle = "Resume your run, manage saves, or tune the current balance"
    if game.menu_mode != "pause":
        title_text = game.font.render(title, True, (248, 244, 224))
        subtitle_text = game.small_font.render(subtitle, True, (206, 220, 236)) if subtitle else None

        accent_rect = pygame.Rect((SCREEN_WIDTH - 520) // 2, 82, 520, 96)
        accent = pygame.Surface((accent_rect.width, accent_rect.height), pygame.SRCALPHA)
        accent.fill((20, 28, 42, 120))
        pygame.draw.rect(accent, (70, 95, 130, 160), accent.get_rect(), 2, border_radius=18)
        pygame.draw.line(accent, (145, 225, 255, 120), (26, 64), (accent_rect.width - 26, 64), 2)
        game.screen.blit(accent, accent_rect.topleft)
        game.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 122)))
        if subtitle_text is not None:
            game.screen.blit(subtitle_text, subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 152)))

    if game.menu_mode == "controls":
        layout = game.controls_layout()
        box_width = layout["box_width"]
        box_height = layout["box_height"]
        left = layout["left"]
        top = layout["top"]
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel.fill((22, 28, 40, 238))
        pygame.draw.rect(panel, (116, 142, 174, 255), panel.get_rect(), 2, border_radius=14)

        tabs = game.controls_tabs()
        draw_tabs(panel, game.small_font, tabs, game.controls_tab, 22, 18, box_width - 44)
        content_rect = game.controls_content_rect()
        viewport = pygame.Surface((content_rect["width"], content_rect["height"]), pygame.SRCALPHA)
        viewport.fill((0, 0, 0, 0))
        content_height = max(content_rect["height"], game.controls_content_height() + 8)
        content = pygame.Surface((content_rect["width"], content_height), pygame.SRCALPHA)
        content.fill((0, 0, 0, 0))
        pygame.draw.rect(viewport, (36, 44, 60, 84), viewport.get_rect(), border_radius=10)
        sections = game.controls_sections()
        section_y = 0
        for heading, lines in sections:
            draw_section_header(content, game.small_font, heading, 0, section_y, content_rect["width"] - 8, COLOR_ACCENT)
            section_y += 26
            for line in lines:
                for surface in wrap_text(game.small_font, line, COLOR_TEXT, content_rect["width"] - 32):
                    content.blit(surface, (8, section_y))
                    section_y += 20
            section_y += 10
        scroll = game.current_controls_scroll()
        viewport.blit(content, (0, -scroll))
        panel.blit(viewport, (content_rect["left"], content_rect["top"]))
        if game.controls_max_scroll() > 0:
            hint = game.small_font.render("Scroll: wheel, Up/Down, or controller vertical input", True, COLOR_ACCENT)
            panel.blit(hint, (content_rect["left"], box_height - 28))
        game.screen.blit(panel, (left, top))
        back_top = layout["back_top"]
        back_width = layout["back_width"]
        back_height = layout["back_height"]
        back_panel = pygame.Surface((back_width, back_height), pygame.SRCALPHA)
        selected = game.menu_index == 0
        back_panel.fill((34, 42, 58, 240) if selected else (22, 28, 40, 230))
        back_border = (255, 222, 134, 255) if selected else (116, 142, 174, 255)
        pygame.draw.rect(back_panel, back_border, back_panel.get_rect(), 2, border_radius=10)
        back_label = game.font.render("Back", True, (255, 246, 214) if selected else COLOR_TEXT)
        back_panel.blit(back_label, back_label.get_rect(center=(back_width // 2, back_height // 2)))
        game.screen.blit(back_panel, ((SCREEN_WIDTH - back_width) // 2, back_top))
        footer = game.small_font.render(game.menu_message or "Back returns here with Enter, Space, Esc, or your controller's back button.", True, COLOR_ACCENT)
        game.screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, back_top + back_height + 22)))
        return

    layout = game.menu_layout()
    box_width = layout["box_width"]
    box_height = layout["box_height"]
    start_y = layout["start_y"]
    gap = layout["gap"]
    visible_options = layout["visible_options"]
    scroll = layout["scroll"]
    for visible_index, option in enumerate(visible_options):
        index = scroll + visible_index
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        rect = pygame.Rect(layout["left"], start_y + visible_index * (box_height + gap), box_width, box_height)
        hovered = rect.collidepoint(*game.mouse_screen_pos)
        disabled = option == "Load Game" and game.menu_mode == "main" and not game.can_load_from_menu()
        selected = index == game.menu_index or hovered
        panel.fill((34, 42, 58, 240) if selected and not disabled else (22, 28, 40, 190) if disabled else (22, 28, 40, 230))
        border = (255, 222, 134, 255) if selected and not disabled else (72, 84, 108, 200) if disabled else (116, 142, 174, 255)
        pygame.draw.rect(panel, border, panel.get_rect(), 2, border_radius=10)
        label_color = (126, 134, 150) if disabled else (255, 246, 214) if selected else COLOR_TEXT
        label = game.font.render(option, True, label_color)
        panel.blit(label, label.get_rect(center=(box_width // 2, box_height // 2)))
        if hovered and not disabled:
            glow = pygame.Surface((box_width + 16, box_height + 16), pygame.SRCALPHA)
            glow.fill((0, 0, 0, 0))
            pygame.draw.rect(glow, (145, 225, 255, 36), glow.get_rect(), border_radius=14)
            game.screen.blit(glow, (rect.left - 8, rect.top - 8))
        game.screen.blit(panel, rect.topleft)

    footer_hint = "Use arrows/Enter or controller D-pad/A." if game.menu_mode == "main" else "Esc resumes. Start or B also work on controller." if game.menu_mode == "pause" else "Use arrows or controller D-pad to browse saves."
    footer = game.small_font.render(game.menu_message or footer_hint, True, COLOR_ACCENT)
    game.screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, start_y + len(visible_options) * (box_height + gap) + 28)))
