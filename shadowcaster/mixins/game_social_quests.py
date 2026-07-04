from __future__ import annotations

import hashlib
import random

from ..models import Quest
from ..game_typing import GameMixinBase

_SOCIAL_ERRAND_SPECS = [
    ("letter",   "Letter",    "Carry a letter",        "letter for {recipient}"),
    ("keepsake", "Keepsake",  "Return a keepsake",     "keepsake for {recipient}"),
    ("word",     "Word",      "Pass along a message",  "word for {recipient}"),
    ("token",    "Token",     "Deliver a token",       "token for {recipient}"),
]

_RECIPIENT_NAMES = [
    "Mira", "Callen", "Tess", "Orin", "Hana",
    "Brek", "Solen", "Vara", "Idris", "Nela",
    "Fyke", "Lota", "Davan", "Suri", "Elen",
]

_SOCIAL_SENDER_KINDS = {"elder", "farmer", "watch", "vendor"}

_SOCIAL_OFFER_TEMPLATES = {
    "letter":   ("Would you carry a letter to {recipient} in {town}? I can't make the trip myself.",
                 "There's a letter that needs to reach {recipient} at {town}. I'd be grateful."),
    "keepsake": ("A keepsake of mine belongs with {recipient} in {town}. I'd trust you to see it there.",
                 "{recipient} in {town} has been waiting on this. Would you bring it?"),
    "word":     ("Could you pass word to {recipient} in {town}? Just tell them I sent you.",
                 "I need {recipient} in {town} to hear something. You look like you're heading that way."),
    "token":    ("This token is meant for {recipient} in {town}. I haven't had the chance to go myself.",
                 "Take this to {recipient} in {town} — they'll know what it means."),
}

_SOCIAL_COMPLETE_LINES = {
    "letter":   "You deliver the letter. {recipient} reads it quietly and thanks you.",
    "keepsake": "You hand over the keepsake. {recipient} holds it carefully and nods.",
    "word":     "You pass along the message. {recipient} seems relieved to hear it.",
    "token":    "You deliver the token. {recipient} turns it over in their hand and presses a coin into yours.",
}


class SocialQuestsMixin(GameMixinBase):

    def _social_quest_target(self):
        """Return (coord, region_name) for a revealed neighboring town, or None."""
        known_towns = [
            (coord, state)
            for key, state in self.world_regions.items()
            if state.get("region_type") == "town"
            for coord in [tuple(map(int, key.split(",")))]
            if coord != self.world_position
        ]
        if not known_towns:
            return None
        coord, state = random.choice(known_towns)
        return coord, state.get("region_name", "a distant town")

    def _social_quest_claim_key(self, resident):
        wx, wy = self.world_position
        return f"social:{resident.kind}:{wx}:{wy}"

    def maybe_offer_social_quest(self, resident):
        """Offer a social quest from this resident if eligible. Returns a message or None."""
        if self.region_type != "town":
            return None
        if resident.kind not in _SOCIAL_SENDER_KINDS:
            return None
        claim_key = self._social_quest_claim_key(resident)
        if claim_key in self.interaction_claims:
            return None
        # Only offer if there is already an active social quest from this resident
        quest_id_prefix = f"social_{self.world_position[0]}_{self.world_position[1]}_{resident.kind}"
        if any(q.id.startswith(quest_id_prefix) and q.status == "active" for q in self.active_quests):
            return None
        target = self._social_quest_target()
        if not target:
            return None
        to_coord, to_name = target
        h = int(hashlib.md5(
            f"social:{self.world_seed}:{self.world_position}:{resident.kind}".encode()
        ).hexdigest(), 16)
        spec = _SOCIAL_ERRAND_SPECS[h % len(_SOCIAL_ERRAND_SPECS)]
        item_key, item_label, _action, item_name_template = spec
        recipient = _RECIPIENT_NAMES[h % len(_RECIPIENT_NAMES)]
        item_name = item_name_template.format(recipient=recipient)
        templates = _SOCIAL_OFFER_TEMPLATES[item_key]
        offer_line = templates[h % len(templates)].format(recipient=recipient, town=to_name)
        reward = 10 + (h % 3) * 5
        quest = Quest(
            id=f"{quest_id_prefix}_{h % 1000}",
            kind="delivery",
            from_world_pos=self.world_position,
            to_world_pos=to_coord,
            to_town_hint=to_name,
            item_key=item_key,
            item_name=item_name,
            description=f"{offer_line} Return here once delivered for {reward}g.",
            reward_gold=reward,
            status="active",
            progress_count=0,
            target_region_name=to_name,
            origin_town_name=self.region_name,
        )
        self.active_quests.append(quest)
        self.interaction_claims.add(claim_key)
        sender = resident.name or f"the {resident.kind}"
        return f"{sender.capitalize()}: {offer_line}"

    def social_quest_arrival_message(self, quest):
        """Called when arriving at destination town with an active social delivery."""
        item_key = quest.item_key
        recipient = quest.item_name.split(" for ")[-1] if " for " in quest.item_name else "someone"
        template = _SOCIAL_COMPLETE_LINES.get(item_key, "You deliver the errand. {recipient} thanks you.")
        return template.format(recipient=recipient)
