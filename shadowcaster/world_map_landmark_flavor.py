LANDMARK_IDENTITIES = {
    "town": ("Settlement", "A place to rest, barter, and gather leads.", "Safe services and new rumors.", "Expect residents, boards, and resupply."),
    "monster_town": ("Monster Town", "A hostile settlement where every street is compromised.", "High danger, uncommon rewards.", "Treat every lane like contested ground."),
    "cave": ("Cave Mouth", "A rough descent into cramped underground passages.", "Depth rewards and hidden gear.", "Useful when you want a quick, risky delve."),
    "dungeon": ("Dungeon Gate", "A structured delve that rewards preparation.", "Strong bottom-floor cache.", "Usually a committed push rather than a quick stop."),
    "castle": ("Castle Site", "A fortified site with heavier resistance.", "Tougher fights and sturdier loot.", "Best approached when resources are healthy."),
    "ruins": ("Ruin Site", "Broken remains that may still hide supplies or secrets.", "Mixed danger and useful finds.", "Expect uneven footing and uncertain payoff."),
    "waystone": ("Waystone", "A worked stone tied to older routes and trail memory.", "Usually grants a clean expedition boon.", "Often worth touching even on a longer route."),
    "barrow": ("Barrow", "An old burial mound with a lingering sense of claim.", "Short risk for a notable payoff.", "Feels older and stranger than the roads around it."),
    "stone_circle": ("Stone Circle", "A ritual ring that still seems to hold attention.", "Mystic boon or uncommon support.", "Best treated like a deliberate stop, not background scenery."),
    "oasis": ("Oasis", "A rare pocket of relief along a punishing route.", "Recovery and route-stabilizing value.", "Especially valuable in attrition-heavy country."),
    "hot_spring": ("Hot Spring", "A natural rest pocket where the frontier briefly softens.", "Reliable healing and reset value.", "A strong recovery waypoint during long pushes."),
    "watchtower": ("Watchtower", "A vantage post built to read movement and distance.", "Intel, warnings, or route clarity.", "Strong pick when you want safer follow-up choices."),
    "grove": ("Grove", "A quiet living pocket that feels protected for a reason.", "Natural boon and gentle support.", "Often a lower-pressure detour with good upside."),
    "necropolis": ("Necropolis", "A larger field of the dead, more deliberate than a single barrow.", "High-risk occult reward.", "Signals danger before you even step inside."),
    "geyser": ("Geyser Field", "A volatile vent site that reshapes the ground around it.", "Sharp payoff with environmental flavor.", "Worth reading before charging straight through."),
    "standing_stone": ("Standing Stone", "A lone marker left to outlast the people who raised it.", "Minor boon or route curiosity.", "Good as a quick detour when nearby."),
    "camp": ("Camp", "A recent frontier stop with signs of trade, retreat, or loss.", "Supplies or trail intel.", "Feels tied to current movement through the region."),
    "inn": ("Inn", "A traveler stop where you can recover before pressing on.", "A free rest on first entry.", "Useful when you need to stabilize a longer run."),
    "clinic": ("Clinic", "A place to patch wounds and clear lingering afflictions.", "Healing and status relief.", "Important if nearby regions inflict poison or burn."),
    "supply": ("Provisioner", "A stock point for ammunition and field medicine.", "Resupply and barter.", "Good anchor for ranged-heavy or attrition-heavy routes."),
    "shrine": ("Forgotten Shrine", "An old roadside altar, still tended by something unseen.", "Full healing and status cleanse.", "Feels like a deliberate reset button."),
    "cache": ("Hidden Cache", "Someone buried supplies here and never came back.", "Substantial supply haul.", "A high-value stop when you're running lean."),
    "smith": ("Smithy", "A work site where gear and trail readiness matter.", "Refit and tonic support.", "Best used before committing to harsher territory."),
    "cartographer": ("Survey Office", "A chart room that turns travel into knowledge.", "Nearby regions revealed.", "Great when you want stronger route choice over raw power."),
}

BIOME_FLAVOR = {
    "forest": "Often hidden among tree cover and winding trails.",
    "plains": "Usually visible from a distance across open ground.",
    "farmland": "Tied closely to roads, labor, and nearby settlements.",
    "desert": "Travel there is exposed, thirsty, and hard to recover from.",
    "swamp": "Approach is awkward and often shaped by poison or poor footing.",
    "mountain": "Getting there safely matters almost as much as what lies inside.",
    "badlands": "The route itself can be harsher than the destination.",
    "tundra": "Exposure and distance are part of the threat profile.",
    "volcanic": "Heat and attrition make each push more committal.",
}


def landmark_site_outlook(counts):
    if counts["entered"] > 0:
        return "Open site leads remain here."
    if counts["located"] > 0:
        return "Known sites are marked but not yet entered."
    if counts["cleared"] > 0 and counts["unvisited"] == 0 and counts["located"] == 0 and counts["entered"] == 0:
        return "All known sites here have been resolved."
    if counts["unvisited"] > 0:
        return "This region may still hide undiscovered places."
    return "No notable site pressure here right now."


def landmark_identity(region_name, parent_biome, landmark_kind):
    label, hook, reward, travel_note = LANDMARK_IDENTITIES.get(
        landmark_kind,
        (
            landmark_kind.replace("_", " ").title(),
            f"A notable site in {region_name}.",
            "Unknown opportunities.",
            "Worth checking once you have a reason to care.",
        ),
    )
    return {
        "label": label,
        "hook": hook,
        "reward_hint": reward,
        "travel_note": travel_note,
        "biome_flavor": BIOME_FLAVOR.get(parent_biome),
    }
