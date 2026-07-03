from __future__ import annotations

import hashlib

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..models import Quest
from .game_quest_text import QuestTextMixin


class QuestsMixin(QuestTextMixin):
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
        reward = 20 + (h % 6) * 10
        region_name = self.quest_preview_region_state(to_pos).get("region_name", f"a settlement to the {dir_name}")
        return Quest(
            id=f"delivery_{wx}_{wy}_{slot}_{cycle}",
            kind="delivery",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=region_name,
            item_key=key,
            item_name=name,
            description=self.delivery_description(desc, region_name, dir_name),
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
        reward = 20 + (h % 5) * 5
        description = self.scout_description(region_name, dir_name, landmark_name)
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
        reward = 18 + target * (3 + danger_tier)
        return Quest(
            id=f"bounty_{wx}_{wy}_{slot}_{cycle}",
            kind="bounty",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=region_name,
            item_key="",
            item_name="",
            description=f"Travel to {region_name} to the {self.quest_direction_name((wx, wy), to_pos)}, {objective}, then return to {self.region_name}.",
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
        reward = 25 + (h % 5) * 10
        objective_key = self.chain_objective_kind(region_name, landmark_name, danger_tier, h)
        target_count = 0
        if landmark_name:
            lead_template, supply_kind, evidence_name = self._CHAIN_LEADS[h % len(self._CHAIN_LEADS)]
            description = self.chain_description(landmark_name, region_name, dir_name, lead_template)
        else:
            lead_template, supply_kind, evidence_name = self._CHAIN_FALLBACK_LEADS[h % len(self._CHAIN_FALLBACK_LEADS)]
            description = self.chain_fallback_description(region_name, dir_name, lead_template)
        if objective_key == "survey":
            description += f" A broad survey of the area will do."
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

    def generate_board_quests(self) -> list:
        if self.region_type != "town":
            return []
        wx, wy = self.world_position
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"board:{self.world_seed}:{wx}:{wy}:{cycle}".encode()).hexdigest(), 16)
        builders = [self._board_quest_delivery, self._board_quest_scout, self._board_quest_bounty]
        quests = [self._board_quest_chain(wx, wy, 0)]
        for slot in range(1, 5):
            idx = (h >> (slot * 3)) % len(builders)
            quests.append(builders[idx](wx, wy, slot))
        return quests

    def open_notice_board(self):
        self.refresh_notice_board(keep_selection=False)
        self.notice_board_open = True
        self.notice_board_scroll = 0
        self.stop_auto_movement()

    def close_notice_board(self):
        self.notice_board_open = False
        self.notice_board_quests = []
        self.notice_board_scroll = 0

    def refresh_notice_board(self, keep_selection=True):
        selected_id = None
        if keep_selection and self.notice_board_quests and 0 <= self.notice_board_index < len(self.notice_board_quests):
            selected_id = self.notice_board_quests[self.notice_board_index].id
        self.notice_board_quests = self.generate_board_quests()
        if not self.notice_board_quests:
            self.notice_board_index = 0
            return
        if selected_id is not None:
            matching_index = next((i for i, quest in enumerate(self.notice_board_quests) if quest.id == selected_id), None)
            if matching_index is not None:
                self.notice_board_index = matching_index
                self.ensure_notice_board_selection_visible()
                return
        self.notice_board_index = max(0, min(self.notice_board_index, len(self.notice_board_quests) - 1)) if keep_selection else 0
        self.ensure_notice_board_selection_visible()

    def notice_board_quest_state(self, quest) -> str:
        existing = next((q for q in self.active_quests if q.id == quest.id), None)
        return existing.status if existing else "available"

    def accept_board_quest(self, index: int):
        if index < 0 or index >= len(self.notice_board_quests):
            return
        template = self.notice_board_quests[index]
        if self.notice_board_quest_state(template) != "available":
            return
        quest = Quest(
            id=template.id,
            kind=template.kind,
            from_world_pos=template.from_world_pos,
            to_world_pos=template.to_world_pos,
            to_town_hint=template.to_town_hint,
            item_key=template.item_key,
            item_name=template.item_name,
            description=template.description,
            reward_gold=template.reward_gold,
            status="active",
            target_count=template.target_count,
            progress_count=self.enemies_defeated,
            stage=template.stage,
            objective_key=template.objective_key,
            target_region_name=template.target_region_name,
            target_landmark_name=template.target_landmark_name,
            target_landmark_kind=template.target_landmark_kind,
            origin_town_name=template.origin_town_name,
        )
        self.active_quests.append(quest)
        if quest.kind == "delivery":
            _, _, _, color = next(d for d in self._DELIVERY_ITEMS if d[0] == quest.item_key)
            self.add_item(quest.item_key, quest.item_name, "quest", color, "quest")
            self.message = f"Quest accepted: deliver {quest.item_name} to {self.quest_target_label(quest)} for {quest.reward_gold}g."
        elif quest.kind == "scout":
            if quest.target_landmark_name:
                self.message = (
                    f"Quest accepted: confirm {quest.target_landmark_name} in {self.quest_target_label(quest)}, "
                    f"then report back to {quest.origin_town_name}."
                )
            else:
                self.message = f"Quest accepted: scout {self.quest_target_label(quest)} and report back to {quest.origin_town_name}."
        elif quest.kind == "bounty":
            self.message = f"Quest accepted: hunt in {self.quest_target_label(quest)} and return for {quest.reward_gold}g."
        elif quest.kind == "chain":
            key = self.region_key(quest.to_world_pos)
            if key not in self.world_regions and key not in self.preview_world_regions:
                state = self.create_world_region_state(quest.to_world_pos)
                self.preview_world_regions[key] = state
            reward_label = self.chain_reward_label(quest.item_key)
            objective_label = self.chain_objective_label(quest.objective_key).lower()
            if quest.objective_key == "hunt":
                self.message = (
                    f"Lead accepted: travel to {self.quest_target_label(quest)}, hunt {quest.target_count} foes, "
                    f"recover {quest.item_name}, and return for {quest.reward_gold}g + {reward_label}."
                )
            elif quest.target_landmark_name:
                self.message = (
                    f"Lead accepted: travel to {self.quest_target_label(quest)}, {objective_label} {quest.target_landmark_name}, "
                    f"recover {quest.item_name}, and return for {quest.reward_gold}g + {reward_label}."
                )
            else:
                self.message = (
                    f"Lead accepted: {objective_label} {self.quest_target_label(quest)}, recover {quest.item_name}, "
                    f"and return for {quest.reward_gold}g + {reward_label}."
                )
        if self.notice_board_open:
            self.refresh_notice_board(keep_selection=True)

    def active_delivery_quest(self) -> "Quest | None":
        return next((q for q in self.active_quests if q.kind == "delivery" and q.status == "active"), None)

    def active_quests_in_progress(self) -> list:
        return [q for q in self.active_quests if q.status == "active"]

    def scout_objective_met(self, quest):
        if self.world_position != quest.to_world_pos:
            return False
        if not quest.target_landmark_name:
            return True
        for landmark in self.landmarks:
            if landmark.name != quest.target_landmark_name:
                continue
            if quest.target_landmark_kind and landmark.kind != quest.target_landmark_kind:
                continue
            return landmark.position in self.seen_tiles
        return False

    def _complete_quest(self, quest):
        quest.status = "complete"
        self.gold += quest.reward_gold
        town_response = self.town_response_line(quest.from_world_pos)
        if quest.kind == "delivery":
            item = self.inventory_item(quest.item_key)
            if item is not None:
                self.inventory.remove(item)
            self.message = f"Quest complete - {quest.item_name} delivered. Received {quest.reward_gold}g. Total: {self.gold}g."
        elif quest.kind == "scout":
            target_label = quest.target_landmark_name or quest.target_region_name or "the region"
            self.message = f"Quest complete - report filed on {target_label}. Received {quest.reward_gold}g. Total: {self.gold}g."
        elif quest.kind == "bounty":
            self.message = f"Quest complete - contract settled for {quest.target_region_name}. Received {quest.reward_gold}g. Total: {self.gold}g."
        elif quest.kind == "chain":
            target_label = quest.target_landmark_name or quest.target_region_name or "the site"
            if quest.item_key == "medkit":
                self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
                supply_note = "+1 healing potion"
            elif quest.item_key == "tonic":
                self.add_item("tonic", "Cleansing Tonic", "consumable", COLOR_ACCENT, "ward", quantity=1, description="Cleanses effects and grants ward.")
                supply_note = "+1 tonic"
            elif quest.item_key == "intel":
                revealed = self.reveal_one_adjacent_world_region()
                if revealed:
                    _coord, region_name = revealed
                    supply_note = f"route intel on {region_name}"
                else:
                    self.ammo += 1
                    supply_note = f"fallback +1 ammo (now {self.ammo})"
            else:
                self.ammo += 2
                supply_note = f"+2 ammo (now {self.ammo})"
            evidence = quest.item_name or "proof"
            self.message = f"Lead closed on {target_label}; {evidence} delivered. Received {quest.reward_gold}g, {supply_note}. Total: {self.gold}g."
        if town_response:
            self.message = f"{self.message} {town_response}"
        if self.notice_board_open and self.region_type == "town":
            self.refresh_notice_board(keep_selection=True)

    def check_quest_completion(self):
        for quest in self.active_quests_in_progress():
            if quest.kind == "delivery":
                if self.region_type == "town" and quest.to_world_pos == self.world_position:
                    self._complete_quest(quest)
            elif quest.kind == "scout":
                if quest.stage == 0 and self.scout_objective_met(quest):
                    quest.stage = 1
                    target_label = quest.target_landmark_name or quest.target_region_name or quest.to_town_hint
                    home_name = quest.origin_town_name or self.region_name
                    self.message = f"Lead confirmed at {target_label}. Return to {home_name} for payment."
                elif quest.stage >= 1 and self.region_type == "town" and self.world_position == quest.from_world_pos:
                    self._complete_quest(quest)
            elif quest.kind == "bounty":
                if quest.stage == 0 and self.world_position == quest.to_world_pos:
                    quest.stage = 1
                    quest.progress_count = self.enemies_defeated
                    self.message = f"Bounty ground reached: {quest.target_region_name}. Make the area safe, then return to {quest.origin_town_name}."
                kills = self.enemies_defeated - quest.progress_count if quest.stage >= 1 else 0
                if kills >= quest.target_count and self.world_position == quest.from_world_pos and self.region_type == "town":
                    self._complete_quest(quest)
            elif quest.kind == "chain":
                if quest.stage == 0 and self.world_position == quest.to_world_pos:
                    quest.stage = 1
                    target_label = quest.target_landmark_name or quest.target_region_name or quest.to_town_hint
                    if quest.objective_key == "hunt":
                        quest.progress_count = self.enemies_defeated
                        self.message = f"You reach {quest.target_region_name}. Hunt {quest.target_count} foes, then secure {quest.item_name or 'proof'}."
                    elif quest.objective_key == "survey":
                        self.message = f"You reach {quest.target_region_name}. Survey the area for {quest.item_name or 'proof'}."
                    else:
                        self.message = f"You reach {quest.target_region_name}. Search {target_label} for {quest.item_name or 'proof'}."
                elif quest.stage == 1 and (
                    (quest.objective_key == "hunt" and self.enemies_defeated - quest.progress_count >= quest.target_count)
                    or (quest.objective_key != "hunt" and self.scout_objective_met(quest))
                ):
                    quest.stage = 2
                    revealed = self.reveal_one_adjacent_world_region()
                    evidence = quest.item_name or "proof"
                    mid_msg = f"{self.chain_mid_message(quest.target_landmark_name, quest.target_region_name)} {evidence.capitalize()} secured."
                    if revealed:
                        _, region_name = revealed
                        self.message = f"{mid_msg} A new route to {region_name} is now visible."
                    else:
                        self.message = mid_msg
                elif quest.stage >= 2 and self.region_type == "town" and self.world_position == quest.from_world_pos:
                    self._complete_quest(quest)

    def _notice_board_interact(self):
        if self.region_type == "town":
            self.open_notice_board()
