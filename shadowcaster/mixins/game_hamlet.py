from __future__ import annotations

from ..game_typing import GameMixinBase
from ..regions import palette_for_region, random_region_name


class HamletMixin(GameMixinBase):

    # ── World notes ────────────────────────────────────────────────────────

    def _world_notes_log(self) -> list:
        if not hasattr(self, "_world_notes"):
            self._world_notes: list = []
        return self._world_notes

    def add_world_note(self, text: str, coord=None, kind: str = "event") -> None:
        self._world_notes_log().append({
            "text": text,
            "coord": list(coord) if coord else None,
            "kind": kind,
            "step": getattr(self, "world_steps", 0),
        })

    # ── Hamlet seeding ─────────────────────────────────────────────────────

    def _hamlet_log(self) -> dict:
        if not hasattr(self, "_town_hamlets"):
            self._town_hamlets: dict = {}
        return self._town_hamlets

    def hamlet_coord_for_town(self, coord=None) -> tuple | None:
        key = self.region_key(coord or self.world_position)
        return self._hamlet_log().get(key)

    def seed_hamlet_if_eligible(self, coord=None) -> bool:
        coord = coord or self.world_position
        parent_key = self.region_key(coord)
        if parent_key in self._hamlet_log():
            return False
        exp = self.expansion_status(coord)
        if not exp["satellite_eligible"]:
            return False
        viable = self.viable_expansion_directions(coord)
        if not viable:
            return False
        non_slow = [(d, c, s) for d, c, s in viable if not s]
        _, hamlet_coord, _ = (non_slow or viable)[0]
        hamlet_key = self.region_key(hamlet_coord)
        if hamlet_key in self.world_regions:
            return False
        parent_name = self.region_name
        hamlet_name = random_region_name("hamlet") or f"{parent_name} Outpost"
        self._hamlet_log()[parent_key] = hamlet_coord
        self.world_regions[hamlet_key] = {
            "region_type": "hamlet",
            "region_name": hamlet_name,
            "region_palette": palette_for_region("town"),
            "danger_tier": max(1, self.danger_tier - 1),
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
            "hamlet_placeholder": True,
            "parent_town_key": parent_key,
        }
        msg = f"{hamlet_name} has been established nearby — a new outpost of {parent_name}."
        self.message = (self.message + " " + msg).strip()
        if hasattr(self, "add_world_note"):
            self.add_world_note(f"{hamlet_name} founded as an outpost of {parent_name}.", coord=hamlet_coord, kind="hamlet_founded")
        return True

    # ── Hamlet fragility ───────────────────────────────────────────────────

    def _hamlet_security_log(self) -> dict:
        if not hasattr(self, "_hamlet_security"):
            self._hamlet_security: dict = {}
        return self._hamlet_security

    def hamlet_fragility_tick(self) -> None:
        """Decrement security for contested placeholder hamlets; abandon if exhausted."""
        _MAX_SECURITY = 3
        for parent_key, hamlet_coord in list(self._hamlet_log().items()):
            hamlet_key = self.region_key(hamlet_coord)
            state = self.world_regions.get(hamlet_key)
            if not state or not state.get("hamlet_placeholder"):
                continue
            safety = self.road_safety_for_town(hamlet_coord) if hasattr(self, "road_safety_for_town") else "safe"
            sec = self._hamlet_security_log().get(hamlet_key, _MAX_SECURITY)
            if safety == "contested":
                sec -= 1
                if sec <= 0:
                    self._abandon_hamlet(parent_key, hamlet_coord, hamlet_key)
                    continue
            else:
                sec = min(_MAX_SECURITY, sec + 1)
            self._hamlet_security_log()[hamlet_key] = sec

    def _abandon_hamlet(self, parent_key: str, hamlet_coord: tuple, hamlet_key: str) -> None:
        hamlet_name = self.world_regions.get(hamlet_key, {}).get("region_name", "the outpost")
        parent_name = self.world_regions.get(parent_key, {}).get("region_name", "")
        self.world_regions.pop(hamlet_key, None)
        self._hamlet_log().pop(parent_key, None)
        self._hamlet_security_log().pop(hamlet_key, None)
        if hasattr(self, "increment_town_dimension"):
            px, py = (int(v) for v in parent_key.split(","))
            self.increment_town_dimension("prosperity", coord=(px, py), amount=-1)
        msg = f"{hamlet_name} has been abandoned — the threat proved too great."
        if parent_name:
            msg += f" {parent_name} takes the loss."
        self.message = (self.message + " " + msg).strip()
        if hasattr(self, "add_world_note"):
            self.add_world_note(f"{hamlet_name} abandoned under sustained threat pressure.", coord=hamlet_coord, kind="hamlet_abandoned")

    def hamlet_security_for(self, hamlet_coord) -> int:
        hamlet_key = self.region_key(hamlet_coord)
        return self._hamlet_security_log().get(hamlet_key, 3)
