import pygame

from .constants import (
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .rendering_primitives import wrap_text


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

    title = game.font.render("Notice Board", True, (240, 218, 140))
    subtitle = game.small_font.render(game.region_name, True, (180, 160, 110))
    panel.blit(title, title.get_rect(centerx=panel_w // 2, y=18))
    panel.blit(subtitle, subtitle.get_rect(centerx=panel_w // 2, y=50))
    pygame.draw.line(panel, (100, 86, 54, 200), (22, layout["header_bottom"] - top), (panel_w - 22, layout["header_bottom"] - top), 1)

    kind_colors = {
        "delivery": (200, 180, 110),
        "scout": (120, 190, 200),
        "bounty": (210, 120, 100),
    }
    status_labels = {"available": "Available", "active": "In Progress", "complete": "Complete"}
    status_colors = {"available": (160, 210, 150), "active": (220, 190, 100), "complete": (130, 160, 130)}

    quests = game.notice_board_quests
    hovered_index = game.notice_board_hovered_index()
    viewport_rect = layout["viewport_rect"]
    viewport = pygame.Surface((viewport_rect.width, viewport_rect.height), pygame.SRCALPHA)
    viewport.fill((20, 26, 38, 120))
    pygame.draw.rect(viewport, (70, 64, 48, 110), viewport.get_rect(), 1, border_radius=10)
    content_height = max(viewport_rect.height, game.notice_board_content_height())
    content = pygame.Surface((viewport_rect.width, content_height), pygame.SRCALPHA)
    content.fill((0, 0, 0, 0))
    for i, quest in enumerate(quests):
        row_rect = layout["row_rects"][i].move(-viewport_rect.left, -viewport_rect.top)
        ry = row_rect.top
        selected = i == game.notice_board_index
        hovered = i == hovered_index
        state = game.notice_board_quest_state(quest)
        fill = (34, 40, 56, 220) if selected else (30, 35, 48, 190) if hovered else (24, 28, 40, 160)
        border = (180, 154, 90, 220) if selected else (112, 126, 150, 190) if hovered else (60, 56, 44, 140)
        pygame.draw.rect(content, fill, row_rect, border_radius=8)
        pygame.draw.rect(content, border, row_rect, 2 if selected else 1, border_radius=8)

        kcolor = kind_colors.get(quest.kind, COLOR_TEXT)
        klabel = game.board_kind_label(quest)
        k_surf = game.small_font.render(f"[{klabel}]", True, kcolor)
        content.blit(k_surf, (row_rect.left + 14, ry + 10))

        scolor = status_colors.get(state, COLOR_TEXT)
        s_surf = game.small_font.render(status_labels.get(state, state), True, scolor)
        content.blit(s_surf, (row_rect.right - s_surf.get_width() - 14, ry + 10))

        context_color = (168, 194, 220) if selected else (158, 184, 206) if hovered else (144, 166, 190)
        context_y = ry + 32
        for line in game.quest_context_lines(quest, include_return=False):
            context_surf = game.small_font.render(line, True, context_color)
            content.blit(context_surf, (row_rect.left + 14, context_y))
            context_y += 17

        desc_color = (220, 210, 185) if selected else (225, 230, 238) if hovered else COLOR_TEXT
        desc_lines = wrap_text(game.small_font, quest.description, desc_color, row_rect.width - 28)
        for li, dl in enumerate(desc_lines):
            content.blit(dl, (row_rect.left + 14, context_y + li * 18))

        reward_label = game.notice_board_reward_label(quest)
        reward_y = context_y + len(desc_lines) * 18 + 6
        r_surf = game.small_font.render(reward_label, True, (160, 200, 140) if selected else (142, 176, 120) if hovered else (120, 150, 100))
        content.blit(r_surf, (row_rect.left + 14, reward_y))
    viewport.blit(content, (0, -game.notice_board_scroll))
    panel.blit(viewport, (viewport_rect.left - left, viewport_rect.top - top))

    max_scroll = game.notice_board_max_scroll()
    if max_scroll > 0:
        track_x = viewport_rect.right - left + 8
        track = pygame.Rect(track_x, viewport_rect.top - top, 6, viewport_rect.height)
        pygame.draw.rect(panel, (42, 52, 70), track, border_radius=4)
        thumb_height = max(28, int(viewport_rect.height * (viewport_rect.height / max(viewport_rect.height, content_height))))
        thumb_y = track.y + int((track.height - thumb_height) * (game.notice_board_scroll / max_scroll))
        thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
        pygame.draw.rect(panel, (180, 154, 90), thumb, border_radius=4)

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
