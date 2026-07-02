import pygame

from .constants import COLOR_BG


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


def draw_world_map_site_marker(screen, rect, kind, color, slot_index):
    marker_size = max(10, rect.width // 4)
    left = rect.left + 6 + slot_index * (marker_size + 4)
    top = rect.top + 6
    marker_rect = pygame.Rect(left, top, marker_size, marker_size)
    pygame.draw.rect(screen, (*color, 235), marker_rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BG, marker_rect, 1, border_radius=4)
    center_x = marker_rect.centerx
    center_y = marker_rect.centery
    if kind == "cave":
        pygame.draw.arc(screen, COLOR_BG, (marker_rect.x + 1, marker_rect.y + 3, marker_rect.width - 2, marker_rect.height - 3), 3.14, 6.28, 2)
    elif kind == "dungeon":
        pygame.draw.rect(screen, COLOR_BG, marker_rect.inflate(-5, -5), 1)
    elif kind == "town":
        pygame.draw.polygon(screen, COLOR_BG, [(center_x, marker_rect.y + 2), (marker_rect.right - 2, marker_rect.y + 6), (marker_rect.x + 2, marker_rect.y + 6)], 1)
        pygame.draw.rect(screen, COLOR_BG, (marker_rect.x + 3, marker_rect.y + 6, marker_rect.width - 6, marker_rect.height - 8), 1)
    elif kind == "castle":
        pygame.draw.rect(screen, COLOR_BG, (marker_rect.x + 2, marker_rect.y + 4, marker_rect.width - 4, marker_rect.height - 6), 1)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.x + 4, marker_rect.y + 2), (marker_rect.x + 4, marker_rect.y + 6), 1)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.right - 4, marker_rect.y + 2), (marker_rect.right - 4, marker_rect.y + 6), 1)
    elif kind == "ruins":
        pygame.draw.line(screen, COLOR_BG, (marker_rect.x + 3, marker_rect.bottom - 3), (marker_rect.x + 4, marker_rect.y + 3), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x, marker_rect.bottom - 3), (center_x + 1, marker_rect.y + 4), 1)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.right - 4, marker_rect.bottom - 3), (marker_rect.right - 5, marker_rect.y + 5), 1)
    elif kind == "monster_town":
        pygame.draw.line(screen, COLOR_BG, (marker_rect.x + 3, marker_rect.y + 3), (marker_rect.right - 3, marker_rect.bottom - 3), 2)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.right - 3, marker_rect.y + 3), (marker_rect.x + 3, marker_rect.bottom - 3), 2)
    elif kind in {"inn", "clinic", "supply", "shrine", "smith", "cartographer"}:
        glyph = {"inn": "I", "clinic": "+", "supply": "S", "shrine": "*", "smith": "H", "cartographer": "M"}[kind]
        font = pygame.font.SysFont("consolas", max(10, marker_size - 1), bold=True)
        text = font.render(glyph, True, COLOR_BG)
        screen.blit(text, text.get_rect(center=marker_rect.center))
    else:
        pygame.draw.circle(screen, COLOR_BG, marker_rect.center, max(2, marker_size // 4), 1)


def world_map_landmark_icon_specs(stats):
    if stats["landmark_summaries"]:
        return [(landmark["kind"], (landmark["kind"], landmark["name"])) for landmark in stats["landmark_summaries"][:2]]
    return []


def draw_world_map_settlement_icon(screen, rect, region_type, settlement_rank, outline):
    if not settlement_rank:
        return
    icon_color = (250, 234, 196) if region_type == "town" else (248, 166, 182)
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
