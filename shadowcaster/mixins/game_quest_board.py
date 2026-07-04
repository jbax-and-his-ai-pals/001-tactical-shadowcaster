from __future__ import annotations

import hashlib

from ..game_typing import GameMixinBase
from ..models import Quest


class QuestBoardMixin(GameMixinBase):
    _PRIORITY_THEME_DATA = {
        "watch": {
            "leads": [
                ("The watch at {civic} is only posting this for proven hands. {landmark} in {region} needs a hard look.", "tonic", "a captain's field brief"),
                ("A senior watcher wants the road near {landmark} in {region} tested before word reaches all of {town}.", "intel", "a watch report bundle"),
            ],
            "fallback": [
                ("The watch at {civic} needs a disciplined sweep of {region}. Only trusted help is being asked.", "tonic", "a sealed watch ledger"),
            ],
            "objectives": ("hunt", "recover"),
        },
        "survey": {
            "leads": [
                ("The hall at {civic} is only posting this for proven hands. {landmark} in {region} needs a proper field report.", "intel", "a sealed survey packet"),
                ("Trusted runners are wanted to verify routes near {landmark} in {region} before {town} posts fresh guidance.", "intel", "a marked route ledger"),
            ],
            "fallback": [
                ("The council meeting at {civic} needs a careful sweep of {region}. Only trusted help is being asked.", "intel", "a survey folio"),
            ],
            "objectives": ("survey", "recover"),
        },
        "relief": {
            "leads": [
                ("Trusted hands are needed near {landmark} in {region}. Bring back something that will help {work} prepare.", "medkit", "a relief satchel"),
                ("A careful run to {landmark} in {region} could bring back badly needed supplies or proof for {town}.", "ammo", "a relief dispatch"),
            ],
            "fallback": [
                ("Word from {region} matters to the stores at {work}. Bring back a proper account.", "medkit", "a sealed dispatch roll"),
            ],
            "objectives": ("recover", "survey"),
        },
    }

    def town_quest_reward_bonus(self, coord):
        score = self.town_attitude_score(coord)
        base = min(24, score * 3)
        track = self.dominant_track()
        if track and track[0] == "Warden":
            base += 12 if track[1] >= 2 else 5
        return base

    def town_quest_slots(self, coord):
        score = self.town_attitude_score(coord)
        if score >= 6:
            return 5
        if score >= 1:
            return 4
        return 3

    def board_builders_for_attitude(self, coord):
        score = self.town_attitude_score(coord)
        if score >= 6:
            return [self._board_quest_delivery, self._board_quest_scout, self._board_quest_bounty, self._board_quest_chain]
        if score >= 1:
            return [self._board_quest_delivery, self._board_quest_scout, self._board_quest_chain]
        return [self._board_quest_delivery, self._board_quest_scout]

    def is_priority_quest(self, quest) -> bool:
        quest_id = quest if isinstance(quest, str) else getattr(quest, "id", "")
        return isinstance(quest_id, str) and quest_id.startswith("priority_")

    def priority_theme_key(self, seed_value):
        names = " ".join(building["name"].lower() for building in self.town_building_data())
        candidates = []
        if any(term in names for term in ("watch", "hall", "gate")):
            candidates.append("watch")
        if any(term in names for term in ("cartographer", "survey", "shrine", "chapel", "library")):
            candidates.append("survey")
        if any(term in names for term in ("granary", "barn", "market", "store", "stable", "clinic")):
            candidates.append("relief")
        if not candidates:
            biome = self.town_biome_context()
            if biome in {"mountain", "badlands", "volcanic"}:
                candidates.append("watch")
            elif biome in {"farmland", "plains", "tundra"}:
                candidates.append("relief")
            else:
                candidates.append("survey")
        return candidates[seed_value % len(candidates)]

    def _board_quest_priority(self, wx, wy, slot):
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"priority:{self.world_seed}:{wx}:{wy}:{slot}:{cycle}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 2 + 2
        to_pos = (wx + dx * dist, wy + dy * dist)
        dir_name = self._QUEST_DIR_NAMES[(dx, dy)]
        region_name, landmark_name, landmark_kind = self.scout_target_details(to_pos, h)
        _name, _region_type, _objective, danger_tier = self.bounty_target_details(to_pos)
        theme_key = self.priority_theme_key(h)
        theme_data = self._PRIORITY_THEME_DATA[theme_key]
        allowed_objectives = list(theme_data["objectives"])
        if "hunt" in allowed_objectives and danger_tier < 3:
            allowed_objectives = [key for key in allowed_objectives if key != "hunt"] or ["recover"]
        objective_key = allowed_objectives[h % len(allowed_objectives)]
        reward = 60 + (h % 6) * 10 + self.town_quest_reward_bonus((wx, wy)) + danger_tier * 6
        target_count = 0
        if landmark_name:
            lead_template, supply_kind, evidence_name = theme_data["leads"][h % len(theme_data["leads"])]
            description = self.chain_description(landmark_name, region_name, dir_name, lead_template, h)
        else:
            lead_template, supply_kind, evidence_name = theme_data["fallback"][h % len(theme_data["fallback"])]
            description = self.chain_fallback_description(region_name, dir_name, lead_template, h)
        if objective_key == "survey":
            description += " Make a thorough survey before you return."
        elif objective_key == "hunt":
            target_count = max(4, min(7, 2 + danger_tier + (h % 2)))
            description += f" Break {target_count} threats on the way and return with {evidence_name}."
        else:
            description += f" Return with {evidence_name} and a clean account."
        return Quest(
            id=f"priority_{wx}_{wy}_{slot}_{cycle}",
            kind="chain",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=region_name,
            item_key=supply_kind,
            item_name=evidence_name,
            description=description,
            reward_gold=reward,
            target_count=target_count,
            target_region_name=region_name,
            target_landmark_name=landmark_name,
            target_landmark_kind=landmark_kind,
            objective_key=objective_key,
            theme_key=theme_key,
            origin_town_name=self.region_name,
        )
