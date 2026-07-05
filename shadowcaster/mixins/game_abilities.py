from __future__ import annotations

import random

from ..game_typing import GameMixinBase

ABILITY_POOL: dict[str, dict] = {
    "bloodthirst": {
        "name": "Bloodthirst",
        "description": "Killing an enemy restores 1 HP.",
        "flavor": "The fight sharpens you.",
    },
    "bulwark": {
        "name": "Bulwark",
        "description": "Taking melee damage grants 1 turn of ward.",
        "flavor": "Pain teaches you to guard.",
    },
    "tactician": {
        "name": "Tactician",
        "description": "Entering a new region grants +1 attack for 5 turns.",
        "flavor": "You read terrain like a language.",
    },
    "scavenger": {
        "name": "Scavenger",
        "description": "Hidden caches have a 25% chance to contain double items.",
        "flavor": "Thoroughness is its own reward.",
    },
    "ranger": {
        "name": "Ranger",
        "description": "Permanently increases your field of view by 1.",
        "flavor": "You see farther than most dare to look.",
    },
    "iron_nerve": {
        "name": "Iron Nerve",
        "description": "No single hit can deal more than 3 damage.",
        "flavor": "You've learned to roll with it.",
    },
}

_CHOICE_COUNT = 3


class AbilitiesMixin(GameMixinBase):

    def pick_ability_choices(self):
        already = getattr(self, "active_ability", "")
        pool = [k for k in ABILITY_POOL if k != already]
        with self.seed_scope("ability_choices", self.world_seed, self.player_xp):
            rng = random.Random()
        choices = rng.sample(pool, min(_CHOICE_COUNT, len(pool)))
        self.levelup_ability_choices = choices
        self.levelup_ability_index = 0

    def confirm_ability_choice(self, index: int):
        choices = getattr(self, "levelup_ability_choices", [])
        if not choices or index < 0 or index >= len(choices):
            return
        self.active_ability = choices[index]
        self.levelup_ability_choices = []
        self.levelup_ability_index = 0
        self.levelup_pending = 0
        spec = ABILITY_POOL.get(self.active_ability, {})
        self.message = f"Ability unlocked: {spec.get('name', self.active_ability)}. {spec.get('flavor', '')}"

    # ── Passive hooks (called from other mixins) ─────────────────────────────

    def ability_on_kill(self):
        if getattr(self, "active_ability", "") == "bloodthirst":
            if self.health < self.max_health:
                self.health = min(self.max_health, self.health + 1)

    def ability_on_hit_received(self, raw_damage: int) -> int:
        """Called before damage is applied. Returns possibly-capped damage."""
        ability = getattr(self, "active_ability", "")
        if ability == "iron_nerve":
            raw_damage = min(raw_damage, 3)
        if ability == "bulwark" and raw_damage > 0:
            self.add_status(self.player_statuses, "ward", 1)
        return raw_damage

    def ability_on_region_enter(self):
        if getattr(self, "active_ability", "") == "tactician":
            self.add_status(self.player_statuses, "fortify_attack", 5)

    def ability_light_bonus(self) -> int:
        return 1 if getattr(self, "active_ability", "") == "ranger" else 0

    def ability_cache_double_chance(self) -> bool:
        return getattr(self, "active_ability", "") == "scavenger" and random.random() < 0.25
