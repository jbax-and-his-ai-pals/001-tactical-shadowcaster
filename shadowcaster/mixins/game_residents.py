from __future__ import annotations

import random
import time

from ..constants import COLOR_FRIEND, COLOR_FRIEND_ANIMAL, FLAVOR_REGION_TYPES
from ..game_typing import GameMixinBase
from ..models import Resident
from ..resident_data import FLAVOR_RESIDENTS
from ..systems import can_step, heuristic


class ResidentsMixin(GameMixinBase):

    def _service_adjacent_tile(self, spot):
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            candidate = (spot[0] + dx, spot[1] + dy)
            if not self.dungeon.is_blocked(*candidate):
                return candidate
        return None

    def spawn_residents(self):
        self.residents = []
        if self.region_type in {"inn", "clinic", "supply", "shrine", "smith", "cartographer", "tavern", "chapel", "stable"}:
            spot = getattr(self.dungeon, "metadata", {}).get("service_spot")
            if spot:
                service_npcs = {
                    "inn":          ("innkeeper",   COLOR_FRIEND, "inn",          "Innkeeper",       ("The sheets are fresh and the fire is warm.", "Stay a moment. Even wanderers need rest.")),
                    "clinic":       ("medic",        COLOR_FRIEND, "clinic",       "Medic",           ("Hold still. Let me take care of those wounds.", "You're steadier once the bandages are set.")),
                    "supply":       ("merchant",     COLOR_FRIEND, "supply",       "Provisioner",     ("Travel light, but never empty.", "If the free bundle is gone, we can still barter.", "A little stock now saves a lot of regret later.")),
                    "shrine":       ("caretaker",    COLOR_FRIEND, "shrine",       "Caretaker",       ("Walk gently. Old blessings still answer here.", "The road bites less sharply when you carry a ward.")),
                    "smith":        ("smith",         COLOR_FRIEND, "smith",        "Smith",           ("Steel and will both need tending.", "If you're heading back out, go with a steadier hand.")),
                    "cartographer": ("surveyor",     COLOR_FRIEND, "cartographer", "Surveyor",        ("The frontier opens up once you've charted its edges.", "Roads are easier to trust when you know what lies beyond them.")),
                    "tavern":       ("barkeep",      COLOR_FRIEND, "tavern",       "Barkeep",         ("Word travels fast through a good bar.", "Rest the feet, rest the mind.", "Travelers keep this place alive.")),
                    "chapel":       ("chaplain",     COLOR_FRIEND, "chapel",       "Chaplain",        ("May the road treat you kindly.", "Blessings run deep when the road runs long.", "Light a thought for those still out there.")),
                    "stable":       ("stablehand",   COLOR_FRIEND, "stable",       "Stable Hand",     ("Good horses know the back roads.", "A rested mount and a clear sky — that's all you need.", "I can point you toward routes the maps miss.")),
                }
                kind, color, marker, title, dialogue = service_npcs[self.region_type]
                npc_pos = self._service_adjacent_tile(spot) or spot
                self.residents.append(Resident(npc_pos, kind, color, marker, title, dialogue, "stationary", npc_pos, self.region_name))
            return
        if self.region_type in FLAVOR_REGION_TYPES:
            self._spawn_flavor_building_residents()
            return
        if self.region_type != "town":
            if hasattr(self, "maybe_spawn_wandering_npc"):
                self.maybe_spawn_wandering_npc()
            return
        metadata = getattr(self.dungeon, "metadata", {})
        size = metadata.get("settlement_size", "hamlet")
        plaza = metadata.get("town_square", self.player)
        town_paths = set(metadata.get("town_paths", set()))
        parent_biome = metadata.get("town_parent_biome", "plains")
        occupied_positions = set()
        residents = self._spawn_town_residents(size, plaza, town_paths, parent_biome, occupied_positions)
        self.residents.extend(residents)

    def _spawn_flavor_building_residents(self):
        pool = FLAVOR_RESIDENTS.get(self.region_type, [])
        if not pool or random.random() < 0.30:
            return
        count = 1 if random.random() < 0.65 else min(2, len(pool))
        candidates = [t for t in self.floor_explorable_tiles if t != self.player]
        random.shuffle(candidates)
        for kind, marker, title, dialogue in pool[:count]:
            if not candidates:
                break
            pos = candidates.pop()
            self.residents.append(Resident(pos, kind, COLOR_FRIEND, marker, title, dialogue, "wander", pos, self.region_name))

    def get_resident_at(self, position):
        return next((resident for resident in self.residents if resident.position == position), None)

    def move_residents(self):
        _t = time.perf_counter()
        if not self.residents:
            if self.perf_overlay:
                self.perf_timings["npc_ms"] = 0.0
            return
        town_paths = set(getattr(self.dungeon, "metadata", {}).get("town_paths", set())) if self.region_type == "town" else set()
        occupied = {enemy.position for enemy in self.enemies}
        occupied.add(self.player)
        if self.stairs:
            occupied.add(self.stairs)
        if self.upgrade_pickup:
            occupied.add(self.upgrade_pickup.position)
        if self.heal_pickup:
            occupied.add(self.heal_pickup)
        for resident in self.residents:
            occupied.add(resident.position)
        for resident in self.residents:
            if resident.behavior == "stationary":
                continue
            if random.random() < 0.45 and resident.behavior != "patrol":
                continue
            occupied.discard(resident.position)
            options = []
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                next_pos = (resident.position[0] + dx, resident.position[1] + dy)
                if next_pos in occupied:
                    continue
                if can_step(self.dungeon, resident.position, next_pos):
                    if town_paths and resident.behavior in {"plaza", "homebound", "patrol"} and next_pos not in town_paths:
                        continue
                    if resident.behavior == "plaza" and resident.anchor and heuristic(next_pos, resident.anchor) > 4:
                        continue
                    if resident.behavior == "homebound" and resident.anchor and heuristic(next_pos, resident.anchor) > 3:
                        continue
                    options.append(next_pos)
            if resident.behavior == "patrol" and resident.patrol_points:
                if resident.position == resident.patrol_points[resident.patrol_index % len(resident.patrol_points)]:
                    resident.patrol_index = (resident.patrol_index + 1) % len(resident.patrol_points)
                target = resident.patrol_points[resident.patrol_index % len(resident.patrol_points)]
                if options:
                    resident.position = min(options, key=lambda option: (heuristic(option, target), random.random()))
            elif options:
                resident.position = random.choice(options)
            occupied.add(resident.position)
        if self.perf_overlay:
            self.perf_timings["npc_ms"] = (time.perf_counter() - _t) * 1000
