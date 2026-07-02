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


def render_notice_board_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 210))
    game.screen.blit(overlay, (0, 0))

    layout = game.notice_board_layout()
    panel_w = layout["panel_w"]
    panel_h = layout["panel_h"]
    left = layout["left"]
    top = layout["top"]

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((18, 22, 32, 245))
    pygame.draw.rect(panel, (180, 154, 90, 255), panel.get_rect(), 2, border_radius=14)
    inner_rect = pygame.Rect(10, 10, panel_w - 20, panel_h - 20)
    pygame.draw.rect(panel, (42, 36, 28, 80), inner_rect, 1, border_radius=12)

    # header
    title = game.font.render("Notice Board", True, (240, 218, 140))
    subtitle = game.small_font.render(game.region_name, True, (180, 160, 110))
    title_y = 18
    subtitle_y = 50
    panel.blit(title, title.get_rect(centerx=panel_w // 2, y=title_y))
    panel.blit(subtitle, subtitle.get_rect(centerx=panel_w // 2, y=subtitle_y))
    pygame.draw.line(panel, (100, 86, 54, 200), (22, layout["header_bottom"] - top), (panel_w - 22, layout["header_bottom"] - top), 1)

    # quest kind labels and colors
    kind_labels = {"delivery": "DELIVERY", "scout": "SCOUTING", "bounty": "BOUNTY"}
    kind_colors = {
        "delivery": (200, 180, 110),
        "scout": (120, 190, 200),
        "bounty": (210, 120, 100),
    }
    status_labels = {"available": "Available", "active": "In Progress", "complete": "Complete"}
    status_colors = {"available": (160, 210, 150), "active": (220, 190, 100), "complete": (130, 160, 130)}

    quests = game.notice_board_quests
    hovered_index = game.notice_board_hovered_index()
    for i, quest in enumerate(quests):
        row_rect = layout["row_rects"][i].move(-left, -top)
        ry = row_rect.top
        selected = i == game.notice_board_index
        hovered = i == hovered_index
        state = game.notice_board_quest_state(quest)
        fill = (34, 40, 56, 220) if selected else (30, 35, 48, 190) if hovered else (24, 28, 40, 160)
        border = (180, 154, 90, 220) if selected else (112, 126, 150, 190) if hovered else (60, 56, 44, 140)
        pygame.draw.rect(panel, fill, row_rect, border_radius=8)
        pygame.draw.rect(panel, border, row_rect, 2 if selected else 1, border_radius=8)

        kcolor = kind_colors.get(quest.kind, COLOR_TEXT)
        klabel = kind_labels.get(quest.kind, quest.kind.upper())
        k_surf = game.small_font.render(f"[{klabel}]", True, kcolor)
        panel.blit(k_surf, (row_rect.left + 14, ry + 10))

        scolor = status_colors.get(state, COLOR_TEXT)
        s_surf = game.small_font.render(status_labels.get(state, state), True, scolor)
        panel.blit(s_surf, (row_rect.right - s_surf.get_width() - 14, ry + 10))

        desc_color = (220, 210, 185) if selected else (225, 230, 238) if hovered else COLOR_TEXT
        desc_lines = wrap_text(game.small_font, quest.description, desc_color, row_rect.width - 28)
        for li, dl in enumerate(desc_lines[:2]):
            panel.blit(dl, (row_rect.left + 14, ry + 34 + li * 18))

        reward_label = f"Reward: {quest.reward_gold}g"
        if quest.kind == "bounty" and state == "active":
            existing = next((q for q in game.active_quests if q.id == quest.id), None)
            if existing:
                kills = game.enemies_defeated - existing.progress_count
                reward_label += f"  —  {min(kills, quest.target_count)}/{quest.target_count} enemies"
        r_surf = game.small_font.render(reward_label, True, (160, 200, 140) if selected else (142, 176, 120) if hovered else (120, 150, 100))
        panel.blit(r_surf, (row_rect.left + 14, row_rect.bottom - 24))

    # footer
    hint_top = layout["hint_top"] - top
    pygame.draw.line(panel, (80, 70, 44, 180), (22, hint_top - 10), (panel_w - 22, hint_top - 10), 1)
    confirm_rect = layout["confirm_rect"].move(-left, -top)
    close_rect = layout["close_rect"].move(-left, -top)
    hovered_kind, _hovered_index_value = game.notice_board_choice_from_screen(*game.mouse_screen_pos)
    confirm_hovered = hovered_kind == "confirm"
    close_hovered = hovered_kind == "close"
    confirm_enabled = game.notice_board_confirm_available()
    confirm_fill = (52, 76, 58, 235) if confirm_enabled else (42, 44, 50, 170)
    if confirm_hovered and confirm_enabled:
        confirm_fill = (62, 92, 70, 235)
    if game.notice_board_index >= 0 and confirm_enabled:
        pygame.draw.rect(panel, confirm_fill, confirm_rect, border_radius=8)
        pygame.draw.rect(panel, (160, 212, 154) if confirm_hovered else (122, 178, 118), confirm_rect, 2, border_radius=8)
    else:
        pygame.draw.rect(panel, confirm_fill, confirm_rect, border_radius=8)
        pygame.draw.rect(panel, (90, 98, 102), confirm_rect, 2, border_radius=8)
    close_fill = (72, 54, 58, 220) if close_hovered else (58, 42, 46, 210)
    pygame.draw.rect(panel, close_fill, close_rect, border_radius=8)
    pygame.draw.rect(panel, (210, 164, 164) if close_hovered else (176, 132, 132), close_rect, 2, border_radius=8)
    confirm_label = game.small_font.render("Accept", True, (238, 245, 236) if confirm_enabled else (128, 136, 142))
    close_label = game.small_font.render("Close", True, (240, 224, 224))
    panel.blit(confirm_label, confirm_label.get_rect(center=confirm_rect.center))
    panel.blit(close_label, close_label.get_rect(center=close_rect.center))

    game.screen.blit(panel, (left, top))


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
    counts = game.quest_summary_counts()
    subtitle = game.small_font.render(
        f"{counts['active']} active  •  {counts['completed']} completed",
        True,
        (180, 202, 224),
    )
    panel.blit(title, title.get_rect(centerx=panel_w // 2, y=16))
    panel.blit(subtitle, subtitle.get_rect(centerx=panel_w // 2, y=48))
    draw_tabs(panel, game.small_font, game.quest_tabs(), game.journal_tab, 22, 18, panel_w - 44)

    viewport = pygame.Surface((viewport_rect.width, viewport_rect.height), pygame.SRCALPHA)
    viewport.fill((20, 26, 38, 168))
    pygame.draw.rect(viewport, (60, 76, 98, 120), viewport.get_rect(), 1, border_radius=10)
    content_height = max(viewport_rect.height, game.journal_content_height() + 12)
    content = pygame.Surface((viewport_rect.width, content_height), pygame.SRCALPHA)
    content.fill((0, 0, 0, 0))

    entries = game.current_journal_entries()
    if not entries:
        empty_lines = ["No quests in this tab yet.", "Visit a town board to pick up new work."]
        y = 16
        for line in empty_lines:
            for surface in wrap_text(game.small_font, line, COLOR_TEXT, viewport_rect.width - 28):
                content.blit(surface, (14, y))
                y += 20
    else:
        y = 12
        content_width = viewport_rect.width - 28
        for quest in entries:
            body_lines = []
            for line in game.journal_entry_lines(quest):
                body_lines.extend(wrap_text_lines(game.small_font, line, content_width - 18))
            row_height = 42 + len(body_lines) * 18 + 14
            row_rect = pygame.Rect(8, y, viewport_rect.width - 16, row_height)
            fill = (26, 34, 48, 210) if quest.status == "active" else (22, 28, 40, 170)
            border = (154, 206, 150) if quest.status == "active" else (108, 126, 148)
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
    close_hovered = close_rect.collidepoint(*game.mouse_screen_pos)
    close_fill = (72, 54, 58, 220) if close_hovered else (58, 42, 46, 210)
    pygame.draw.rect(panel, close_fill, local_close, border_radius=8)
    pygame.draw.rect(panel, (210, 164, 164) if close_hovered else (176, 132, 132), local_close, 2, border_radius=8)
    close_label = game.small_font.render("Close", True, (240, 224, 224))
    panel.blit(close_label, close_label.get_rect(center=local_close.center))

    hint = game.small_font.render("Scroll to review your log of accepted and completed work.", True, COLOR_ACCENT)
    panel.blit(hint, (22, panel_h - 38))
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
    content_height = max(viewport_rect.height, game.log_content_height() + 12)
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
                content.blit(game.small_font.render(line, True, COLOR_TEXT), (row_rect.left + 42, line_y))
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
