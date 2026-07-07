import pygame

from .constants import (
    COLOR_ACCENT,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .rendering_primitives import (
    draw_tabs,
    wrap_text,
    wrap_text_lines,
)


from .rendering_notice_board import render_notice_board_overlay  # noqa: F401


def render_journal_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 214))
    game.screen.blit(overlay, (0, 0))

    layout = game.journal_layout()
    left = layout["left"]
    top = layout["top"]
    panel_w = layout["panel_w"]
    panel_h = layout["panel_h"]
    viewport_rect = layout["viewport"]
    close_rect = layout["close_rect"]

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((18, 22, 32, 245))
    pygame.draw.rect(panel, (132, 166, 196, 255), panel.get_rect(), 2, border_radius=14)
    inner_rect = pygame.Rect(10, 10, panel_w - 20, panel_h - 20)
    pygame.draw.rect(panel, (34, 42, 58, 88), inner_rect, 1, border_radius=12)

    title = game.font.render("Journal", True, (236, 244, 252))
    summary_lines = game.current_journal_summary_lines()
    panel.blit(title, title.get_rect(centerx=panel_w // 2, y=16))
    for index, line in enumerate(summary_lines):
        summary = game.small_font.render(line, True, (180, 202, 224) if index == 0 else (166, 188, 212))
        panel.blit(summary, summary.get_rect(centerx=panel_w // 2, y=48 + index * 20))
    draw_tabs(panel, game.small_font, game.quest_tabs(), game.journal_tab, 22, layout["tab_top"] - top, panel_w - 44)

    viewport = pygame.Surface((viewport_rect.width, viewport_rect.height), pygame.SRCALPHA)
    viewport.fill((20, 26, 38, 168))
    pygame.draw.rect(viewport, (60, 76, 98, 120), viewport.get_rect(), 1, border_radius=10)
    content_height = max(viewport_rect.height, game.journal_content_height())
    content = pygame.Surface((viewport_rect.width, content_height), pygame.SRCALPHA)
    content.fill((0, 0, 0, 0))

    entries = game.current_journal_entries()
    if not entries and game.journal_tab == 2:
        char_rows = game.character_journal_rows()
        y = 12
        row_w = viewport_rect.width - 16
        skill_rows = [r for r in char_rows if r.get("selectable")]
        sel_skill_idx = getattr(game, "journal_skill_index", 0)
        skill_counter = 0
        for row in char_rows:
            is_section = row.get("section", False)
            is_selectable = row.get("selectable", False)
            is_selected = is_selectable and skill_counter == sel_skill_idx
            if is_selectable:
                skill_counter += 1
            header_surf = game.small_font.render(row["header"], True, row["color"])
            detail_surfaces = wrap_text(game.small_font, row["detail"], COLOR_TEXT, row_w - 28)
            row_height = (14 + 14) if is_section else (20 + len(detail_surfaces) * 18 + 14)
            row_rect = pygame.Rect(8, y, row_w, row_height)
            if is_section:
                content.blit(header_surf, (row_rect.left + 12, row_rect.top + 4))
                sp_surf = game.small_font.render(row["detail"], True, (160, 200, 160))
                content.blit(sp_surf, (row_rect.right - sp_surf.get_width() - 12, row_rect.top + 4))
            else:
                bg = (40, 50, 28) if is_selected else (26, 34, 50, 200)
                border_color = (*row["color"][:3], 220) if is_selected else (*row["color"][:3], 160)
                pygame.draw.rect(content, bg, row_rect, border_radius=10)
                pygame.draw.rect(content, border_color, row_rect, 1 if not is_selected else 2, border_radius=10)
                content.blit(header_surf, (row_rect.left + 12, row_rect.top + 8))
                line_y = row_rect.top + 28
                for surf in detail_surfaces:
                    content.blit(surf, (row_rect.left + 12, line_y))
                    line_y += 18
            y += row_height + 8
    elif not entries and game.journal_tab == 4:
        notes = list(reversed(getattr(game, "_world_notes", [])))
        _NOTE_COLORS = {
            "hamlet_founded": (140, 210, 140),
            "hamlet_abandoned": (210, 120, 90),
            "archetype": (160, 170, 240),
            "raid": (220, 100, 80),
            "road": (220, 200, 100),
            "event": (180, 196, 218),
        }
        if not notes:
            hint = game.small_font.render("Significant world changes will be recorded here.", True, COLOR_TEXT)
            content.blit(hint, (14, 16))
        else:
            y = 8
            row_w = viewport_rect.width - 16
            for note in notes:
                kind_color = _NOTE_COLORS.get(note.get("kind", "event"), (180, 196, 218))
                row_rect = pygame.Rect(8, y, row_w, 48)
                pygame.draw.rect(content, (26, 34, 50, 200), row_rect, border_radius=8)
                pygame.draw.rect(content, (*kind_color[:3], 120), row_rect, 1, border_radius=8)
                note_surf = game.small_font.render(note["text"], True, (230, 240, 250))
                content.blit(note_surf, (row_rect.left + 12, row_rect.top + 8))
                step = note.get("step", 0)
                step_surf = game.tiny_font.render(f"Step {step}", True, kind_color)
                content.blit(step_surf, (row_rect.left + 12, row_rect.top + 28))
                y += 56
    elif not entries and game.journal_tab == 3:
        town_rows = game.town_reputation_rows()
        if not town_rows:
            hint = game.small_font.render("Visit towns to see your reputation here.", True, COLOR_TEXT)
            content.blit(hint, (14, 16))
        else:
            y = 8
            row_w = viewport_rect.width - 16
            for tr in town_rows:
                score = tr["score"]
                standing_color = (160, 220, 160) if score >= 6 else (220, 200, 130) if score >= 3 else (200, 160, 140)
                row_rect = pygame.Rect(8, y, row_w, 48)
                pygame.draw.rect(content, (26, 34, 50, 200), row_rect, border_radius=8)
                pygame.draw.rect(content, (*standing_color[:3], 120), row_rect, 1, border_radius=8)
                name_surf = game.small_font.render(tr["name"], True, (230, 240, 250))
                content.blit(name_surf, (row_rect.left + 12, row_rect.top + 8))
                detail = game.small_font.render(
                    f"Standing: {tr['label']}  ·  Prosperity: {tr['prosperity']}",
                    True, standing_color,
                )
                content.blit(detail, (row_rect.left + 12, row_rect.top + 26))
                y += 56
    elif not entries:
        empty_lines = ["No quests in this tab yet.", "Visit a town board to pick up new work."]
        y = 16
        for line in empty_lines:
            for surface in wrap_text(game.small_font, line, COLOR_TEXT, viewport_rect.width - 28):
                content.blit(surface, (14, y))
                y += 20
    else:
        y = 12
        content_width = viewport_rect.width - 28
        for index, quest in enumerate(entries):
            body_lines = []
            for line in game.journal_entry_lines(quest):
                body_lines.extend(wrap_text_lines(game.small_font, line, content_width - 18))
            row_height = 42 + len(body_lines) * 18 + 14
            row_rect = pygame.Rect(8, y, viewport_rect.width - 16, row_height)
            selected = index == game.journal_index
            fill = (32, 42, 58, 220) if selected else (26, 34, 48, 210) if quest.status == "active" else (22, 28, 40, 170)
            border = (212, 188, 118) if selected else (154, 206, 150) if quest.status == "active" else (108, 126, 148)
            pygame.draw.rect(content, fill, row_rect, border_radius=10)
            pygame.draw.rect(content, border, row_rect, 2 if quest.status == "active" else 1, border_radius=10)

            status = game.quest_status_label(quest)
            header = game.small_font.render(status, True, border)
            reward = game.small_font.render(f"{quest.reward_gold}g", True, (220, 208, 132))
            content.blit(header, (row_rect.left + 12, row_rect.top + 10))
            content.blit(reward, (row_rect.right - reward.get_width() - 12, row_rect.top + 10))

            line_y = row_rect.top + 32
            for line in body_lines:
                content.blit(game.small_font.render(line, True, COLOR_TEXT), (row_rect.left + 12, line_y))
                line_y += 18
            y += row_height + 10

    viewport.blit(content, (0, -game.journal_scroll))
    panel.blit(viewport, (viewport_rect.left - left, viewport_rect.top - top))

    max_scroll = game.journal_max_scroll()
    if max_scroll > 0:
        track = pygame.Rect(panel_w - 20, viewport_rect.top - top, 6, viewport_rect.height)
        pygame.draw.rect(panel, (42, 52, 70), track, border_radius=4)
        thumb_height = max(28, int(viewport_rect.height * (viewport_rect.height / max(viewport_rect.height, content_height))))
        thumb_y = track.y + int((track.height - thumb_height) * (game.journal_scroll / max_scroll))
        thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
        pygame.draw.rect(panel, (130, 168, 206), thumb, border_radius=4)

    local_close = close_rect.move(-left, -top)
    show_map_rect = layout["show_map_rect"].move(-left, -top)
    abandon_rect = layout["abandon_rect"].move(-left, -top)
    close_hovered = close_rect.collidepoint(*game.mouse_screen_pos)
    show_map_hovered = layout["show_map_rect"].collidepoint(*game.mouse_screen_pos)
    abandon_hovered = layout["abandon_rect"].collidepoint(*game.mouse_screen_pos)
    show_map_enabled = game.can_show_map_for_selected_journal_quest()
    abandon_enabled = game.can_abandon_selected_journal_quest()
    show_map_fill = (48, 66, 90, 220) if show_map_hovered and show_map_enabled else (40, 54, 74, 210) if show_map_enabled else (42, 44, 50, 170)
    show_map_border = (144, 182, 220) if show_map_hovered and show_map_enabled else (118, 156, 194) if show_map_enabled else (90, 98, 102)
    pygame.draw.rect(panel, show_map_fill, show_map_rect, border_radius=8)
    pygame.draw.rect(panel, show_map_border, show_map_rect, 2, border_radius=8)
    show_map_label = game.small_font.render("Show Map", True, (238, 245, 252) if show_map_enabled else (128, 136, 142))
    panel.blit(show_map_label, show_map_label.get_rect(center=show_map_rect.center))
    abandon_fill = (86, 54, 54, 220) if abandon_hovered and abandon_enabled else (70, 44, 44, 208) if abandon_enabled else (42, 44, 50, 170)
    abandon_border = (210, 154, 154) if abandon_hovered and abandon_enabled else (176, 132, 132) if abandon_enabled else (90, 98, 102)
    pygame.draw.rect(panel, abandon_fill, abandon_rect, border_radius=8)
    pygame.draw.rect(panel, abandon_border, abandon_rect, 2, border_radius=8)
    abandon_label = game.small_font.render("Abandon", True, (244, 230, 230) if abandon_enabled else (128, 136, 142))
    panel.blit(abandon_label, abandon_label.get_rect(center=abandon_rect.center))
    close_fill = (72, 54, 58, 220) if close_hovered else (58, 42, 46, 210)
    pygame.draw.rect(panel, close_fill, local_close, border_radius=8)
    pygame.draw.rect(panel, (210, 164, 164) if close_hovered else (176, 132, 132), local_close, 2, border_radius=8)
    close_label = game.small_font.render("Close", True, (240, 224, 224))
    panel.blit(close_label, close_label.get_rect(center=local_close.center))
    game.screen.blit(panel, (left, top))


def render_log_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 214))
    game.screen.blit(overlay, (0, 0))

    layout = game.log_layout()
    left = layout["left"]
    top = layout["top"]
    panel_w = layout["panel_w"]
    panel_h = layout["panel_h"]
    viewport_rect = layout["viewport"]
    close_rect = layout["close_rect"]

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((18, 22, 32, 245))
    pygame.draw.rect(panel, (132, 166, 196, 255), panel.get_rect(), 2, border_radius=14)
    inner_rect = pygame.Rect(10, 10, panel_w - 20, panel_h - 20)
    pygame.draw.rect(panel, (34, 42, 58, 88), inner_rect, 1, border_radius=12)

    title = game.font.render("Recent Messages", True, (236, 244, 252))
    subtitle = game.small_font.render(f"{len(game.message_log)} messages recorded", True, (180, 202, 224))
    panel.blit(title, title.get_rect(centerx=panel_w // 2, y=18))
    panel.blit(subtitle, subtitle.get_rect(centerx=panel_w // 2, y=48))

    viewport = pygame.Surface((viewport_rect.width, viewport_rect.height), pygame.SRCALPHA)
    viewport.fill((20, 26, 38, 168))
    pygame.draw.rect(viewport, (60, 76, 98, 120), viewport.get_rect(), 1, border_radius=10)
    content_height = max(viewport_rect.height, game.log_content_height())
    content = pygame.Surface((viewport_rect.width, content_height), pygame.SRCALPHA)
    content.fill((0, 0, 0, 0))

    y = 12
    if not game.message_log:
        for surface in wrap_text(game.small_font, "Nothing has happened yet.", COLOR_TEXT, viewport_rect.width - 28):
            content.blit(surface, (14, y))
            y += 20
    else:
        for index, entry in enumerate(reversed(game.message_log), start=1):
            wrapped = wrap_text_lines(game.small_font, entry, viewport_rect.width - 48)
            row_height = 16 + len(wrapped) * 18 + 10
            row_rect = pygame.Rect(8, y, viewport_rect.width - 16, row_height)
            fill = (26, 34, 48, 210) if index == 1 else (22, 28, 40, 168)
            border = (142, 176, 208) if index == 1 else (94, 112, 136)
            pygame.draw.rect(content, fill, row_rect, border_radius=10)
            pygame.draw.rect(content, border, row_rect, 1, border_radius=10)
            stamp = game.small_font.render(f"#{len(game.message_log) - index + 1}", True, COLOR_ACCENT if index == 1 else (170, 188, 206))
            content.blit(stamp, (row_rect.left + 10, row_rect.top + 8))
            line_y = row_rect.top + 8
            for line in wrapped:
                content.blit(game.small_font.render(line, True, COLOR_TEXT), (row_rect.left + 50, line_y))
                line_y += 18
            y += row_height + 8

    viewport.blit(content, (0, -game.log_scroll))
    panel.blit(viewport, (viewport_rect.left - left, viewport_rect.top - top))

    max_scroll = game.log_max_scroll()
    if max_scroll > 0:
        track = pygame.Rect(panel_w - 20, viewport_rect.top - top, 6, viewport_rect.height)
        pygame.draw.rect(panel, (42, 52, 70), track, border_radius=4)
        thumb_height = max(28, int(viewport_rect.height * (viewport_rect.height / max(viewport_rect.height, content_height))))
        thumb_y = track.y + int((track.height - thumb_height) * (game.log_scroll / max_scroll))
        thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
        pygame.draw.rect(panel, (130, 168, 206), thumb, border_radius=4)

    local_close = close_rect.move(-left, -top)
    close_hovered = close_rect.collidepoint(*game.mouse_screen_pos)
    close_fill = (72, 54, 58, 220) if close_hovered else (58, 42, 46, 210)
    pygame.draw.rect(panel, close_fill, local_close, border_radius=8)
    pygame.draw.rect(panel, (210, 164, 164) if close_hovered else (176, 132, 132), local_close, 2, border_radius=8)
    close_label = game.small_font.render("Close", True, (240, 224, 224))
    panel.blit(close_label, close_label.get_rect(center=local_close.center))

    hint = game.small_font.render("Scroll to review earlier messages.", True, COLOR_ACCENT)
    panel.blit(hint, (22, panel_h - 38))
    game.screen.blit(panel, (left, top))
