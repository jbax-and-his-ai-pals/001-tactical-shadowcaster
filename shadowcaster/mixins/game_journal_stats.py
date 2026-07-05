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

    def progression_tracks(self):
        """Returns {name: (score, tier)} for all 4 tracks. Tier 0=unranked, 1=named, 2=mastery."""
        counts = self.completed_quest_counts()
        surface = len(getattr(self, "claimed_surface_landmark_keys", set()))
        pc = self.powerups_collected
        kills = getattr(self, "total_monsters_killed", 0)
        clears = getattr(self, "full_clears", 0)
        world_seen = len(getattr(self, "world_regions", {}))
        scores = {
            "Scout":      counts.get("scout", 0) * 4 + surface * 2,
            "Delver":     kills // 5 + pc.get("power", 0) * 4 + pc.get("vitality", 0) * 3 + clears * 5,
            "Warden":     counts.get("bounty", 0) * 4 + self.total_towns_helped() * 3 + counts.get("chain", 0) * 3,
            "Pathfinder": world_seen + surface * 3 + counts.get("delivery", 0) * 2,
        }
        return {n: (s, 2 if s >= 20 else 1 if s >= 8 else 0) for n, s in scores.items()}

    def dominant_track(self):
        """Returns (track_name, tier) for the highest-scoring named track, or None."""
        tracks = self.progression_tracks()
        best = max(tracks.items(), key=lambda kv: kv[1][0])
        name, (score, tier) = best
        return (name, tier) if tier >= 1 else None

    def track_tier_label(self, name, tier):
        labels = {("Scout", 1): "Scout", ("Scout", 2): "Master Scout",
                  ("Delver", 1): "Delver", ("Delver", 2): "Master Delver",
                  ("Warden", 1): "Warden", ("Warden", 2): "Master Warden",
                  ("Pathfinder", 1): "Pathfinder", ("Pathfinder", 2): "Master Pathfinder"}
        return labels.get((name, tier), name)

    def character_journal_rows(self) -> list[dict]:
        """Return display rows for the Character tab."""
        from .game_xp import XP_THRESHOLDS, LEVEL_UNLOCKS
        from .game_abilities import ABILITY_POOL
        rows = []
        level = getattr(self, "player_level", 1)
        title = self.player_title() if hasattr(self, "player_title") else "Wanderer"
        xp = getattr(self, "player_xp", 0)
        if level >= 5:
            xp_line = "Max level reached."
        else:
            threshold = XP_THRESHOLDS.get(level + 1, 0)
            xp_line = f"XP: {xp} / {threshold}  ({threshold - xp} to next level)"
        rows.append({"header": f"Level {level} — {title}", "detail": xp_line, "color": (220, 208, 132)})
        unlock = LEVEL_UNLOCKS.get(level, "")
        if unlock:
            rows.append({"header": "Current unlock", "detail": unlock, "color": (180, 202, 224)})
        ability_key = getattr(self, "active_ability", "")
        if ability_key and ability_key in ABILITY_POOL:
            spec = ABILITY_POOL[ability_key]
            rows.append({"header": f"Ability: {spec['name']}", "detail": spec["description"], "color": (196, 160, 255)})
        elif level >= 4:
            rows.append({"header": "Ability: None chosen", "detail": "No ability active.", "color": (140, 140, 160)})
        track = self.dominant_track()
        if track:
            label = self.track_tier_label(track[0], track[1])
            rows.append({"header": f"Role: {label}", "detail": f"Lead track: {track[0]}.", "color": (160, 210, 180)})
        else:
            rows.append({"header": "Role: Unnamed", "detail": "Complete quests and explore to earn a role.", "color": (140, 148, 156)})
        return rows

    def current_journal_summary_lines(self):
        counts = self.quest_summary_counts()
        track = self.dominant_track()
        track_label = self.track_tier_label(track[0], track[1]) if track else "Unnamed"
        if self.journal_tab == 2:
            level = getattr(self, "player_level", 1)
            title = self.player_title() if hasattr(self, "player_title") else "Wanderer"
            lines = [f"Level {level} — {title}"]
        elif self.journal_tab == 3:
            town_count = sum(1 for s in self.world_regions.values() if s.get("region_type") == "town")
            lines = [f"{town_count} town{'s' if town_count != 1 else ''} visited"]
        elif self.journal_tab == 0:
            lines = [f"{counts['active']} active"]
        else:
            lines = [
                f"{counts['completed']} completed",
                f"Towns helped {counts['towns_helped']}  -  D {counts['delivery']} / S {counts['scout']} / B {counts['bounty']} / C {counts['chain']}",
                f"Role: {track_label}",
            ]
        if self.region_type == "town" and self.journal_tab not in (2, 3):
            lines.append(
                f"Town standing {self.town_attitude_label()}  -  Prosperity {self.town_prosperity_label(self.world_position)}"
            )
        return lines

    def town_reputation_rows(self):
        rows = []
        for key, state in self.world_regions.items():
            if state.get("region_type") != "town":
                continue
            try:
                px, py = key.split(",")
                coord = (int(px), int(py))
            except (ValueError, AttributeError):
                continue
            name = state.get("region_name", key)
            label = self.town_attitude_label(coord)
            prosperity = self.town_prosperity_label(coord)
            score = self.town_attitude_score(coord)
            rows.append({"name": name, "label": label, "prosperity": prosperity, "score": score})
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows
