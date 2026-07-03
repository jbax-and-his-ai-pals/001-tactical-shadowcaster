from __future__ import annotations

from ..game_typing import GameMixinBase


class TownReactionsMixin(GameMixinBase):
    def town_response_line(self, coord=None):
        coord = coord or self.world_position
        score = self.town_prosperity_score(coord)
        if score >= 10:
            return "The town feels genuinely lively now."
        if score >= 6:
            return "The streets feel busier than they used to."
        if score >= 3:
            return "People seem a little more at ease here."
        if score >= 1:
            return "The town is starting to recover its confidence."
        return ""

    def town_work_summary_line(self, coord=None):
        coord = coord or self.world_position
        counts = self.completed_quest_counts(coord)
        if sum(counts.values()) <= 0:
            return ""
        parts = []
        if counts.get("delivery", 0):
            parts.append(f"{counts['delivery']} deliveries")
        if counts.get("scout", 0):
            parts.append(f"{counts['scout']} reports")
        if counts.get("bounty", 0):
            parts.append(f"{counts['bounty']} bounties")
        if counts.get("chain", 0):
            parts.append(f"{counts['chain']} leads")
        return "Completed here: " + ", ".join(parts[:3]) + "."

    def resident_town_response_line(self, resident):
        if self.region_type != "town":
            return ""
        response = self.town_response_line()
        if not response:
            return ""
        role_lines = {
            "guide": "More folk are asking about the roads lately.",
            "scout": "People are taking the nearby routes more seriously now.",
            "farmer": "A steadier town means fuller tables.",
            "watch": "It's easier to hold the square when the town has heart.",
            "vendor": "Trade picks up when people feel safer.",
            "elder": "These streets remember who helps them.",
        }
        return role_lines.get(resident.kind, response)
