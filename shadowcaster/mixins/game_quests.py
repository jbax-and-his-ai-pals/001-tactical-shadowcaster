from __future__ import annotations

import hashlib

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..models import Quest
from .game_quest_board import QuestBoardMixin
from .game_quest_generation import QuestGenerationMixin


class QuestsMixin(QuestGenerationMixin, QuestBoardMixin):

    def generate_board_quests(self) -> list:
        if self.region_type != "town":
            return []
        wx, wy = self.world_position
        cycle = self.quest_posting_cycle()
        h = int(hashlib.md5(f"board:{self.world_seed}:{wx}:{wy}:{cycle}".encode()).hexdigest(), 16)
        builders = self.board_builders_for_attitude((wx, wy))
        quest_slots = self.town_quest_slots((wx, wy))
        quests = []
        if self.town_attitude_score((wx, wy)) >= 6:
            quests.append(self._board_quest_priority(wx, wy, 0))
            start_slot = 1
        elif self.town_attitude_score((wx, wy)) >= 1:
            quests.append(self._board_quest_chain(wx, wy, 0))
            start_slot = 1
        else:
            quests.append(self._board_quest_scout(wx, wy, 0))
            start_slot = 1
        for slot in range(start_slot, quest_slots):
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
            theme_key=template.theme_key,
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
            if self.is_priority_quest(quest):
                theme_label = {
                    "watch": "Priority watch contract accepted:",
                    "survey": "Priority survey contract accepted:",
                    "relief": "Priority relief contract accepted:",
                }.get(quest.theme_key, "Priority lead accepted:")
                lead_prefix = theme_label
            else:
                lead_prefix = "Lead accepted:"
            if quest.objective_key == "hunt":
                self.message = (
                    f"{lead_prefix} travel to {self.quest_target_label(quest)}, hunt {quest.target_count} foes, "
                    f"recover {quest.item_name}, and return for {quest.reward_gold}g + {reward_label}."
                )
            elif quest.target_landmark_name:
                self.message = (
                    f"{lead_prefix} travel to {self.quest_target_label(quest)}, {objective_label} {quest.target_landmark_name}, "
                    f"recover {quest.item_name}, and return for {quest.reward_gold}g + {reward_label}."
                )
            else:
                self.message = (
                    f"{lead_prefix} {objective_label} {self.quest_target_label(quest)}, recover {quest.item_name}, "
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

    def _record_quest_consequences(self, quest):
        """Persist map-intel and supply-depth side-effects after quest completion."""
        if quest.kind == "scout":
            target_key = self.region_key(quest.to_world_pos)
            if target_key in self.world_regions:
                self.world_regions[target_key]["scouted"] = True
        # Survey-theme chains (intel item_key) mark the target as scouted too
        if quest.kind == "chain" and quest.item_key == "intel":
            target_key = self.region_key(quest.to_world_pos)
            if target_key in self.world_regions:
                self.world_regions[target_key]["scouted"] = True
        if quest.kind in ("delivery", "chain") and not self._is_social_quest(quest):
            dest_key = self.region_key(quest.to_world_pos)
            dest = self.world_regions.get(dest_key)
            if dest and dest.get("region_type") == "town":
                # Relief-theme chains (medkit/ammo) give double supply depth gain
                is_relief = quest.kind == "chain" and quest.item_key in ("medkit", "ammo")
                depth_gain = 2 if is_relief else 1
                dest["supply_depth"] = dest.get("supply_depth", 0) + depth_gain

    def _complete_quest(self, quest):
        quest.status = "complete"
        self._record_quest_consequences(quest)
        self.gold += quest.reward_gold
        town_response = self.town_response_line(quest.from_world_pos)
        if quest.kind == "delivery" and self._is_social_quest(quest):
            self.message = f"Errand complete — {quest.item_name} delivered. Received {quest.reward_gold}g. Total: {self.gold}g."
        elif quest.kind == "delivery":
            item = self.inventory_item(quest.item_key)
            if item is not None:
                self.inventory.remove(item)
            lead = self.reveal_one_adjacent_world_region_from(quest.to_world_pos)
            route_note = f" Your contact there points you toward {lead[1]}." if lead else ""
            self.message = f"Quest complete - {quest.item_name} delivered. Received {quest.reward_gold}g. Total: {self.gold}g.{route_note}"
        elif quest.kind == "scout":
            target_label = quest.target_landmark_name or quest.target_region_name or "the region"
            revealed = self.reveal_adjacent_world_regions_from(quest.to_world_pos)
            # Scout track bonus: extend the survey one step further for each tier
            track = self.dominant_track()
            if track and track[0] == "Scout":
                extra_hops = track[1]  # tier 1 → 1, tier 2 → 2
                for coord, _ in list(revealed)[:extra_hops]:
                    for bonus in self.reveal_adjacent_world_regions_from(coord):
                        if bonus not in revealed:
                            revealed.append(bonus)
            if revealed:
                names = ", ".join(n for _, n in revealed[:2])
                extra = f" and {len(revealed) - 2} more" if len(revealed) > 2 else ""
                map_note = f" Survey adds routes to the map: {names}{extra}."
            else:
                map_note = ""
            self.message = f"Quest complete - report filed on {target_label}. Received {quest.reward_gold}g. Total: {self.gold}g.{map_note}"
        elif quest.kind == "bounty":
            lead = self.reveal_one_adjacent_world_region_from(quest.to_world_pos)
            route_note = f" The cleared ground opens a route to {lead[1]}." if lead else ""
            target_state = self.world_regions.get(self.region_key(quest.to_world_pos), {})
            full_clear = target_state.get("enemies_remaining", -1) == 0 and target_state.get("enemies_spawned", 0) > 0
            if full_clear:
                bonus = 15
                self.gold += bonus
                clear_note = f" Full-clear bonus: +{bonus}g."
            else:
                clear_note = ""
            self.message = f"Quest complete - contract settled for {quest.target_region_name}. Received {quest.reward_gold}g.{clear_note} Total: {self.gold}g.{route_note}"
        elif quest.kind == "chain":
            target_label = quest.target_landmark_name or quest.target_region_name or "the site"
            if quest.item_key == "medkit":
                self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
                supply_note = "+1 healing potion"
            elif quest.item_key == "tonic":
                self.add_item("tonic", "Cleansing Tonic", "consumable", COLOR_ACCENT, "ward", quantity=1, description="Cleanses effects and grants ward.")
                supply_note = "+1 tonic"
            elif quest.item_key == "intel":
                revealed = self.reveal_adjacent_world_regions_from(quest.to_world_pos)
                if revealed:
                    names = ", ".join(n for _, n in revealed[:3])
                    extra = f" and {len(revealed) - 3} more" if len(revealed) > 3 else ""
                    supply_note = f"survey intel — routes added: {names}{extra}"
                else:
                    self.ammo += 1
                    supply_note = f"fallback +1 ammo (now {self.ammo})"
            else:
                self.ammo += 2
                supply_note = f"+2 ammo (now {self.ammo})"
            evidence = quest.item_name or "proof"
            lead_label = "Priority lead closed" if self.is_priority_quest(quest) else "Lead closed"
            self.message = f"{lead_label} on {target_label}; {evidence} delivered. Received {quest.reward_gold}g, {supply_note}. Total: {self.gold}g."
        if town_response:
            self.message = f"{self.message} {town_response}"
        if self.notice_board_open and self.region_type == "town":
            self.refresh_notice_board(keep_selection=True)

    def _chain_landmark_cleared(self, quest):
        """True when the quest's named landmark in the target region has been cleared."""
        if self.world_position != quest.to_world_pos:
            return False
        target_key = self.region_key(quest.to_world_pos)
        state = self.world_regions.get(target_key)
        if state is None:
            return False
        for lm in state.get("landmarks", []):
            if lm.name == quest.target_landmark_name:
                prog = self.landmark_progress(quest.to_world_pos, lm)
                return prog.get("cleared", False)
        # No named landmark found — fall back to region full-clear
        return state.get("enemies_remaining", 1) == 0

    def _is_social_quest(self, quest):
        return quest.kind == "delivery" and quest.id.startswith("social_")

    def check_quest_completion(self):
        for quest in self.active_quests_in_progress():
            if self._is_social_quest(quest):
                if quest.stage == 0 and self.region_type == "town" and quest.to_world_pos == self.world_position:
                    quest.stage = 1
                    arrival_msg = self.social_quest_arrival_message(quest) if hasattr(self, "social_quest_arrival_message") else f"You deliver {quest.item_name}."
                    home = quest.origin_town_name or "the town you came from"
                    self.message = f"{arrival_msg} Return to {home} for {quest.reward_gold}g."
                elif quest.stage >= 1 and self.region_type == "town" and self.world_position == quest.from_world_pos:
                    self._complete_quest(quest)
            elif quest.kind == "delivery":
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
                    elif quest.objective_key == "clear_landmark":
                        site = quest.target_landmark_name or "the site"
                        self.message = f"You reach {quest.target_region_name}. Clear {site} — every enemy must fall."
                    else:
                        self.message = f"You reach {quest.target_region_name}. Search {target_label} for {quest.item_name or 'proof'}."
                elif quest.stage == 1 and (
                    (quest.objective_key == "hunt" and self.enemies_defeated - quest.progress_count >= quest.target_count)
                    or (quest.objective_key == "clear_landmark" and self._chain_landmark_cleared(quest))
                    or (quest.objective_key not in ("hunt", "clear_landmark") and self.scout_objective_met(quest))
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
