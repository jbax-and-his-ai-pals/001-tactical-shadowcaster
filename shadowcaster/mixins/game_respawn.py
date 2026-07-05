from __future__ import annotations

from ..game_typing import GameMixinBase
from ..systems import heuristic


class RespawnMixin(GameMixinBase):

    def record_shrine_visit(self):
        """Called when the player enters a shrine region. Adds to discovered_shrines."""
        pos = self.world_position
        if pos not in self.discovered_shrines:
            self.discovered_shrines.append(pos)

    def set_homepoint(self):
        """Mark the current shrine as the player's respawn homepoint."""
        pos = self.world_position
        self.record_shrine_visit()
        if self.homepoint_coord == pos:
            self.message = "This shrine is already your homepoint."
            return
        self.homepoint_coord = pos
        self.message = f"Homepoint set to {self.region_name}. You will respawn here if you fall."

    def _respawn_position(self) -> tuple:
        """Return the world_position the player should respawn at."""
        # Priority 1: explicit homepoint
        if self.homepoint_coord is not None:
            return self.homepoint_coord
        # Priority 2: nearest discovered shrine by world distance
        if self.discovered_shrines:
            origin = (0, 0)
            return min(self.discovered_shrines, key=lambda p: heuristic(p, origin))
        # Priority 3: origin
        return (0, 0)

    def _respawn_label(self, pos: tuple) -> str:
        if pos == self.homepoint_coord:
            key = self.region_key(pos)
            state = self.world_regions.get(key)
            name = state["region_name"] if state else "shrine"
            return f"homepoint shrine ({name})"
        if pos in self.discovered_shrines:
            key = self.region_key(pos)
            state = self.world_regions.get(key)
            name = state["region_name"] if state else "shrine"
            return f"discovered shrine ({name})"
        return "starting town"

    def trigger_death(self, cause: str):
        """Handle player death: record loss, mark for respawn."""
        self.game_over = True
        self.death_cause = cause
        self.death_gold_lost = self.gold
        respawn_pos = self._respawn_position()
        self.death_respawn_label = self._respawn_label(respawn_pos)
        self.stop_auto_movement()
        self.hovered_world_tile = None
        self.selected_inspect_tile = None
        self.message = f"You were slain by {self.death_cause}. {self.gold}g lost. Respawn at {self.death_respawn_label}."

    def respawn(self):
        """Execute respawn: drop gold, reset death region, move to respawn point."""
        if not self.game_over:
            return

        # Clear the death region's enemies in world_regions so it respawns fresh
        death_region_key = self.region_key(self.world_position)
        if death_region_key in self.world_regions:
            state = self.world_regions[death_region_key]
            state["enemies"] = []
            state["enemies_defeated"] = 0
            state["enemies_spawned"] = 0

        # Lose carried gold
        self.gold = 0

        # Restore health to half max
        self.health = max(1, self.max_health // 2)

        # Clear harmful statuses
        for s in ("poison", "burn"):
            if s in self.player_statuses:
                self.clear_player_status(s)

        # Move to respawn point
        respawn_pos = self._respawn_position()
        self.game_over = False
        self.death_cause = ""
        self.respawn_pending = True

        # Navigate to respawn world position
        self.store_current_region()
        self.world_position = respawn_pos
        region_key = self.region_key(respawn_pos)
        if region_key in self.world_regions:
            self.load_region_state(self.world_regions[region_key])
        else:
            self._generate_region_at(respawn_pos)

        self.respawn_pending = False
        self.close_menu()
        label = self.death_respawn_label or "the starting town"
        self.message = f"You recover at {label}, lighter by {self.death_gold_lost}g. The road waits."
        self.death_gold_lost = 0
        self.death_respawn_label = ""
        self.update_visibility()

    def _generate_region_at(self, pos):
        """Fallback: generate a fresh region at pos if not already in world_regions."""
        # Just reset to the origin floor via the existing generate_region path
        self.world_position = pos
        if hasattr(self, "generate_overworld_region"):
            self.generate_overworld_region(arrival_direction=None)
        else:
            # Last resort: respawn at (0,0) known start
            self.world_position = (0, 0)
            key = self.region_key((0, 0))
            if key in self.world_regions:
                self.load_region_state(self.world_regions[key])
