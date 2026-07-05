import pygame

from .constants import (
    COLOR_ACCENT,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .rendering_primitives import (
    draw_scrollbar,
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
    elif game.menu_mode == "controls":
        title = "Controls"
    elif game.menu_mode == "confirm_main_menu":
        title = "Save before returning?"
    elif game.menu_mode == "confirm_exit_game":
        title = "Save before quitting?"
    elif game.menu_mode == "load":
        title = "Load Game"
    elif game.menu_mode == "settings":
        title = "Settings"
    else:
        title = "Game Menu"
    if game.menu_mode not in ("pause", "controls"):
        title_text = game.font.render(title, True, (248, 244, 224))

        accent_rect = pygame.Rect((SCREEN_WIDTH - 520) // 2, 82, 520, 64)
        accent = pygame.Surface((accent_rect.width, accent_rect.height), pygame.SRCALPHA)
        accent.fill((20, 28, 42, 120))
        pygame.draw.rect(accent, (70, 95, 130, 160), accent.get_rect(), 2, border_radius=18)
        game.screen.blit(accent, accent_rect.topleft)
        game.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 114)))

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
        sb_x = content_rect["left"] + content_rect["width"] + 2
        draw_scrollbar(panel, sb_x, content_rect["top"], content_rect["height"],
                       scroll, content_height, content_rect["height"])
        footer_h = layout["footer_h"]
        back_width = layout["back_width"]
        back_height = layout["back_height"]
        separator_y = box_height - footer_h
        pygame.draw.line(panel, (70, 95, 130, 180), (16, separator_y), (box_width - 16, separator_y), 1)
        selected = game.menu_index == 0
        bx = box_width - back_width - 16
        by = separator_y + (footer_h - back_height) // 2
        back_rect = pygame.Rect(bx, by, back_width, back_height)
        pygame.draw.rect(panel, (34, 42, 58, 240) if selected else (22, 28, 40, 200), back_rect, border_radius=8)
        pygame.draw.rect(panel, (255, 222, 134, 255) if selected else (116, 142, 174, 255), back_rect, 2, border_radius=8)
        back_label = game.small_font.render("Back", True, (255, 246, 214) if selected else COLOR_TEXT)
        panel.blit(back_label, back_label.get_rect(center=back_rect.center))
        game.screen.blit(panel, (left, top))
        return

    if game.menu_mode == "load":
        game.load_scroll_clamp()
        layout = game.load_layout()
        box_width = layout["box_width"]
        box_height = layout["box_height"]
        left = layout["left"]
        top = layout["top"]
        footer_h = layout["footer_h"]
        row_h = layout["row_h"]
        content_top = layout["content_top"]
        content_left = layout["content_left"]
        content_w = layout["content_w"]
        content_visible_h = layout["content_visible_h"]
        max_visible = layout["max_visible"]
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel.fill((22, 28, 40, 238))
        pygame.draw.rect(panel, (116, 142, 174, 255), panel.get_rect(), 2, border_radius=14)
        saves = game.save_entries
        if not saves:
            empty = game.small_font.render("No saves found.", True, COLOR_TEXT)
            panel.blit(empty, empty.get_rect(center=(box_width // 2, box_height // 2 - footer_h // 2)))
        else:
            scroll = game.menu_scroll
            for vi in range(max_visible):
                si = scroll + vi
                if si >= len(saves):
                    break
                entry = saves[si]
                selected = si == game.menu_index
                ry = content_top + vi * row_h
                row_rect = pygame.Rect(content_left, ry, content_w, row_h - 4)
                panel.fill((38, 48, 68, 220) if selected else (26, 32, 46, 180), row_rect)
                pygame.draw.rect(panel, (255, 222, 134, 255) if selected else (70, 90, 120, 200), row_rect, 2, border_radius=8)
                label = game.small_font.render(entry["label"], True, (255, 246, 214) if selected else COLOR_TEXT)
                panel.blit(label, (content_left + 14, ry + (row_h - 4 - label.get_height()) // 2))
            if len(saves) > max_visible:
                sb_x = content_left + content_w + 4
                draw_scrollbar(panel, sb_x, content_top, content_visible_h,
                               game.menu_scroll * row_h, len(saves) * row_h, max_visible * row_h)
        separator_y = box_height - footer_h
        pygame.draw.line(panel, (70, 95, 130, 180), (16, separator_y), (box_width - 16, separator_y), 1)
        back_width = layout["back_width"]
        back_height = layout["back_height"]
        by = layout["back_top"] - layout["top"]
        bx = layout["back_left"] - layout["left"]
        back_rect = pygame.Rect(bx, by, back_width, back_height)
        pygame.draw.rect(panel, (22, 28, 40, 200), back_rect, border_radius=8)
        pygame.draw.rect(panel, (116, 142, 174, 255), back_rect, 2, border_radius=8)
        panel.blit(game.small_font.render("Back", True, COLOR_TEXT), game.small_font.render("Back", True, COLOR_TEXT).get_rect(center=back_rect.center))
        has_selection = saves and game.menu_index < len(saves)
        lbx = layout["load_btn_left"] - layout["left"]
        lby = by
        load_rect = pygame.Rect(lbx, lby, layout["load_btn_width"], layout["load_btn_height"])
        load_fill = (38, 56, 38, 240) if has_selection else (28, 32, 38, 160)
        load_border = (120, 200, 120, 255) if has_selection else (60, 72, 88, 180)
        load_color = (200, 240, 200) if has_selection else (80, 90, 100)
        pygame.draw.rect(panel, load_fill, load_rect, border_radius=8)
        pygame.draw.rect(panel, load_border, load_rect, 2, border_radius=8)
        panel.blit(game.small_font.render("Load Game", True, load_color), game.small_font.render("Load Game", True, load_color).get_rect(center=load_rect.center))
        game.screen.blit(panel, (left, top))
        if game.menu_message:
            footer = game.small_font.render(game.menu_message, True, COLOR_ACCENT)
            game.screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, top + box_height + 18)))
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

    if game.menu_message:
        footer = game.small_font.render(game.menu_message, True, COLOR_ACCENT)
        game.screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, start_y + len(visible_options) * (box_height + gap) + 28)))
