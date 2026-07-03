from __future__ import annotations

from ..game_typing import GameMixinBase


class WorldMapStatsMixin(GameMixinBase):
    def landmark_progress_counts(self, coord, landmarks):
        counts = {"unvisited": 0, "located": 0, "entered": 0, "cleared": 0}
        for landmark in landmarks:
            progress = self.landmark_progress(coord, landmark)
            if progress["cleared"]:
                counts["cleared"] += 1
            elif progress.get("entered"):
                counts["entered"] += 1
            elif progress["visited"]:
                counts["located"] += 1
            else:
                counts["unvisited"] += 1
        return counts

    def landmark_site_outlook(self, counts):
        if counts["entered"] > 0:
            return "Open site leads remain here."
        if counts["located"] > 0:
            return "Known sites are marked but not yet entered."
        if counts["cleared"] > 0 and counts["unvisited"] == 0 and counts["located"] == 0 and counts["entered"] == 0:
            return "All known sites here have been resolved."
        if counts["unvisited"] > 0:
            return "This region may still hide undiscovered places."
        return "No notable site pressure here right now."

    def landmark_identity(self, coord, state, landmark):
        region_type = state["region_type"]
        region_name = state["region_name"]
        parent_biome = state.get("town_parent_biome") or state.get("parent_biome") or region_type
        defaults = {
            "town": ("Settlement", "A place to rest, barter, and gather leads.", "Safe services and new rumors."),
            "monster_town": ("Monster Town", "A hostile settlement where every street is compromised.", "High danger, uncommon rewards."),
            "cave": ("Cave Mouth", "A rough descent into cramped underground passages.", "Depth rewards and hidden gear."),
            "dungeon": ("Dungeon Gate", "A structured delve that rewards preparation.", "Strong bottom-floor cache."),
            "castle": ("Castle Site", "A fortified site with heavier resistance.", "Tougher fights and sturdier loot."),
            "ruins": ("Ruin Site", "Broken remains that may still hide supplies or secrets.", "Mixed danger and useful finds."),
            "inn": ("Inn", "A traveler stop where you can recover before pressing on.", "A free rest on first entry."),
            "clinic": ("Clinic", "A place to patch wounds and clear lingering afflictions.", "Healing and status relief."),
            "supply": ("Provisioner", "A stock point for ammunition and field medicine.", "Resupply and barter."),
            "shrine": ("Forgotten Shrine", "An old roadside altar, still tended by something unseen.", "Full healing and status cleanse."),
            "cache": ("Hidden Cache", "Someone buried supplies here and never came back.", "Substantial supply haul."),
            "smith": ("Smithy", "A work site where gear and trail readiness matter.", "Refit and tonic support."),
            "cartographer": ("Survey Office", "A chart room that turns travel into knowledge.", "Nearby regions revealed."),
        }
        label, hook, reward = defaults.get(
            landmark.kind,
            (landmark.kind.replace("_", " ").title(), f"A notable site in {region_name}.", "Unknown opportunities."),
        )
        biome_flavor = {
            "forest": "Often hidden among tree cover and winding trails.",
            "plains": "Usually visible from a distance across open ground.",
            "farmland": "Tied closely to roads, labor, and nearby settlements.",
            "desert": "Travel there is exposed, thirsty, and hard to recover from.",
            "swamp": "Approach is awkward and often shaped by poison or poor footing.",
            "mountain": "Getting there safely matters almost as much as what lies inside.",
            "badlands": "The route itself can be harsher than the destination.",
            "tundra": "Exposure and distance are part of the threat profile.",
            "volcanic": "Heat and attrition make each push more committal.",
        }.get(parent_biome)
        return {
            "label": label,
            "hook": hook,
            "reward_hint": reward,
            "biome_flavor": biome_flavor,
        }

    def region_world_theme(self, region_type=None, state=None):
        region_type = region_type or (state["region_type"] if state else self.region_type)
        theme_map = {
            "forest": "verdant",
            "plains": "verdant",
            "farmland": "settled",
            "town": "settled",
            "inn": "settled",
            "clinic": "settled",
            "supply": "settled",
            "cartographer": "settled",
            "shrine": "sanctum",
            "cache": "depths",
            "smith": "sanctum",
            "desert": "arid",
            "badlands": "arid",
            "swamp": "wild",
            "mountain": "stone",
            "castle": "stone",
            "ruins": "stone",
            "dungeon": "depths",
            "cave": "depths",
            "maze": "wild",
            "tundra": "cold",
            "volcanic": "blight",
            "monster_town": "blight",
        }
        return theme_map.get(region_type, "wild")

    def region_theme_color(self, theme):
        return {
            "verdant": (126, 182, 104),
            "settled": (214, 186, 120),
            "sanctum": (188, 178, 232),
            "arid": (216, 162, 92),
            "wild": (112, 156, 118),
            "stone": (152, 162, 176),
            "depths": (126, 132, 158),
            "cold": (194, 220, 238),
            "blight": (214, 108, 98),
        }.get(theme, (150, 160, 174))

    def continuity_summary(self, coord, state, regions_map=None):
        theme = self.region_world_theme(state=state)
        if regions_map is None:
            regions_map = self.world_map_regions()
        neighbors = []
        for delta in self.DIRECTION_VECTORS.values():
            neighbor_coord = (coord[0] + delta[0], coord[1] + delta[1])
            neighbor_state = regions_map.get(neighbor_coord)
            if neighbor_state is None:
                continue
            neighbors.append(neighbor_state)
        if not neighbors:
            return "No nearby regions charted yet."
        same_theme = sum(1 for neighbor_state in neighbors if self.region_world_theme(state=neighbor_state) == theme)
        harsher = sum(1 for neighbor_state in neighbors if neighbor_state.get("danger_tier", 1) > state.get("danger_tier", 1))
        safer = sum(1 for neighbor_state in neighbors if neighbor_state.get("danger_tier", 1) < state.get("danger_tier", 1))
        if same_theme >= 3:
            base = "This region sits inside a broad continuous belt."
        elif same_theme == 2:
            base = "Nearby regions feel fairly consistent."
        elif same_theme == 1:
            base = "This area feels like a transition zone."
        else:
            base = "This region stands apart from its neighbors."
        if harsher >= 2:
            return base + " The frontier grows more dangerous nearby."
        if safer >= 2:
            return base + " Nearby territory looks gentler."
        return base

    def region_stats(self, coord, regions_map=None):
        if regions_map is None:
            regions_map = self.world_map_regions()
        discovered = self.discovered_world_regions()
        fully_discovered_coords = {self.parse_region_key(key) for key in self.world_regions}
        fully_discovered_coords.add(self.world_position)
        if coord == self.world_position and self.in_local_region():
            state = self.snapshot_current_region()
        else:
            if coord in discovered:
                state = discovered[coord]
            elif self.world_map_mode == "local_debug":
                preview_key = self.region_key(coord)
                state = self.preview_world_regions.get(preview_key)
                if state is None:
                    state = self.preview_placeholder_state(coord)
            else:
                return None
        if state is None:
            return None
        if state.get("expandable_preview"):
            return {
                "coord": coord,
                "distance": abs(coord[0]) + abs(coord[1]),
                "name": f"Expand to ({coord[0]}, {coord[1]})",
                "region_type": state["region_type"],
                "region_label": "Frontier",
                "palette": state["region_palette"],
                "theme": "survey",
                "theme_color": (152, 168, 190),
                "continuity_text": "Click to generate this neighboring region.",
                "is_preview": True,
                "loading_preview": False,
                "expandable_preview": True,
                "preview_generated": False,
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
                "landmarks_cleared": 0,
                "landmark_type_counts": [],
                "landmark_summaries": [],
                "neighbor_summaries": [],
                "is_current": False,
                "settlement_size": None,
                "settlement_rank": 0,
                "settlement_buildings": 0,
                "parent_biome": None,
            }
        if state.get("loading_preview"):
            return {
                "coord": coord,
                "distance": abs(coord[0]) + abs(coord[1]),
                "name": state["region_name"],
                "region_type": state["region_type"],
                "region_label": "Preview",
                "palette": state["region_palette"],
                "theme": "survey",
                "theme_color": (152, 168, 190),
                "continuity_text": "Preview generation in progress.",
                "is_preview": True,
                "loading_preview": True,
                "expandable_preview": False,
                "preview_generated": False,
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
                "landmarks_cleared": 0,
                "landmark_type_counts": [],
                "landmark_summaries": [],
                "neighbor_summaries": [],
                "is_current": coord == self.world_position,
                "settlement_size": None,
                "settlement_rank": 0,
                "settlement_buildings": 0,
                "parent_biome": None,
            }
        theme = self.region_world_theme(state=state)
        exits_found = len(state.get("edge_exits", {}))
        exit_directions = sorted(state.get("edge_exits", {}))
        foes_remaining = len(state["enemies"])
        landmarks = state.get("landmarks", [])
        neighbors = []
        for direction, delta in self.DIRECTION_VECTORS.items():
            neighbor_coord = (coord[0] + delta[0], coord[1] + delta[1])
            neighbor_state = regions_map.get(neighbor_coord)
            if neighbor_state is None:
                neighbors.append(
                    {
                        "direction": direction,
                        "coord": neighbor_coord,
                        "name": None,
                        "label": "Unknown",
                        "danger_tier": None,
                        "is_preview": False,
                    }
                )
                continue
            neighbors.append(
                {
                    "direction": direction,
                    "coord": neighbor_coord,
                    "name": neighbor_state["region_name"],
                    "label": self.region_display_label(state=neighbor_state),
                    "danger_tier": neighbor_state.get("danger_tier", 1),
                    "is_preview": neighbor_coord not in fully_discovered_coords and neighbor_coord != self.world_position,
                }
            )
        landmark_progress_cache = [self.landmark_progress(coord, lm) for lm in landmarks]
        landmark_summaries = []
        landmark_counts = {"unvisited": 0, "located": 0, "entered": 0, "cleared": 0}
        for prog in landmark_progress_cache:
            if prog["cleared"]:
                landmark_counts["cleared"] += 1
            elif prog.get("entered"):
                landmark_counts["entered"] += 1
            elif prog["visited"]:
                landmark_counts["located"] += 1
            else:
                landmark_counts["unvisited"] += 1
        for i, landmark in enumerate(landmarks[:6]):
            progress = landmark_progress_cache[i]
            identity = self.landmark_identity(coord, state, landmark)
            landmark_summaries.append(
                {
                    "name": landmark.name,
                    "kind": landmark.kind,
                    "label": identity["label"],
                    "status": progress["status"],
                    "detail": progress["detail"],
                    "hook": identity["hook"],
                    "reward_hint": identity["reward_hint"],
                    "biome_flavor": identity["biome_flavor"],
                    "visited": progress["visited"],
                    "entered": progress.get("entered", False),
                    "cleared": progress["cleared"],
                }
            )
        quest_counts = self.completed_quest_counts(coord)
        prosperity_score = self.town_prosperity_score(coord)
        active_quest_summary = self.active_quest_region_summary(coord)
        return {
            "coord": coord,
            "distance": abs(coord[0]) + abs(coord[1]),
            "name": state["region_name"],
            "region_type": state["region_type"],
            "region_label": self.region_display_label(state=state),
            "palette": state["region_palette"],
            "theme": theme,
            "theme_color": self.region_theme_color(theme),
            "continuity_text": self.continuity_summary(coord, state, regions_map),
            "is_preview": coord not in fully_discovered_coords and coord != self.world_position,
            "loading_preview": state.get("loading_preview", False),
            "expandable_preview": state.get("expandable_preview", False),
            "preview_generated": state.get("preview_generated", False),
            "danger_tier": state.get("danger_tier", 1),
            "exploration": self.region_exploration_percent(state),
            "foes_defeated": state.get("enemies_defeated", 0),
            "foes_remaining": foes_remaining,
            "foes_spawned": state.get("enemies_spawned", foes_remaining + state.get("enemies_defeated", 0)),
            "residents": len(state["residents"]),
            "depth": state.get("region_depth", 1),
            "max_depth": state.get("region_max_depth", 1),
            "full_clear_reward_claimed": 100 in state["claimed_exploration_rewards"],
            "bottom_reward_claimed": state.get("bottom_reward_claimed", False),
            "exits_found": exits_found,
            "exit_directions": exit_directions,
            "landmarks_total": len(landmarks),
            "landmarks_visited": sum(1 for p in landmark_progress_cache if p["visited"]),
            "landmarks_entered": sum(1 for p in landmark_progress_cache if p.get("entered")),
            "landmarks_cleared": sum(1 for p in landmark_progress_cache if p["cleared"]),
            "landmarks_unvisited": landmark_counts["unvisited"],
            "landmarks_located_only": landmark_counts["located"],
            "landmarks_open": landmark_counts["entered"],
            "site_outlook": self.landmark_site_outlook(landmark_counts),
            "landmark_type_counts": self.site_type_counts(landmarks),
            "landmark_summaries": landmark_summaries,
            "neighbor_summaries": neighbors,
            "quests_completed": sum(quest_counts.values()),
            "quest_delivery": quest_counts.get("delivery", 0),
            "quest_scout": quest_counts.get("scout", 0),
            "quest_bounty": quest_counts.get("bounty", 0),
            "prosperity_score": prosperity_score,
            "prosperity_label": self.town_prosperity_label(coord),
            "active_quest_posted_here": active_quest_summary["posted_here"],
            "active_quest_targets_here": active_quest_summary["targets_here"],
            "active_quest_turnins_here": active_quest_summary["report_here"],
            "active_quest_kinds": sorted(active_quest_summary["kinds"]),
            "active_quest_lines": active_quest_summary["lines"],
            "is_current": coord == self.world_position,
            "settlement_size": self.settlement_label(state),
            "settlement_rank": self.settlement_size_rank(state),
            "settlement_buildings": self.settlement_building_count(state),
            "parent_biome": self.settlement_parent_biome(state),
        }

    def region_walkable_count(self, state):
        if "walkable_count" not in state:
            dungeon = state["dungeon"]
            state["walkable_count"] = sum(1 for x in range(dungeon.width) for y in range(dungeon.height) if dungeon.tiles[x][y] == 0)
        return state["walkable_count"]

    def region_exploration_percent(self, state):
        walkable = self.region_walkable_count(state)
        explored = len(state["seen_tiles"])
        return int((explored / max(1, walkable)) * 100)

    def site_type_counts(self, landmarks):
        counts = {}
        for landmark in landmarks:
            label = landmark.kind.replace("_", " ").title()
            counts[label] = counts.get(label, 0) + 1
        return [f"{label} x{counts[label]}" for label in sorted(counts)]
