from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..regions import RegionChoice, palette_for_region, random_region_name

_EXPANSION_BLOCKED = frozenset({
    "badlands", "swamp", "volcanic", "desert", "cave", "dungeon", "maze",
    "monster_town", "castle", "ruins",
})
_EXPANSION_SLOW = frozenset({"mountain", "tundra"})

_HOSTILE_BORDER = frozenset({
    "badlands", "swamp", "volcanic", "monster_town",
})


class ExpansionMixin(GameMixinBase):

    def viable_expansion_directions(self, coord=None):
        """Return list of (direction, neighbor_coord, is_slow) for viable expansion from a town."""
        coord = coord or self.world_position
        regions_map = self.world_map_regions()
        viable = []
        for direction, delta in self.DIRECTION_VECTORS.items():
            neighbor = (coord[0] + delta[0], coord[1] + delta[1])
            state = regions_map.get(neighbor)
            if state is None:
                continue
            rtype = state.get("region_type", "")
            if rtype in _EXPANSION_BLOCKED:
                continue
            if rtype in ("town", "hamlet"):
                continue
            is_slow = rtype in _EXPANSION_SLOW
            viable.append((direction, neighbor, is_slow))
        return viable

    def hostile_border_directions(self, coord=None):
        """Return directions where a hostile biome borders the town."""
        coord = coord or self.world_position
        regions_map = self.world_map_regions()
        hostile = []
        for direction, delta in self.DIRECTION_VECTORS.items():
            neighbor = (coord[0] + delta[0], coord[1] + delta[1])
            state = regions_map.get(neighbor)
            if state is None:
                continue
            if state.get("region_type", "") in _HOSTILE_BORDER:
                hostile.append(direction)
        return hostile

    def town_is_hemmed_in(self, coord=None) -> bool:
        return len(self.viable_expansion_directions(coord)) == 0

    def town_expansion_npc_line(self) -> str:
        if self.town_is_hemmed_in():
            return random.choice([
                "We can't push outward — the terrain sees to that. So we dig deeper.",
                "No room to grow from here. But the walls are getting thicker.",
                "Hemmed in on all sides. Keeps things tight, at least.",
            ])
        exp = self.expansion_status()
        if exp.get("satellite_eligible"):
            return random.choice([
                "There's talk of putting down a small camp to the east. Nothing decided yet.",
                "If things keep going well, we might push a settlement out into the open ground.",
            ])
        return ""

    def town_history_npc_line(self) -> str:
        archetype = self.town_archetype() if hasattr(self, "town_archetype") else "survivor"
        dims = self.town_dimensions() if hasattr(self, "town_dimensions") else {}
        if archetype == "frontier_post" and dims.get("security", 0) >= 5:
            return random.choice([
                "Used to be rougher here before the patrols started.",
                "The watch doubled up after that last bad season. Seems to have held.",
                "We've kept the perimeter tight. That's not nothing out here.",
            ])
        if archetype == "trade_hub" and dims.get("prosperity", 0) >= 5:
            return random.choice([
                "Caravans started stopping here regular once word got out.",
                "This crossroads has been good to us. More coming through every season.",
                "Trade draws people, people draw more trade. You know how it goes.",
            ])
        if archetype == "learning_seat" and dims.get("knowledge", 0) >= 5:
            return random.choice([
                "We've been building a proper record of this region. Slow work, but it adds up.",
                "The archive started as a shelf in someone's home. Look at it now.",
                "People send reports here from far off. We're becoming a kind of center.",
            ])
        if archetype == "social_anchor" and dims.get("connections", 0) >= 5:
            return random.choice([
                "We know half the settlements in the region by name now. That used to feel impossible.",
                "Being well-connected keeps this town alive in ways you can't always see.",
                "Word travels fast when you've got good relations. Keeps us ahead of trouble.",
            ])
        return ""

    def choose_connected_region(self, coord=None):
        coord = coord or self.world_position
        coord_key = self.region_key(coord)
        # Check if this coord is a seeded hamlet target
        for parent_key, hamlet_coord in self._hamlet_log().items():
            if self.region_key(hamlet_coord) == coord_key:
                parent_name = self.world_regions.get(parent_key, {}).get("region_name", "")
                hamlet_name = self.world_regions.get(coord_key, {}).get("region_name") or random_region_name("hamlet")
                summary = f"A small outpost established by {parent_name}." if parent_name else "A small frontier outpost."
                return RegionChoice(region_type="hamlet", name=hamlet_name, summary=summary,
                                    context={"parent_town_key": parent_key, "parent_town_name": parent_name})
        # Check if this coord is a seeded waystation
        state = self.world_regions.get(coord_key, {})
        if state.get("waystation_placeholder"):
            ws_name = state.get("region_name", "Waystation")
            summary = "A rest stop established between two connected settlements."
            return RegionChoice(region_type="waystation", name=ws_name, summary=summary,
                                context={"parent_town_a": state.get("parent_town_a"), "parent_town_b": state.get("parent_town_b")})
        return super().choose_connected_region(coord)  # type: ignore[misc]

    # ── Buffer zone ─────────────────────────────────────────────────────────

    def buffer_zone_strength(self, coord=None) -> int:
        """Return 0-3 buffer zone strength from security dimension (0 = none)."""
        dims = self.town_dimensions(coord) if hasattr(self, "town_dimensions") else {}
        sec = dims.get("security", 0)
        if sec <= 0:
            return 0
        if sec <= 2:
            return 1
        if sec <= 5:
            return 2
        return 3

    def has_buffer_zone(self, coord=None) -> bool:
        if not self.hostile_border_directions(coord):
            return False
        return self.buffer_zone_strength(coord) >= 1

    def buffer_zone_status(self, coord=None) -> dict:
        strength = self.buffer_zone_strength(coord)
        directions = self.hostile_border_directions(coord)
        labels = {1: "thin", 2: "established", 3: "hardened"}
        return {
            "active": strength >= 1 and bool(directions),
            "strength": strength,
            "strength_label": labels.get(strength, "none"),
            "hostile_directions": directions,
        }

    def buffer_zone_npc_line(self) -> str:
        status = self.buffer_zone_status()
        if not status["active"]:
            return ""
        dirs = " and ".join(status["hostile_directions"][:2])
        strength = status["strength_label"]
        import random as _random
        if strength == "hardened":
            return _random.choice([
                f"The {dirs} perimeter is solid. We've put real work into keeping it that way.",
                f"Nothing gets past the {dirs} line without us knowing. Took years, but we've earned it.",
                f"The buffer on the {dirs} side is as deep as it's ever been.",
            ])
        if strength == "established":
            return _random.choice([
                f"We keep a clear strip on the {dirs} side. The watch patrols it twice a day.",
                f"The {dirs} border is patrolled. Not impenetrable, but it's held so far.",
                f"There's a maintained zone on the {dirs} edge. It's given us warning when we needed it.",
            ])
        return _random.choice([
            f"We've started pushing the {dirs} edge back a little. Early days.",
            f"The {dirs} approach is being cleared. The watch is stretched thin, but it's started.",
            f"Thin perimeter on the {dirs} side. Better than nothing, not as good as we need.",
        ])

    # ── Road waystation seeding ─────────────────────────────────────────────

    def _waystation_log(self) -> dict:
        if not hasattr(self, "_town_waystations"):
            self._town_waystations: dict = {}
        return self._town_waystations

    def seed_waystations(self) -> None:
        """Seed waystation tiles between sufficiently connected town pairs."""
        dims_by_key: dict = {}
        town_coords: list[tuple] = []
        for key, state in self.world_regions.items():
            if state.get("region_type") != "town":
                continue
            parts = key.split(",")
            if len(parts) != 2:
                continue
            coord = (int(parts[0]), int(parts[1]))
            town_coords.append(coord)
            dims = self.town_dimensions(coord) if hasattr(self, "town_dimensions") else {}
            dims_by_key[key] = dims

        for i, ca in enumerate(town_coords):
            for cb in town_coords[i + 1:]:
                dx = abs(ca[0] - cb[0])
                dy = abs(ca[1] - cb[1])
                dist = dx + dy
                if dist < 2 or dist > 5:
                    continue  # too close (adjacent) or too far
                key_a = self.region_key(ca)
                key_b = self.region_key(cb)
                pair_key = f"{min(key_a, key_b)}|{max(key_a, key_b)}"
                if pair_key in self._waystation_log():
                    continue
                conn_a = dims_by_key.get(key_a, {}).get("connections", 0)
                conn_b = dims_by_key.get(key_b, {}).get("connections", 0)
                if conn_a < 3 or conn_b < 3:
                    continue
                safety_a = self.road_safety_for_town(ca) if hasattr(self, "road_safety_for_town") else "safe"
                safety_b = self.road_safety_for_town(cb) if hasattr(self, "road_safety_for_town") else "safe"
                if safety_a == "contested" or safety_b == "contested":
                    continue
                # Midpoint
                mid = ((ca[0] + cb[0]) // 2, (ca[1] + cb[1]) // 2)
                mid_key = self.region_key(mid)
                if mid_key in self.world_regions:
                    continue
                # Seed waystation placeholder
                name_a = self.world_regions.get(key_a, {}).get("region_name", "")
                name_b = self.world_regions.get(key_b, {}).get("region_name", "")
                ws_name = f"Waystation"
                if name_a and name_b:
                    ws_name = f"{name_a[:8]}-{name_b[:8]} Waystation"
                self._waystation_log()[pair_key] = mid
                self.world_regions[mid_key] = {
                    "region_type": "waystation",
                    "region_name": ws_name,
                    "region_palette": palette_for_region("town"),
                    "danger_tier": 1,
                    "danger_floor": 1,
                    "floor": 1,
                    "dungeon": None,
                    "player": None,
                    "entrance": (1, 1),
                    "up_stairs": None,
                    "stairs": (1, 1),
                    "edge_exits": {},
                    "seen_tiles": set(),
                    "terrain_features": {},
                    "upgrade_pickup": None,
                    "heal_pickup": None,
                    "floor_items": [],
                    "landmarks": [],
                    "enemies": [],
                    "residents": [],
                    "exploration_milestones": [100],
                    "claimed_exploration_rewards": set(),
                    "claimed_surface_landmark_keys": set(),
                    "region_depth": 1,
                    "region_max_depth": 1,
                    "player_status_sources": {},
                    "service_type": None,
                    "service_claimed": False,
                    "interaction_claims": set(),
                    "bottom_reward_claimed": False,
                    "delve_goal": None,
                    "return_portal": None,
                    "enemies_defeated": 0,
                    "enemies_spawned": 0,
                    "growth_tier_acked": 0,
                    "supply_depth": 0,
                    "waystation_placeholder": True,
                    "parent_town_a": key_a,
                    "parent_town_b": key_b,
                }
                if hasattr(self, "add_world_note"):
                    self.add_world_note(f"{ws_name} established between {name_a} and {name_b}.", coord=mid, kind="road")

    def expansion_status(self, coord=None) -> dict:
        dims = self.town_dimensions(coord) if hasattr(self, "town_dimensions") else {}
        max_dim = max(dims.values(), default=0)
        viable = self.viable_expansion_directions(coord)
        hostile = self.hostile_border_directions(coord)
        hemmed = len(viable) == 0
        outer_district_eligible = max_dim >= 4 and len(viable) > 0
        satellite_eligible = max_dim >= 6 and len(viable) > 0
        return {
            "viable_directions": [d for d, _, _ in viable],
            "hostile_borders": hostile,
            "hemmed_in": hemmed,
            "outer_district_eligible": outer_district_eligible,
            "satellite_eligible": satellite_eligible,
            "max_dimension": max_dim,
        }
