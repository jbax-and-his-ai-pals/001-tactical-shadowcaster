import pygame

from .constants import (
    COLOR_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .rendering_primitives import draw_tabs
from .rendering_world_map_helpers import (
    _render_world_map_detail,
    draw_world_map_chip,
    draw_world_map_connection,
    draw_world_map_route,
    draw_world_map_section,
    draw_world_map_site_marker,
    world_map_landmark_icon_specs,
    draw_world_map_settlement_icon,
)



def render_world_map_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 236))
    game.screen.blit(overlay, (0, 0))

    title = game.font.render("World Map", True, (248, 244, 224))
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 82)))

    tabs = ["Discovered", "Local Debug"]
    active_tab = 0 if game.world_map_mode == "discovered" else 1
    draw_tabs(game.screen, game.small_font, tabs, active_tab, SCREEN_WIDTH // 2 - 180, 118, 360)

    quest_hint_coords = {
        q.to_world_pos for q in game.active_quests
        if q.kind == "chain" and q.status == "active"
        and game.region_key(q.to_world_pos) not in game.world_regions
    }

    regions = game.world_map_regions()
    if not regions:
        empty = game.small_font.render("No world regions discovered yet.", True, COLOR_TEXT)
        game.screen.blit(empty, empty.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        return

    layout = game.world_map_layout(regions)
    cell_size = layout["cell_size"]
    content_rect = pygame.Rect(
        layout["map_left"] + layout["map_content_left_pad"],
        layout["map_top"] + layout["map_content_top_pad"],
        layout["map_area_width"] - layout["map_content_left_pad"] - layout["map_content_right_pad"],
        layout["map_area_height"] - layout["map_content_top_pad"] - layout["map_content_bottom_pad"],
    )
    map_frame = pygame.Rect(layout["map_left"], layout["map_top"], layout["map_area_width"], layout["map_area_height"])
    detail_frame = pygame.Rect(layout["detail_left"], layout["detail_top"], layout["detail_width"], layout["detail_height"])
    pygame.draw.rect(game.screen, (18, 24, 36), map_frame, border_radius=16)
    pygame.draw.rect(game.screen, COLOR_PANEL_BORDER, map_frame, 2, border_radius=16)
    pygame.draw.rect(game.screen, (20, 26, 40), detail_frame, border_radius=16)
    pygame.draw.rect(game.screen, COLOR_PANEL_BORDER, detail_frame, 2, border_radius=16)

    draw_world_map_section(game.screen, game.small_font, "Region Grid", map_frame.x + 18, map_frame.y + 16, map_frame.width - 36, (214, 228, 246))
    recenter_rect = game.world_map_recenter_rect()
    recenter_hovered = recenter_rect.collidepoint(*game.mouse_screen_pos)
    recenter_fill = (34, 42, 58, 236) if recenter_hovered else (24, 30, 42, 216)
    recenter_border = (255, 222, 134) if recenter_hovered else (116, 142, 174)
    pygame.draw.rect(game.screen, recenter_fill, recenter_rect, border_radius=10)
    pygame.draw.rect(game.screen, recenter_border, recenter_rect, 2, border_radius=10)
    recenter_label = game.small_font.render("Recenter", True, COLOR_TEXT)
    game.screen.blit(recenter_label, recenter_label.get_rect(center=recenter_rect.center))

    discovered = game.discovered_world_regions()
    focused_coord = game.focused_world_region()
    focused_neighbors = set()
    if focused_coord is not None:
        for delta in game.DIRECTION_VECTORS.values():
            focused_neighbors.add((focused_coord[0] + delta[0], focused_coord[1] + delta[1]))
    region_rects = {}
    visible_coords = []
    for coord, state in regions.items():
        left = int(round(layout["center_pixel_x"] - cell_size / 2 + (coord[0] - layout["center_x"]) * cell_size))
        top = int(round(layout["center_pixel_y"] - cell_size / 2 + (coord[1] - layout["center_y"]) * cell_size))
        rect = pygame.Rect(left, top, cell_size, cell_size)
        if rect.right < content_rect.left or rect.left > content_rect.right or rect.bottom < content_rect.top or rect.top > content_rect.bottom:
            continue
        region_rects[coord] = rect
        visible_coords.append(coord)
    stats_coords = set(visible_coords)
    if focused_coord in regions:
        stats_coords.add(focused_coord)
        for delta in game.DIRECTION_VECTORS.values():
            neighbor = (focused_coord[0] + delta[0], focused_coord[1] + delta[1])
            if neighbor in regions:
                stats_coords.add(neighbor)
    region_stats_map = {coord: game.region_stats(coord, regions_map=regions) for coord in stats_coords}
    map_clip = game.screen.get_clip()
    game.screen.set_clip(content_rect)
    for coord, rect in region_rects.items():
        if focused_coord is None or coord != focused_coord:
            continue
        for direction, delta in game.DIRECTION_VECTORS.items():
            if direction not in regions[coord].get("edge_exits", {}):
                continue
            neighbor = (coord[0] + delta[0], coord[1] + delta[1])
            neighbor_rect = region_rects.get(neighbor)
            if neighbor_rect is None:
                continue
            focused_stats = region_stats_map.get(coord)
            neighbor_stats = region_stats_map.get(neighbor)
            same_theme = focused_stats and neighbor_stats and focused_stats["theme"] == neighbor_stats["theme"]
            route_color = (138, 212, 154) if same_theme else (132, 198, 255) if neighbor in discovered or neighbor == game.world_position else (104, 132, 164)
            draw_world_map_route(game.screen, rect, neighbor_rect, route_color)
    deferred_highlights = []
    preview_coords = [c for c in visible_coords if regions[c].get("expandable_preview") or regions[c].get("loading_preview")]
    real_coords = [c for c in visible_coords if not regions[c].get("expandable_preview") and not regions[c].get("loading_preview")]
    for coord in preview_coords:
        state = regions[coord]
        rect = region_rects[coord]
        is_expandable = state.get("expandable_preview", False)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(game.screen, (8, 10, 16), rect.move(0, 2), border_radius=10)
        if is_expandable:
            pygame.draw.rect(game.screen, (22, 26, 34), rect, border_radius=8)
            pygame.draw.rect(game.screen, (12, 14, 20), inner, border_radius=6)
            pygame.draw.rect(game.screen, (106, 118, 136), rect, 1, border_radius=8)
            preview_rect = rect.inflate(-18, -18)
            pygame.draw.rect(game.screen, (126, 136, 152), preview_rect, 1, border_radius=6)
            preview_label = game.font.render("+", True, (186, 196, 210))
            game.screen.blit(preview_label, preview_label.get_rect(center=rect.center))
        else:
            pygame.draw.rect(game.screen, (26, 30, 38), rect, border_radius=8)
            pygame.draw.rect(game.screen, (14, 16, 24), inner, border_radius=6)
            pygame.draw.rect(game.screen, (106, 118, 136), rect, 1, border_radius=8)
            preview_rect = rect.inflate(-18, -18)
            pygame.draw.rect(game.screen, (210, 220, 236), preview_rect, 1, border_radius=6)
            preview_label = game.small_font.render("...", True, (214, 224, 236))
            game.screen.blit(preview_label, preview_label.get_rect(center=rect.center))
    river_coords = game.world_river_coord_set
    city = getattr(game, "world_city", {})
    city_hub = city.get("hub")
    city_districts = city.get("districts", {})
    for coord in real_coords:
        state = regions[coord]
        rect = region_rects[coord]
        stats_for_cell = region_stats_map.get(coord)
        palette = state["region_palette"]
        is_expandable = state.get("expandable_preview", False)
        is_loading = state.get("loading_preview", False)
        is_generated_preview = bool(stats_for_cell and stats_for_cell.get("preview_generated"))
        is_preview = is_expandable or is_loading
        is_hint = coord in quest_hint_coords
        inner = rect.inflate(-10, -10)
        shadow = rect.move(0, 2)
        pygame.draw.rect(game.screen, (8, 10, 16), shadow, border_radius=10)
        if is_hint:
            dim_wall = tuple(int(v * 0.45) for v in palette.wall)
            dim_floor = tuple(int(v * 0.35) for v in palette.floor)
            pygame.draw.rect(game.screen, dim_wall, rect, border_radius=8)
            pygame.draw.rect(game.screen, dim_floor, inner, border_radius=6)
        else:
            pygame.draw.rect(game.screen, palette.wall, rect, border_radius=8)
            pygame.draw.rect(game.screen, palette.floor, inner, border_radius=6)
        if coord in river_coords and not is_hint:
            rband_h = max(5, inner.height // 4)
            rband = pygame.Rect(inner.x, inner.centery - rband_h // 2, inner.width, rband_h)
            pygame.draw.rect(game.screen, (48, 96, 180), rband, border_radius=3)
        if stats_for_cell and not is_hint:
            theme_band = pygame.Rect(inner.x + 2, inner.y + 2, max(10, inner.width - 4), max(4, rect.height // 10))
            pygame.draw.rect(game.screen, stats_for_cell["theme_color"], theme_band, border_radius=4)
        selected = coord == game.selected_world_region
        hovered = coord == game.hovered_world_region
        is_neighbor = coord in focused_neighbors
        if not is_hint and coord == city_hub:
            pygame.draw.rect(game.screen, (220, 190, 60), rect.inflate(4, 4), 3, border_radius=10)
        elif not is_hint and coord in city_districts:
            pygame.draw.rect(game.screen, (160, 120, 60), rect.inflate(2, 2), 2, border_radius=9)
        border = (255, 232, 126) if coord == game.world_position else (180, 148, 80) if is_hint else palette.banner_border
        pygame.draw.rect(game.screen, border, rect, 3, border_radius=8)
        if state.get("edge_exits") and not is_hint:
            for direction in state["edge_exits"]:
                draw_world_map_connection(game.screen, rect, direction, border)
        if coord == game.world_position:
            marker = pygame.Rect(0, 0, max(10, cell_size // 3), max(10, cell_size // 3))
            marker.center = rect.center
            pygame.draw.rect(game.screen, (255, 244, 148), marker, border_radius=4)
            pygame.draw.rect(game.screen, COLOR_BG, marker, 2, border_radius=4)
        if is_hint:
            badge_size = max(12, cell_size // 4)
            badge_rect = pygame.Rect(rect.right - badge_size - 4, rect.top + 4, badge_size, badge_size)
            pygame.draw.rect(game.screen, (180, 148, 80), badge_rect, border_radius=3)
            pygame.draw.rect(game.screen, COLOR_BG, badge_rect, 1, border_radius=3)
            q_label = game.small_font.render("?", True, COLOR_BG)
            game.screen.blit(q_label, q_label.get_rect(center=badge_rect.center))
        else:
            draw_world_map_settlement_icon(game.screen, rect, state["region_type"], game.settlement_size_rank(state), COLOR_BG)
            danger = max(1, min(5, state.get("danger_tier", 1)))
            for index in range(danger):
                pip_x = rect.left + 8 + index * 7
                pip_y = rect.bottom - 8
                pip_color = (255, 214, 114) if index < 2 else (255, 154, 90) if index < 4 else (255, 96, 96)
                pygame.draw.circle(game.screen, pip_color, (pip_x, pip_y), 2)
            landmark_specs = world_map_landmark_icon_specs(stats_for_cell) if stats_for_cell else []
            if landmark_specs:
                for slot_index, (kind, color, landmark_summary) in enumerate(landmark_specs):
                    draw_world_map_site_marker(game.screen, rect, kind, color, slot_index, color)
            elif state.get("landmarks"):
                for slot_index, landmark in enumerate(state["landmarks"][:2]):
                    draw_world_map_site_marker(game.screen, rect, landmark.kind, landmark.color, slot_index)
            if is_generated_preview:
                survey_rect = pygame.Rect(rect.right - 16, rect.bottom - 16, 10, 10)
                pygame.draw.rect(game.screen, (166, 220, 255), survey_rect, border_radius=3)
                pygame.draw.rect(game.screen, COLOR_BG, survey_rect, 1, border_radius=3)
            if stats_for_cell and stats_for_cell.get("active_quest_targets_here"):
                quest_target_rect = pygame.Rect(rect.right - 16, rect.top + 6, 10, 10)
                pygame.draw.rect(game.screen, (255, 210, 116), quest_target_rect, border_radius=3)
                pygame.draw.rect(game.screen, COLOR_BG, quest_target_rect, 1, border_radius=3)
            if stats_for_cell and stats_for_cell.get("active_quest_turnins_here"):
                turnin_rect = pygame.Rect(rect.right - 16, rect.top + 20, 10, 10)
                pygame.draw.rect(game.screen, (148, 230, 162), turnin_rect, border_radius=3)
                pygame.draw.rect(game.screen, COLOR_BG, turnin_rect, 1, border_radius=3)
        if selected or hovered or is_neighbor:
            deferred_highlights.append((rect, selected, hovered, is_neighbor))
    for rect, selected, hovered, is_neighbor in deferred_highlights:
        if selected:
            pygame.draw.rect(game.screen, (60, 80, 110), rect.inflate(20, 20), 4, border_radius=14)
            pygame.draw.rect(game.screen, (140, 200, 255), rect.inflate(14, 14), 3, border_radius=13)
            pygame.draw.rect(game.screen, (255, 255, 255), rect.inflate(8, 8), 3, border_radius=12)
        elif hovered:
            pygame.draw.rect(game.screen, (168, 230, 255), rect.inflate(6, 6), 1, border_radius=10)
        elif is_neighbor:
            pygame.draw.rect(game.screen, (94, 138, 178), rect.inflate(4, 4), 1, border_radius=10)
    # Zone name labels — dim text centered on each zone anchor tile if visible
    for zone in game.world_zones:
        anchor_rect = region_rects.get(zone["center"])
        if anchor_rect is None:
            continue
        r, g, b = zone["color"]
        label_surf = game.small_font.render(zone["name"], True, (r // 2, g // 2, b // 2))
        label_rect = label_surf.get_rect(center=(anchor_rect.centerx, anchor_rect.bottom + 10))
        if content_rect.colliderect(label_rect):
            game.screen.blit(label_surf, label_rect)
    # City hub label — gold text above hub tile
    if city_hub:
        hub_rect = region_rects.get(city_hub)
        if hub_rect and content_rect.colliderect(hub_rect):
            city_label = game.small_font.render(city.get("name", ""), True, (200, 170, 60))
            city_label_rect = city_label.get_rect(center=(hub_rect.centerx, hub_rect.top - 8))
            if content_rect.colliderect(city_label_rect):
                game.screen.blit(city_label, city_label_rect)
    game.screen.set_clip(map_clip)
    _render_world_map_detail(game, detail_frame, focused_coord, region_stats_map, quest_hint_coords)

    help_text = game.small_font.render("Hover or click regions. WASD or arrows pan. Wheel scrolls panel; over map it pans. R or Home recenters. Tab switches mode.", True, (204, 218, 234))
    game.screen.blit(help_text, help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 34)))

