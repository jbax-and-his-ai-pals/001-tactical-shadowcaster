def site_state_lines(stats):
    if not stats["landmarks_total"]:
        return ["No major sites marked here yet."]
    lines = [
        f"Hidden {stats['landmarks_unvisited']}  /  Marked {stats['landmarks_located_only']}  /  Open {stats['landmarks_open']}  /  Cleared {stats['landmarks_cleared']}",
        f"Entered {stats['landmarks_entered']} of {stats['landmarks_total']} sites.",
    ]
    if stats["landmark_type_counts"]:
        lines.append("Site mix: " + ", ".join(stats["landmark_type_counts"][:4]))
    return lines


def opportunity_lines(stats):
    lines = []
    if stats.get("active_quest_targets_here"):
        lines.append("Active work is already pulling you here.")
    elif stats.get("active_quest_turnins_here"):
        lines.append("This is a strong return stop for current work.")

    if stats["landmarks_open"] > 0:
        lines.append("Open sites make this a good immediate push.")
    elif stats["landmarks_located_only"] > 0:
        lines.append("Marked sites make this a good scouting follow-up.")
    elif stats["landmarks_unvisited"] > 0:
        lines.append("Unseen sites make this better for broad exploration.")

    if stats["settlement_size"]:
        if stats["attitude_score"] >= 6:
            lines.append("Trusted standing here means stronger contracts and services.")
        elif stats["attitude_score"] >= 1:
            lines.append("Steady local standing makes this a useful hub stop.")
        else:
            lines.append("A little local work could improve this town's value quickly.")

    if stats["max_depth"] > 1 and not stats["bottom_reward_claimed"]:
        lines.append("An uncleared deep reward still waits somewhere below.")

    if stats["foes_remaining"] == 0 and stats["exploration"] < 100:
        lines.append("Low combat pressure makes this a safe cleanup route.")
    elif stats["foes_remaining"] > 0 and stats["danger_tier"] >= 3:
        lines.append("Expect a committed run rather than a casual detour.")

    if not lines:
        lines.append("No urgent pressure here; choose this region for route continuity or cleanup.")
    return lines[:4]
