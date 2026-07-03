import pygame

from .constants import (
    COLOR_TEXT,
    COLOR_TERRAIN_BOG,
    COLOR_TERRAIN_REEDS,
    COLOR_TERRAIN_CYPRESS,
    COLOR_TERRAIN_CLIFF,
    COLOR_TERRAIN_PINE,
    COLOR_TERRAIN_MESA,
    COLOR_TERRAIN_SCRUB,
    COLOR_TERRAIN_LAVAFIELD,
    COLOR_TERRAIN_OBSIDIAN,
    COLOR_TERRAIN_EMBER,
    COLOR_TERRAIN_HIGHGROUND,
    COLOR_TERRAIN_WELL,
    COLOR_TERRAIN_PATH,
    COLOR_TERRAIN_FLOWERS,
    COLOR_TERRAIN_POND,
    COLOR_TERRAIN_BED,
    COLOR_TERRAIN_CRATE,
    COLOR_TERRAIN_ALTAR,
    COLOR_TERRAIN_FORGE,
    COLOR_TERRAIN_TABLE,
    COLOR_TERRAIN_SHELVES,
    COLOR_TERRAIN_PEW,
    COLOR_TERRAIN_ANVIL,
    COLOR_TERRAIN_FOUNTAIN,
    COLOR_TERRAIN_BRAZIER,
    COLOR_TERRAIN_STALL,
    COLOR_TERRAIN_HITCH,
    COLOR_TERRAIN_NOTICE,
    COLOR_TERRAIN_SHRUB,
    COLOR_TERRAIN_TREE,
    COLOR_TERRAIN_GARDEN,
    COLOR_TERRAIN_DEADBRUSH,
    COLOR_TERRAIN_DUNE,
    COLOR_TERRAIN_FROST,
    COLOR_TERRAIN_WHEAT,
    COLOR_TERRAIN_CROP,
    COLOR_TERRAIN_FALLOW,
    COLOR_TERRAIN_HAYSTACK,
    COLOR_TERRAIN_FENCE,
    COLOR_TERRAIN_MUCK,
    COLOR_TERRAIN_BARREL,
    COLOR_TERRAIN_SIGN,
    VIEW_HEIGHT,
    VIEW_WIDTH,
    TILE_SIZE,
)


def terrain_marker_color(kind):
    return {
        "muck": COLOR_TERRAIN_MUCK,
        "bog": COLOR_TERRAIN_BOG,
        "bog_reeds": COLOR_TERRAIN_REEDS,
        "bog_cypress": COLOR_TERRAIN_CYPRESS,
        "cliff": COLOR_TERRAIN_CLIFF,
        "cliff_pine": COLOR_TERRAIN_PINE,
        "mesa": COLOR_TERRAIN_MESA,
        "mesa_scrub": COLOR_TERRAIN_SCRUB,
        "lavafield": COLOR_TERRAIN_LAVAFIELD,
        "lavafield_obsidian": COLOR_TERRAIN_OBSIDIAN,
        "embers": COLOR_TERRAIN_EMBER,
        "high_ground": COLOR_TERRAIN_HIGHGROUND,
        "well": COLOR_TERRAIN_WELL,
        "path": COLOR_TERRAIN_PATH,
        "flowers": COLOR_TERRAIN_FLOWERS,
        "pond": COLOR_TERRAIN_POND,
        "bed": COLOR_TERRAIN_BED,
        "crate": COLOR_TERRAIN_CRATE,
        "altar": COLOR_TERRAIN_ALTAR,
        "forge": COLOR_TERRAIN_FORGE,
        "table": COLOR_TERRAIN_TABLE,
        "shelves": COLOR_TERRAIN_SHELVES,
        "pew": COLOR_TERRAIN_PEW,
        "anvil": COLOR_TERRAIN_ANVIL,
        "fountain": COLOR_TERRAIN_FOUNTAIN,
        "brazier": COLOR_TERRAIN_BRAZIER,
        "stall": COLOR_TERRAIN_STALL,
        "hitch_post": COLOR_TERRAIN_HITCH,
        "notice_board": COLOR_TERRAIN_NOTICE,
        "shrub": COLOR_TERRAIN_SHRUB,
        "tree": COLOR_TERRAIN_TREE,
        "garden": COLOR_TERRAIN_GARDEN,
        "deadbrush": COLOR_TERRAIN_DEADBRUSH,
        "dune": COLOR_TERRAIN_DUNE,
        "frost": COLOR_TERRAIN_FROST,
        "wheat": COLOR_TERRAIN_WHEAT,
        "crop_row": COLOR_TERRAIN_CROP,
        "fallow": COLOR_TERRAIN_FALLOW,
        "haystack": COLOR_TERRAIN_HAYSTACK,
        "fence": COLOR_TERRAIN_FENCE,
        "barrel": COLOR_TERRAIN_BARREL,
        "sign": COLOR_TERRAIN_SIGN,
    }.get(kind, COLOR_TEXT)


def draw_terrain_marker(screen, screen_x, screen_y, kind, memory=False):
    left = screen_x * TILE_SIZE
    top = screen_y * TILE_SIZE
    center_x = left + TILE_SIZE // 2
    center_y = top + TILE_SIZE // 2
    base = terrain_marker_color(kind)
    color = tuple(max(14, c // 2) for c in base) if memory else base
    if kind == "muck":
        pygame.draw.circle(screen, color, (center_x, center_y + 2), 5, 2)
    elif kind == "bog":
        pygame.draw.arc(screen, color, (left + 4, top + 9, TILE_SIZE - 8, 8), 0.2, 2.9, 2)
        pygame.draw.arc(screen, color, (left + 5, top + 5, TILE_SIZE - 10, 8), 3.4, 6.0, 2)
    elif kind == "bog_reeds":
        pygame.draw.arc(screen, COLOR_TERRAIN_BOG, (left + 4, top + 9, TILE_SIZE - 8, 8), 0.2, 2.9, 2)
        for offset in (0, 4, 8):
            pygame.draw.line(screen, color, (left + 6 + offset, top + TILE_SIZE - 6), (left + 7 + offset, top + 6), 2)
    elif kind == "bog_cypress":
        pygame.draw.arc(screen, COLOR_TERRAIN_BOG, (left + 4, top + 9, TILE_SIZE - 8, 8), 0.2, 2.9, 2)
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x, top + 8), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 5), (center_x + 5, top + 12), (center_x - 5, top + 12)], 2)
    elif kind == "cliff":
        pygame.draw.lines(screen, color, False, [(left + 5, top + 9), (left + 9, top + 5), (left + 13, top + 10), (left + 18, top + 6)], 2)
        pygame.draw.line(screen, color, (left + 7, top + TILE_SIZE - 6), (left + TILE_SIZE - 7, top + TILE_SIZE - 10), 2)
    elif kind == "cliff_pine":
        pygame.draw.lines(screen, COLOR_TERRAIN_CLIFF, False, [(left + 5, top + 9), (left + 9, top + 5), (left + 13, top + 10), (left + 18, top + 6)], 2)
        pygame.draw.line(screen, COLOR_TERRAIN_CLIFF, (left + 7, top + TILE_SIZE - 6), (left + TILE_SIZE - 7, top + TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x, top + 9), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 6), (center_x + 5, top + 13), (center_x - 5, top + 13)], 2)
    elif kind == "mesa":
        pygame.draw.lines(screen, color, False, [(left + 5, top + 8), (left + 10, top + 6), (left + 14, top + 10), (left + 18, top + 7)], 2)
        pygame.draw.line(screen, color, (left + 6, top + TILE_SIZE - 7), (left + TILE_SIZE - 6, top + TILE_SIZE - 9), 2)
    elif kind == "mesa_scrub":
        pygame.draw.lines(screen, COLOR_TERRAIN_MESA, False, [(left + 5, top + 8), (left + 10, top + 6), (left + 14, top + 10), (left + 18, top + 7)], 2)
        pygame.draw.line(screen, COLOR_TERRAIN_MESA, (left + 6, top + TILE_SIZE - 7), (left + TILE_SIZE - 6, top + TILE_SIZE - 9), 2)
        pygame.draw.line(screen, color, (center_x - 3, top + TILE_SIZE - 6), (center_x - 1, top + 9), 2)
        pygame.draw.line(screen, color, (center_x + 2, top + TILE_SIZE - 7), (center_x + 4, top + 11), 2)
    elif kind == "lavafield":
        pygame.draw.arc(screen, color, (left + 4, top + 6, TILE_SIZE - 8, TILE_SIZE - 10), 0.2, 2.9, 2)
        pygame.draw.arc(screen, color, (left + 5, top + 10, TILE_SIZE - 10, TILE_SIZE - 10), 3.5, 5.9, 2)
    elif kind == "lavafield_obsidian":
        pygame.draw.arc(screen, COLOR_TERRAIN_LAVAFIELD, (left + 4, top + 6, TILE_SIZE - 8, TILE_SIZE - 10), 0.2, 2.9, 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 5), (left + TILE_SIZE - 7, center_y), (center_x + 1, top + TILE_SIZE - 5), (left + 7, center_y + 1)], 2)
    elif kind == "embers":
        points = [(center_x, top + 5), (left + TILE_SIZE - 7, center_y), (center_x + 2, top + TILE_SIZE - 5), (left + 7, center_y + 2)]
        pygame.draw.polygon(screen, color, points, 2)
    elif kind == "high_ground":
        pygame.draw.rect(screen, color, (left + 6, top + 6, TILE_SIZE - 12, TILE_SIZE - 12), 2)
    elif kind == "well":
        pygame.draw.circle(screen, color, (center_x, center_y), 5, 2)
        pygame.draw.circle(screen, color, (center_x, center_y), 2)
    elif kind == "path":
        pygame.draw.line(screen, color, (left + 5, center_y), (left + TILE_SIZE - 5, center_y), 2)
    elif kind == "flowers":
        pygame.draw.circle(screen, color, (center_x - 3, center_y), 2)
        pygame.draw.circle(screen, color, (center_x + 3, center_y - 1), 2)
        pygame.draw.circle(screen, color, (center_x, center_y + 3), 2)
    elif kind == "pond":
        pygame.draw.ellipse(screen, color, (left + 4, top + 7, TILE_SIZE - 8, TILE_SIZE - 12), 2)
    elif kind == "bed":
        pygame.draw.rect(screen, color, (left + 5, top + 7, TILE_SIZE - 10, TILE_SIZE - 9), 2)
        pygame.draw.rect(screen, color, (left + 6, top + 8, 5, 4), 1)
    elif kind == "crate":
        pygame.draw.rect(screen, color, (left + 6, top + 6, TILE_SIZE - 12, TILE_SIZE - 12), 2)
        pygame.draw.line(screen, color, (left + 6, top + 6), (left + TILE_SIZE - 6, top + TILE_SIZE - 6), 1)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 6, top + 6), (left + 6, top + TILE_SIZE - 6), 1)
    elif kind == "altar":
        pygame.draw.rect(screen, color, (left + 7, top + 8, TILE_SIZE - 14, TILE_SIZE - 12), 2)
        pygame.draw.line(screen, color, (center_x, top + 5), (center_x, top + TILE_SIZE - 5), 1)
    elif kind == "forge":
        pygame.draw.rect(screen, color, (left + 5, top + 9, TILE_SIZE - 10, TILE_SIZE - 10), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 5), (center_x + 4, top + 11), (center_x - 4, top + 11)], 2)
    elif kind == "table":
        pygame.draw.rect(screen, color, (left + 5, top + 8, TILE_SIZE - 10, 6), 2)
        pygame.draw.line(screen, color, (left + 8, top + 14), (left + 8, top + TILE_SIZE - 5), 1)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 8, top + 14), (left + TILE_SIZE - 8, top + TILE_SIZE - 5), 1)
    elif kind == "shelves":
        pygame.draw.line(screen, color, (left + 5, top + 8), (left + TILE_SIZE - 5, top + 8), 2)
        pygame.draw.line(screen, color, (left + 5, center_y), (left + TILE_SIZE - 5, center_y), 2)
    elif kind == "pew":
        pygame.draw.line(screen, color, (left + 5, center_y), (left + TILE_SIZE - 5, center_y), 2)
        pygame.draw.line(screen, color, (left + 7, center_y - 3), (left + 7, center_y + 3), 1)
    elif kind == "anvil":
        pygame.draw.line(screen, color, (left + 6, top + 10), (left + TILE_SIZE - 6, top + 10), 2)
        pygame.draw.line(screen, color, (center_x, top + 10), (center_x, top + TILE_SIZE - 5), 2)
    elif kind == "fountain":
        pygame.draw.circle(screen, color, (center_x, center_y), 5, 2)
        pygame.draw.circle(screen, color, (center_x, center_y), 2)
        pygame.draw.line(screen, color, (center_x, top + 6), (center_x, center_y - 2), 1)
    elif kind == "brazier":
        pygame.draw.rect(screen, color, (left + 7, top + 12, TILE_SIZE - 14, 5), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 5), (center_x + 4, top + 11), (center_x - 4, top + 11)], 2)
    elif kind == "stall":
        pygame.draw.rect(screen, color, (left + 5, top + 10, TILE_SIZE - 10, TILE_SIZE - 9), 2)
        pygame.draw.line(screen, color, (left + 5, top + 10), (left + TILE_SIZE - 5, top + 10), 2)
        pygame.draw.line(screen, color, (left + 9, top + 6), (left + 9, top + TILE_SIZE - 6), 1)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 9, top + 6), (left + TILE_SIZE - 9, top + TILE_SIZE - 6), 1)
    elif kind == "hitch_post":
        pygame.draw.line(screen, color, (left + 7, center_y + 4), (left + 7, top + 7), 2)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 7, center_y + 4), (left + TILE_SIZE - 7, top + 7), 2)
        pygame.draw.line(screen, color, (left + 7, top + 9), (left + TILE_SIZE - 7, top + 9), 2)
    elif kind == "shrub":
        pygame.draw.arc(screen, color, (left + 5, top + 10, TILE_SIZE - 10, 10), 0.0, 3.14, 2)
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x, top + 14), 1)
    elif kind == "tree":
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x, top + 11), 2)
        pygame.draw.polygon(screen, color, [(center_x, top + 4), (center_x + 7, top + 14), (center_x - 7, top + 14)], 2)
    elif kind == "garden":
        pygame.draw.circle(screen, color, (center_x - 4, center_y - 1), 2)
        pygame.draw.circle(screen, color, (center_x + 3, center_y - 3), 2)
        pygame.draw.circle(screen, color, (center_x, center_y + 3), 2)
        pygame.draw.line(screen, color, (center_x - 4, center_y + 1), (center_x - 4, top + TILE_SIZE - 6), 1)
        pygame.draw.line(screen, color, (center_x + 3, center_y - 1), (center_x + 3, top + TILE_SIZE - 6), 1)
    elif kind == "notice_board":
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x, top + 8), 2)
        pygame.draw.rect(screen, color, (left + 7, top + 7, TILE_SIZE - 14, 8), 2)
    elif kind == "deadbrush":
        pygame.draw.line(screen, color, (center_x, center_y + 4), (center_x, top + TILE_SIZE - 4), 1)
        pygame.draw.line(screen, color, (center_x, center_y + 2), (center_x - 5, top + 8), 1)
        pygame.draw.line(screen, color, (center_x, center_y + 2), (center_x + 5, top + 8), 1)
        pygame.draw.line(screen, color, (center_x - 2, center_y + 4), (center_x - 7, center_y + 1), 1)
        pygame.draw.line(screen, color, (center_x + 2, center_y + 4), (center_x + 7, center_y + 1), 1)
    elif kind == "dune":
        pygame.draw.arc(screen, color, (left + 3, top + 9, TILE_SIZE - 6, 10), 0.0, 3.14, 2)
        pygame.draw.arc(screen, color, (left + 6, top + 13, TILE_SIZE - 12, 7), 0.0, 3.14, 1)
    elif kind == "frost":
        pygame.draw.line(screen, color, (center_x, top + 6), (center_x, top + TILE_SIZE - 6), 1)
        pygame.draw.line(screen, color, (left + 6, center_y), (left + TILE_SIZE - 6, center_y), 1)
        pygame.draw.line(screen, color, (left + 8, top + 8), (left + TILE_SIZE - 8, top + TILE_SIZE - 8), 1)
        pygame.draw.line(screen, color, (left + TILE_SIZE - 8, top + 8), (left + 8, top + TILE_SIZE - 8), 1)
    elif kind == "wheat":
        for ox in (-4, 0, 4):
            pygame.draw.line(screen, color, (center_x + ox, top + TILE_SIZE - 5), (center_x + ox, top + 8), 1)
            pygame.draw.line(screen, color, (center_x + ox, top + 8), (center_x + ox + 3, top + 5), 1)
    elif kind == "crop_row":
        for oy in (-4, 0, 4):
            pygame.draw.line(screen, color, (left + 5, center_y + oy), (left + TILE_SIZE - 5, center_y + oy), 1)
            pygame.draw.circle(screen, color, (center_x, center_y + oy), 2, 1)
    elif kind == "fallow":
        for ox in (-3, 0, 3):
            pygame.draw.line(screen, color, (center_x + ox, top + 6), (center_x + ox, top + TILE_SIZE - 6), 1)
    elif kind == "haystack":
        pygame.draw.ellipse(screen, color, (left + 5, center_y - 2, TILE_SIZE - 10, 10), 2)
        pygame.draw.line(screen, color, (left + 7, center_y + 5), (left + TILE_SIZE - 7, center_y + 5), 1)
    elif kind == "fence":
        pygame.draw.line(screen, color, (left + 4, center_y - 2), (left + TILE_SIZE - 4, center_y - 2), 2)
        pygame.draw.line(screen, color, (left + 4, center_y + 3), (left + TILE_SIZE - 4, center_y + 3), 1)
        for fx in (left + 6, center_x, left + TILE_SIZE - 6):
            pygame.draw.line(screen, color, (fx, top + 7), (fx, top + TILE_SIZE - 7), 1)
    elif kind == "barrel":
        pygame.draw.ellipse(screen, color, (left + 7, top + 6, TILE_SIZE - 14, TILE_SIZE - 10), 2)
        pygame.draw.line(screen, color, (left + 7, center_y - 1), (left + TILE_SIZE - 7, center_y - 1), 1)
        pygame.draw.line(screen, color, (left + 7, center_y + 3), (left + TILE_SIZE - 7, center_y + 3), 1)
    elif kind == "sign":
        pygame.draw.line(screen, color, (center_x, top + TILE_SIZE - 5), (center_x, top + 10), 2)
        pygame.draw.rect(screen, color, (left + 6, top + 6, TILE_SIZE - 12, 9), 1)


def draw_feature_footprint(screen, game, anchor, kind, memory=False):
    tiles = sorted(game.feature_tiles(anchor))
    if kind != "notice_board" or len(tiles) <= 1:
        draw_terrain_marker(screen, anchor[0] - game.camera_x, anchor[1] - game.camera_y, kind, memory=memory)
        return
    local_tiles = [
        (x - game.camera_x, y - game.camera_y)
        for x, y in tiles
        if game.camera_x <= x < game.camera_x + VIEW_WIDTH and game.camera_y <= y < game.camera_y + VIEW_HEIGHT
    ]
    if not local_tiles:
        return
    min_x = min(tile[0] for tile in local_tiles)
    max_x = max(tile[0] for tile in local_tiles)
    min_y = min(tile[1] for tile in local_tiles)
    max_y = max(tile[1] for tile in local_tiles)
    left = min_x * TILE_SIZE
    top = min_y * TILE_SIZE
    width = (max_x - min_x + 1) * TILE_SIZE
    height = (max_y - min_y + 1) * TILE_SIZE
    base = terrain_marker_color(kind)
    color = tuple(max(14, c // 2) for c in base) if memory else base
    board_rect = pygame.Rect(left + 4, top + max(5, height // 5), width - 8, max(10, height // 2 - 2))
    fill = tuple(max(10, component // 4) for component in base) if memory else tuple(min(255, component // 3 + 24) for component in base)
    pygame.draw.rect(screen, fill, board_rect)
    pygame.draw.rect(screen, color, board_rect, 2)
    post_left = left + max(8, width // 4)
    post_right = left + width - max(8, width // 4)
    pygame.draw.line(screen, color, (post_left, board_rect.bottom), (post_left, top + height - 5), 2)
    pygame.draw.line(screen, color, (post_right, board_rect.bottom), (post_right, top + height - 5), 2)
    for line_y in (board_rect.top + 5, board_rect.top + 10, board_rect.top + 15):
        if line_y < board_rect.bottom - 2:
            pygame.draw.line(screen, color, (board_rect.left + 5, line_y), (board_rect.right - 5, line_y), 1)
