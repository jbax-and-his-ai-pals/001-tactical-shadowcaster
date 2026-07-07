from __future__ import annotations

from ..game_typing import GameMixinBase


class WorldMapStatsHelpersMixin(GameMixinBase):

    def region_walkable_count(self, state):
        if "walkable_count" not in state:
            dungeon = state["dungeon"]
            state["walkable_count"] = sum(1 for x in range(dungeon.width) for y in range(dungeon.height) if dungeon.tiles[x][y] == 0)
        return state["walkable_count"]

    def region_exploration_percent(self, state):
        walkable = self.region_walkable_count(state)
        explored = len(state["seen_tiles"])
        return int((explored / max(1, walkable)) * 100)

    def hamlet_placeholder_stats(self, coord, state) -> dict:
        return {
            "coord": coord,
            "distance": abs(coord[0]) + abs(coord[1]),
            "name": state["region_name"],
            "region_type": "hamlet",
            "region_label": "Hamlet",
            "palette": state["region_palette"],
            "theme": "settled",
            "theme_color": self.region_theme_color("settled"),
            "continuity_text": "A small outpost. Travel here to explore it.",
            "is_preview": True,
            "loading_preview": False,
            "expandable_preview": False,
            "preview_generated": False,
            "hamlet_placeholder": True,
            "danger_tier": state.get("danger_tier", 1),
            "exploration": 0,
            "foes_defeated": 0,
            "foes_remaining": 0,
            "foes_spawned": 0,
            "residents": 0,
            "depth": 1,
            "max_depth": 1,
            "full_clear_reward_claimed": False,
            "bottom_reward_claimed": False,
            "exits_found": 0,
            "exit_directions": [],
            "landmarks_total": 0,
            "landmarks_visited": 0,
            "landmarks_entered": 0,
            "landmarks_cleared": 0,
            "landmarks_unvisited": 0,
            "landmarks_located_only": 0,
            "landmarks_open": 0,
            "site_outlook": "Unvisited outpost.",
            "site_state_lines": [],
            "forecast_lines": [],
            "opportunity_lines": ["Travel to this hamlet to see what's there."],
            "landmark_type_counts": [],
            "landmark_summaries": [],
            "neighbor_summaries": [],
            "quests_completed": 0,
            "quest_delivery": 0, "quest_scout": 0, "quest_bounty": 0, "quest_chain": 0,
            "prosperity_score": 0,
            "prosperity_label": "",
            "attitude_score": 0,
            "attitude_label": "",
            "active_quest_posted_here": False,
            "active_quest_targets_here": False,
            "active_quest_turnins_here": False,
            "active_quest_kinds": [],
            "active_quest_lines": [],
            "is_current": coord == self.world_position,
            "settlement_size": "hamlet",
            "settlement_rank": 1,
            "settlement_buildings": 0,
            "parent_biome": None,
            "scouted": False,
            "supply_depth": 0,
            "service_preview_lines": [],
            "road_safety": None,
            "road_safety_label": None,
            "road_safety_color": None,
            "town_archetype": None,
            "town_archetype_label": None,
            "expansion": None,
            "coast_proximity": 0.0,
            "zone_name": None,
            "is_city_hub": False,
            "is_city_district": False,
            "city_name": None,
            "city_district_type": None,
        }

    def waystation_placeholder_stats(self, coord, state) -> dict:
        base = self.hamlet_placeholder_stats(coord, state)
        base.update({
            "region_type": "waystation",
            "region_label": "Waystation",
            "continuity_text": "A road rest stop. Travel here to explore it.",
            "waystation_placeholder": True,
            "hamlet_placeholder": False,
            "settlement_size": "waystation",
            "settlement_rank": 1,
            "site_outlook": "Unvisited waystation.",
            "opportunity_lines": ["Travel to this waystation to resupply."],
        })
        return base

    def site_type_counts(self, landmarks):
        counts = {}
        for landmark in landmarks:
            label = landmark.kind.replace("_", " ").title()
            counts[label] = counts.get(label, 0) + 1
        return [f"{label} x{counts[label]}" for label in sorted(counts)]
