import math

import pygame

from .constants import COLOR_BG


def landmark_state_visual(landmark):
    if landmark.get("cleared"):
        return (110, 210, 150), "Cleared"
    if landmark.get("entered"):
        return (255, 210, 90), "Open"
    if landmark.get("visited"):
        return (160, 208, 255), "Marked"
    return (144, 154, 170), "Hidden"


def world_map_landmark_icon_specs(stats):
    if stats["landmark_summaries"]:
        specs = []
        for landmark in stats["landmark_summaries"][:2]:
            state_color, _state_label = landmark_state_visual(landmark)
            specs.append((landmark["kind"], state_color, landmark))
        return specs
    return []


def _draw_site_marker_icon(screen, kind, marker_rect, center_x, center_y, marker_size):
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
    elif kind in {"inn", "clinic", "supply", "shrine", "smith", "cartographer", "tavern", "chapel", "stable"}:
        glyph = {"inn": "I", "clinic": "+", "supply": "S", "shrine": "*", "smith": "H",
                 "cartographer": "M", "tavern": "T", "chapel": "C", "stable": "L"}[kind]
        font = pygame.font.SysFont("consolas", max(10, marker_size - 1), bold=True)
        text = font.render(glyph, True, COLOR_BG)
        screen.blit(text, text.get_rect(center=marker_rect.center))
    elif kind == "waystone":
        pygame.draw.line(screen, COLOR_BG, (center_x, marker_rect.y + 2), (center_x, marker_rect.bottom - 2), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x - 3, marker_rect.y + 4), (center_x + 3, marker_rect.y + 4), 1)
    elif kind == "barrow":
        pygame.draw.arc(screen, COLOR_BG, (marker_rect.x + 2, marker_rect.y + 2, marker_rect.width - 4, marker_rect.height - 4), 0, math.pi, 2)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.x + 2, center_y + 1), (marker_rect.right - 2, center_y + 1), 1)
    elif kind == "stone_circle":
        pygame.draw.circle(screen, COLOR_BG, marker_rect.center, max(3, marker_size // 3), 1)
    elif kind == "oasis":
        r = max(2, marker_size // 5)
        pygame.draw.circle(screen, COLOR_BG, (center_x, center_y + 1), r, 1)
        pygame.draw.line(screen, COLOR_BG, (center_x - r - 1, center_y - 2), (center_x + r + 1, center_y - 2), 1)
    elif kind == "hot_spring":
        for dx in (-3, 0, 3):
            pygame.draw.line(screen, COLOR_BG, (center_x + dx, marker_rect.bottom - 2), (center_x + dx, center_y), 1)
    elif kind == "watchtower":
        pygame.draw.rect(screen, COLOR_BG, (center_x - 2, marker_rect.y + 1, 4, marker_rect.height - 2), 1)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.x + 2, marker_rect.y + 3), (marker_rect.right - 2, marker_rect.y + 3), 1)
    elif kind == "grove":
        pygame.draw.polygon(screen, COLOR_BG, [
            (center_x, marker_rect.y + 2),
            (marker_rect.right - 2, marker_rect.bottom - 2),
            (marker_rect.x + 2, marker_rect.bottom - 2),
        ], 1)
    elif kind == "necropolis":
        pygame.draw.line(screen, COLOR_BG, (center_x, marker_rect.y + 2), (center_x, marker_rect.bottom - 2), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x - 3, marker_rect.y + 4), (center_x + 3, marker_rect.y + 4), 1)
        pygame.draw.ellipse(screen, COLOR_BG, (center_x - 2, marker_rect.y + 1, 4, 3), 1)
    elif kind == "geyser":
        pygame.draw.line(screen, COLOR_BG, (center_x, marker_rect.bottom - 2), (center_x, marker_rect.y + 2), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x - 1, marker_rect.bottom - 2), (center_x - 3, marker_rect.y + 3), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x + 1, marker_rect.bottom - 2), (center_x + 3, marker_rect.y + 3), 1)
    elif kind == "standing_stone":
        pygame.draw.rect(screen, COLOR_BG, (center_x - 1, marker_rect.y + 2, 2, marker_rect.height - 4), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x - 2, marker_rect.bottom - 3), (center_x + 2, marker_rect.bottom - 3), 1)
    elif kind == "camp":
        apex = (center_x, marker_rect.y + 2)
        base_l = (marker_rect.x + 2, marker_rect.bottom - 2)
        base_r = (marker_rect.right - 2, marker_rect.bottom - 2)
        pygame.draw.line(screen, COLOR_BG, apex, base_l, 1)
        pygame.draw.line(screen, COLOR_BG, apex, base_r, 1)
        pygame.draw.line(screen, COLOR_BG, base_l, (center_x - 2, marker_rect.bottom - 2), 1)
        pygame.draw.line(screen, COLOR_BG, (center_x + 2, marker_rect.bottom - 2), base_r, 1)
    elif kind == "cache":
        pygame.draw.rect(screen, COLOR_BG, (marker_rect.x + 2, marker_rect.y + 3, marker_rect.width - 4, marker_rect.height - 5), 1)
        pygame.draw.line(screen, COLOR_BG, (marker_rect.x + 2, center_y), (marker_rect.right - 2, center_y), 1)
    else:
        pygame.draw.circle(screen, COLOR_BG, marker_rect.center, max(2, marker_size // 4), 1)


def draw_world_map_site_marker(screen, rect, kind, color, slot_index, state_color=None):
    marker_size = max(10, rect.width // 4)
    left = rect.left + 6 + slot_index * (marker_size + 4)
    top = rect.top + 6
    marker_rect = pygame.Rect(left, top, marker_size, marker_size)
    pygame.draw.rect(screen, (*color, 235), marker_rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BG, marker_rect, 1, border_radius=4)
    _draw_site_marker_icon(screen, kind, marker_rect, marker_rect.centerx, marker_rect.centery, marker_size)
    if state_color:
        badge = pygame.Rect(marker_rect.right - 6, marker_rect.bottom - 6, 5, 5)
        pygame.draw.rect(screen, state_color, badge, border_radius=2)
        pygame.draw.rect(screen, COLOR_BG, badge, 1, border_radius=2)
