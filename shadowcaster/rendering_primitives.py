import pygame

from .constants import COLOR_TEXT
from .rendering_shapes import (
    draw_tile, draw_marker, draw_health_bar, draw_status_pips,
    terrain_marker_color, draw_terrain_marker, draw_feature_footprint,
)


def wrap_text(font, text, color, width):
    words = text.split()
    if not words:
        return [font.render("", True, color)]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= width:
            current = trial
        else:
            lines.append(font.render(current, True, color))
            current = word
    lines.append(font.render(current, True, color))
    return lines


def draw_section_header(screen, font, label, x, y, width, color):
    text_x = x + 8
    text = font.render(label, True, color)
    screen.blit(text, (text_x, y))
    line_y = y + text.get_height() // 2 + 1
    pygame.draw.line(screen, color, (text_x + text.get_width() + 10, line_y), (x + width, line_y), 2)
    pygame.draw.rect(screen, color, (x + 1, y + 5, 4, 4))


def draw_tabs(screen, font, labels, active_index, left, top, width):
    gap = 10
    tab_width = max(110, (width - gap * max(0, len(labels) - 1)) // max(1, len(labels)))
    for index, label in enumerate(labels):
        tab_left = left + index * (tab_width + gap)
        rect = pygame.Rect(tab_left, top, tab_width, 34)
        active = index == active_index
        pygame.draw.rect(screen, (36, 46, 66) if active else (24, 30, 42), rect, border_radius=10)
        pygame.draw.rect(screen, (255, 222, 134) if active else (110, 145, 185), rect, 2, border_radius=10)
        text = font.render(label, True, (255, 246, 214) if active else COLOR_TEXT)
        screen.blit(text, text.get_rect(center=rect.center))


def draw_scrollbar(surface, x, y, track_h, scroll, content_h, visible_h, width=6):
    if content_h <= visible_h:
        return
    pygame.draw.rect(surface, (28, 35, 52, 140), pygame.Rect(x, y, width, track_h), border_radius=3)
    ratio = visible_h / max(content_h, 1)
    thumb_h = max(20, int(track_h * ratio))
    max_scroll = max(1, content_h - visible_h)
    thumb_y = y + int((track_h - thumb_h) * scroll / max_scroll)
    thumb_y = max(y, min(y + track_h - thumb_h, thumb_y))
    pygame.draw.rect(surface, (90, 115, 158, 220), pygame.Rect(x, thumb_y, width, thumb_h), border_radius=3)


def wrap_text_lines(font, text, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines
