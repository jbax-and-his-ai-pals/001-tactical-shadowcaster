import pygame

from .constants import (
    COLOR_HIDDEN,
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
    render_log_overlay,
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
    elif active_overlay == "game_over":
        render_game_over_overlay(game)
    if game.menu_mode:
        render_menu_overlay(game)
    pygame.display.flip()
