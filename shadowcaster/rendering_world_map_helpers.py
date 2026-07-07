import pygame

from .constants import COLOR_BG, COLOR_TEXT
from .rendering_primitives import wrap_text_lines
from .rendering_world_map_icons import (
    draw_world_map_site_marker,
    landmark_state_visual,
    world_map_landmark_icon_specs,
)
from .rendering_world_map_quest_helpers import world_map_active_quests_for_coord


def draw_world_map_chip(screen, font, text, left, top, fill_color, text_color=COLOR_BG):
    label = font.render(text, True, text_color)
    rect = pygame.Rect(left, top, label.get_width() + 18, label.get_height() + 8)
    pygame.draw.rect(screen, fill_color, rect, border_radius=9)
    pygame.draw.rect(screen, COLOR_BG, rect, 1, border_radius=9)
    screen.blit(label, (rect.x + 9, rect.y + 4))
    return rect.width


def draw_world_map_connection(screen, rect, direction, color):
    mid_x = rect.centerx
    mid_y = rect.centery
    if direction == "north":
        pygame.draw.line(screen, color, (mid_x, rect.top + 3), (mid_x, rect.top - 7), 3)
    elif direction == "south":
        pygame.draw.line(screen, color, (mid_x, rect.bottom - 3), (mid_x, rect.bottom + 7), 3)
    elif direction == "west":
        pygame.draw.line(screen, color, (rect.left + 3, mid_y), (rect.left - 7, mid_y), 3)
    elif direction == "east":
        pygame.draw.line(screen, color, (rect.right - 3, mid_y), (rect.right + 7, mid_y), 3)


def draw_world_map_route(screen, start_rect, end_rect, color):
    pygame.draw.line(screen, color, start_rect.center, end_rect.center, 4)
    pygame.draw.line(screen, COLOR_BG, start_rect.center, end_rect.center, 1)


_ARCHETYPE_ICON_TINTS = {
    "frontier_post": (210, 150, 100),
    "trade_hub": (200, 220, 120),
    "learning_seat": (140, 180, 230),
    "social_anchor": (190, 150, 220),
    "survivor": (250, 234, 196),
}


def draw_world_map_settlement_icon(screen, rect, region_type, settlement_rank, outline, archetype=None):
    if not settlement_rank:
        return
    if region_type == "town":
        icon_color = _ARCHETYPE_ICON_TINTS.get(archetype or "survivor", (250, 234, 196))
    else:
        icon_color = (248, 166, 182)
    base_y = rect.bottom - 8
    building_width = max(5, rect.width // 7)
    gap = max(2, rect.width // 16)
    building_heights = {
        1: [rect.width // 5],
        2: [rect.width // 5, rect.width // 4],
        3: [rect.width // 5, rect.width // 4, rect.width // 3],
        4: [rect.width // 5, rect.width // 4, rect.width // 3, rect.width // 2],
    }[settlement_rank]
    total_width = len(building_heights) * building_width + max(0, len(building_heights) - 1) * gap
    start_x = rect.centerx - total_width // 2
    for index, height in enumerate(building_heights):
        left = start_x + index * (building_width + gap)
        building_rect = pygame.Rect(left, base_y - height, building_width, height)
        pygame.draw.rect(screen, icon_color, building_rect, border_radius=2)
        pygame.draw.rect(screen, outline, building_rect, 1, border_radius=2)
    if region_type == "monster_town":
        pygame.draw.line(screen, outline, (rect.centerx - 6, rect.top + 10), (rect.centerx + 6, rect.top + 18), 2)
        pygame.draw.line(screen, outline, (rect.centerx + 6, rect.top + 10), (rect.centerx - 6, rect.top + 18), 2)


def draw_world_map_section(screen, font, title, left, top, width, color):
    label = font.render(title, True, color)
    screen.blit(label, (left, top))
    line_y = top + label.get_height() // 2 + 1
    pygame.draw.line(screen, color, (left + label.get_width() + 10, line_y), (left + width, line_y), 1)
    return top + label.get_height() + 8
