from __future__ import annotations

from ..game_typing import GameMixinBase


class JournalStatsMixin(GameMixinBase):
    def completed_quests(self):
        return [quest for quest in self.active_quests if quest.status == "complete"]

    def completed_quest_counts(self, coord=None):
        counts = {"delivery": 0, "scout": 0, "bounty": 0, "chain": 0}
        for quest in self.completed_quests():
            if coord is not None and quest.from_world_pos != coord:
                continue
            counts[quest.kind] = counts.get(quest.kind, 0) + 1
        return counts

    def town_prosperity_score(self, coord):
        counts = self.completed_quest_counts(coord)
        return counts.get("delivery", 0) + counts.get("scout", 0) + counts.get("chain", 0) * 2 + counts.get("bounty", 0) * 2

    def town_prosperity_label(self, coord):
        score = self.town_prosperity_score(coord)
        if score >= 10:
            return "Thriving"
        if score >= 6:
            return "Busy"
        if score >= 3:
            return "Steady"
        if score >= 1:
            return "Recovering"
        return "Quiet"

    def total_towns_helped(self):
        return len({quest.from_world_pos for quest in self.completed_quests()})

    def active_quests_for_region(self, coord):
        return [quest for quest in self.active_quests if quest.status == "active" and (quest.from_world_pos == coord or quest.to_world_pos == coord)]

    def active_quest_region_summary(self, coord):
        summary = {
            "posted_here": 0,
            "targets_here": 0,
            "report_here": 0,
            "kinds": set(),
            "lines": [],
        }
        for quest in self.active_quests:
            if quest.status != "active":
                continue
            touches_origin = quest.from_world_pos == coord
            touches_target = quest.to_world_pos == coord
            if not touches_origin and not touches_target:
                continue
            summary["kinds"].add(quest.kind)
            if touches_origin:
                summary["posted_here"] += 1
            if touches_target:
                summary["targets_here"] += 1
            if quest.kind == "scout" and quest.stage >= 1 and quest.from_world_pos == coord:
                summary["report_here"] += 1
            if quest.kind == "bounty" and quest.stage >= 1 and quest.from_world_pos == coord:
                summary["report_here"] += 1
            if quest.kind == "delivery":
                if touches_target:
                    summary["lines"].append(f"Delivery incoming from {quest.origin_town_name}.")
                elif touches_origin:
                    summary["lines"].append(f"Delivery posted for {quest.target_region_name}.")
            elif quest.kind == "scout":
                if touches_target and quest.stage == 0:
                    label = quest.target_landmark_name or quest.target_region_name
                    summary["lines"].append(f"Scout target: confirm {label}.")
                elif touches_origin and quest.stage >= 1:
                    summary["lines"].append("Scout report ready to turn in here.")
                elif touches_origin:
                    summary["lines"].append(f"Scout posted toward {quest.target_region_name}.")
            elif quest.kind == "bounty":
                if touches_target and quest.stage == 0:
                    summary["lines"].append(f"Bounty hunt active: {quest.target_count} foes.")
                elif touches_origin and quest.stage >= 1:
                    summary["lines"].append("Bounty turn-in ready here.")
                elif touches_origin:
                    summary["lines"].append(f"Bounty posted toward {quest.target_region_name}.")
            elif quest.kind == "chain":
                if touches_target and quest.stage <= 1:
                    if quest.objective_key == "hunt":
                        summary["lines"].append(f"Lead active: hunt {quest.target_count} foes.")
                    else:
                        summary["lines"].append(f"Lead active: recover {quest.item_name or 'proof'}.")
                elif touches_origin and quest.stage >= 2:
                    summary["lines"].append("Lead return ready here.")
                elif touches_origin:
                    summary["lines"].append(f"Lead posted toward {quest.target_region_name}.")
        deduped = []
        for line in summary["lines"]:
            if line not in deduped:
                deduped.append(line)
        summary["lines"] = deduped[:4]
        return summary

    def quest_status_label(self, quest):
        if quest.status == "complete":
            return "Complete"
        if self.is_priority_quest(quest):
            theme_label = {
                "watch": "Watch",
                "survey": "Survey",
                "relief": "Relief",
            }.get(getattr(quest, "theme_key", ""), "Priority")
            if quest.stage >= 2:
                return f"{theme_label} Return"
            if quest.objective_key == "hunt" and quest.stage == 1:
                return f"{theme_label} Hunt"
            if quest.objective_key == "survey" and quest.stage == 1:
                return f"{theme_label} Survey"
            return f"{theme_label} Lead"
        if quest.kind == "delivery":
            return "Delivery"
        if quest.kind == "scout":
            return "Report Back" if quest.stage >= 1 else "Scouting"
        if quest.kind == "bounty":
            return "Turn In" if quest.stage >= 1 else "Bounty"
        if quest.kind == "chain":
            if quest.stage >= 2:
                return "Return Lead"
            if quest.objective_key == "hunt" and quest.stage == 1:
                return "Hunt Lead"
            if quest.objective_key == "survey" and quest.stage == 1:
                return "Survey Lead"
            if quest.stage == 1:
                return "Search Site"
            return "Follow Lead"
        return quest.kind.title()

    def quest_progress_text(self, quest):
        if quest.status == "complete":
            extra = ""
            if quest.kind == "chain":
                extra = f" + {self.chain_reward_label(quest.item_key)}"
            return f"Completed for {quest.reward_gold}g{extra}."
        if quest.kind == "delivery":
            return f"Deliver to {self.quest_target_label(quest)} for {quest.reward_gold}g."
        if quest.kind == "scout":
            if quest.stage >= 1:
                home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
                return f"Lead confirmed. Return to {home_name} for {quest.reward_gold}g."
            if quest.target_landmark_name:
                target_label = f"{quest.target_landmark_name} in {self.quest_target_label(quest)}"
            else:
                target_label = self.quest_target_label(quest)
            home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
            return f"Confirm {target_label}, then return to {home_name} for {quest.reward_gold}g."
        if quest.kind == "bounty":
            if quest.stage == 0:
                return f"Reach {self.quest_target_label(quest)}, hunt {quest.target_count} foes, then return for {quest.reward_gold}g."
            kills = max(0, self.enemies_defeated - quest.progress_count)
            if quest.status == "complete":
                kills = quest.target_count
            home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
            return f"{min(kills, quest.target_count)}/{quest.target_count} foes defeated. Return to {home_name} for {quest.reward_gold}g."
        if quest.kind == "chain":
            return self.chain_stage_text(quest)
        return f"Reward {quest.reward_gold}g."

    def journal_entry_lines(self, quest):
        region_name = quest.origin_town_name or self.region_name
        origin_label = f"{region_name} - ({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
        status_line = f"Completed from {origin_label}." if quest.status == "complete" else f"Posted from {origin_label}."
        return [*self.quest_context_lines(quest), self.quest_progress_text(quest), status_line]

    def quest_summary_counts(self):
        active = len([quest for quest in self.active_quests if quest.status == "active"])
        completed = len(self.completed_quests())
        helped = self.total_towns_helped()
        counts = self.completed_quest_counts()
        return {
            "active": active,
            "completed": completed,
            "towns_helped": helped,
            "delivery": counts.get("delivery", 0),
            "scout": counts.get("scout", 0),
            "bounty": counts.get("bounty", 0),
            "chain": counts.get("chain", 0),
        }

    def current_journal_summary_lines(self):
        counts = self.quest_summary_counts()
        lines = [f"{counts['active']} active"] if self.journal_tab == 0 else [
            f"{counts['completed']} completed",
            f"Towns helped {counts['towns_helped']}  -  D {counts['delivery']} / S {counts['scout']} / B {counts['bounty']} / C {counts['chain']}",
        ]
        if self.region_type == "town":
            lines.append(
                f"Town standing {self.town_attitude_label()}  -  Prosperity {self.town_prosperity_label(self.world_position)}"
            )
        return lines
