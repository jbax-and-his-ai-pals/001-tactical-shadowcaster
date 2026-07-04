from __future__ import annotations

from ..game_typing import GameMixinBase


class TownReactionsMixin(GameMixinBase):
    def town_attitude_score(self, coord=None):
        coord = coord or self.world_position
        return self.town_prosperity_score(coord)

    def town_attitude_label(self, coord=None):
        score = self.town_attitude_score(coord)
        if score >= 10:
            return "Beloved"
        if score >= 6:
            return "Trusted"
        if score >= 3:
            return "Welcome"
        if score >= 1:
            return "Known"
        return "Wary"

    def town_attitude_board_summary(self, coord=None):
        label = self.town_attitude_label(coord)
        return f"Standing here: {label}."

    def town_service_bonus_tier(self, coord=None):
        score = self.town_attitude_score(coord)
        if score >= 10:
            return 2
        if score >= 6:
            return 1
        return 0

    def with_town_attitude_dialogue(self, text, resident=None):
        if self.region_type != "town" or not text:
            return text
        label = self.town_attitude_label()
        role = getattr(resident, "kind", "")
        if label == "Beloved":
            suffix = {
                "guide": "The guide treats you like one of their own now.",
                "scout": "The scout speaks to you like a trusted runner.",
                "vendor": "The vendor grins like you're good business and good company.",
            }.get(role, "People here are plainly glad to see you.")
        elif label == "Trusted":
            suffix = "You get the sense this town trusts your judgment."
        elif label == "Welcome":
            suffix = "The town seems comfortable having you around."
        elif label == "Known":
            suffix = "At least the locals recognize you now."
        else:
            suffix = "You still feel a little unproven here."
        return f"{text} {suffix}".strip()

    def town_response_line(self, coord=None):
        coord = coord or self.world_position
        score = self.town_attitude_score(coord)
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
