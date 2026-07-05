from __future__ import annotations

import random

from ..constants import COLOR_FRIEND
from ..game_typing import GameMixinBase
from ..models import Resident


_WANDERING_NPC_TYPES = {
    "merchant": {
        "kind": "wandering_merchant",
        "color": (255, 210, 100),
        "marker": "settler",
        "title": "Wandering Merchant",
        "dialogue": (
            "I carry things the towns haven't seen yet.",
            "A rare find now and then keeps the road worth walking.",
            "Not everything I carry was easy to get.",
        ),
    },
    "lorekeeper": {
        "kind": "lorekeeper",
        "color": (180, 160, 240),
        "marker": "shaman",
        "title": "Lorekeeper",
        "dialogue": (
            "I've walked this world longer than most remember.",
            "The old sites hold more than people think.",
            "Ask what you will. I keep records.",
        ),
    },
}

_VALID_BIOMES = {
    "plains", "farmland", "forest", "desert", "swamp",
    "mountain", "badlands", "tundra", "volcanic",
}


class RareNPCsMixin(GameMixinBase):

    def generate_wandering_npcs(self) -> dict:
        """Seed 3-5 world positions per world where a rare NPC lives."""
        result: dict[str, str] = {}
        with self.seed_scope("wandering_npcs"):
            npc_count = random.randint(3, 5)
            types = list(_WANDERING_NPC_TYPES.keys())
            for i in range(npc_count):
                x = random.randint(-12, 12)
                y = random.randint(-12, 12)
                if abs(x) + abs(y) < 3:
                    continue
                key = f"{x},{y}"
                if key not in result:
                    result[key] = types[i % len(types)]
        return result

    def wandering_npc_at(self, world_pos) -> dict | None:
        """Return NPC spec if a wandering NPC is seeded at this world position."""
        key = f"{world_pos[0]},{world_pos[1]}"
        npc_type = getattr(self, "wandering_npcs", {}).get(key)
        if npc_type is None:
            return None
        return _WANDERING_NPC_TYPES.get(npc_type)

    def maybe_spawn_wandering_npc(self):
        """Called from spawn_residents — adds wandering NPC if one is seeded here."""
        if self.region_type not in _VALID_BIOMES:
            return
        spec = self.wandering_npc_at(self.world_position)
        if spec is None:
            return
        candidates = [
            t for t in self.floor_explorable_tiles
            if t != self.player and t != self.entrance
        ]
        if not candidates:
            return
        with self.seed_scope("wandering_npc_pos", self.world_position):
            pos = random.choice(candidates)
        self.residents.append(Resident(
            pos, spec["kind"], spec["color"], spec["marker"],
            spec["title"], spec["dialogue"], "wander", pos, self.region_name,
        ))
