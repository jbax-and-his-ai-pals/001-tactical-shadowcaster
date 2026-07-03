from __future__ import annotations

from ..game_typing import GameMixinBase
from ..constants import (
    ACTION_AUTOEXPLORE,
    ACTION_CLEANSE,
    ACTION_DESCEND,
    ACTION_HEAL,
    ACTION_INVENTORY,
    ACTION_JOURNAL,
    ACTION_LOG,
    ACTION_MELEE,
    ACTION_RANGED,
    ACTION_WORLD_MAP,
    COLOR_ACCENT, COLOR_HEAL, COLOR_STAIRS, COLOR_TEXT,
    SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT, VIEW_WIDTH,
)


class InspectMixin(GameMixinBase):

    def inspect_title(self, title, position):
        return f"{title} - ({position[0]}, {position[1]})"

    def inspect_tile_info(self, position):
        if position is None:
            return None
        feature_position = self.feature_anchor_at(position) or position
        if position == self.player:
            return {"title": self.inspect_title("You", position), "lines": [f"HP {self.health}/{self.max_health}", f"Status {self.status_summary()}", f"Light radius {self.light_radius}"], "color": COLOR_ACCENT}
        enemy = self.get_enemy_at(position)
        if enemy and position in self.visible_tiles:
            statuses = ", ".join(sorted(enemy.status_effects)) if enemy.status_effects else "none"
            effect_text = enemy.on_hit_effect or "none"
            if enemy.on_hit_effect:
                effect_text = f"{enemy.on_hit_effect} {self.enemy_status_duration(enemy)}t"
            return {
                "title": self.inspect_title(enemy.kind.title(), position),
                "lines": [f"HP {enemy.health}/{enemy.max_health}", f"Damage {enemy.damage}", f"Range {enemy.attack_range}", f"Effect {effect_text}", f"Status {statuses}"],
                "color": enemy.color,
            }
        resident = self.get_resident_at(position)
        if resident and position in self.visible_tiles:
            disposition = "Peaceful" if self.region_type == "town" else "Local"
            title = resident.title or resident.kind.title()
            lines = [disposition, f"Marker {resident.marker.replace('_', ' ')}"]
            if self.region_type == "town":
                role_summary = self.resident_role_summary(resident)
                if role_summary:
                    lines.append(role_summary)
                if resident.home_name:
                    lines.append(f"Based at {resident.home_name}")
                routine_summary = self.resident_routine_summary(resident)
                if routine_summary:
                    lines.append(routine_summary)
            lines.append("Interact from nearby")
            return {"title": self.inspect_title(title, position), "lines": lines, "color": resident.color}
        if self.region_type == "town" and (position in self.visible_tiles or position in self.seen_tiles):
            building = next((entry for entry in self.town_building_data() if entry.get("door") == position), None)
            if building:
                role_lines = {
                    "home": ["A lived-in town home"],
                    "work": ["A practical working building"],
                    "civic": ["A gathering place for locals"],
                    "service": ["Enter from this doorway"],
                }
                lines = role_lines.get(building.get("role"), ["Part of the settlement"])
                if building.get("enterable"):
                    lines = [building["kind"].replace("_", " ").title(), "Enter from this doorway"]
                district = building.get("district")
                if district:
                    lines.append(f"District: {district}")
                return {"title": self.inspect_title(building["name"], position), "lines": lines, "color": COLOR_ACCENT}
        landmark = next((landmark for landmark in self.landmarks if landmark.position == position), None)
        if landmark and (position in self.visible_tiles or position in self.seen_tiles):
            progress = self.landmark_progress(self.world_position, landmark)
            identity = self.landmark_identity(self.world_position, self.snapshot_current_region(), landmark)
            landmark_lines = [identity["hook"], progress["status"], progress["detail"]]
            if landmark.kind == "inn":
                landmark_lines = ["Rest and recover", "One free rest", progress["detail"]]
            elif landmark.kind == "clinic":
                landmark_lines = ["Patch wounds and clear afflictions", "One free treatment", progress["detail"]]
            elif landmark.kind == "supply":
                landmark_lines = ["Ammo and medkit resupply", "Free bundle, then barter", progress["detail"]]
            elif landmark.kind == "shrine":
                landmark_lines = ["Gain a protective blessing", "One free warding rite", progress["detail"]]
            elif landmark.kind == "smith":
                landmark_lines = ["Tune gear for the road", "One free field refit", progress["detail"]]
            elif landmark.kind == "cartographer":
                landmark_lines = ["Reveal nearby regions", "One local survey", progress["detail"]]
            elif identity.get("reward_hint"):
                landmark_lines.append(identity["reward_hint"])
            return {
                "title": self.inspect_title(landmark.name, position),
                "lines": landmark_lines,
                "color": landmark.color,
            }
        if self.upgrade_pickup and position == self.upgrade_pickup.position and position in self.visible_tiles:
            return {"title": self.inspect_title("Upgrade Cache", position), "lines": [self.upgrade_pickup.kind.title(), "Claim by stepping here"], "color": self.upgrade_pickup.color}
        if self.heal_pickup and position == self.heal_pickup and position in self.visible_tiles:
            return {"title": self.inspect_title("Medical Pickup", position), "lines": [f"Restore {self.tuning['heal_pickup_restore']} HP", "Claim by stepping here"], "color": self.heal_color}
        floor_item = self.floor_item_at(position)
        if floor_item and position in self.visible_tiles:
            item = floor_item.item
            detail = item.description or "Claim by stepping here"
            if item.category == "weapon":
                detail = f"+{item.melee_bonus} melee, +{item.ranged_bonus} ranged" if item.ranged_bonus else f"+{item.melee_bonus} melee"
            elif item.category == "armor":
                detail = f"+{item.defense_bonus} defense"
            return {"title": self.inspect_title(item.name, position), "lines": [detail, "Claim by stepping here"], "color": item.color}
        if self.stairs and feature_position == self.stairs and (position in self.visible_tiles or position in self.seen_tiles):
            return {"title": self.inspect_title("Down Stairs", position), "lines": ["Travel to a deeper floor", "Stand here and press Enter or ."], "color": COLOR_STAIRS}
        if self.up_stairs and feature_position == self.up_stairs and (position in self.visible_tiles or position in self.seen_tiles):
            return {"title": self.inspect_title("Up Stairs", position), "lines": ["Travel back to the previous depth", "Stand here and press Enter or ."], "color": COLOR_STAIRS}
        if self.delve_goal and feature_position == self.delve_goal and (position in self.visible_tiles or position in self.seen_tiles):
            if self.bottom_reward_claimed:
                return {"title": self.inspect_title("Return Portal", position), "lines": ["Back to the overworld", "Stand here and press Enter or ."], "color": COLOR_ACCENT}
            return {"title": self.inspect_title("Delve Terminus", position), "lines": ["Step here to choose a reward"], "color": COLOR_ACCENT}
        if position in self.edge_exits.values() and (position in self.visible_tiles or position in self.seen_tiles):
            direction = next(direction for direction, tile in self.edge_exits.items() if tile == position)
            return {"title": self.inspect_title("Region Exit", position), "lines": [f"Leads {direction}", "Step here to travel"], "color": COLOR_ACCENT}
        terrain = self.terrain_kind_at(position)
        if terrain and (position in self.visible_tiles or position in self.seen_tiles):
            terrain_names = {
                "muck": "Muck",
                "bog": "Deep Bog",
                "bog_reeds": "Reed Bog",
                "bog_cypress": "Cypress Bog",
                "cliff": "Rock Face",
                "cliff_pine": "Pine Cliff",
                "mesa": "Mesa Shelf",
                "mesa_scrub": "Scrub Mesa",
                "lavafield": "Cooling Lava",
                "lavafield_obsidian": "Obsidian Flow",
                "embers": "Hot Embers",
                "high_ground": "High Ground",
                "well": "Well",
                "path": "Town Path",
                "flowers": "Flower Bed",
                "pond": "Pond",
                "bed": "Bed",
                "crate": "Supplies",
                "altar": "Altar",
                "forge": "Forge",
                "table": "Table",
                "shelves": "Shelves",
                "pew": "Pew",
                "anvil": "Anvil",
                "fountain": "Fountain",
                "brazier": "Brazier",
                "stall": "Market Stall",
                "hitch_post": "Hitching Post",
                "notice_board": "Notice Board",
                "shrub": "Shrub",
                "tree": "Tree",
                "garden": "Garden Patch",
                "deadbrush": "Dead Brush",
                "dune": "Sand Dune",
                "frost": "Frost",
                "wheat": "Wheat",
                "crop_row": "Crop Row",
                "fallow": "Fallow Ground",
                "haystack": "Haystack",
                "fence": "Fence",
            }
            terrain_text = {
                "muck": "Can poison",
                "bog": "Impassable swamp water",
                "bog_reeds": "Impassable reeds and standing water",
                "bog_cypress": "Impassable cypress-choked bog",
                "cliff": "Impassable but visible mountain rock",
                "cliff_pine": "Impassable cliffside marked with hardy pines",
                "mesa": "Impassable but visible badlands shelf",
                "mesa_scrub": "Impassable scrub-choked rock shelf",
                "lavafield": "Impassable but visible cooling lava",
                "lavafield_obsidian": "Impassable obsidian flow",
                "embers": "Can burn",
                "high_ground": "Boosts sight",
                "well": "Restorative water",
                "path": "A worn, natural route through town",
                "flowers": "A bright little planted patch",
                "pond": "Still water gathers here",
                "bed": "Simple lodging",
                "crate": "Packed trade goods",
                "altar": "A place of offering",
                "forge": "A working forge",
                "table": "A busy work surface",
                "shelves": "Stored wares and notes",
                "pew": "A quiet seat",
                "anvil": "A heavy shaping block",
                "fountain": "A public fountain anchors the square",
                "brazier": "A civic fire keeps the space warm and bright",
                "stall": "A small market stall fronts the square",
                "hitch_post": "Travelers tie off mounts and loads here",
                "notice_board": self._notice_board_text(),
                "shrub": "A patch of rough scrub grows here",
                "tree": "A lone tree marks this corner",
                "garden": "Someone tends a small kitchen garden here",
                "deadbrush": "Dry, brittle brush — nothing thrives here",
                "dune": "A low drift of wind-piled sand",
                "frost": "A patch of ice crystals on the ground",
                "wheat": "A tall stand of ripening grain",
                "crop_row": "Neat rows of cultivated vegetables",
                "fallow": "Ground left to rest between plantings",
                "haystack": "A mound of dried grass, bound and stacked",
                "fence": "A post-and-rail fence marks this plot",
            }
            lines = [terrain_text.get(terrain, "Terrain feature")]
            if terrain == "notice_board" and len(self.feature_tiles(feature_position)) > 1:
                lines.append("A larger civic fixture that dominates the square")
            return {"title": self.inspect_title(terrain_names.get(terrain, terrain.title()), position), "lines": lines, "color": COLOR_TEXT}
        if position in self.seen_tiles:
            tile_type = "Wall" if self.dungeon.tiles[position[0]][position[1]] == 1 else "Floor"
            return {"title": self.inspect_title(tile_type, position), "lines": [], "color": COLOR_TEXT}
        return None

    def current_inspect_info(self):
        if self.active_overlay():
            return None
        if self.world_from_screen(*self.mouse_screen_pos) is not None:
            hovered = self.inspect_tile_info(self.hovered_world_tile)
            if hovered:
                return hovered
        return self.inspect_tile_info(self.selected_inspect_tile)
