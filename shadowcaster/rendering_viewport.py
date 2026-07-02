import pygame

from .constants import (
    COLOR_ACCENT,
    COLOR_ATTACK,
    COLOR_BG,
    COLOR_FRIEND,
    COLOR_HIDDEN,
    COLOR_MEMORY_HEAL,
    COLOR_MEMORY_STAIRS,
    COLOR_PANEL,
    COLOR_PANEL_BORDER,
    COLOR_PLAYER,
    COLOR_SHOT,
    COLOR_STAIRS,
    COLOR_TERRAIN_BOG,
    COLOR_TERRAIN_BOG_MEMORY,
    COLOR_TERRAIN_CLIFF,
    COLOR_TERRAIN_LAVAFIELD,
    COLOR_TERRAIN_MESA,
    COLOR_TERRAIN_POND,
    COLOR_TEXT,
    SIDE_PANEL_WIDTH,
    VIEW_HEIGHT,
    VIEW_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
)
from .rendering_primitives import (
    draw_tile, draw_marker, draw_health_bar, draw_status_pips,
    draw_terrain_marker, draw_feature_footprint,
    wrap_text, draw_section_header,
)


def render_viewport(screen, game, start_x, end_x, start_y, end_y):
    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            if (x, y) not in game.visible_tiles and (x, y) not in game.seen_tiles:
                draw_tile(screen, x - game.camera_x, y - game.camera_y, COLOR_HIDDEN)
                continue
            visible = (x, y) in game.visible_tiles
            color = game.region_palette.wall if game.dungeon.tiles[x][y] == 1 else game.region_palette.floor
            if not visible:
                color = game.region_palette.memory_wall if game.dungeon.tiles[x][y] == 1 else game.region_palette.memory_floor
            house_colors = getattr(game.dungeon, "metadata", {}).get("house_colors", {})
            if game.dungeon.tiles[x][y] == 1 and (x, y) in house_colors:
                hc = house_colors[(x, y)]
                color = hc if visible else tuple(max(12, c // 2) for c in hc)
            terrain_kind = game.terrain_features.get((x, y))
            if terrain_kind in {"bog", "bog_reeds", "bog_cypress"}:
                color = COLOR_TERRAIN_BOG if visible else COLOR_TERRAIN_BOG_MEMORY
            elif terrain_kind in {"cliff", "cliff_pine"}:
                color = COLOR_TERRAIN_CLIFF if visible else tuple(component // 2 for component in COLOR_TERRAIN_CLIFF)
            elif terrain_kind in {"mesa", "mesa_scrub"}:
                color = COLOR_TERRAIN_MESA if visible else tuple(component // 2 for component in COLOR_TERRAIN_MESA)
            elif terrain_kind in {"lavafield", "lavafield_obsidian"}:
                color = COLOR_TERRAIN_LAVAFIELD if visible else tuple(component // 2 for component in COLOR_TERRAIN_LAVAFIELD)
            elif terrain_kind == "pond":
                color = COLOR_TERRAIN_POND if visible else tuple(component // 2 for component in COLOR_TERRAIN_POND)
            if (x, y) == game.stairs:
                color = COLOR_STAIRS if visible else COLOR_MEMORY_STAIRS
            elif (x, y) == game.up_stairs:
                color = COLOR_STAIRS if visible else COLOR_MEMORY_STAIRS
            elif game.return_portal and game.bottom_reward_claimed and (x, y) == game.return_portal:
                color = COLOR_STAIRS if visible else COLOR_MEMORY_STAIRS
            elif game.delve_goal and not game.bottom_reward_claimed and (x, y) == game.delve_goal:
                color = COLOR_STAIRS if visible else COLOR_MEMORY_STAIRS
            elif game.upgrade_pickup and (x, y) == game.upgrade_pickup.position:
                color = game.upgrade_pickup.color if visible else game.upgrade_pickup.memory_color
            elif game.heal_pickup and (x, y) == game.heal_pickup:
                color = game.heal_color if visible else COLOR_MEMORY_HEAL
            else:
                floor_item = game.floor_item_at((x, y))
                if floor_item is not None:
                    base = floor_item.item.color
                    color = base if visible else tuple(max(18, component // 2) for component in base)
            draw_tile(screen, x - game.camera_x, y - game.camera_y, color)
            if (x, y) == game.stairs:
                draw_marker(screen, x - game.camera_x, y - game.camera_y, "stairs", COLOR_TEXT if visible else COLOR_ACCENT)
            elif (x, y) == game.up_stairs:
                draw_marker(screen, x - game.camera_x, y - game.camera_y, "stairs_up", COLOR_TEXT if visible else COLOR_ACCENT)
            elif game.return_portal and game.bottom_reward_claimed and (x, y) == game.return_portal:
                draw_marker(screen, x - game.camera_x, y - game.camera_y, "portal", COLOR_TEXT if visible else COLOR_ACCENT)
            elif game.delve_goal and not game.bottom_reward_claimed and (x, y) == game.delve_goal:
                draw_marker(screen, x - game.camera_x, y - game.camera_y, "portal", COLOR_TEXT if visible else COLOR_ACCENT)
            elif game.upgrade_pickup and (x, y) == game.upgrade_pickup.position:
                draw_marker(screen, x - game.camera_x, y - game.camera_y, game.upgrade_pickup.kind, COLOR_BG)
            elif game.heal_pickup and (x, y) == game.heal_pickup:
                draw_marker(screen, x - game.camera_x, y - game.camera_y, "vitality", COLOR_BG)
            elif (x, y) in game.edge_exits.values():
                direction = next(direction for direction, tile in game.edge_exits.items() if tile == (x, y))
                draw_marker(screen, x - game.camera_x, y - game.camera_y, f"exit_{direction}", COLOR_ACCENT if visible else COLOR_TEXT)
            else:
                floor_item = game.floor_item_at((x, y))
                if floor_item is not None:
                    draw_marker(screen, x - game.camera_x, y - game.camera_y, floor_item.item.marker, COLOR_BG)
            landmark = next((landmark for landmark in game.landmarks if landmark.position == (x, y)), None)
            if landmark and ((x, y) in game.visible_tiles or (x, y) in game.seen_tiles):
                marker_color = landmark.color if visible else tuple(max(28, component // 2) for component in landmark.color)
                draw_marker(screen, x - game.camera_x, y - game.camera_y, landmark.marker, marker_color)
            terrain_kind_at = game.terrain_features.get((x, y))
            if terrain_kind_at and ((x, y) in game.visible_tiles or (x, y) in game.seen_tiles):
                if len(game.feature_tiles((x, y))) <= 1:
                    draw_terrain_marker(screen, x - game.camera_x, y - game.camera_y, terrain_kind_at, memory=not visible)
    for anchor, kind in game.terrain_features.items():
        footprint = game.feature_tiles(anchor)
        if len(footprint) <= 1:
            continue
        if not any(tile in game.visible_tiles or tile in game.seen_tiles for tile in footprint):
            continue
        visible = any(tile in game.visible_tiles for tile in footprint)
        draw_feature_footprint(screen, game, anchor, kind, memory=not visible)
    for enemy in game.enemies:
        if enemy.position in game.visible_tiles:
            draw_tile(screen, enemy.position[0] - game.camera_x, enemy.position[1] - game.camera_y, enemy.color)
            draw_marker(screen, enemy.position[0] - game.camera_x, enemy.position[1] - game.camera_y, enemy.marker, COLOR_BG)
            draw_health_bar(screen, enemy.position[0] - game.camera_x, enemy.position[1] - game.camera_y, enemy.health, enemy.max_health, COLOR_TEXT)
            draw_status_pips(screen, enemy.position[0] - game.camera_x, enemy.position[1] - game.camera_y, enemy.status_effects)
    for resident in game.residents:
        if resident.position in game.visible_tiles:
            draw_tile(screen, resident.position[0] - game.camera_x, resident.position[1] - game.camera_y, resident.color)
            draw_marker(screen, resident.position[0] - game.camera_x, resident.position[1] - game.camera_y, resident.marker, COLOR_BG if resident.marker != "friend" else COLOR_FRIEND)
    for shot_tile in game.shot_flash:
        if shot_tile in game.visible_tiles and start_x <= shot_tile[0] < end_x and start_y <= shot_tile[1] < end_y:
            draw_tile(screen, shot_tile[0] - game.camera_x, shot_tile[1] - game.camera_y, COLOR_SHOT)
    if game.attack_flash and game.attack_flash in game.visible_tiles and start_x <= game.attack_flash[0] < end_x and start_y <= game.attack_flash[1] < end_y:
        draw_tile(screen, game.attack_flash[0] - game.camera_x, game.attack_flash[1] - game.camera_y, COLOR_ATTACK)
    draw_tile(screen, game.player[0] - game.camera_x, game.player[1] - game.camera_y, COLOR_PLAYER)
    draw_marker(screen, game.player[0] - game.camera_x, game.player[1] - game.camera_y, "player", COLOR_BG)
    draw_health_bar(screen, game.player[0] - game.camera_x, game.player[1] - game.camera_y, game.health, game.max_health, COLOR_ACCENT)
    draw_status_pips(screen, game.player[0] - game.camera_x, game.player[1] - game.camera_y, game.player_statuses)
    if not game.active_overlay():
        for position, border_color in ((game.selected_inspect_tile, (255, 226, 120)), (game.hovered_world_tile, (210, 240, 255))):
            if not position:
                continue
            if start_x <= position[0] < end_x and start_y <= position[1] < end_y:
                rect = pygame.Rect((position[0] - game.camera_x) * TILE_SIZE, (position[1] - game.camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, border_color, rect, 2, border_radius=4)
    if game.touch_ui_active and not game.active_overlay():
        for button in game.touch_action_buttons():
            panel = pygame.Surface((button["rect"].width, button["rect"].height), pygame.SRCALPHA)
            panel.fill((22, 30, 44, 214))
            pygame.draw.rect(panel, (110, 145, 185, 255), panel.get_rect(), 2, border_radius=10)
            label = game.small_font.render(button["label"], True, COLOR_TEXT)
            panel.blit(label, label.get_rect(center=(button["rect"].width // 2, button["rect"].height // 2)))
            screen.blit(panel, button["rect"].topleft)


def render_side_panel(screen, game, map_pixel_width):
    panel_rect = pygame.Rect(map_pixel_width, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, COLOR_PANEL, panel_rect)
    pygame.draw.line(screen, COLOR_PANEL_BORDER, panel_rect.topleft, panel_rect.bottomleft, 2)

    panel_x = map_pixel_width + 14
    panel_width = SIDE_PANEL_WIDTH - 28
    y = 12

    region_title = game.small_font.render(game.region_name, True, game.region_palette.banner_text)
    region_subtitle = game.small_font.render(game.region_subtitle_text(), True, COLOR_TEXT)
    region_box = pygame.Surface((panel_width, 64), pygame.SRCALPHA)
    region_box.fill((*game.region_palette.banner_fill, 220))
    pygame.draw.rect(region_box, (*game.region_palette.banner_border, 240), region_box.get_rect(), 2, border_radius=10)
    pygame.draw.line(region_box, (*game.region_palette.banner_border, 220), (12, 30), (panel_width - 12, 30), 1)
    region_box.blit(region_title, (12, 10))
    region_box.blit(region_subtitle, (12, 34))
    screen.blit(region_box, (panel_x, y))
    y += 78

    depth_text = f"{game.region_depth}/{game.region_max_depth}" if game.region_max_depth > 1 else "-"
    coord_x, coord_y = game.display_region_coords()
    weapon = game.equipped_weapon
    armor = game.equipped_armor
    status_chips = [
        ("HP", f"{game.health}/{game.max_health}"),
        ("Atk", f"{game.effective_melee_damage}/{game.effective_ranged_damage}"),
        ("Armor", f"+{armor.defense_bonus}" if armor else "0"),
        ("Ammo", str(game.ammo)),
        ("Kits", str(game.inventory_quantity("medkit"))),
        ("Tonics", str(game.inventory_quantity("tonic"))),
        ("Foes", str(len(game.enemies))),
        ("Explore", f"{game.exploration_progress}%"),
        ("Light", str(game.light_radius)),
        ("Gold", str(game.gold)),
        ("Floor", str(game.floor)),
        ("Depth", depth_text),
        ("Coords", f"{coord_x},{coord_y}"),
        ("Upg", str(game.total_upgrade_count())),
    ]
    draw_section_header(screen, game.small_font, "Status", panel_x, y, panel_width - 4, COLOR_ACCENT)
    y += 28
    stat_box = pygame.Surface((panel_width + 6, 170), pygame.SRCALPHA)
    stat_box.fill((24, 28, 40, 180))
    pygame.draw.rect(stat_box, (70, 95, 130, 210), stat_box.get_rect(), 1, border_radius=10)
    summary_line = game.small_font.render(
        f"{weapon.name if weapon else game.weapon_name}  •  {armor.name if armor else 'No armor'}  •  {game.status_summary()}",
        True,
        COLOR_TEXT,
    )
    stat_box.blit(summary_line, (14, 12))
    chip_left = 14
    chip_top = 40
    chip_gap = 8
    chip_height = 24
    x_cursor = chip_left
    y_cursor = chip_top
    max_width = panel_width - 8
    for label, value in status_chips:
        chip_text = f"{label} {value}"
        text_surface = game.small_font.render(chip_text, True, COLOR_TEXT)
        chip_width = text_surface.get_width() + 18
        if x_cursor + chip_width > max_width:
            x_cursor = chip_left
            y_cursor += chip_height + chip_gap
        chip_rect = pygame.Rect(x_cursor, y_cursor, chip_width, chip_height)
        pygame.draw.rect(stat_box, (34, 42, 58, 230), chip_rect, border_radius=8)
        pygame.draw.rect(stat_box, (96, 126, 156, 220), chip_rect, 1, border_radius=8)
        stat_box.blit(text_surface, (chip_rect.x + 9, chip_rect.y + 4))
        x_cursor += chip_width + chip_gap
    screen.blit(stat_box, (panel_x, y))
    y += 182

    draw_section_header(screen, game.small_font, "Inspect", panel_x, y, panel_width - 4, COLOR_ACCENT)
    y += 24
    inspect = game.current_inspect_info()
    inspect_box_height = 96 if inspect else 46
    inspect_box = pygame.Surface((panel_width, inspect_box_height), pygame.SRCALPHA)
    inspect_box.fill((22, 30, 40, 188))
    border_color = inspect["color"] if inspect else COLOR_PANEL_BORDER
    pygame.draw.rect(inspect_box, (*border_color, 220) if len(border_color) == 3 else border_color, inspect_box.get_rect(), 2, border_radius=10)
    if inspect:
        inspect_box.blit(game.small_font.render(inspect["title"], True, border_color), (12, 10))
        line_y = 36
        for line in inspect["lines"][:4]:
            for surface in wrap_text(game.small_font, line, COLOR_TEXT, panel_width - 24):
                inspect_box.blit(surface, (12, line_y))
                line_y += 19
    else:
        hint = game.small_font.render("Hover or click something known to inspect it.", True, COLOR_TEXT)
        inspect_box.blit(hint, (12, 13))
    screen.blit(inspect_box, (panel_x, y))
    y += inspect_box_height + 12

    journal_rect = game.journal_button_rect()
    log_rect = game.log_button_rect()
    journal_selected = journal_rect.collidepoint(*game.mouse_screen_pos) or game.journal_open
    log_selected = log_rect.collidepoint(*game.mouse_screen_pos) or game.log_open
    journal_box = pygame.Surface((journal_rect.width, journal_rect.height), pygame.SRCALPHA)
    journal_box.fill((32, 38, 54, 224) if journal_selected else (24, 30, 42, 196))
    pygame.draw.rect(journal_box, (255, 222, 134) if journal_selected else (120, 150, 182), journal_box.get_rect(), 2, border_radius=10)
    counts = game.quest_summary_counts()
    journal_title = game.small_font.render("Journal", True, (245, 248, 252))
    journal_detail = game.small_font.render(
        f"{counts['active']} active  •  {counts['completed']} complete",
        True,
        COLOR_TEXT,
    )
    journal_box.blit(journal_title, (12, 7))
    journal_box.blit(journal_detail, (12, 22))
    screen.blit(journal_box, journal_rect.topleft)
    log_box = pygame.Surface((log_rect.width, log_rect.height), pygame.SRCALPHA)
    log_box.fill((32, 38, 54, 224) if log_selected else (24, 30, 42, 196))
    pygame.draw.rect(log_box, (255, 222, 134) if log_selected else (120, 150, 182), log_box.get_rect(), 2, border_radius=10)
    log_title = game.small_font.render("Log", True, (245, 248, 252))
    log_detail = game.small_font.render(f"{len(game.message_log)} messages", True, COLOR_TEXT)
    log_box.blit(log_title, (12, 7))
    log_box.blit(log_detail, (12, 22))
    screen.blit(log_box, log_rect.topleft)
    y = journal_rect.bottom + 10

    draw_section_header(screen, game.small_font, "Recent", panel_x, y, panel_width - 4, COLOR_ACCENT)
    y += 24
    recent_box_height = SCREEN_HEIGHT - y - 14
    recent_box = pygame.Surface((panel_width + 6, recent_box_height), pygame.SRCALPHA)
    recent_box.fill((22, 26, 38, 168))
    pygame.draw.rect(recent_box, (70, 95, 130, 210), recent_box.get_rect(), 1, border_radius=10)
    visible_entries = list(reversed(game.message_log))[:4]
    line_y = 12
    for entry in visible_entries:
        wrapped = wrap_text(game.small_font, entry, COLOR_TEXT, panel_width - 30)
        entry_height = len(wrapped) * 20 + 4
        if line_y + entry_height > recent_box_height - 30:
            break
        for surface in wrapped:
            recent_box.blit(surface, (12, line_y))
            line_y += 20
        line_y += 4
    if game.message_log:
        scroll_hint = game.small_font.render("Open Log for full history", True, COLOR_ACCENT)
        recent_box.blit(scroll_hint, (12, recent_box_height - 24))
    screen.blit(recent_box, (panel_x, y))
