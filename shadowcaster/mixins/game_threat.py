from __future__ import annotations

import random

from ..game_typing import GameMixinBase

_THREAT_REGION_TYPES = {"monster_town"}
_PRESSURE_RADIUS = 3
_WATCHED_RADIUS = 4  # cleared sources still create a "watched" zone slightly wider


class ThreatMixin(GameMixinBase):

    def threat_sources(self) -> list[tuple[tuple[int, int], bool]]:
        """Return (coord, is_cleared) for every known hostile source in the world."""
        sources = []
        for key, state in self.world_regions.items():
            if state.get("region_type") not in _THREAT_REGION_TYPES:
                continue
            parts = key.split(",")
            if len(parts) != 2:
                continue
            coord = (int(parts[0]), int(parts[1]))
            spawned = state.get("enemies_spawned", 0)
            defeated = state.get("enemies_defeated", 0)
            cleared = spawned > 0 and defeated >= spawned
            sources.append((coord, cleared))
        return sources

    def road_safety_for_town(self, coord=None) -> str:
        """Return 'contested', 'watched', or 'safe' for the roads approaching a town coord."""
        coord = coord or self.world_position
        sources = self.threat_sources()
        nearest_uncleared = None
        nearest_cleared = None
        for source_coord, cleared in sources:
            dist = abs(source_coord[0] - coord[0]) + abs(source_coord[1] - coord[1])
            if not cleared and dist <= _PRESSURE_RADIUS:
                if nearest_uncleared is None or dist < nearest_uncleared:
                    nearest_uncleared = dist
            elif cleared and dist <= _WATCHED_RADIUS:
                if nearest_cleared is None or dist < nearest_cleared:
                    nearest_cleared = dist
        if nearest_uncleared is not None:
            return "contested"
        if nearest_cleared is not None:
            return "watched"
        return "safe"

    def road_safety_label(self, coord=None) -> str:
        safety = self.road_safety_for_town(coord)
        return {"contested": "Contested", "watched": "Watched", "safe": "Safe"}.get(safety, "Safe")

    def road_safety_color(self, coord=None) -> tuple[int, int, int]:
        safety = self.road_safety_for_town(coord)
        return {
            "contested": (200, 80, 60),
            "watched": (200, 180, 80),
            "safe": (80, 160, 100),
        }.get(safety, (80, 160, 100))

    def road_pressure_npc_line(self) -> str:
        """Return a contextual line for NPCs in towns under road pressure."""
        safety = self.road_safety_for_town()
        coord_key = f"{self.world_position[0]},{self.world_position[1]}"
        was_raided = coord_key in self._raided_log()
        if safety == "contested":
            if was_raided:
                return random.choice([
                    "They hit us while the roads were down. We're still putting things back together.",
                    "The raid set us back more than I'd like to admit. Roads need clearing.",
                    "We took losses when the routes went dark. Something has to change.",
                ])
            return random.choice([
                "The roads east have been rough lately. Caravans are holding off.",
                "We've had reports of movement in the hills. The routes aren't safe.",
                "I wouldn't head out without knowing what's on the roads right now.",
                "The notice board has something about the situation if you haven't looked.",
            ])
        if safety == "watched":
            return random.choice([
                "The roads have been quieter since someone dealt with that camp.",
                "Still cautious out there, but it's better than it was.",
                "Word is the situation on the road has improved. Patrols are back.",
            ])
        return ""

    def town_under_threat(self, coord=None) -> bool:
        return self.road_safety_for_town(coord) == "contested"

    # ── Pressure propagation ────────────────────────────────────────────────

    _RAID_THRESHOLD = 5  # contested visits before a raid fires

    def _pressure_log(self) -> dict:
        if not hasattr(self, "_road_pressure_ticks"):
            self._road_pressure_ticks: dict = {}
        return self._road_pressure_ticks

    def _raided_log(self) -> set:
        if not hasattr(self, "_raided_towns"):
            self._raided_towns: set = set()
        return self._raided_towns

    def road_pressure_tick(self) -> None:
        """Called on each town arrival. Tracks sustained threat pressure and triggers raids."""
        coord = self.world_position
        coord_key = f"{coord[0]},{coord[1]}"
        safety = self.road_safety_for_town(coord)
        pressure = self._pressure_log()
        if safety == "contested":
            pressure[coord_key] = pressure.get(coord_key, 0) + 1
            if pressure[coord_key] >= self._RAID_THRESHOLD and coord_key not in self._raided_log():
                self._trigger_raid(coord, coord_key)
        else:
            # Recovery: reduce pressure each safe/watched visit
            if coord_key in pressure:
                pressure[coord_key] = max(0, pressure[coord_key] - 1)

    def _trigger_raid(self, coord: tuple, coord_key: str) -> None:
        self._raided_log().add(coord_key)
        town_name = self.region_name
        msg = f"Signs of a recent raid are visible in {town_name} — the roads have been contested too long."
        self.message = (self.message + " " + msg).strip()
        if hasattr(self, "add_world_note"):
            self.add_world_note(f"{town_name} suffered a raid after sustained road pressure.", coord=coord, kind="raid")
        if hasattr(self, "increment_town_dimension"):
            self.increment_town_dimension("prosperity", coord=coord, amount=-1)

    # ── Wildlife pressure ───────────────────────────────────────────────────

    _WILDLIFE_BIOMES = {
        "forest":   ("wolf packs", [
            "Wolves have been coming in close at night. More than usual for this time of year.",
            "The hunters say the forest packs are moving. Something's pushing them toward us.",
            "We've lost two chickens to the wood-edge this week. The forest is restless.",
        ]),
        "swamp":    ("bog crawlers", [
            "Things from the marsh have been seen on the near road. Watch yourself out there.",
            "The bog edge is active — whatever lives in there is ranging further than normal.",
            "Travelers from the south have been reporting creatures on the road. Bog season.",
        ]),
        "volcanic": ("ember sprites", [
            "Ash-born things drift in when the wind changes. Unpleasant this time of year.",
            "The volcanic edge has been active. Some of what lives there wanders when it does.",
            "We've had flare-ups on the south edge. Ember sprites. Annoying and dangerous.",
        ]),
        "badlands": ("canyon predators", [
            "The badlands send things our way in the dry season. Nothing organized, just hungry.",
            "Raiders and worse come out of the canyon when it gets lean out there.",
            "Badlands pressure goes up every few months. We've been expecting this.",
        ]),
        "tundra":   ("frost stalkers", [
            "The cold season brings things down from the frost. Keep an eye on the north road.",
            "Frost stalkers have been spotted near the treeline. It's that time again.",
            "The tundra pushes its hunters south when the pickings get thin up there.",
        ]),
        "mountain": ("highland brutes", [
            "Something big has been moving in the high rocks. The pass watchers flagged it.",
            "Mountain hunters come down when the high routes freeze over. That's now.",
            "The elevation breeds things with patience. They're ranging low right now.",
        ]),
        "plains":   ("plains drifters", [
            "Something's been following the open road in. Not organized, just persistent.",
            "The wide ground to the west is drawing pressure toward us this season.",
            "Plains hunters drift in when there's not enough prey further out.",
        ]),
        "desert":   ("dune hunters", [
            "The dry stretch to the east is sending things our way. Hungry and lean.",
            "Sand-side creatures range toward water in dry season. We're the nearest source.",
            "Dune predators have been spotted on the near road. Keep your wits.",
        ]),
    }
    _WILDLIFE_SEASON_LENGTH = 20  # world_steps per season; pressure active every other season

    def wildlife_pressure_adjacent_biomes(self, coord=None) -> list[str]:
        coord = coord or self.world_position
        regions = self.world_map_regions()
        biomes = []
        for delta in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (coord[0] + delta[0], coord[1] + delta[1])
            state = regions.get(neighbor)
            if state:
                biomes.append(state.get("region_type", ""))
        return biomes

    def wildlife_pressure_npc_line(self) -> str:
        """Return a wildlife pressure line if seasonal conditions and security are low."""
        steps = getattr(self, "world_steps", 0)
        season = (steps // self._WILDLIFE_SEASON_LENGTH) % 2
        if season == 0:
            return ""  # off-season
        dims = self.town_dimensions() if hasattr(self, "town_dimensions") else {}
        if dims.get("security", 0) >= 3:
            return ""  # secure town has counter-measures
        adjacent = self.wildlife_pressure_adjacent_biomes()
        for biome in adjacent:
            if biome in self._WILDLIFE_BIOMES:
                _, lines = self._WILDLIFE_BIOMES[biome]
                return random.choice(lines)
        return ""

    def road_pressure_level(self, coord=None) -> int:
        """Return current pressure tick count for a town (0 = none, ≥ threshold = raided)."""
        coord = coord or self.world_position
        coord_key = f"{coord[0]},{coord[1]}"
        return self._pressure_log().get(coord_key, 0)
