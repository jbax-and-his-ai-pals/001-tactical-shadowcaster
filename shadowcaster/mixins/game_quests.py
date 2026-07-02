from __future__ import annotations
import hashlib
import random
from ..models import Quest
from ..game_typing import GameMixinBase


class QuestsMixin(GameMixinBase):
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
        import hashlib
        seed_str = f"{self.world_seed}:{self.world_position[0]}:{self.world_position[1]}"
        h = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        postings = [
            "Travelers warned: reports of unusual creature movement along the eastern route",
            "Lost: a grey pack mule last seen near the mill — reward offered",
            "Work available at the granary — strong backs needed before the harvest",
            "Route north is slow going after recent weather — allow extra time",
            "Notice: new toll in effect at the river crossing, two coins each way",
            "Caution: fog sits heavy in the low ground to the west each morning",
            "Seeking reliable passage to neighboring settlements — ask at the inn",
            "Reminder: all disputes over land boundaries to be settled at the hall",
            "A shipment of supply goods is overdue — anyone with information, please report",
            "Trade route reopened after repairs; roads are passable but muddy",
            "Experienced guides wanted for escort through the borderlands — fair pay",
            "Notice of annual gathering at the town square — all residents welcome",
            "Lost: small carved amulet, silver-grey, near the market stalls",
            "Warnings of rough weather inbound from the mountain pass",
            "A wagon of trade goods is missing along the southern road — inquire within",
        ]
        return postings[h % len(postings)]

    _QUEST_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    _QUEST_DIR_NAMES = {
        (1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north",
        (1, 1): "southeast", (1, -1): "northeast", (-1, 1): "southwest", (-1, -1): "northwest",
    }
    _DELIVERY_ITEMS = [
        ("quest_letter", "Sealed Letter", "a sealed letter", (220, 210, 160)),
        ("quest_package", "Small Package", "a small package", (160, 130, 100)),
        ("quest_medicine", "Medicine Bundle", "a medicine bundle", (160, 210, 180)),
        ("quest_parcel", "Wrapped Parcel", "a wrapped parcel", (190, 180, 140)),
    ]

    def _board_quest_delivery(self, wx, wy, slot):
        import hashlib
        h = int(hashlib.md5(f"delivery:{self.world_seed}:{wx}:{wy}:{slot}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 2 + 1
        to_pos = (wx + dx * dist, wy + dy * dist)
        dir_name = self._QUEST_DIR_NAMES[(dx, dy)]
        key, name, desc, _ = self._DELIVERY_ITEMS[h % len(self._DELIVERY_ITEMS)]
        reward = 20 + (h % 6) * 10
        return Quest(
            id=f"delivery_{wx}_{wy}_{slot}",
            kind="delivery",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=f"a settlement to the {dir_name}",
            item_key=key,
            item_name=name,
            description=f"Carry {desc} to {dir_name}.",
            reward_gold=reward,
        )

    def _board_quest_scout(self, wx, wy, slot):
        import hashlib
        h = int(hashlib.md5(f"scout:{self.world_seed}:{wx}:{wy}:{slot}".encode()).hexdigest(), 16)
        dx, dy = self._QUEST_DIRECTIONS[h % 8]
        dist = (h >> 3) % 3 + 1
        to_pos = (wx + dx * dist, wy + dy * dist)
        dir_name = self._QUEST_DIR_NAMES[(dx, dy)]
        reward = 15 + (h % 4) * 5
        return Quest(
            id=f"scout_{wx}_{wy}_{slot}",
            kind="scout",
            from_world_pos=(wx, wy),
            to_world_pos=to_pos,
            to_town_hint=f"to the {dir_name}",
            item_key="",
            item_name="",
            description=f"Survey the region to the {dir_name} and report back.",
            reward_gold=reward,
        )

    def _board_quest_bounty(self, wx, wy, slot):
        import hashlib
        h = int(hashlib.md5(f"bounty:{self.world_seed}:{wx}:{wy}:{slot}".encode()).hexdigest(), 16)
        target = (h % 4 + 1) * 5
        reward = target * 4
        return Quest(
            id=f"bounty_{wx}_{wy}_{slot}",
            kind="bounty",
            from_world_pos=(wx, wy),
            to_world_pos=(wx, wy),
            to_town_hint="here",
            item_key="",
            item_name="",
            description=f"Defeat {target} enemies and return to claim your reward.",
            reward_gold=reward,
            target_count=target,
        )

    def generate_board_quests(self) -> list:
        import hashlib
        if self.region_type != "town":
            return []
        wx, wy = self.world_position
        h = int(hashlib.md5(f"board:{self.world_seed}:{wx}:{wy}".encode()).hexdigest(), 16)
        builders = [self._board_quest_delivery, self._board_quest_scout, self._board_quest_bounty]
        order = [(h >> (i * 2)) % 3 for i in range(3)]
        seen = set()
        quests = []
        for idx in order:
            if idx in seen:
                idx = next(i for i in range(3) if i not in seen)
            seen.add(idx)
            quests.append(builders[idx](wx, wy, idx))
        return quests

    def open_notice_board(self):
        self.refresh_notice_board(keep_selection=False)
        self.notice_board_open = True
        self.stop_auto_movement()

    def close_notice_board(self):
        self.notice_board_open = False
        self.notice_board_quests = []

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
                return
        if keep_selection:
            self.notice_board_index = max(0, min(self.notice_board_index, len(self.notice_board_quests) - 1))
        else:
            self.notice_board_index = 0

    def notice_board_quest_state(self, quest) -> str:
        existing = next((q for q in self.active_quests if q.id == quest.id), None)
        if existing:
            return existing.status
        return "available"

    def accept_board_quest(self, index: int):
        if index < 0 or index >= len(self.notice_board_quests):
            return
        template = self.notice_board_quests[index]
        state = self.notice_board_quest_state(template)
        if state != "available":
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
        )
        self.active_quests.append(quest)
        if quest.kind == "delivery":
            _, name, _, color = next(
                d for d in self._DELIVERY_ITEMS if d[0] == quest.item_key
            )
            self.add_item(quest.item_key, quest.item_name, "quest", color, "quest")
            self.message = f"Quest accepted: deliver {quest.item_name} to {quest.to_town_hint} for {quest.reward_gold}g."
        elif quest.kind == "scout":
            self.message = f"Quest accepted: scout {quest.to_town_hint} for {quest.reward_gold}g."
        elif quest.kind == "bounty":
            self.message = f"Quest accepted: defeat {quest.target_count} enemies for {quest.reward_gold}g."
        if self.notice_board_open:
            self.refresh_notice_board(keep_selection=True)

    def active_delivery_quest(self) -> "Quest | None":
        return next((q for q in self.active_quests if q.kind == "delivery" and q.status == "active"), None)

    def active_quests_in_progress(self) -> list:
        return [q for q in self.active_quests if q.status == "active"]

    def _complete_quest(self, quest):
        quest.status = "complete"
        self.gold += quest.reward_gold
        if quest.kind == "delivery":
            item = self.inventory_item(quest.item_key)
            if item is not None:
                self.inventory.remove(item)
            self.message = f"Quest complete — {quest.item_name} delivered. Received {quest.reward_gold}g. Total: {self.gold}g."
        elif quest.kind == "scout":
            self.message = f"Quest complete — region scouted. Received {quest.reward_gold}g. Total: {self.gold}g."
        elif quest.kind == "bounty":
            self.message = f"Quest complete — bounty fulfilled. Received {quest.reward_gold}g. Total: {self.gold}g."
        if self.notice_board_open and self.region_type == "town":
            self.refresh_notice_board(keep_selection=True)

    def check_quest_completion(self):
        for quest in self.active_quests_in_progress():
            if quest.kind in {"delivery", "scout"}:
                if self.region_type == "town" and quest.to_world_pos == self.world_position:
                    self._complete_quest(quest)
            elif quest.kind == "bounty":
                kills = self.enemies_defeated - quest.progress_count
                if kills >= quest.target_count and self.world_position == quest.from_world_pos and self.region_type == "town":
                    self._complete_quest(quest)

    def _notice_board_interact(self):
        if self.region_type == "town":
            self.open_notice_board()
