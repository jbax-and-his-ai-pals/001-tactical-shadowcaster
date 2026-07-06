from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..skills import (
    SKILL_REGISTRY, SKILL_ORDER,
    can_afford_next_rank, rank_cost, skill_rank, upgrade_skill,
)


class SkillsMixin(GameMixinBase):

    # ── Core spend / query ───────────────────────────────────────────────────

    def get_skill_rank(self, skill_key: str) -> int:
        return skill_rank(getattr(self, "player_skills", {}), skill_key)

    def spend_skill_point(self, skill_key: str) -> str:
        skills = getattr(self, "player_skills", {})
        points = getattr(self, "player_skill_points", 0)
        if not can_afford_next_rank(skills, points, skill_key):
            current = skills.get(skill_key, 0)
            spec = SKILL_REGISTRY.get(skill_key, {})
            if current >= spec.get("max_rank", 5):
                return f"{spec['name']} is already at max rank."
            cost = rank_cost(current + 1)
            return f"Need {cost} skill point{'s' if cost > 1 else ''} — you have {points}."
        new_rank, cost = upgrade_skill(skills, skill_key)
        self.player_skills = skills
        self.player_skill_points = points - cost
        spec = SKILL_REGISTRY[skill_key]
        return f"{spec['name']} raised to rank {new_rank}. ({self.player_skill_points} points remaining.)"

    # ── Combat skill effects ─────────────────────────────────────────────────

    def skill_melee_bonus(self) -> int:
        return self.get_skill_rank("swordsmanship")

    def skill_ranged_bonus(self) -> int:
        return self.get_skill_rank("archery")

    def skill_max_hp_bonus(self) -> int:
        return self.get_skill_rank("toughness") * 3

    def skill_damage_reduction(self) -> int:
        rank = self.get_skill_rank("toughness")
        return (1 if rank >= 3 else 0) + (1 if rank >= 5 else 0)

    def skill_parry_chance(self) -> float:
        rank = self.get_skill_rank("swordsmanship")
        return 0.15 if rank >= 4 else 0.0

    def skill_archery_free_shot(self) -> bool:
        """Returns True if this ranged shot should be free (ammo not spent)."""
        rank = self.get_skill_rank("archery")
        if rank < 3:
            return False
        count = getattr(self, "_archery_shot_count", 0) + 1
        self._archery_shot_count = count
        return count % 5 == 0

    def skill_stealth_bonus(self) -> int:
        """Bonus damage on the first melee attack after entering a region."""
        if getattr(self, "_stealth_ambush_used", True):
            return 0
        return self.get_skill_rank("stealth")

    def consume_stealth_ambush(self):
        self._stealth_ambush_used = True

    def reset_stealth_ambush(self):
        self._stealth_ambush_used = False

    # ── Economy skill effects ────────────────────────────────────────────────

    def skill_buy_discount(self) -> int:
        return self.get_skill_rank("bartering") * 2

    def skill_sell_bonus(self) -> int:
        return self.get_skill_rank("bartering")

    def skill_shop_ilvl_bonus(self) -> int:
        rank = self.get_skill_rank("bartering")
        if rank >= 5:
            return 4
        if rank >= 4:
            return 2
        return 0

    def skill_quest_gold_bonus(self, base_gold: int) -> int:
        rank = self.get_skill_rank("diplomacy")
        return int(base_gold * rank * 0.10)

    def skill_attitude_multiplier(self) -> float:
        """Multiplier applied to completed-quest counts for attitude scoring."""
        rank = self.get_skill_rank("diplomacy")
        if rank >= 3:
            return 1.0 + rank * 0.10
        return 1.0

    def skill_scavenge_gold(self) -> int:
        return self.get_skill_rank("scavenging")

    def skill_gem_drop_bonus(self) -> float:
        rank = self.get_skill_rank("scavenging")
        return rank * 0.01

    def skill_container_drop_bonus(self) -> float:
        return 1.5 if self.get_skill_rank("scavenging") >= 5 else 1.0

    # ── Knowledge skill effects ──────────────────────────────────────────────

    def skill_herbalism_sell_bonus(self) -> int:
        """Extra gold per herb unit when selling at market."""
        return self.get_skill_rank("herbalism")

    def skill_fieldcraft_node_bonus(self) -> int:
        """Extra harvest nodes when generating a region (fieldcraft rank 3+ = +1)."""
        rank = self.get_skill_rank("fieldcraft")
        return 1 if rank >= 3 else 0

    def skill_fieldcraft_speed_bonus(self) -> int:
        """Autoexplore interval reduction (ms) from fieldcraft."""
        return self.get_skill_rank("fieldcraft") * 10

    def skill_arcana_rank(self) -> int:
        return self.get_skill_rank("arcana")

    def skill_shows_quality(self) -> bool:
        return self.skill_arcana_rank() >= 1

    def skill_shows_affixes(self) -> bool:
        return self.skill_arcana_rank() >= 3

    def skill_arcana_region_bonus(self) -> bool:
        return self.skill_arcana_rank() >= 5

    # ── Lockpicking ──────────────────────────────────────────────────────────

    def can_attempt_lockpick(self, item) -> bool:
        return getattr(item, "lock_difficulty", 0) > 0

    def attempt_lockpick(self, item) -> str:
        rank = self.get_skill_rank("lockpicking")
        difficulty = getattr(item, "lock_difficulty", 1)
        if rank == 0:
            return "You have no lockpicking skill. Find a locksmith in town."
        if rank < difficulty:
            gap = difficulty - rank
            chance = max(0.10, 0.60 - gap * 0.15)
            if random.random() > chance:
                return f"Your pick slips. The {item.name} resists you. (Need rank {difficulty} to guarantee success.)"
        return self._lockpick_success(item)

    def _lockpick_success(self, item) -> str:
        from ..constants import COLOR_ITEM_CONSUMABLE as COLOR_CONSUMABLE
        from ..mixins.game_locksmith import LOCKED_CONTAINER_DEFS
        defn = LOCKED_CONTAINER_DEFS.get(item.key, {})
        item.quantity -= 1
        if item.quantity <= 0:
            self.inventory.remove(item)
        gold_min, gold_max = defn.get("loot_gold", (2, 8))
        found_gold = random.randint(gold_min, gold_max)
        self.gold += found_gold
        msg = f"You pick the {item.name} open. Inside: {found_gold}g"
        loot_key, loot_chance = defn.get("loot_item", ("medkit", 0))
        if random.random() < loot_chance * 0.7:
            loot_defs = {
                "medkit": {"name": "Healing Potion", "description": "Restores 4 HP when used.", "heal_amount": 4},
                "tonic":  {"name": "Ward Tonic",     "description": "Grants 6 turns of ward when used.", "ward_duration": 6},
            }
            ld = loot_defs.get(loot_key, {})
            if ld:
                self.add_item(loot_key, ld["name"], "consumable", COLOR_CONSUMABLE, loot_key,
                              description=ld.get("description", ""), heal_amount=ld.get("heal_amount", 0),
                              ward_duration=ld.get("ward_duration", 0), cleanses=False)
                msg += f" and a {ld['name']}!"
        else:
            msg += "."
        self.store_current_region()
        return msg

    # ── Alchemy ──────────────────────────────────────────────────────────────

    def can_brew_alchemy(self) -> bool:
        return self.get_skill_rank("alchemy") >= 1 and self.inventory_quantity("herbs") >= 1

    def brew_alchemy(self, brew_key: str = "medkit") -> str:
        rank = self.get_skill_rank("alchemy")
        if rank == 0:
            return "You have no alchemy skill."
        herbs = self.inventory_item("herbs")
        if herbs is None or herbs.quantity < 1:
            return "You have no herbs to brew with."
        from ..constants import COLOR_ITEM_CONSUMABLE as COLOR_CONSUMABLE, COLOR_ACCENT
        if brew_key == "tonic" and rank < 3:
            return "You need alchemy rank 3 to brew ward tonics."
        if brew_key == "elixir" and rank < 5:
            return "You need alchemy rank 5 to brew elixirs."
        herbs.quantity -= 1
        if herbs.quantity <= 0:
            self.inventory.remove(herbs)
        if brew_key == "tonic":
            qty = 1 + (1 if rank >= 4 else 0)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=qty, description="Clears statuses and grants ward.", ward_duration=6, cleanses=True)
            return f"You brew {'a tonic' if qty == 1 else '2 tonics'} from the herbs."
        if brew_key == "elixir":
            self.add_item("elixir", "Elixir of Vitality", "consumable", (255, 180, 80), "vitality",
                          quantity=1, description="Restores 8 HP and grants regen for 4 turns.",
                          heal_amount=8, ward_duration=0, cleanses=False)
            return "You distill an Elixir of Vitality from the herbs."
        qty = 1 + (1 if rank >= 2 else 0)
        self.add_item("medkit", "Healing Potion", "consumable", COLOR_CONSUMABLE, "vitality",
                      quantity=qty, description="Restores health.", heal_amount=4, cleanses=False)
        return f"You brew {'a potion' if qty == 1 else '2 potions'} from the herbs."

    # ── Trainer interaction ──────────────────────────────────────────────────

    def open_trainer(self, skill_key: str | None = None):
        self.trainer_open = True
        self.trainer_skill_key = skill_key
        # Start on first non-header row
        rows = self.trainer_skill_rows()
        start = 0
        for i, row in enumerate(rows):
            if not row.get("is_header"):
                start = i
                break
        self.trainer_skill_index = start

    def close_trainer(self):
        self.trainer_open = False
        self.trainer_skill_key = None

    def _trainer_move(self, delta: int):
        rows = self.trainer_skill_rows()
        if not rows:
            return
        idx = getattr(self, "trainer_skill_index", 0)
        idx = (idx + delta) % len(rows)
        # Skip header rows
        steps = 0
        while rows[idx].get("is_header") and steps < len(rows):
            idx = (idx + delta) % len(rows)
            steps += 1
        self.trainer_skill_index = idx

    def _trainer_confirm(self):
        rows = self.trainer_skill_rows()
        idx = getattr(self, "trainer_skill_index", 0)
        if not rows or idx >= len(rows):
            return
        row = rows[idx]
        if row.get("is_header"):
            return
        self.message = self.trainer_purchase(row["key"])

    def trainer_purchase(self, skill_key: str) -> str:
        skills = getattr(self, "player_skills", {})
        spec = SKILL_REGISTRY.get(skill_key, {})
        current = skills.get(skill_key, 0)
        max_rank = spec.get("max_rank", 5)
        if current >= max_rank:
            return f"{spec['name']} is already at max rank."
        gold_costs = {1: 15, 2: 30, 3: 60, 4: 100, 5: 150}
        cost = gold_costs.get(current + 1, 150)
        attitude = self.town_attitude_score() if hasattr(self, "town_attitude_score") else 0
        discount = min(20, attitude * 2)
        cost = max(1, cost - discount)
        if self.gold < cost:
            return f"Training costs {cost}g. (You have {self.gold}g.)"
        self.gold -= cost
        new_rank, _ = upgrade_skill(skills, skill_key)
        self.player_skills = skills
        return f"Trained {spec['name']} to rank {new_rank} for {cost}g."

    def trainer_skill_rows(self) -> list[dict]:
        rows = []
        skills = getattr(self, "player_skills", {})
        attitude = self.town_attitude_score() if hasattr(self, "town_attitude_score") else 0
        gold_costs = {1: 15, 2: 30, 3: 60, 4: 100, 5: 150}
        discount = min(20, attitude * 2)
        current_group = None
        for key in SKILL_ORDER:
            spec = SKILL_REGISTRY[key]
            group = spec.get("group", "")
            if group != current_group:
                current_group = group
                rows.append({"is_header": True, "label": f"── {group} ──", "key": None})
            current = skills.get(key, 0)
            max_rank = spec["max_rank"]
            raw = gold_costs.get(current + 1, 150)
            cost = max(1, raw - discount)
            rows.append({
                "key": key, "name": spec["name"], "rank": current,
                "max_rank": max_rank, "cost": cost,
                "description": spec.get("description", ""),
                "color": spec["color"],
            })
        return rows
