from __future__ import annotations

import hashlib

from ..models import Quest
from ..game_typing import GameMixinBase


class QuestGenerationMixin(GameMixinBase):

    def chain_objective_kind(self, target_region_name, landmark_name, danger_tier, seed_value):
        if landmark_name:
            if danger_tier >= 3 and seed_value % 4 == 0:
                return "hunt"
            if seed_value % 3 == 0:
                return "survey"
            return "recover"
        if danger_tier >= 2 and seed_value % 2 == 0:
            return "hunt"
        return "survey"

    def _board_quest_delivery(self, wx, wy, slot):
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"delivery:{self.world_seed}:{wx}:{wy}:{slot}:{cycle}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 2 + 1
        to_pos = (wx + dx * dist, wy + dy * dist)
        dir_name = self._QUEST_DIR_NAMES[(dx, dy)]
        key, name, desc, _ = self._DELIVERY_ITEMS[h % len(self._DELIVERY_ITEMS)]
        reward = 20 + (h % 6) * 10 + self.town_quest_reward_bonus((wx, wy))
        delivery_state = self.quest_preview_region_state(to_pos)
        region_name = delivery_state.get("region_name", f"a settlement to the {dir_name}")
        d_region_type = delivery_state.get("region_type", "")
        d_danger_tier = max(1, int(delivery_state.get("danger_tier", 1)))
        return Quest(
            id=f"delivery_{wx}_{wy}_{slot}_{cycle}",
            kind="delivery",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=region_name,
            item_key=key,
            item_name=name,
            description=self.delivery_description(desc, region_name, dir_name, h, region_type=d_region_type, danger_tier=d_danger_tier),
            reward_gold=reward,
            target_region_name=region_name,
            origin_town_name=self.region_name,
        )

    def _board_quest_scout(self, wx, wy, slot):
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"scout:{self.world_seed}:{wx}:{wy}:{slot}:{cycle}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 3 + 1
        to_pos = (wx + dx * dist, wy + dy * dist)
        dir_name = self._QUEST_DIR_NAMES[(dx, dy)]
        region_name, landmark_name, landmark_kind = self.scout_target_details(to_pos, h)
        _sname, _stype, _sobj, s_danger = self.bounty_target_details(to_pos)
        reward = 20 + (h % 5) * 5 + self.town_quest_reward_bonus((wx, wy))
        description = self.scout_description(region_name, dir_name, landmark_name, h, landmark_kind=landmark_kind, region_type=_stype, danger_tier=s_danger)
        return Quest(
            id=f"scout_{wx}_{wy}_{slot}_{cycle}",
            kind="scout",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=region_name,
            item_key="",
            item_name="",
            description=description,
            reward_gold=reward,
            target_region_name=region_name,
            target_landmark_name=landmark_name,
            target_landmark_kind=landmark_kind,
            origin_town_name=self.region_name,
        )

    def _board_quest_bounty(self, wx, wy, slot):
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"bounty:{self.world_seed}:{wx}:{wy}:{slot}:{cycle}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 2 + 1
        to_pos = (wx + dx * dist, wy + dy * dist)
        region_name, _region_type, objective, danger_tier = self.bounty_target_details(to_pos)
        target = max(4, 3 + danger_tier * 2 + (h % 4))
        reward = 18 + target * (3 + danger_tier) + self.town_quest_reward_bonus((wx, wy))
        return Quest(
            id=f"bounty_{wx}_{wy}_{slot}_{cycle}",
            kind="bounty",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=region_name,
            item_key="",
            item_name="",
            description=self.bounty_description(region_name, self.quest_direction_name((wx, wy), to_pos), objective, _region_type, h, danger_tier=danger_tier),
            reward_gold=reward,
            target_count=target,
            target_region_name=region_name,
            origin_town_name=self.region_name,
        )

    def _board_quest_chain(self, wx, wy, slot):
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"chain:{self.world_seed}:{wx}:{wy}:{slot}:{cycle}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 2 + 1
        to_pos = (wx + dx * dist, wy + dy * dist)
        dir_name = self._QUEST_DIR_NAMES[(dx, dy)]
        region_name, landmark_name, landmark_kind = self.scout_target_details(to_pos, h)
        _name, _region_type, _objective, danger_tier = self.bounty_target_details(to_pos)
        reward = 25 + (h % 5) * 10 + self.town_quest_reward_bonus((wx, wy))
        objective_key = self.chain_objective_kind(region_name, landmark_name, danger_tier, h)
        target_count = 0
        if landmark_name:
            lead_template, supply_kind, evidence_name = self._CHAIN_LEADS[h % len(self._CHAIN_LEADS)]
            description = self.chain_description(landmark_name, region_name, dir_name, lead_template, h)
        else:
            lead_template, supply_kind, evidence_name = self._CHAIN_FALLBACK_LEADS[h % len(self._CHAIN_FALLBACK_LEADS)]
            description = self.chain_fallback_description(region_name, dir_name, lead_template, h)
        if objective_key == "survey":
            description += " A broad survey of the area will do."
        elif objective_key == "hunt":
            target_count = max(2, min(5, 1 + danger_tier + (h % 2)))
            description += f" Thin out {target_count} local threats before you head back."
        return Quest(
            id=f"chain_{wx}_{wy}_{slot}_{cycle}",
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
            origin_town_name=self.region_name,
        )
