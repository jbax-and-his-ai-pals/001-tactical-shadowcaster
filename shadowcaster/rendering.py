import pygame

from .constants import (
    COLOR_BG,
    COLOR_HIDDEN,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VIEW_HEIGHT,
    VIEW_WIDTH,
    TILE_SIZE,
)
from .rendering_primitives import (
    draw_tile, draw_marker, draw_health_bar, draw_status_pips,
    terrain_marker_color, draw_terrain_marker, draw_feature_footprint,
    wrap_text, wrap_text_lines, draw_section_header, draw_tabs,
)
from .rendering_viewport import render_viewport, render_side_panel
from .rendering_world_map import render_world_map_overlay
from .rendering_overlays import (
    render_completion_modal, render_reward_choice_overlay, render_tuner_overlay,
    render_inventory_overlay, render_game_over_overlay, render_travel_overlay,
    render_menu_overlay, render_notice_board_overlay, render_journal_overlay,
    render_log_overlay, render_service_modal,
)


def render_region_banner(game):
    label = f"{game.region_name}  [{game.region_subtitle_text()}]"
    text = game.small_font.render(label, True, game.region_palette.banner_text)
    padding_x = 16
    padding_y = 8
    box_width = text.get_width() + padding_x * 2
    box_height = text.get_height() + padding_y * 2
    x = (SCREEN_WIDTH - box_width) // 2
    y = 10

    surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    surface.fill((*game.region_palette.banner_fill, 210))
    pygame.draw.rect(surface, (*game.region_palette.banner_border, 240), surface.get_rect(), 2, border_radius=10)
    surface.blit(text, (padding_x, padding_y))
    game.screen.blit(surface, (x, y))


def render_game(game):
    screen = game.screen
    screen.fill(COLOR_HIDDEN)
    map_pixel_width = VIEW_WIDTH * TILE_SIZE
    start_x = game.camera_x
    end_x = min(game.dungeon.width, game.camera_x + VIEW_WIDTH)
    start_y = game.camera_y
    end_y = min(game.dungeon.height, game.camera_y + VIEW_HEIGHT)
    render_viewport(screen, game, start_x, end_x, start_y, end_y)
    render_side_panel(screen, game, map_pixel_width)
    game.attack_flash = None
    game.shot_flash = []
    render_completion_modal(game)
    active_overlay = game.active_non_menu_overlay()
    if active_overlay == "travel":
        render_travel_overlay(game)
    elif active_overlay == "world_map":
        render_world_map_overlay(game)
    elif active_overlay == "tuner":
        render_tuner_overlay(game)
    elif active_overlay == "inventory":
        render_inventory_overlay(game)
    elif active_overlay == "journal":
        render_journal_overlay(game)
    elif active_overlay == "log":
        render_log_overlay(game)
    elif active_overlay == "choice":
        render_reward_choice_overlay(game)
    elif active_overlay == "notice_board":
        render_notice_board_overlay(game)
    elif active_overlay == "service_modal":
        render_service_modal(game)
    elif active_overlay == "game_over":
        render_game_over_overlay(game)
    if game.menu_mode:
        render_menu_overlay(game)
    if game.perf_overlay:
        render_perf_overlay(game)
    pygame.display.flip()


def render_perf_overlay(game):
    t = game.perf_timings
    fps = t.get("fps", 0.0)
    work = t.get("work_ms", 0.0)
    logic = t.get("logic_ms", 0.0)
    render = t.get("render_ms", 0.0)
    fov = t.get("fov_ms", 0.0)
    npc = t.get("npc_ms", 0.0)
    n_npcs = len(getattr(game, "residents", []))
    n_enemies = len(getattr(game, "enemies", []))
    n_visible = len(getattr(game, "visible_tiles", set()))
    n_seen = len(getattr(game, "seen_tiles", set()))
    dungeon = getattr(game, "dungeon", None)
    region_size = f"{dungeon.width}x{dungeon.height}" if dungeon else "?"

    rows = [
        f"F9: perf on    FPS {fps:5.1f}    work {work:5.1f}ms  (logic {logic:4.1f}ms  render {render:4.1f}ms)",
        f"fov {fov:4.1f}ms   npc {npc:4.1f}ms   npcs {n_npcs}  enemies {n_enemies}",
        f"visible {n_visible}  seen {n_seen}  region {region_size}",
    ]

    font = game.tiny_font
    line_h = font.get_height() + 2
    pad = 6
    box_w = max(font.size(r)[0] for r in rows) + pad * 2
    box_h = len(rows) * line_h + pad * 2
    box_x = 4
    box_y = SCREEN_HEIGHT - box_h - 4

    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    pygame.draw.rect(surf, (*COLOR_TEXT, 80), surf.get_rect(), 1)
    for i, row in enumerate(rows):
        label = font.render(row, True, COLOR_TEXT)
        surf.blit(label, (pad, pad + i * line_h))
    game.screen.blit(surf, (box_x, box_y))
