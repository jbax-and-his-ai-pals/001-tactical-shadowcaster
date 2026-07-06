from __future__ import annotations

from ..game_typing import GameMixinBase

# XP required to reach each level (cumulative)
XP_THRESHOLDS = {
    2: 10,
    3: 25,
    4: 50,
    5: 85,
}

LEVEL_TITLES = {
    1: "Wanderer",
    2: "Seasoned",
    3: "Experienced",
    4: "Veteran",
    5: "Master",
}

LEVEL_UNLOCKS = {
    2: "Trinket slot unlocked. Named elites begin appearing in the world.",
    3: "Reputation spreads. NPCs greet you by title. Harder board jobs appear at allied towns.",
    4: "Active ability unlocked. Choose your combat signature at level-up.",
    5: "Legendary sites become enterable. The named city's stronghold opens.",
}

# XP sources: key → (amount, description)
XP_SOURCES = {
    # region first-visit
    "biome_forest":       (1, "first forest visited"),
    "biome_swamp":        (1, "first swamp visited"),
    "biome_plains":       (1, "first plains visited"),
    "biome_farmland":     (1, "first farmland visited"),
    "biome_desert":       (1, "first desert visited"),
    "biome_mountain":     (1, "first mountain visited"),
    "biome_tundra":       (1, "first tundra visited"),
    "biome_volcanic":     (1, "first volcanic region visited"),
    "biome_cave":         (1, "first cave visited"),
    "biome_dungeon":      (1, "first dungeon visited"),
    "biome_ruins":        (1, "first ruins visited"),
    "biome_castle":       (1, "first castle visited"),
    "biome_badlands":     (1, "first badlands visited"),
    "biome_maze":         (1, "first maze visited"),
    "biome_monster_town": (2, "first monster town encountered"),
    "biome_ossuary":      (3, "first ossuary discovered"),
    "biome_mirrorwood":   (3, "first mirrorwood discovered"),
    # delve bottoms
    "delve_bottom_dungeon": (2, "first dungeon fully delved"),
    "delve_bottom_cave":    (2, "first cave fully delved"),
    "delve_bottom_ruins":   (2, "first ruins fully delved"),
    "delve_bottom_castle":  (2, "first castle fully delved"),
    # world distance milestones
    "dist_5":  (2, "ventured 5 regions from home"),
    "dist_8":  (3, "ventured 8 regions from home"),
    "dist_10": (4, "ventured 10 regions from home"),
    # quest milestones
    "quest_first_chain":       (2, "first chain quest completed"),
    "quest_first_social":      (2, "first cross-town social quest completed"),
    "quest_first_scout":       (1, "first scout quest completed"),
    "quest_first_bounty":      (1, "first bounty quest completed"),
    # attitude milestones
    "attitude_tier1_first": (2, "first town reached attitude tier 1"),
    "attitude_tier2_first": (3, "first town reached attitude tier 2"),
    # rare discoveries (set when triggered externally)
    "found_named_elite":    (3, "first named elite defeated"),
    "found_rare_region":    (3, "first rare region type entered"),
}


class XPMixin(GameMixinBase):

    def award_xp(self, source_key: str) -> bool:
        """Award XP for a one-time milestone. Returns True if XP was granted."""
        if source_key in self.xp_milestones_claimed:
            return False
        spec = XP_SOURCES.get(source_key)
        if spec is None:
            return False
        amount, description = spec
        self.xp_milestones_claimed.add(source_key)
        self.player_xp += amount
        self._check_level_up()
        return True

    def _check_level_up(self):
        if self.player_level >= 5:
            return
        next_level = self.player_level + 1
        threshold = XP_THRESHOLDS.get(next_level)
        if threshold is not None and self.player_xp >= threshold:
            self.player_level = next_level
            self.levelup_pending = next_level
            self._apply_level_unlock(next_level)

    def _apply_level_unlock(self, level: int):
        self.player_skill_points = getattr(self, "player_skill_points", 0) + 5
        gains = ["+5 Skill Points"]
        hp_bonus = self.skill_max_hp_bonus() if hasattr(self, "skill_max_hp_bonus") else 0
        if hp_bonus > 0:
            gains.append(f"Max HP: {self.max_health} (toughness bonus active)")
        unlock_text = LEVEL_UNLOCKS.get(level, "")
        if unlock_text:
            gains.append(unlock_text)
        self.levelup_gains = gains
        if level == 4 and hasattr(self, "pick_ability_choices"):
            self.pick_ability_choices()

    def xp_to_next_level(self) -> int | None:
        if self.player_level >= 5:
            return None
        return XP_THRESHOLDS.get(self.player_level + 1, 0) - self.player_xp

    def player_title(self) -> str:
        return LEVEL_TITLES.get(self.player_level, "Wanderer")

    # ── XP source triggers ───────────────────────────────────────────────────

    def xp_check_biome_visit(self):
        key = f"biome_{self.region_type}"
        if key in XP_SOURCES:
            self.award_xp(key)
        if self.region_type in ("ossuary", "mirrorwood"):
            self.award_xp("found_rare_region")

    def xp_check_world_distance(self):
        wx, wy = self.world_position
        dist = abs(wx) + abs(wy)
        for threshold, source_key in ((10, "dist_10"), (8, "dist_8"), (5, "dist_5")):
            if dist >= threshold:
                self.award_xp(source_key)
                break

    def xp_check_delve_bottom(self):
        rt = self.region_type
        key = f"delve_bottom_{rt}"
        if key in XP_SOURCES:
            self.award_xp(key)

    def xp_check_quest(self, quest):
        kind = getattr(quest, "kind", "")
        if kind == "chain" and not getattr(quest, "_is_social", False):
            self.award_xp("quest_first_chain")
        elif kind == "chain" and getattr(quest, "_is_social", False):
            self.award_xp("quest_first_social")
        elif kind == "scout":
            self.award_xp("quest_first_scout")
        elif kind == "bounty":
            self.award_xp("quest_first_bounty")

    def xp_check_attitude(self, world_pos):
        score = self.town_attitude_score(world_pos)
        if score >= 6:
            self.award_xp("attitude_tier2_first")
        elif score >= 1:
            self.award_xp("attitude_tier1_first")

    def dismiss_levelup(self):
        if getattr(self, "levelup_ability_choices", []):
            return  # must pick an ability first
        self.levelup_pending = 0
