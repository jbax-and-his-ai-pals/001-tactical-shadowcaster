from __future__ import annotations

from typing import cast

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase, RegionMapLike
from ..persistence import has_save, load_game, save_game
from ..systems import flood_reachable_tiles


class WorldStateMixin(GameMixinBase):

    def snapshot_current_region(self):
        return {
            "floor": self.floor,
            "region_type": self.region_type,
            "region_name": self.region_name,
            "danger_tier": self.danger_tier,
            "danger_floor": self.danger_floor,
            "region_palette": self.region_palette,
            "dungeon": self.dungeon,
            "player": self.player,
            "entrance": self.entrance,
            "up_stairs": self.up_stairs,
            "stairs": self.stairs,
            "edge_exits": dict(self.edge_exits),
            "seen_tiles": set(self.seen_tiles),
            "terrain_features": dict(self.terrain_features),
            "upgrade_pickup": self.upgrade_pickup,
            "heal_pickup": self.heal_pickup,
            "floor_items": self.floor_items[:],
            "landmarks": self.landmarks[:],
            "enemies": self.enemies[:],
            "residents": self.residents[:],
            "exploration_milestones": list(self.exploration_milestones),
            "claimed_exploration_rewards": set(self.claimed_exploration_rewards),
            "claimed_surface_landmark_keys": set(self.claimed_surface_landmark_keys),
            "region_depth": self.region_depth,
            "region_max_depth": self.region_max_depth,
            "player_status_sources": dict(self.player_status_sources),
            "service_type": self.service_type,
            "service_claimed": self.service_claimed,
            "interaction_claims": set(self.interaction_claims),
            "bottom_reward_claimed": self.bottom_reward_claimed,
            "delve_goal": self.delve_goal,
            "return_portal": self.return_portal,
            "enemies_defeated": self.enemies_defeated,
            "enemies_spawned": self.enemies_spawned,
            "growth_tier_acked": getattr(self, "_growth_tier_acked", 0),
            "supply_depth": getattr(self, "_supply_depth", 0),
        }

    def store_current_region(self):
        if self.in_local_region():
            self.local_regions[self.current_local_region] = self.snapshot_current_region()
        else:
            self.world_regions[self.region_key(self.world_position)] = self.snapshot_current_region()

    def local_region_depth_key(self, base_key, depth):
        return f"{base_key}::depth:{depth}"

    def local_region_base_key(self):
        if not self.current_local_region:
            return None
        marker = "::depth:"
        return self.current_local_region.split(marker, 1)[0] if marker in self.current_local_region else self.current_local_region

    def parent_local_region_key(self):
        base_key = self.local_region_base_key()
        if not base_key:
            return None
        parts = base_key.split("::")
        if len(parts) <= 2:
            return None
        parent_base = "::".join(parts[:-1])
        return self.local_region_depth_key(parent_base, 1)

    def landmark_base_key(self, coord, landmark_key):
        return f"{self.region_key(coord)}::{landmark_key}"

    def landmark_local_states(self, coord, landmark):
        base_key = self.landmark_base_key(coord, landmark.key)
        states = []
        direct_state = self.local_regions.get(base_key)
        if direct_state:
            states.append((1, direct_state))
        prefix = f"{base_key}::depth:"
        for key, state in self.local_regions.items():
            if not key.startswith(prefix):
                continue
            try:
                depth = int(key.split("::depth:", 1)[1])
            except (IndexError, ValueError):
                continue
            states.append((depth, state))
        return sorted(states, key=lambda item: item[0])

    def landmark_progress(self, coord, landmark):
        states = self.landmark_local_states(coord, landmark)
        world_state = self.world_regions.get(self.region_key(coord))
        discovered_in_world = bool(world_state and landmark.position in world_state.get("seen_tiles", set()))
        if not states:
            if discovered_in_world:
                return {
                    "visited": True,
                    "cleared": False,
                    "entered": False,
                    "status": "Located",
                    "detail": "Site marked on your map",
                }
            return {
                "visited": False,
                "cleared": False,
                "entered": False,
                "status": "Unvisited",
                "detail": "No delve entered yet",
            }
        deepest_depth, deepest_state = states[-1]
        max_depth = max(state.get("region_max_depth", depth) for depth, state in states)
        bottom_claimed = any(state.get("bottom_reward_claimed", False) for _, state in states)
        if bottom_claimed:
            status = "Cleared"
            if max_depth > 1:
                detail = f"Reached the bottom ({max_depth}/{max_depth})"
            else:
                detail = "Site explored"
        elif max_depth > 1:
            status = "Delving"
            detail = f"Deepest reach {deepest_depth}/{max_depth}"
        else:
            status = "Visited"
            detail = "Site entered"
        return {
            "visited": True,
            "cleared": bottom_claimed,
            "entered": True,
            "status": status,
            "detail": detail,
        }

    def can_load_from_menu(self):
        return has_save() if self.menu_mode == "main" else bool(self.save_entries)

    def start_new_game(self):
        self.world_seed = self.new_run_seed()
        self.reset()
        self.close_menu()
        controls = "WASD or arrows to move. Space attacks, F fires."
        self.message = f"A new journey begins in {self.region_name}. {controls} Seed {self.world_seed_label()}."

    def save_run(self):
        if self.menu_mode == "main":
            self.menu_message = "Start or load a run first."
            return
        self.store_current_region()
        save_path = save_game(self)
        self.menu_message = f"Saved to {save_path.stem}."
        self.message = f"Game saved to {save_path.stem}."

    def load_run(self, path):
        if path is None:
            self.menu_message = "No save file found."
            return
        try:
            data = load_game(path)
            self.apply_loaded_state(data)
        except (KeyError, ValueError, TypeError, OSError):
            self.menu_message = "Save file is corrupted or unreadable."
            return
        self.close_menu()
        self.message = "Game loaded."

    def apply_loaded_state(self, data):
        self.world_seed = data.get("world_seed", self.new_run_seed())
        self.max_health = data["max_health"]
        self.health = data["health"]
        self.weapon_name = data["weapon_name"]
        self.ammo = data["ammo"]
        self.base_light_radius = data["base_light_radius"]
        self.light_bonus = data["light_bonus"]
        self.melee_damage = data["melee_damage"]
        self.ranged_damage = data["ranged_damage"]
        if "inventory" in data:
            self.inventory = list(data["inventory"])
        else:
            self.inventory = []
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=data.get("medkits", 0), description="Restores health.")
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=data.get("tonics", 0), description="Clears statuses and grants ward.")
        self.gold = data.get("gold", 0)
        self.active_quests = list(data.get("active_quests", []))
        self.player_statuses = data["player_statuses"]
        self.player_status_sources = data.get("player_status_sources", {})
        self.facing = data["facing"]
        self.travel_mode = False
        self.travel_choices = []
        self.world_map_open = False
        self.world_map_mode = "discovered"
        self.selected_world_region = None
        self.preview_world_regions = {}
        self.tuner_open = False
        self.tuner_return_mode = None
        self.world_position = data["world_position"]
        self.world_regions = data["world_regions"]
        self.world_rivers = self.generate_world_rivers()
        self.world_zones = self.generate_world_zones()
        self.world_coast = self.generate_world_coast()
        self.world_city = self.generate_world_city()
        self.local_regions = data.get("local_regions", {})
        self.current_local_region = data.get("current_local_region")
        self.service_type = data.get("service_type")
        self.service_claimed = data.get("service_claimed", False)
        self.region_depth = data.get("region_depth", 1)
        self.region_max_depth = data.get("region_max_depth", 1)
        self.bottom_reward_claimed = data.get("bottom_reward_claimed", False)
        self.delve_reward_pending = data.get("delve_reward_pending", False)
        self.haste_bonus = data.get("haste_bonus", 0)
        self.reach_bonus = data.get("reach_bonus", 0)
        self.delve_goal = data.get("delve_goal")
        self.return_portal = data.get("return_portal")
        self.enemies_defeated = data.get("enemies_defeated", 0)
        self.enemies_spawned = data.get("enemies_spawned", 0)
        self.total_steps = data.get("total_steps", 0)
        self.total_monsters_killed = data.get("total_monsters_killed", 0)
        self.powerups_collected = {"light": 0, "vitality": 0, "power": 0, "haste": 0, "reach": 0, "heal": 0}
        self.powerups_collected.update(data.get("powerups_collected", {}))
        self.medkits_used = data.get("medkits_used", 0)
        self.tonics_used = data.get("tonics_used", 0)
        self.best_exploration_percent = data.get("best_exploration_percent", 0)
        self.full_clears = data.get("full_clears", 0)
        self.game_over = data["game_over"]
        self.death_cause = data.get("death_cause", "")
        self.death_gold_lost = data.get("death_gold_lost", 0)
        self.death_respawn_label = data.get("death_respawn_label", "")
        hp_raw = data.get("homepoint_coord")
        self.homepoint_coord = tuple(hp_raw) if hp_raw else None
        self.discovered_shrines = [tuple(p) for p in data.get("discovered_shrines", [])]
        self.player_xp = data.get("player_xp", 0)
        self.player_level = data.get("player_level", 1)
        self.xp_milestones_claimed = set(data.get("xp_milestones_claimed", []))
        self.levelup_pending = 0
        self.active_ability = data.get("active_ability", "")
        self.levelup_ability_choices = []
        self.levelup_ability_index = 0
        self.wandering_npcs = data.get("wandering_npcs", {})
        self.attack_flash = None
        self.shot_flash = []
        self.auto_move_path = []
        self.clear_manual_movement()
        self.next_auto_move_ms = 0
        self.completion_modal_until = 0
        self.completion_modal_started = 0
        self.completion_modal_text = data.get("completion_modal_text", "")
        self.tuning = self.default_tuning()
        self.tuning.update(data.get("tuning", {}))
        self.exploration_reward_pending = data.get("exploration_reward_pending")
        self.town_choice_pending = None
        self.exploration_choice_index = 0
        if self.current_local_region and "::depth:" not in self.current_local_region:
            depth_key = self.local_region_depth_key(self.current_local_region, self.region_depth)
            if depth_key not in self.local_regions and self.current_local_region in self.local_regions:
                self.local_regions[depth_key] = self.local_regions[self.current_local_region]
            self.current_local_region = depth_key
        if self.current_local_region:
            self.load_region_state(self.local_regions[self.current_local_region])
        else:
            region_key = self.region_key(self.world_position)
            self.load_region_state(self.world_regions[region_key])

    def load_region_state(self, state, arrival_direction=None):
        self.floor = state["floor"]
        self.region_type = state["region_type"]
        self.region_name = state["region_name"]
        self.danger_tier = state.get("danger_tier", 1)
        self.danger_floor = state.get("danger_floor", self.floor)
        self.region_palette = state["region_palette"]
        self.dungeon = cast(RegionMapLike, state["dungeon"])
        self.region_depth = state.get("region_depth", 1)
        self.region_max_depth = state.get("region_max_depth", 1)
        self.rules = self.region_rules()
        self.player_status_sources = dict(state.get("player_status_sources", {}))
        self.service_type = state.get("service_type")
        self.service_claimed = state.get("service_claimed", False)
        self.interaction_claims = set(state.get("interaction_claims", set()))
        self.bottom_reward_claimed = state.get("bottom_reward_claimed", False)
        self.delve_goal = state.get("delve_goal")
        self.return_portal = state.get("return_portal")
        self.enemies_defeated = state.get("enemies_defeated", 0)
        self.enemies_spawned = state.get("enemies_spawned", len(state["enemies"]) + self.enemies_defeated)
        self._growth_tier_acked = state.get("growth_tier_acked", 0)
        self._supply_depth = state.get("supply_depth", 0)
        self.entrance = state["entrance"]
        self.up_stairs = state.get("up_stairs")
        self.stairs = state["stairs"]
        self.edge_exits = dict(state.get("edge_exits", {}))
        self.edge_exits = self.normalize_edge_exits(self.edge_exits)
        self.seen_tiles = set(state["seen_tiles"])
        self.terrain_features = dict(state["terrain_features"])
        self.sync_vision_transparency()
        self.upgrade_pickup = state["upgrade_pickup"]
        self.heal_pickup = state["heal_pickup"]
        self.floor_items = state.get("floor_items", [])[:]
        self.landmarks = state.get("landmarks", [])[:]
        self.enemies = state["enemies"][:]
        self.residents = state["residents"][:]
        self.exploration_milestones = list(state["exploration_milestones"])
        if not self.exploration_rewards_enabled(self.region_type):
            self.exploration_milestones = []
        self.claimed_exploration_rewards = set(state["claimed_exploration_rewards"])
        self.claimed_surface_landmark_keys = set(state.get("claimed_surface_landmark_keys", set()))
        self.attack_flash = None
        self.shot_flash = []
        self.auto_move_path = []
        self.clear_manual_movement()
        self.world_map_open = False
        self.selected_world_region = None
        self.floor_explorable_tiles = flood_reachable_tiles(self.dungeon, self.entrance)
        self.player = self.arrival_position(arrival_direction) if arrival_direction else state.get("player", self.entrance)
        self.update_visibility()
        self.last_interest_tiles = self.visible_interest_tiles()
        self.update_camera()
        self.check_quest_completion()
