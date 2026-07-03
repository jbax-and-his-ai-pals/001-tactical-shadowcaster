import pygame

from .constants import (
    COLOR_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .rendering_primitives import draw_tabs, wrap_text_lines
from .rendering_world_map_helpers import (
    draw_world_map_chip,
    draw_world_map_connection,
    draw_world_map_route,
    draw_world_map_site_marker,
    world_map_landmark_icon_specs,
    draw_world_map_settlement_icon,
)


def draw_world_map_section(screen, font, title, left, top, width, color):
    label = font.render(title, True, color)
    screen.blit(label, (left, top))
    line_y = top + label.get_height() // 2 + 1
    pygame.draw.line(screen, color, (left + label.get_width() + 10, line_y), (left + width, line_y), 1)
    return top + label.get_height() + 8


def render_world_map_overlay(game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 236))
    game.screen.blit(overlay, (0, 0))

    title = game.font.render("World Map", True, (248, 244, 224))
    game.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 82)))

    tabs = ["Discovered", "Local Debug"]
    active_tab = 0 if game.world_map_mode == "discovered" else 1
    draw_tabs(game.screen, game.small_font, tabs, active_tab, SCREEN_WIDTH // 2 - 180, 118, 360)

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
    region_stats_map = {coord: game.region_stats(coord) for coord in stats_coords}
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
    for coord in visible_coords:
        state = regions[coord]
        rect = region_rects[coord]
        stats_for_cell = region_stats_map.get(coord)
        palette = state["region_palette"]
        is_expandable = state.get("expandable_preview", False)
        is_loading = state.get("loading_preview", False)
        is_generated_preview = bool(stats_for_cell and stats_for_cell.get("preview_generated"))
        is_preview = is_expandable or is_loading
        inner = rect.inflate(-10, -10)
        shadow = rect.move(0, 2)
        pygame.draw.rect(game.screen, (8, 10, 16), shadow, border_radius=10)
        if is_expandable:
            pygame.draw.rect(game.screen, (22, 26, 34), rect, border_radius=8)
            pygame.draw.rect(game.screen, (12, 14, 20), inner, border_radius=6)
        elif is_loading:
            pygame.draw.rect(game.screen, (26, 30, 38), rect, border_radius=8)
            pygame.draw.rect(game.screen, (14, 16, 24), inner, border_radius=6)
        else:
            pygame.draw.rect(game.screen, palette.wall, rect, border_radius=8)
            pygame.draw.rect(game.screen, palette.floor, inner, border_radius=6)
        if stats_for_cell and not is_preview:
            theme_band = pygame.Rect(inner.x + 2, inner.y + 2, max(10, inner.width - 4), max(4, rect.height // 10))
            pygame.draw.rect(game.screen, stats_for_cell["theme_color"], theme_band, border_radius=4)
        selected = coord == game.selected_world_region
        hovered = coord == game.hovered_world_region
        is_neighbor = coord in focused_neighbors
        if is_expandable:
            border = (106, 118, 136)
            border_width = 1
        else:
            border = (255, 232, 126) if coord == game.world_position else (210, 240, 255) if selected else (158, 216, 255) if hovered else palette.banner_border
            border_width = 3
        pygame.draw.rect(game.screen, border, rect, border_width, border_radius=8)
        if state.get("edge_exits"):
            for direction in state["edge_exits"]:
                draw_world_map_connection(game.screen, rect, direction, border)
        if is_expandable or is_loading:
            preview_rect = rect.inflate(-18, -18)
            preview_border = (126, 136, 152) if is_expandable else (210, 220, 236)
            pygame.draw.rect(game.screen, preview_border, preview_rect, 1, border_radius=6)
        if coord == game.world_position:
            marker = pygame.Rect(0, 0, max(10, cell_size // 3), max(10, cell_size // 3))
            marker.center = rect.center
            pygame.draw.rect(game.screen, (255, 244, 148), marker, border_radius=4)
            pygame.draw.rect(game.screen, COLOR_BG, marker, 2, border_radius=4)
        if not is_preview:
            draw_world_map_settlement_icon(game.screen, rect, state["region_type"], game.settlement_size_rank(state), COLOR_BG)
            danger = max(1, min(5, state.get("danger_tier", 1)))
            for index in range(danger):
                pip_x = rect.left + 8 + index * 7
                pip_y = rect.bottom - 8
                pip_color = (255, 214, 114) if index < 2 else (255, 154, 90) if index < 4 else (255, 96, 96)
                pygame.draw.circle(game.screen, pip_color, (pip_x, pip_y), 2)
            if state.get("landmarks"):
                landmark_specs = [(landmark.kind, landmark.color) for landmark in state["landmarks"][:2]]
                for slot_index, (kind, color) in enumerate(landmark_specs):
                    draw_world_map_site_marker(game.screen, rect, kind, color, slot_index)
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
        if selected:
            glow = rect.inflate(10, 10)
            pygame.draw.rect(game.screen, (164, 222, 255), glow, 1, border_radius=12)
        elif hovered and not is_expandable:
            glow = rect.inflate(6, 6)
            pygame.draw.rect(game.screen, (168, 230, 255), glow, 1, border_radius=10)
        elif is_neighbor:
            glow = rect.inflate(4, 4)
            pygame.draw.rect(game.screen, (94, 138, 178), glow, 1, border_radius=10)
        if is_expandable:
            preview_label = game.font.render("+", True, (186, 196, 210))
            game.screen.blit(preview_label, preview_label.get_rect(center=rect.center))
        elif is_loading:
            preview_label = game.small_font.render("...", True, (214, 224, 236))
            game.screen.blit(preview_label, preview_label.get_rect(center=rect.center))
    game.screen.set_clip(map_clip)

    stats = region_stats_map.get(focused_coord)
    if stats:
        inset = detail_frame.inflate(-24, -24)
        header_rect = pygame.Rect(inset.x, inset.y, inset.width, 76)
        pygame.draw.rect(game.screen, stats["palette"].banner_fill, header_rect, border_radius=12)
        pygame.draw.rect(game.screen, stats["palette"].banner_border, header_rect, 2, border_radius=12)
        title = game.font.render(stats["name"], True, stats["palette"].banner_text)
        subtitle = game.small_font.render(stats["region_label"], True, stats["palette"].banner_text)
        coord_text = game.small_font.render(f"({stats['coord'][0]}, {stats['coord'][1]})  Distance {stats['distance']}", True, stats["palette"].banner_text)
        game.screen.blit(title, (header_rect.x + 14, header_rect.y + 10))
        game.screen.blit(subtitle, (header_rect.x + 14, header_rect.y + 40))
        game.screen.blit(coord_text, (header_rect.right - coord_text.get_width() - 14, header_rect.y + 42))

        chip_x = header_rect.x + 14
        chip_y = header_rect.bottom + 10
        if stats["is_current"]:
            chip_x += draw_world_map_chip(game.screen, game.small_font, "Current", chip_x, chip_y, (255, 230, 126))
            chip_x += 8
        if stats.get("is_preview"):
            chip_x += draw_world_map_chip(game.screen, game.small_font, "Preview", chip_x, chip_y, (164, 218, 255))
            chip_x += 8
        if game.hovered_world_region == stats["coord"]:
            chip_x += draw_world_map_chip(game.screen, game.small_font, "Hover", chip_x, chip_y, (198, 238, 255))
            chip_x += 8
        if stats["max_depth"] > 1:
            chip_x += draw_world_map_chip(game.screen, game.small_font, f"Depth {stats['depth']}/{stats['max_depth']}", chip_x, chip_y, (190, 168, 255))
            chip_x += 8
        chip_x += draw_world_map_chip(game.screen, game.small_font, f"Danger {stats['danger_tier']}", chip_x, chip_y, (255, 154, 90))
        if stats.get("landmarks_open"):
            chip_x += 8
            chip_x += draw_world_map_chip(game.screen, game.small_font, f"Sites Open {stats['landmarks_open']}", chip_x, chip_y, (255, 210, 116))
        elif stats.get("landmarks_cleared") and stats.get("landmarks_total") and stats["landmarks_cleared"] == stats["landmarks_total"]:
            chip_x += 8
            chip_x += draw_world_map_chip(game.screen, game.small_font, "Sites Cleared", chip_x, chip_y, (148, 230, 162))
        if stats.get("active_quest_targets_here"):
            chip_x += 8
            chip_x += draw_world_map_chip(game.screen, game.small_font, "Quest Target", chip_x, chip_y, (255, 210, 116))
        if stats.get("active_quest_turnins_here"):
            chip_x += 8
            chip_x += draw_world_map_chip(game.screen, game.small_font, "Turn-In", chip_x, chip_y, (148, 230, 162))
        if stats.get("expandable_preview"):
            loading = game.small_font.render("Frontier expansion available.", True, COLOR_TEXT)
            hint = game.small_font.render("Click the + tile to generate that region.", True, (204, 218, 234))
            game.screen.blit(loading, (inset.x, chip_y + 42))
            game.screen.blit(hint, (inset.x, chip_y + 64))
            return
        if stats.get("loading_preview"):
            loading = game.small_font.render("Generating local preview...", True, COLOR_TEXT)
            hint = game.small_font.render("Nearby regions will appear one by one.", True, (204, 218, 234))
            game.screen.blit(loading, (inset.x, chip_y + 42))
            game.screen.blit(hint, (inset.x, chip_y + 64))
            return
        detail_content_top = chip_y + 38
        viewport_height = detail_frame.height - (detail_content_top - detail_frame.y) - 16
        viewport_rect = pygame.Rect(inset.x, detail_content_top, inset.width, viewport_height)
        viewport = pygame.Surface((viewport_rect.width, viewport_rect.height), pygame.SRCALPHA)
        viewport.fill((0, 0, 0, 0))
        content = pygame.Surface((viewport_rect.width, 1800), pygame.SRCALPHA)
        content.fill((0, 0, 0, 0))

        section_y = 0
        section_y = draw_world_map_section(content, game.small_font, "Overview", 0, section_y, inset.width, (232, 240, 248))
        outlook = stats["site_outlook"]
        outlook_color = (
            (110, 210, 150) if "resolved" in outlook or "No notable" in outlook
            else (255, 210, 90) if "Open site" in outlook or "not yet entered" in outlook
            else COLOR_TEXT
        )
        overview_lines = [
            (f"Exploration {stats['exploration']}%", COLOR_TEXT),
            (f"Foes {stats['foes_remaining']} remaining, {stats['foes_defeated']} defeated", COLOR_TEXT),
            (f"Residents seen {stats['residents']}", COLOR_TEXT),
            (f"Links {stats['exits_found']} ({', '.join(direction.title() for direction in stats['exit_directions']) if stats['exit_directions'] else 'none marked'})", COLOR_TEXT),
            (f"Sites located {stats['landmarks_visited']} / {stats['landmarks_total']}", COLOR_TEXT),
            (outlook, outlook_color),
            (f"Theme {stats['theme'].title()}", COLOR_TEXT),
        ]
        if stats["settlement_size"]:
            overview_lines.append((f"Settlement {stats['settlement_size']} with {stats['settlement_buildings']} structures", COLOR_TEXT))
            overview_lines.append((f"Prosperity {stats['prosperity_label']} ({stats['prosperity_score']})", COLOR_TEXT))
        if stats["parent_biome"]:
            overview_lines.append((f"Parent biome {stats['parent_biome'].title()}", COLOR_TEXT))
        text_y = section_y
        for line, color in overview_lines:
            for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                surface = game.small_font.render(wrapped, True, color)
                content.blit(surface, (0, text_y))
                text_y += 19

        section_y = text_y + 8
        section_y = draw_world_map_section(content, game.small_font, "Progress", 0, section_y, inset.width, (232, 240, 248))
        progress_lines = []
        if stats["landmarks_total"]:
            progress_lines.append(
                f"Site states: hidden {stats['landmarks_unvisited']} / marked {stats['landmarks_located_only']} / open {stats['landmarks_open']} / cleared {stats['landmarks_cleared']}"
            )
            progress_lines.append(f"Sites entered {stats['landmarks_entered']} / {stats['landmarks_total']}")
            progress_lines.append(f"Sites cleared {stats['landmarks_cleared']} / {stats['landmarks_total']}")
            if stats["landmark_type_counts"]:
                progress_lines.append("Site mix: " + ", ".join(stats["landmark_type_counts"][:4]))
        else:
            progress_lines.append("No major sites marked here yet.")
        if stats["quests_completed"]:
            progress_lines.append(
                f"Contracts completed {stats['quests_completed']} "
                f"(D {stats['quest_delivery']} / S {stats['quest_scout']} / B {stats['quest_bounty']})"
            )
        if stats["full_clear_reward_claimed"]:
            progress_lines.append("Full-clear reward claimed")
        if stats["bottom_reward_claimed"] and stats["max_depth"] > 1:
            progress_lines.append("Bottom-floor cache claimed")
        if not progress_lines:
            progress_lines.append("No tracked progress yet.")
        text_y = section_y
        for line in progress_lines:
            for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                surface = game.small_font.render(wrapped, True, COLOR_TEXT)
                content.blit(surface, (0, text_y))
                text_y += 19

        section_y = text_y + 8
        if stats["active_quest_lines"]:
            section_y = draw_world_map_section(content, game.small_font, "Active Work", 0, section_y, inset.width, (232, 240, 248))
            text_y = section_y
            for line in stats["active_quest_lines"]:
                for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                    surface = game.small_font.render(wrapped, True, COLOR_TEXT)
                    content.blit(surface, (0, text_y))
                    text_y += 19
            section_y = text_y + 8

        section_y = draw_world_map_section(content, game.small_font, "Continuity", 0, section_y, inset.width, (232, 240, 248))
        text_y = section_y
        for wrapped in wrap_text_lines(game.small_font, stats["continuity_text"], inset.width - 4):
            surface = game.small_font.render(wrapped, True, COLOR_TEXT)
            content.blit(surface, (0, text_y))
            text_y += 19

        section_y = text_y + 8
        section_y = draw_world_map_section(content, game.small_font, "Notable Sites", 0, section_y, inset.width, (232, 240, 248))
        text_y = section_y
        if stats["landmark_summaries"]:
            for landmark in stats["landmark_summaries"]:
                heading = f"{landmark['name']} [{landmark['label']}]"
                for wrapped in wrap_text_lines(game.small_font, heading, inset.width - 4):
                    surface = game.small_font.render(wrapped, True, (166, 224, 255))
                    content.blit(surface, (0, text_y))
                    text_y += 19
                status_color = (
                    (110, 210, 150) if landmark["cleared"]
                    else (255, 210, 90) if landmark["entered"]
                    else COLOR_TEXT
                )
                detail_lines = [
                    (f"{landmark['status']} — {landmark['detail']}", status_color),
                    (landmark["hook"], COLOR_TEXT),
                    (landmark["reward_hint"], (220, 196, 110)),
                ]
                if landmark.get("biome_flavor"):
                    detail_lines.append((landmark["biome_flavor"], (168, 182, 196)))
                for line, color in detail_lines:
                    for wrapped in wrap_text_lines(game.small_font, line, inset.width - 10):
                        surface = game.small_font.render(wrapped, True, color)
                        content.blit(surface, (8, text_y))
                        text_y += 18
                text_y += 4
        else:
            empty = game.small_font.render("No notable sites recorded.", True, COLOR_TEXT)
            content.blit(empty, (0, text_y))
            text_y += 19

        section_y = text_y + 8
        section_y = draw_world_map_section(content, game.small_font, "Neighbors", 0, section_y, inset.width, (232, 240, 248))
        text_y = section_y
        for neighbor in stats["neighbor_summaries"]:
            label = neighbor["label"] if neighbor["name"] is None else f"{neighbor['name']} [{neighbor['label']}]"
            if neighbor["danger_tier"] is not None:
                label += f"  D{neighbor['danger_tier']}"
            if neighbor["is_preview"]:
                label += "  Preview"
            line = f"{neighbor['direction'].title()}: {label}"
            for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                surface = game.small_font.render(wrapped, True, COLOR_TEXT if neighbor["name"] else (152, 164, 182))
                content.blit(surface, (0, text_y))
                text_y += 18
        content_height = text_y + 8
        game.scroll_world_map_details(0, content_height)
        viewport.blit(content, (0, -game.world_map_detail_scroll))
        game.screen.blit(viewport, viewport_rect.topleft)
        if content_height > viewport_rect.height + 8:
            track = pygame.Rect(detail_frame.right - 14, viewport_rect.y, 6, viewport_rect.height)
            pygame.draw.rect(game.screen, (42, 52, 70), track, border_radius=4)
            thumb_height = max(28, int(viewport_rect.height * (viewport_rect.height / max(viewport_rect.height, content_height))))
            max_scroll = max(1, content_height - viewport_rect.height)
            thumb_y = track.y + int((track.height - thumb_height) * (game.world_map_detail_scroll / max_scroll))
            thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
            pygame.draw.rect(game.screen, (130, 168, 206), thumb, border_radius=4)

    help_text = game.small_font.render("Hover or click regions. WASD or arrows pan. Wheel scrolls panel; over map it pans. R or Home recenters. Tab switches mode.", True, (204, 218, 234))
    game.screen.blit(help_text, help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 34)))
