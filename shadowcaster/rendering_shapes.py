import pygame

from .constants import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BURN,
    COLOR_POISON,
    TILE_SIZE,
)

from .rendering_terrain import terrain_marker_color, draw_terrain_marker, draw_feature_footprint


def draw_tile(screen, screen_x, screen_y, color):
    rect = pygame.Rect(screen_x * TILE_SIZE, screen_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, COLOR_BG, rect, 1)


def draw_marker(screen, screen_x, screen_y, kind, color):
    left = screen_x * TILE_SIZE
    top = screen_y * TILE_SIZE
    center_x = left + TILE_SIZE // 2
    center_y = top + TILE_SIZE // 2
    inset = 5
    if kind == "stairs":
        for offset in (6, 11, 16):
            pygame.draw.line(screen, color, (left + 5, top + offset), (left + TILE_SIZE - 5, top + offset), 2)
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (left + 8, top + 11), 2)
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (left + TILE_SIZE - 8, top + 11), 2)
    elif kind == "stairs_up":
        for offset in (5, 11, 17):
            pygame.draw.line(screen, color, (left + 5, top + offset), (left + TILE_SIZE - 5, top + offset), 2)
        pygame.draw.line(screen, color, (center_x, top + 4), (left + 7, top + 11), 2)
        pygame.draw.line(screen, color, (center_x, top + 4), (left + TILE_SIZE - 7, top + 11), 2)
    elif kind == "portal":
        pygame.draw.circle(screen, color, (center_x, center_y), 7, 2)
        pygame.draw.circle(screen, color, (center_x, center_y), 3, 1)
        pygame.draw.arc(screen, color, (left + 4, top + 4, TILE_SIZE - 8, TILE_SIZE - 8), 0.45, 2.65, 2)
        pygame.draw.arc(screen, color, (left + 6, top + 6, TILE_SIZE - 12, TILE_SIZE - 12), 3.5, 5.8, 2)
    elif kind == "light":
        pygame.draw.circle(screen, color, (center_x, center_y), 6, 2)
        pygame.draw.line(screen, color, (center_x, top + 3), (center_x, top + 7), 2)
    elif kind == "vitality":
        pygame.draw.line(screen, color, (center_x, top + inset), (center_x, top + TILE_SIZE - inset), 3)
        pygame.draw.line(screen, color, (left + inset, center_y), (left + TILE_SIZE - inset, center_y), 3)
    elif kind == "power":
        points = [(center_x, top + 4), (left + TILE_SIZE - 5, center_y), (center_x, top + TILE_SIZE - 4), (left + 5, center_y)]
        pygame.draw.polygon(screen, color, points, 2)
    elif kind == "haste":
        for dx in (-4, 2):
            pygame.draw.line(screen, color, (left + 6 + dx, top + 6), (left + 11 + dx, center_y), 2)
            pygame.draw.line(screen, color, (left + 6 + dx, top + TILE_SIZE - 6), (left + 11 + dx, center_y), 2)
    elif kind == "reach":
        pygame.draw.line(screen, color, (left + 4, center_y), (left + TILE_SIZE - 4, center_y), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 9, center_y - 5), (left + TILE_SIZE - 4, center_y), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 9, center_y + 5), (left + TILE_SIZE - 4, center_y), 2)
    elif kind == "player":
        pygame.draw.rect(screen, color, (left + 5, top + 5, TILE_SIZE - 10, TILE_SIZE - 10), 2, border_radius=4)
        pygame.draw.line(screen, color, (center_x, top + 7), (center_x, top + TILE_SIZE - 7), 2)
    elif kind == "enemy":
        pygame.draw.circle(screen, color, (center_x, center_y + 1), 6, 2)
        pygame.draw.line(screen, color, (left + 8, top + 8), (left + 11, top + 4), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 8, top + 8), (left + TILE_SIZE - 11, top + 4), 2)
        pygame.draw.circle(screen, color, (center_x - 3, center_y), 1)
        pygame.draw.circle(screen, color, (center_x + 3, center_y), 1)
    elif kind == "friend":
        pygame.draw.circle(screen, color, (center_x, center_y), 5, 2)
    elif kind == "animal":
        pygame.draw.circle(screen, color, (center_x, center_y), 4)
        pygame.draw.circle(screen, color, (center_x - 4, center_y - 5), 2)
        pygame.draw.circle(screen, color, (center_x + 4, center_y - 5), 2)
    elif kind == "settler":
        pygame.draw.line(screen, color, (center_x, top + 4), (center_x, top + TILE_SIZE - 5), 2)
        pygame.draw.line(screen, color, (left + 6, center_y), (left + TILE_SIZE - 6, center_y), 2)
    elif kind == "beast":
        points = [(center_x, top + 5), (left + TILE_SIZE - 6, top + TILE_SIZE - 6), (left + 6, top + TILE_SIZE - 6)]
        pygame.draw.polygon(screen, color, points, 2)
        pygame.draw.line(screen, color, (left + 9, top + 10), (left + 6, top + 5), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 9, top + 10), (left + TILE_SIZE - 6, top + 5), 2)
    elif kind == "archer":
        pygame.draw.arc(screen, color, (left + 5, top + 5, TILE_SIZE - 10, TILE_SIZE - 10), -1.1, 1.1, 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 8, top + 5), (left + TILE_SIZE - 8, top + TILE_SIZE - 5), 2)
        pygame.draw.line(screen, color, (left + 7, center_y), (left + TILE_SIZE - 3, center_y), 2)
    elif kind == "shaman":
        pygame.draw.circle(screen, color, (center_x, center_y), 5, 2)
        pygame.draw.line(screen, color, (center_x + 4, top + 5), (center_x + 4, top + TILE_SIZE - 5), 2)
        pygame.draw.circle(screen, color, (center_x + 4, top + 5), 2)
    elif kind == "exit_west":
        pygame.draw.polygon(screen, color, [(left + 5, center_y), (left + TILE_SIZE - 6, top + 5), (left + TILE_SIZE - 6, top + TILE_SIZE - 5)], 2)
    elif kind == "exit_east":
        pygame.draw.polygon(screen, color, [(left + TILE_SIZE - 5, center_y), (left + 6, top + 5), (left + 6, top + TILE_SIZE - 5)], 2)
    elif kind == "exit_north":
        pygame.draw.polygon(screen, color, [(center_x, top + 5), (left + 5, top + TILE_SIZE - 6), (left + TILE_SIZE - 5, top + TILE_SIZE - 6)], 2)
    elif kind == "exit_south":
        pygame.draw.polygon(screen, color, [(center_x, top + TILE_SIZE - 5), (left + 5, top + 6), (left + TILE_SIZE - 5, top + 6)], 2)
    elif kind == "cave":
        pygame.draw.arc(screen, color, (left + 4, top + 6, TILE_SIZE - 8, TILE_SIZE - 8), 3.14, 6.28, 3)
        pygame.draw.line(screen, color, (left + 6, top + TILE_SIZE - 6), (left + TILE_SIZE - 6, top + TILE_SIZE - 6), 2)
    elif kind == "dungeon":
        pygame.draw.rect(screen, color, (left + 5, top + 5, TILE_SIZE - 10, TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (center_x, top + 7), (center_x, top + TILE_SIZE - 7), 2)
        pygame.draw.line(screen, color, (left + 8, center_y), (left + TILE_SIZE - 8, center_y), 2)
    elif kind == "town":
        pygame.draw.rect(screen, color, (left + 6, top + 10, TILE_SIZE - 12, TILE_SIZE - 8), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 4), (left + TILE_SIZE - 4, top + 11), (left + 4, top + 11)], 2)
    elif kind == "inn":
        pygame.draw.rect(screen, color, (left + 6, top + 9, TILE_SIZE - 12, TILE_SIZE - 8), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 4), (left + TILE_SIZE - 5, top + 10), (left + 5, top + 10)], 2)
        pygame.draw.line(screen, color, (left + 9, center_y), (left + TILE_SIZE - 9, center_y), 2)
    elif kind == "clinic":
        pygame.draw.rect(screen, color, (left + 6, top + 7, TILE_SIZE - 12, TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (center_x, top + 9), (center_x, top + TILE_SIZE - 9), 2)
        pygame.draw.line(screen, color, (left + 8, center_y), (left + TILE_SIZE - 8, center_y), 2)
    elif kind == "supply":
        pygame.draw.rect(screen, color, (left + 6, top + 8, TILE_SIZE - 12, TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (left + 9, top + 11), (left + TILE_SIZE - 9, top + 11), 2)
        pygame.draw.line(screen, color, (left + 9, center_y), (left + TILE_SIZE - 9, center_y), 2)
    elif kind == "shrine":
        pygame.draw.polygon(screen, color, [(center_x, top + 4), (left + 7, top + 11), (left + TILE_SIZE - 7, top + 11)], 2)
        pygame.draw.rect(screen, color, (left + 8, top + 12, TILE_SIZE - 16, TILE_SIZE - 8), 2)
        pygame.draw.line(screen, color, (center_x, top + 8), (center_x, top + TILE_SIZE - 8), 2)
    elif kind == "smith":
        pygame.draw.rect(screen, color, (left + 6, top + 9, TILE_SIZE - 12, TILE_SIZE - 8), 2)
        pygame.draw.line(screen, color, (left + 8, top + 10), (left + 12, top + 5), 2)
        pygame.draw.line(screen, color, (left + 12, top + 5), (left + 16, top + 9), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 12, top + 6), (left + TILE_SIZE - 12, top + TILE_SIZE - 6), 2)
    elif kind == "cartographer":
        pygame.draw.rect(screen, color, (left + 5, top + 7, TILE_SIZE - 10, TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (left + 8, top + 10), (left + TILE_SIZE - 8, top + 10), 2)
        pygame.draw.line(screen, color, (center_x, top + 10), (center_x, top + TILE_SIZE - 7), 2)
        pygame.draw.circle(screen, color, (left + 9, top + 8), 2)
    elif kind == "castle":
        pygame.draw.rect(screen, color, (left + 5, top + 7, TILE_SIZE - 10, TILE_SIZE - 8), 2)
        pygame.draw.line(screen, color, (left + 9, top + 4), (left + 9, top + 10), 2)
        pygame.draw.line(screen, color, (center_x, top + 4), (center_x, top + 10), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 9, top + 4), (left + TILE_SIZE - 9, top + 10), 2)
    elif kind == "ruins":
        pygame.draw.line(screen, color, (left + 6, top + TILE_SIZE - 5), (left + 8, top + 6), 2)
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x + 1, top + 8), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 7, top + TILE_SIZE - 5), (left + TILE_SIZE - 9, top + 10), 2)
    elif kind == "cache":
        pygame.draw.rect(screen, color, (left + 6, top + 9, TILE_SIZE - 12, TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (left + 6, top + 13), (left + TILE_SIZE - 6, top + 13), 2)
        pygame.draw.rect(screen, color, (left + 9, top + 7, TILE_SIZE - 18, 3), 2)
    elif kind == "monster_town":
        pygame.draw.rect(screen, color, (left + 6, top + 10, TILE_SIZE - 12, TILE_SIZE - 8), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 3), (left + TILE_SIZE - 5, top + 11), (left + 5, top + 11)], 2)
        pygame.draw.line(screen, color, (left + 8, top + 13), (left + TILE_SIZE - 8, top + TILE_SIZE - 6), 2)
    elif kind == "weapon":
        pygame.draw.line(screen, color, (left + 7, top + TILE_SIZE - 6), (left + TILE_SIZE - 7, top + 6), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 9, top + 8), (left + TILE_SIZE - 6, top + 5), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 10, top + 10), (left + TILE_SIZE - 4, top + 4), 2)
    elif kind == "armor":
        pygame.draw.polygon(
            screen,
            color,
            [(center_x, top + 5), (left + TILE_SIZE - 6, top + 9), (left + TILE_SIZE - 8, top + TILE_SIZE - 6), (left + 8, top + TILE_SIZE - 6), (left + 6, top + 9)],
            2,
        )
        pygame.draw.line(screen, color, (center_x, top + 8), (center_x, top + TILE_SIZE - 8), 1)


def draw_health_bar(screen, screen_x, screen_y, current, maximum, fill_color):
    if maximum <= 1:
        return
    left = screen_x * TILE_SIZE + 3
    top = screen_y * TILE_SIZE + TILE_SIZE - 5
    width = TILE_SIZE - 6
    pygame.draw.rect(screen, COLOR_BG, (left, top, width, 3))
    filled = max(1, int(width * max(0, current) / maximum))
    pygame.draw.rect(screen, fill_color, (left, top, filled, 3))


def draw_status_pips(screen, screen_x, screen_y, statuses):
    if not statuses:
        return
    left = screen_x * TILE_SIZE + 3
    top = screen_y * TILE_SIZE + 3
    for index, status in enumerate(sorted(statuses)[:2]):
        color = COLOR_POISON if status == "poison" else COLOR_BURN if status == "burn" else COLOR_ACCENT
        pygame.draw.circle(screen, color, (left + index * 6 + 2, top + 2), 2)


