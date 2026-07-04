_BIOME_THREAT_HINT = {
    "forest": "pouncers — fast melee rushers, fragile",
    "swamp": "boglings and shamans — poison risk at range",
    "mountain": "sentinels — high HP, slow advance",
    "tundra": "sentinels — high HP, slow advance",
    "plains": "archers — ranged harassment, prefer distance",
    "farmland": "archers and stalkers — mixed threat",
    "desert": "archers and hexers — ranged status pressure",
    "badlands": "archers and hexers — aggressive ranged pressure",
    "volcanic": "shamans — burn on hit, prefer distance",
    "cave": "boglings and lurkers — ambush in tight corridors",
    "maze": "boglings — ambush pressure in winding corridors",
    "dungeon": "lurkers — fast ambushers, close fast",
    "ruins": "sentinels and lurkers — mixed melee",
    "castle": "sentinels and wardens — high-HP blockers",
    "monster_town": "settlers and beasts — coordinated swarms",
}

_BIOME_HARVEST_HINT = {
    "farmland": "Grain harvest available — provisioner trade.",
    "plains": "Grain harvest available — provisioner trade.",
    "forest": "Herb harvest available — provisioner trade.",
    "swamp": "Herb harvest available — provisioner trade.",
    "tundra": "Herb harvest available — provisioner trade.",
    "mountain": "Ore harvest available — provisioner trade.",
}


def forecast_lines(region_type, danger_tier):
    lines = []
    hint = _BIOME_THREAT_HINT.get(region_type)
    if hint:
        lines.append(f"Threats: {hint}.")
    if danger_tier <= 1:
        lines.append("Loot grade: basic — common gear, small gold.")
    elif danger_tier <= 2:
        lines.append("Loot grade: standard — mixed gear, moderate gold.")
    elif danger_tier <= 3:
        lines.append("Loot grade: good — quality gear likely, strong rewards.")
    else:
        lines.append("Loot grade: high — rare equipment and significant gold.")
    harvest = _BIOME_HARVEST_HINT.get(region_type)
    if harvest:
        lines.append(harvest)
    return lines


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
