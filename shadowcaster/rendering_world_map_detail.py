import pygame

from .constants import COLOR_BG, COLOR_TEXT
from .rendering_primitives import wrap_text_lines
from .rendering_world_map_helpers import draw_world_map_chip, draw_world_map_section
from .rendering_world_map_icons import (
    draw_world_map_site_marker,
    landmark_state_visual,
)
from .rendering_world_map_quest_helpers import world_map_active_quests_for_coord

_SITE_ACTION = {
    "Hidden": "Visit the region to locate this site.",
    "Marked": "Enter the site to begin the encounter.",
    "Open": "Explore fully to claim the reward.",
    "Cleared": "Reward claimed — nothing further required.",
}


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
    if stats.get("hamlet_placeholder"):
        hamlet_y = detail_content_top + 4
        hamlet_line1 = game.small_font.render("Unvisited outpost — travel here to explore it.", True, (200, 218, 190))
        hamlet_line2 = game.small_font.render("This hamlet was established by a nearby town.", True, (160, 178, 156))
        game.screen.blit(hamlet_line1, (inset.x, hamlet_y))
        game.screen.blit(hamlet_line2, (inset.x, hamlet_y + 22))
        return
    if stats.get("waystation_placeholder"):
        ws_y = detail_content_top + 4
        ws_line1 = game.small_font.render("Unvisited waystation — travel here to resupply.", True, (200, 218, 190))
        ws_line2 = game.small_font.render("Established between two connected settlements.", True, (160, 178, 156))
        game.screen.blit(ws_line1, (inset.x, ws_y))
        game.screen.blit(ws_line2, (inset.x, ws_y + 22))
        return
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
        if stats.get("town_archetype_label"):
            overview_lines.append((f"Archetype: {stats['town_archetype_label']}", (214, 186, 120)))
        if stats.get("road_safety_label"):
            road_colors = {"Contested": (200, 80, 60), "Watched": (200, 180, 80), "Safe": (80, 160, 100)}
            overview_lines.append((f"Roads: {stats['road_safety_label']}", road_colors.get(stats["road_safety_label"], COLOR_TEXT)))
        exp = stats.get("expansion")
        if exp is not None:
            if exp["hemmed_in"]:
                overview_lines.append(("Growth: Hemmed in — improving inward", (180, 160, 130)))
            elif exp["satellite_eligible"]:
                dirs = ", ".join(d.title() for d in exp["viable_directions"][:3])
                overview_lines.append((f"Growth: Satellite expansion possible ({dirs})", (148, 230, 162)))
            elif exp["outer_district_eligible"]:
                dirs = ", ".join(d.title() for d in exp["viable_directions"][:3])
                overview_lines.append((f"Growth: Outer district forming ({dirs})", (200, 220, 160)))
            elif exp["viable_directions"]:
                dirs = ", ".join(d.title() for d in exp["viable_directions"][:3])
                overview_lines.append((f"Growth: Open toward {dirs}", (180, 200, 190)))
    bz = stats.get("buffer_zone")
    if bz and bz.get("active"):
        dirs = " & ".join(d.title() for d in bz["hostile_directions"][:2])
        label = bz["strength_label"].title()
        bz_color = {1: (200, 160, 80), 2: (200, 120, 80), 3: (210, 80, 60)}.get(bz["strength"], (180, 130, 90))
        overview_lines.append((f"Buffer zone {label}: {dirs} border", bz_color))
    if stats["parent_biome"]:
        overview_lines.append((f"Parent biome {stats['parent_biome'].title()}", COLOR_TEXT))
    if stats.get("zone_name"):
        overview_lines.append((f"Zone: {stats['zone_name'].title()}", (148, 190, 148)))
    if stats.get("coast_proximity", 0.0) >= 0.75:
        sea_name = getattr(game, "world_coast", {}).get("name", "the sea")
        overview_lines.append((f"Coastal — {sea_name} is near", (110, 160, 210)))
    text_y = section_y
    for line, color in overview_lines:
        for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
            surface = game.small_font.render(wrapped, True, color)
            content.blit(surface, (0, text_y))
            text_y += 19

    service_preview = stats.get("service_preview_lines", [])
    if service_preview:
        text_y += 4
        section_y = draw_world_map_section(content, game.small_font, "Services", 0, text_y, inset.width, (232, 240, 248))
        text_y = section_y
        for line in service_preview:
            for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                col = (220, 196, 110) if "tier" in line.lower() or "complete" in line.lower() else (204, 218, 234)
                surface = game.small_font.render(wrapped, True, col)
                content.blit(surface, (0, text_y))
                text_y += 19

    section_y = text_y + 8
    forecast = stats.get("forecast_lines", [])
    if forecast:
        section_y = draw_world_map_section(content, game.small_font, "Forecast", 0, section_y, inset.width, (232, 240, 248))
        text_y = section_y
        for line in forecast:
            for wrapped in wrap_text_lines(game.small_font, line, inset.width - 4):
                surface = game.small_font.render(wrapped, True, (210, 220, 200))
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
    lm_open = stats.get("landmarks_open", 0)
    lm_marked = stats.get("landmarks_located_only", 0)
    lm_cleared = stats.get("landmarks_cleared", 0)
    lm_hidden = stats.get("landmarks_unvisited", 0)
    lm_parts = []
    if lm_open:
        lm_parts.append(f"{lm_open} open")
    if lm_marked:
        lm_parts.append(f"{lm_marked} marked")
    if lm_hidden:
        lm_parts.append(f"{lm_hidden} hidden")
    if lm_cleared:
        lm_parts.append(f"{lm_cleared} cleared")
    sites_heading = "Notable Sites" + (f" — {', '.join(lm_parts)}" if lm_parts else "")
    section_y = draw_world_map_section(content, game.small_font, sites_heading, 0, section_y, inset.width, (232, 240, 248))
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
            action_hint = _SITE_ACTION.get(state_label, "")
            detail_lines = [
                (action_hint, state_color),
                (landmark["hook"], COLOR_TEXT),
                (landmark["reward_hint"], (220, 196, 110)),
            ]
            if landmark.get("travel_note"):
                detail_lines.append((landmark["travel_note"], (194, 206, 220)))
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
