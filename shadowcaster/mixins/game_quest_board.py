from __future__ import annotations

import hashlib

from ..game_typing import GameMixinBase


class QuestBoardMixin(GameMixinBase):

    def board_kind_label(self, quest):
        if self.is_priority_quest(quest):
            theme_label = self._PRIORITY_THEME_LABELS.get(getattr(quest, "theme_key", ""), "Priority")
            if quest.stage >= 2:
                return theme_label.upper()
            if quest.stage == 1 and quest.objective_key == "hunt":
                return f"{theme_label} HUNT".upper()
            if quest.stage == 1 and quest.objective_key == "survey":
                return f"{theme_label} SURVEY".upper()
            if quest.stage == 1:
                return theme_label.upper()
            return theme_label.upper()
        if quest.kind == "bounty" and quest.stage >= 1:
            return "TURN-IN"
        if quest.kind == "scout" and quest.stage >= 1:
            return "REPORT"
        if quest.kind == "chain" and quest.stage == 1:
            return self._CHAIN_OBJECTIVE_LABELS.get(quest.objective_key, "LEAD").upper()
        if quest.kind == "chain" and quest.stage >= 2:
            return "RETURN"
        return {
            "delivery": "DELIVERY",
            "scout": "SCOUTING",
            "bounty": "BOUNTY",
            "chain": "CHAIN",
        }.get(quest.kind, quest.kind.upper())

    def notice_board_reward_label(self, quest):
        reward_extra = self.chain_reward_label(quest.item_key)
        reward_label = f"Reward: {quest.reward_gold}g + {reward_extra}"
        if quest.kind != "chain":
            reward_label = f"Reward: {quest.reward_gold}g"
        existing = next((q for q in self.active_quests if q.id == quest.id), None)
        if quest.kind == "bounty" and existing is not None and existing.status == "active":
            if existing.stage == 0:
                return f"Reward: {quest.reward_gold}g - Reach {quest.target_region_name}"
            kills = self.enemies_defeated - existing.progress_count
            return f"Reward: {quest.reward_gold}g - {min(kills, quest.target_count)}/{quest.target_count} enemies"
        if quest.kind == "scout" and existing is not None and existing.status == "active" and existing.stage >= 1:
            return f"Reward: {quest.reward_gold}g - Return to {existing.origin_town_name}"
        if quest.kind == "chain" and existing is not None and existing.status == "active":
            if existing.stage == 0:
                return f"{reward_label} - Travel to {existing.target_region_name}"
            if existing.stage == 1:
                return f"{reward_label} - Recover {existing.item_name or 'proof'}"
            return f"{reward_label} - Return {existing.item_name or 'proof'} to {existing.origin_town_name}"
        return reward_label

    def chain_reward_label(self, reward_key):
        return self._CHAIN_REWARD_LABELS.get(reward_key, "supplies")

    def chain_objective_label(self, objective_key):
        return self._CHAIN_OBJECTIVE_LABELS.get(objective_key or "recover", "Lead")

    def chain_stage_text(self, quest):
        evidence = quest.item_name or "proof"
        objective = quest.objective_key or "recover"
        if quest.stage <= 0:
            if objective == "hunt":
                return f"Reach {self.quest_target_label(quest)}, then bring down {quest.target_count} foes and return with {evidence}."
            if objective == "clear_landmark":
                site = quest.target_landmark_name or "the site"
                return f"Reach {self.quest_target_label(quest)}, then fully clear {site}."
            return f"Reach {self.quest_target_label(quest)}, then search for {evidence}."
        if quest.stage == 1:
            if objective == "survey":
                return f"Survey {self.quest_target_label(quest)} and recover {evidence}."
            if objective == "hunt":
                kills = max(0, self.enemies_defeated - quest.progress_count)
                return f"Hunt {min(kills, quest.target_count)}/{quest.target_count} foes in {self.quest_target_label(quest)}, then return with {evidence}."
            if objective == "clear_landmark":
                site = quest.target_landmark_name or "the site"
                return f"Clear {site} in {self.quest_target_label(quest)} — enemies must fall."
            target_label = quest.target_landmark_name or "the site"
            return f"Search {target_label} in {self.quest_target_label(quest)} and recover {evidence}."
        home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
        return f"{evidence.capitalize()} secured. Return to {home_name} for {quest.reward_gold}g + {self.chain_reward_label(quest.item_key)}."

    def quest_target_label(self, quest):
        direction = self.quest_direction_name(quest.from_world_pos, quest.to_world_pos)
        region_name = quest.target_region_name or quest.to_town_hint
        return f"{region_name} to the {direction}"

    def quest_destination_summary(self, quest):
        dx = quest.to_world_pos[0] - quest.from_world_pos[0]
        dy = quest.to_world_pos[1] - quest.from_world_pos[1]
        dist = max(abs(dx), abs(dy))
        region_name = quest.target_region_name or quest.to_town_hint
        direction = self.quest_direction_name(quest.from_world_pos, quest.to_world_pos)
        region_str = f"{region_name}, " if region_name else ""
        dist_str = f"{dist} region{'s' if dist > 1 else ''} {direction}"
        coord_str = f" ({quest.to_world_pos[0]},{quest.to_world_pos[1]})"
        return f"Go: {region_str}{dist_str}{coord_str}."

    def quest_objective_summary(self, quest):
        if quest.kind == "delivery":
            return f"Carry: {quest.item_name}."
        if quest.kind == "scout":
            if quest.target_landmark_name:
                return f"Confirm: {quest.target_landmark_name}."
            return "Objective: survey the area."
        if quest.kind == "bounty":
            return f"Clear: {quest.target_count} local threats."
        if quest.kind == "chain":
            if quest.objective_key == "hunt":
                return f"{self.chain_objective_label(quest.objective_key)}: {quest.target_count} threats."
            if quest.objective_key == "clear_landmark":
                site = quest.target_landmark_name or "the site"
                return f"Clear: {site} — full sweep required."
            if quest.target_landmark_name:
                return f"{self.chain_objective_label(quest.objective_key)}: {quest.target_landmark_name}."
            if quest.item_name:
                return f"{self.chain_objective_label(quest.objective_key)}: {quest.item_name}."
            return f"{self.chain_objective_label(quest.objective_key)}: field proof."
        return f"Reward: {quest.reward_gold}g."

    def quest_return_summary(self, quest):
        if quest.kind == "delivery":
            return ""
        home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
        return f"Return: {home_name}."

    def quest_context_lines(self, quest, include_return=True):
        lines = [self.quest_destination_summary(quest), self.quest_objective_summary(quest)]
        if include_return:
            return_line = self.quest_return_summary(quest)
            if return_line:
                lines.append(return_line)
        return lines

    def notice_board_context(self):
        building_names = [building["name"] for building in self.town_building_data()]
        home_name = next(
            (name for name in building_names if "house" in name.lower() or "cottage" in name.lower() or "hut" in name.lower()),
            self.region_name,
        )
        work_name = next(
            (
                name
                for name in building_names
                if any(term in name.lower() for term in ("granary", "barn", "store", "shed", "yard", "kiln", "stable", "market"))
            ),
            self.region_name,
        )
        civic_name = next(
            (
                name
                for name in building_names
                if any(term in name.lower() for term in ("hall", "square", "shrine", "office", "clinic"))
            ),
            self.region_name,
        )
        return {"home": home_name, "work": work_name, "civic": civic_name, "town": self.region_name}

    def _notice_board_text(self):
        response = self.town_response_line()
        work_summary = self.town_work_summary_line()
        attitude = self.town_attitude_board_summary()
        if response and work_summary:
            return f"{attitude} {response} {work_summary}"
        if response:
            return f"{attitude} {response}"
        if work_summary:
            return f"{attitude} {work_summary}"
        if response:
            return response
        seed_str = f"{self.world_seed}:{self.world_position[0]}:{self.world_position[1]}"
        h = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        postings = [
            "Travelers warned: reports of unusual creature movement along the eastern route",
            "Lost: a grey pack mule last seen near the mill - reward offered",
            "Work available at the granary - strong backs needed before the harvest",
            "Route north is slow going after recent weather - allow extra time",
            "Notice: new toll in effect at the river crossing, two coins each way",
            "Caution: fog sits heavy in the low ground to the west each morning",
            "Seeking reliable passage to neighboring settlements - ask at the inn",
            "Reminder: all disputes over land boundaries to be settled at the hall",
            "A shipment of supply goods is overdue - anyone with information, please report",
            "Trade route reopened after repairs; roads are passable but muddy",
            "Experienced guides wanted for escort through the borderlands - fair pay",
            "Notice of annual gathering at the town square - all residents welcome",
            "Lost: small carved amulet, silver-grey, near the market stalls",
            "Warnings of rough weather inbound from the mountain pass",
            "A wagon of trade goods is missing along the southern road - inquire within",
        ]
        return postings[h % len(postings)]
