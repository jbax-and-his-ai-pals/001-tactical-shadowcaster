from __future__ import annotations

from ..game_typing import GameMixinBase
from ..quest_flavor import (
    ARCHETYPE_BOUNTY_INTROS,
    ARCHETYPE_DELIVERY_INTROS,
    ARCHETYPE_SCOUT_INTROS,
    BOUNTY_INTROS,
    CHAIN_RETURN_LINES,
    DELIVERY_INTROS,
    SCOUT_INTROS,
    archetype_flavored_text,
    flavored_text,
)


class QuestTextMixin(GameMixinBase):
    _QUEST_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    _QUEST_DIR_NAMES = {
        (1, 0): "east",
        (-1, 0): "west",
        (0, 1): "south",
        (0, -1): "north",
        (1, 1): "southeast",
        (1, -1): "northeast",
        (-1, 1): "southwest",
        (-1, -1): "northwest",
    }
    _DELIVERY_ITEMS = [
        ("quest_letter", "Sealed Letter", "a sealed letter", (220, 210, 160)),
        ("quest_package", "Small Package", "a small package", (160, 130, 100)),
        ("quest_medicine", "Medicine Bundle", "a medicine bundle", (160, 210, 180)),
        ("quest_parcel", "Wrapped Parcel", "a wrapped parcel", (190, 180, 140)),
    ]
    _CHAIN_LEADS = [
        ("Strange markings were spotted near {landmark} in {region}. Someone at {civic} wants proper eyes on it.", "ammo", "field notes"),
        ("Word came through {work} that {landmark} in {region} has gone quiet. We need a first-hand account.", "medkit", "a witness sketch"),
        ("A courier passing {town} mentioned something odd about {landmark} near {region}. Worth a look.", "tonic", "a courier's note"),
        ("A trader reached {work} with news of {landmark} out in {region}. The details did not add up.", "intel", "a trader's ledger scrap"),
        ("The scouts at {civic} flagged {landmark} in {region} as worth checking before the next route posting.", "ammo", "survey marks"),
        ("An old map note kept near {home} pointed to {landmark} somewhere around {region}. Confirm it still stands.", "tonic", "a map rubbing"),
    ]
    _CHAIN_FALLBACK_LEADS = [
        ("Someone passed through {town} with unsettled news from {region}. Survey the area and bring back what you find.", "ammo", "field notes"),
        ("The routes discussed at {civic} have ignored {region} for too long. A firsthand look would help.", "intel", "a survey sketch"),
    ]
    _CHAIN_REWARD_LABELS = {
        "ammo": "+2 ammo",
        "medkit": "+1 healing potion",
        "tonic": "+1 tonic",
        "intel": "route intel",
    }
    _CHAIN_OBJECTIVE_LABELS = {
        "survey": "Survey",
        "recover": "Recover",
        "hunt": "Hunt",
        "clear_landmark": "Clear",
    }
    _PRIORITY_THEME_LABELS = {
        "watch": "Watch Contract",
        "survey": "Survey Contract",
        "relief": "Relief Contract",
    }
    _BOUNTY_TARGETS = {
        "forest": "drive off prowlers",
        "plains": "thin the roaming pack",
        "farmland": "clear raiders from the fields",
        "desert": "hunt the road stalkers",
        "swamp": "cut down the marsh predators",
        "mountain": "break the pass ambushers",
        "badlands": "scatter the canyon raiders",
        "tundra": "cull the frost-bitten hunters",
        "volcanic": "put down the ash-born threat",
        "ruins": "clean out the ruin-haunters",
        "castle": "push back the garrison remnants",
        "cave": "clear the cave mouth",
        "dungeon": "cut down the delve hostiles",
        "monster_town": "survive the hostile streets",
    }

    def quest_direction_name(self, from_world_pos, to_world_pos):
        dx = to_world_pos[0] - from_world_pos[0]
        dy = to_world_pos[1] - from_world_pos[1]
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        return self._QUEST_DIR_NAMES.get((step_x, step_y), "unknown")

    def quest_preview_region_state(self, coord):
        if not self.in_local_region() and coord == self.world_position:
            return self.snapshot_current_region()
        key = self.region_key(coord)
        state = self.world_regions.get(key)
        if state is not None:
            return state
        state = self.preview_world_regions.get(key)
        if state is None:
            state = self.create_world_region_state(coord)
            self.preview_world_regions[key] = state
        return state

    def scout_target_details(self, coord, seed_value):
        state = self.quest_preview_region_state(coord)
        region_name = state.get("region_name", f"Region {coord[0]}, {coord[1]}")
        landmarks = list(state.get("landmarks", []))
        if not landmarks:
            return region_name, "", ""
        landmark = landmarks[seed_value % len(landmarks)]
        return region_name, landmark.name, landmark.kind

    def town_biome_context(self):
        return getattr(self.dungeon, "metadata", {}).get("town_parent_biome", "plains")

    def _board_archetype(self):
        if hasattr(self, "town_archetype") and self.region_type == "town":
            return self.town_archetype()
        return "survivor"

    def quest_posting_cycle(self) -> int:
        return sum(1 for quest in self.active_quests if quest.status == "complete" and quest.from_world_pos == self.world_position)

    def bounty_target_details(self, coord):
        state = self.quest_preview_region_state(coord)
        region_type = state.get("region_type", "plains")
        region_name = state.get("region_name", f"Region {coord[0]}, {coord[1]}")
        objective = self._BOUNTY_TARGETS.get(region_type, "deal with the local threat")
        danger_tier = max(1, int(state.get("danger_tier", 1)))
        return region_name, region_type, objective, danger_tier

    def scout_description(self, region_name, dir_name, landmark_name, seed_value, landmark_kind="", region_type="", danger_tier=1):
        biome = self.town_biome_context()
        ctx = self.notice_board_context()
        intro = archetype_flavored_text(ARCHETYPE_SCOUT_INTROS, self._board_archetype(), ctx, seed_value) \
            or flavored_text(SCOUT_INTROS, biome, ctx, seed_value)
        if landmark_name:
            base = f"{intro} Travel to {region_name} to the {dir_name}, confirm {landmark_name}, then return to {self.region_name}."
        else:
            base = f"{intro} Travel to {region_name} to the {dir_name}, survey the area, then return to {self.region_name}."
        intel = self._quest_intel_suffix(region_type, danger_tier, landmark_kind)
        return f"{base} {intel}".strip() if intel else base

    def _quest_intel_suffix(self, region_type, danger_tier, landmark_kind=None):
        """One or two sentences of pre-arrival context about the destination."""
        landmark_notes = {
            "barrow":        "Local word: an old burial mound — grave goods may remain.",
            "dungeon":       "Local word: a deep site, expect organized resistance inside.",
            "castle":        "Local word: a fortification — well-guarded but worth the trip.",
            "ruins":         "Local word: ruins that still draw scavengers.",
            "cave":          "Local word: a cave system that runs deeper than it looks.",
            "shrine":        "Local word: an old shrine, still active by some accounts.",
            "grove":         "Local word: a dense grove — worth the detour.",
            "necropolis":    "Local word: a necropolis — wealth and risk in equal measure.",
            "monster_town":  "Local word: hostile ground. Clear the gate before pushing in.",
            "watchtower":    "Local word: a watchtower with a clear view of the roads.",
            "waystone":      "Local word: a waystone — old routes marked in stone.",
            "standing_stone":"Local word: a standing stone with old directions scratched into it.",
            "oasis":         "Local word: a clean oasis — water and rest before the next stretch.",
            "hot_spring":    "Local word: a hot spring — good for clearing ailments.",
            "stone_circle":  "Local word: a stone circle with a palpable resonance.",
            "geyser":        "Local word: a geyser — a traveler's kit was spotted nearby.",
            "camp":          "Local word: an abandoned camp — someone left in a hurry.",
        }
        type_notes = {
            "dungeon":       "Organized resistance expected inside.",
            "castle":        "The site is fortified — come prepared.",
            "ruins":         "Scavengers have been through; something may still be worth finding.",
            "cave":          "The cave system runs deeper than it looks.",
            "monster_town":  "Hostile ground. Push in ready to fight.",
            "shrine":        "The shrine still draws travelers.",
        }
        parts = []
        if landmark_kind and landmark_kind in landmark_notes:
            parts.append(landmark_notes[landmark_kind])
        elif region_type in type_notes:
            parts.append(type_notes[region_type])
        if danger_tier >= 3:
            parts.append("Danger runs high in this stretch — come ready.")
        elif danger_tier >= 2:
            parts.append(f"Threat tier {danger_tier} reported in the area.")
        return " ".join(parts)

    def delivery_description(self, desc, region_name, dir_name, seed_value, region_type="", danger_tier=1):
        biome = self.town_biome_context()
        ctx = self.notice_board_context()
        intro = archetype_flavored_text(ARCHETYPE_DELIVERY_INTROS, self._board_archetype(), ctx, seed_value) \
            or flavored_text(DELIVERY_INTROS, biome, ctx, seed_value)
        base = f"{intro} Carry {desc} to {region_name} to the {dir_name}."
        intel = self._quest_intel_suffix(region_type, danger_tier)
        return f"{base} {intel}".strip() if intel else base

    def bounty_description(self, region_name, dir_name, objective, region_type, seed_value, danger_tier=1):
        biome = self.town_biome_context()
        ctx = self.notice_board_context()
        intro = archetype_flavored_text(ARCHETYPE_BOUNTY_INTROS, self._board_archetype(), ctx, seed_value) \
            or flavored_text(BOUNTY_INTROS, biome, ctx, seed_value)
        base = f"{intro} Travel to {region_name} to the {dir_name}, {objective}, then return to {self.region_name}."
        intel = self._quest_intel_suffix(region_type, danger_tier)
        return f"{base} {intel}".strip() if intel else base

    def chain_description(self, landmark_name, region_name, dir_name, lead_template, seed_value):
        context = {**self.notice_board_context(), "landmark": landmark_name, "region": region_name, "dir_name": dir_name}
        text = lead_template.format(**context)
        return_line = flavored_text(CHAIN_RETURN_LINES, self.town_biome_context(), self.notice_board_context(), seed_value)
        return f"{text} {return_line}"

    def chain_fallback_description(self, region_name, dir_name, lead_template, seed_value):
        context = {**self.notice_board_context(), "region": region_name, "dir_name": dir_name}
        text = lead_template.format(**context)
        return_line = flavored_text(CHAIN_RETURN_LINES, self.town_biome_context(), self.notice_board_context(), seed_value)
        return f"{text} {return_line}"

    def chain_mid_message(self, landmark_name, region_name):
        if landmark_name:
            return f"Lead confirmed: {landmark_name} in {region_name}. Return to {self.region_name} for payment."
        return f"Survey complete in {region_name}. Return to {self.region_name} for payment."

