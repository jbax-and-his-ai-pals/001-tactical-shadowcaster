import pygame

from .constants import COLOR_BG, COLOR_TEXT
from .rendering_primitives import wrap_text_lines
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


def landmark_state_visual(landmark):
    if landmark.get("cleared"):
        return (110, 210, 150), "Cleared"
    if landmark.get("entered"):
        return (255, 210, 90), "Open"
    if landmark.get("visited"):
        return (160, 208, 255), "Marked"
    return (144, 154, 170), "Hidden"


def draw_world_map_site_marker(screen, rect, kind, color, slot_index, state_color=None):
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
    elif kind in {"inn", "clinic", "supply", "shrine", "smith", "cartographer", "tavern", "chapel", "stable"}:
        glyph = {"inn": "I", "clinic": "+", "supply": "S", "shrine": "*", "smith": "H", "cartographer": "M", "tavern": "T", "chapel": "C", "stable": "L"}[kind]
        font = pygame.font.SysFont("consolas", max(10, marker_size - 1), bold=True)
        text = font.render(glyph, True, COLOR_BG)
        screen.blit(text, text.get_rect(center=marker_rect.center))
    else:
        pygame.draw.circle(screen, COLOR_BG, marker_rect.center, max(2, marker_size // 4), 1)
    if state_color:
        badge = pygame.Rect(marker_rect.right - 6, marker_rect.bottom - 6, 5, 5)
        pygame.draw.rect(screen, state_color, badge, border_radius=2)
        pygame.draw.rect(screen, COLOR_BG, badge, 1, border_radius=2)


def world_map_landmark_icon_specs(stats):
    if stats["landmark_summaries"]:
        specs = []
        for landmark in stats["landmark_summaries"][:2]:
            state_color, _state_label = landmark_state_visual(landmark)
            specs.append((landmark["kind"], state_color, landmark))
        return specs
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


def draw_world_map_section(screen, font, title, left, top, width, color):
    label = font.render(title, True, color)
    screen.blit(label, (left, top))
    line_y = top + label.get_height() // 2 + 1
    pygame.draw.line(screen, color, (left + label.get_width() + 10, line_y), (left + width, line_y), 1)
    return top + label.get_height() + 8


def _render_world_map_detail(game, detail_frame, focused_coord, region_stats_map, quest_hint_coords):
    stats = region_stats_map.get(focused_coord)
    if not stats:
        return
    inset = detail_frame.inflate(-24, -24)
    header_rect = pygame.Rect(inset.x, inset.y, inset.width, 76)
    is_focused_hint = focused_coord in quest_hint_coords
    if is_focused_hint:
        hint_fill = tuple(int(v * 0.5) for v in stats["palette"].banner_fill)
        pygame.draw.rect(game.screen, hint_fill, header_rect, border_radius=12)
        pygame.draw.rect(game.screen, (180, 148, 80), header_rect, 2, border_radius=12)
        title = game.font.render("Uncharted Territory", True, (200, 178, 120))
        subtitle = game.small_font.render("A lead points here — travel to reveal it", True, (168, 148, 100))
        coord_text = game.small_font.render(f"({stats['coord'][0]}, {stats['coord'][1]})  Distance {stats['distance']}", True, (168, 148, 100))
    else:
        pygame.draw.rect(game.screen, stats["palette"].banner_fill, header_rect, border_radius=12)
        pygame.draw.rect(game.screen, stats["palette"].banner_border, header_rect, 2, border_radius=12)
        title = game.font.render(stats["name"], True, stats["palette"].banner_text)
        subtitle = game.small_font.render(stats["region_label"], True, stats["palette"].banner_text)
        coord_text = game.small_font.render(f"({stats['coord'][0]}, {stats['coord'][1]})  Distance {stats['distance']}", True, stats["palette"].banner_text)
    game.screen.blit(title, (header_rect.x + 14, header_rect.y + 10))
    game.screen.blit(subtitle, (header_rect.x + 14, header_rect.y + 40))
    game.screen.blit(coord_text, (header_rect.right - coord_text.get_width() - 14, header_rect.y + 42))

    chip_band_top = header_rect.bottom + 10
    chip_band_height = 38
    chip_height = game.small_font.get_height() + 8
    chip_x = header_rect.x + 14
    chip_y = chip_band_top + (chip_band_height - chip_height) // 2
    if is_focused_hint:
        chip_x += draw_world_map_chip(game.screen, game.small_font, "Lead", chip_x, chip_y, (180, 148, 80))
        chip_x += 8
    if stats["is_current"]:
        chip_x += draw_world_map_chip(game.screen, game.small_font, "Current", chip_x, chip_y, (255, 230, 126))
        chip_x += 8
    if stats.get("is_preview") and not is_focused_hint:
        chip_x += draw_world_map_chip(game.screen, game.small_font, "Preview", chip_x, chip_y, (164, 218, 255))
        chip_x += 8
    if game.hovered_world_region == stats["coord"]:
        chip_x += draw_world_map_chip(game.screen, game.small_font, "Hover", chip_x, chip_y, (198, 238, 255))
        chip_x += 8
    if not is_focused_hint and stats["max_depth"] > 1:
        chip_x += draw_world_map_chip(game.screen, game.small_font, f"Depth {stats['depth']}/{stats['max_depth']}", chip_x, chip_y, (190, 168, 255))
        chip_x += 8
    if not is_focused_hint:
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
    if is_focused_hint:
        chain_quest = next(
            (q for q in game.active_quests if q.kind == "chain" and q.status == "active" and q.to_world_pos == focused_coord),
            None,
        )
        lead_y = chip_band_top + 38 + 4
        if chain_quest:
            for line in game.quest_context_lines(chain_quest):
                for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                    line_surf = game.small_font.render(wrapped, True, (220, 206, 166))
                    game.screen.blit(line_surf, (inset.x, lead_y))
                    lead_y += 18
            lead_y += 4
            for wrapped in wrap_text_lines(game.small_font, chain_quest.description, inset.width - 4):
                line_surf = game.small_font.render(wrapped, True, (204, 184, 140))
                game.screen.blit(line_surf, (inset.x, lead_y))
                lead_y += 19
            if chain_quest.target_landmark_name:
                lead_y += 6
                hint_line = game.small_font.render(f"Looking for: {chain_quest.target_landmark_name}", True, (255, 210, 116))
                game.screen.blit(hint_line, (inset.x, lead_y))
        return
    detail_content_top = chip_band_top + 38
    if stats.get("expandable_preview"):
        loading = game.small_font.render("Frontier expansion available.", True, COLOR_TEXT)
        hint = game.small_font.render("Click the + tile to generate that region.", True, (204, 218, 234))
        game.screen.blit(loading, (inset.x, detail_content_top + 4))
        game.screen.blit(hint, (inset.x, detail_content_top + 26))
        return
    if stats.get("loading_preview"):
        loading = game.small_font.render("Generating local preview...", True, COLOR_TEXT)
        hint = game.small_font.render("Nearby regions will appear one by one.", True, (204, 218, 234))
        game.screen.blit(loading, (inset.x, detail_content_top + 4))
        game.screen.blit(hint, (inset.x, detail_content_top + 26))
        return
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
        overview_lines.append((f"Standing {stats['attitude_label']} ({stats['attitude_score']})", COLOR_TEXT))
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
    progress_lines.extend(stats.get("site_state_lines", []))
    if stats["landmarks_total"]:
        progress_lines.append(f"Cleared {stats['landmarks_cleared']} / {stats['landmarks_total']} sites.")
    if stats["quests_completed"]:
        progress_lines.append(
            f"Contracts completed {stats['quests_completed']} "
            f"(D {stats['quest_delivery']} / S {stats['quest_scout']} / B {stats['quest_bounty']} / C {stats['quest_chain']})"
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
    section_y = draw_world_map_section(content, game.small_font, "Opportunity", 0, section_y, inset.width, (232, 240, 248))
    text_y = section_y
    for line in stats.get("opportunity_lines", []):
        for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
            surface = game.small_font.render(wrapped, True, (204, 218, 234))
            content.blit(surface, (0, text_y))
            text_y += 19

    section_y = text_y + 8
    if stats["active_quest_lines"]:
        section_y = draw_world_map_section(content, game.small_font, "Active Work", 0, section_y, inset.width, (232, 240, 248))
        text_y = section_y
        active_quests = world_map_active_quests_for_coord(game, focused_coord)
        if active_quests:
            for role, quest in active_quests[:4]:
                role_color = (255, 210, 116) if "Destination" in role or "Grounds" in role else (148, 230, 162)
                role_surface = game.small_font.render(role, True, role_color)
                content.blit(role_surface, (0, text_y))
                text_y += 18
                for line in game.quest_context_lines(quest):
                    for wrapped in wrap_text_lines(game.small_font, line, inset.width - 10):
                        surface = game.small_font.render(wrapped, True, COLOR_TEXT)
                        content.blit(surface, (8, text_y))
                        text_y += 18
                text_y += 4
        else:
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
            state_color, state_label = landmark_state_visual(landmark)
            draw_world_map_site_marker(content, pygame.Rect(0, text_y + 1, 22, 22), landmark["kind"], state_color, 0, state_color)
            draw_world_map_chip(content, game.small_font, state_label, inset.width - 102, text_y - 2, state_color)
            heading = f"{landmark['name']} [{landmark['label']}]"
            for wrapped in wrap_text_lines(game.small_font, heading, inset.width - 128):
                surface = game.small_font.render(wrapped, True, (166, 224, 255))
                content.blit(surface, (28, text_y))
                text_y += 19
            detail_lines = [
                (f"{landmark['status']} - {landmark['detail']}", state_color),
                (landmark["hook"], COLOR_TEXT),
                (landmark["reward_hint"], (220, 196, 110)),
            ]
            if landmark.get("travel_note"):
                detail_lines.append((landmark["travel_note"], (194, 206, 220)))
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
